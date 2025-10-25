from os import getenv
import logging
import httpx
from mcp.server import Server, Tool, ToolType
import mcp.types as types

# Configure logging for debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server-chatgpt-codex")

OPENAI_API_KEY = getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY environment variable not set!")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

server = Server("mcp-server-chatgpt-codex")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        Tool(
            id="chatgpt-codex",
            description="OpenAI Codex code assistant",
            tool_type=ToolType.CODE,
        )
    ]

@server.tool("chatgpt-codex")
async def run_codex(messages: list[types.Message]) -> types.Message:
    prompt = messages[-1].content

    json_body = {
        "model": "code-davinci-002",  # Update to latest recommended Codex model
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.3,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "n": 1,
        "stop": None,
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(OPENAI_API_URL, json=json_body, headers=headers)
            response.raise_for_status()
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            logger.info("Codex API call successful.")
            return types.Message(role=types.Role.ASSISTANT, content=answer)

    except httpx.HTTPStatusError as exc:
        logger.error(f"HTTP error from OpenAI API: {exc.response.status_code} - {exc.response.text}")
        return types.Message(role=types.Role.ASSISTANT, content="Error: failed to call OpenAI API.")
    except Exception as exc:
        logger.error(f"Unexpected error: {exc}")
        return types.Message(role=types.Role.ASSISTANT, content="Error: unexpected error in Codex server.")

if __name__ == "__main__":
    logger.info("Starting ChatGPT Codex MCP server...")
    server.run()
