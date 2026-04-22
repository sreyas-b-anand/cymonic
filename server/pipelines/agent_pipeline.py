import logging
from agents import FactAgent , WriterAgent  , EditorAgent
from services.llm_services import GroqClient

logger = logging.getLogger(__name__)


class AgentPipeline:
    def __init__(self):
        groq_client = GroqClient(model="llama-3.3-70b-versatile")
        self.fact_agent = FactAgent(groq_client)
        self.writer_agent = WriterAgent(groq_client)
        self.editor_agent = EditorAgent(groq_client)

    async def run(self, source_text: str):
        facts = await self.fact_agent.run(source_text)

        logger.info("facts_extracted: %s", facts)
        
        draft = await self.writer_agent.generate(facts)
        
        logger.info("draft_generated: %s", draft)
        
        edited = await self.editor_agent.review(facts, draft)
        
        logger.info("draft_reviewed: %s", edited)
        

        return edited