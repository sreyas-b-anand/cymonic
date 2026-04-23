import logging
from agents import FactAgent, WriterAgent, EditorAgent
from services.llm_services import GroqClient
from langgraph.graph import StateGraph, END
from schemas.graph import GraphState
from config import SupabaseConfig
logger = logging.getLogger(__name__)

ALL_PIECES = ["blog_post", "social_thread", "email_teaser"]
MAX_ITERATIONS = 2


class AgentPipeline:
    def __init__(self):
        
        groq_client = GroqClient(model="llama-3.1-8b-instant")

        self.fact_agent = FactAgent(groq_client)
        self.writer_agent = WriterAgent(groq_client)
        self.editor_agent = EditorAgent(groq_client)

        self.supabase = SupabaseConfig()
        self._build_graph()


    async def fact_node(self, state: GraphState):
        logger.info("fact_node: starting")
        facts = await self.fact_agent.run(state["source_text"])
        return {"fact_sheet": facts, "iterations": 0}

    async def writer_node(self, state: GraphState):
        logger.info("writer_node: starting")
        draft = await self.writer_agent.generate(state["fact_sheet"])

        if not draft or "error" in draft or "blog_post" not in draft:
            logger.error("writer_node: failed — %s", draft)
            return {"drafts": {
                "blog_post": "",
                "social_thread": [],
                "email_teaser": ""
            }}

        return {"drafts": draft}

    async def editor_node(self, state: GraphState):
        logger.info("editor_node: starting (iteration=%d)", state.get("iterations", 0))

        review = await self.editor_agent.review(
            state["fact_sheet"],
            state["drafts"]
        )

        if not review or "error" in review:
            logger.error("editor_node: failed — %s", review)
           
            return {
                "review": review,
                "status": "rejected",
                "feedback": "Editor failed",
                "iterations": state.get("iterations", 0) + 1
            }

        approved = all(review.get(p, {}).get("approved", False) for p in ALL_PIECES)

        feedback = ""
        if not approved:
            feedback = " | ".join(
                f"{p}: {review[p].get('correction_note', '')}"
                for p in ALL_PIECES
                if not review.get(p, {}).get("approved", False)
            )

        logger.info("editor_node: approved=%s", approved)

        return {
            "review": review,
            "status": "approved" if approved else "rejected",
            "feedback": feedback,
            "iterations": state.get("iterations", 0) + 1
        }

    async def revise_node(self, state: GraphState):
        logger.info("revise_node: starting")

        drafts = dict(state.get("drafts", {}))  # copy — don't mutate state directly
        review = state.get("review", {})

        for piece in ALL_PIECES:
            if review.get(piece, {}).get("approved", True):
                logger.info("revise_node: %s already approved — skipping", piece)
                continue

            if piece not in drafts:
                logger.warning("revise_node: %s missing from drafts — skipping", piece)
                continue

            correction_note = review[piece].get("correction_note", "Fix all flagged issues.")
            logger.info("revise_node: revising %s", piece)

            result = await self.writer_agent.revise(
                piece=piece,
                old_draft=drafts[piece],
                correction_note=correction_note,
                fact_sheet=state.get("fact_sheet", {})
            )

            
            if result and "error" not in result and piece in result:
                drafts[piece] = result[piece]
                logger.info("revise_node: %s revised successfully", piece)
            else:
                logger.warning("revise_node: %s revision failed — keeping old draft. result=%s", piece, result)

        return {"drafts": drafts}


    def router(self, state: GraphState) -> str:
        if state.get("status") == "approved":
            logger.info("router: approved -> END")
            return "end"

        if state.get("iterations", 0) >= MAX_ITERATIONS:
            logger.warning("router: max iterations reached -> END")
            return "end"

        logger.info("router: rejected -> revise")
        return "revise"


    def _build_graph(self):
        self.graph = StateGraph(GraphState)

        self.graph.add_node("fact",   self.fact_node)
        self.graph.add_node("writer", self.writer_node)
        self.graph.add_node("editor", self.editor_node)
        self.graph.add_node("revise", self.revise_node)

        self.graph.set_entry_point("fact")

        self.graph.add_edge("fact",   "writer")
        self.graph.add_edge("writer", "editor")

        self.graph.add_conditional_edges(
            "editor",
            self.router,
            {"revise": "revise", "end": END}
        )

        self.graph.add_edge("revise", "editor")

        self.app = self.graph.compile()


    async def run(self, source_text: str):
        result = await self.app.ainvoke({
            "source_text": source_text,
            "fact_sheet": {},
            "drafts": {},
            "review": {},
            "feedback": "",
            "status": "",
            "iterations": 0
        })

        logger.info("pipeline_completed: status=%s iterations=%d",
                    result.get("status"), result.get("iterations", 0))
        
        try:
            self.supabase.client.table("campaigns").insert({
                "input_text": source_text,
                "output": result,
                "status": result.get("status", ""),
                "error": result.get("feedback", ""),
                "iterations": result.get("iterations", 0)
            }).execute()
        except Exception as e:
            logger.error("Error occurred while inserting into Supabase: %s", e)
        
        return result