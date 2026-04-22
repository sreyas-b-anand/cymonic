def extract_json_fn(response: str):
    import json

    try:
        return json.loads(response)

    except:
        pass

    try:
        # Second attempt: strip wrapper quotes
        cleaned = response.strip()

        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1]

        return json.loads(cleaned)

    except:
        pass

    try:
        # Final fallback: extract braces
        start = response.find("{")
        end = response.rfind("}") + 1

        if start == -1 or end == -1:
            return {
                "error": "No JSON found",
                "raw_output": response
            }

        return json.loads(response[start:end])

    except:
        return {
            "error": "Invalid JSON from LLM",
            "raw_output": response
        }