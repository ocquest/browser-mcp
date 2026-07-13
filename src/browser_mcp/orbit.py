import base64
from openai import AsyncOpenAI

_client = None


def init_orbit(api_key: str, base_url: str):
    global _client
    _client = AsyncOpenAI(api_key=api_key, base_url=f"{base_url}/openai/v1")


async def ask_orbit(prompt: str, image_b64: str) -> str:
    if _client is None:
        return "OrbitLLM not initialized. Call init_orbit() first."
    try:
        resp = await _client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_b64}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            ],
            max_tokens=4096,
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        return f"OrbitLLM error: {e}"
