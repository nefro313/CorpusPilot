import tiktoken

from core.config import get_settings
from services.llm import get_embeddings


async def embed_query(text: str) -> list[float]:
    return await get_embeddings().aembed_query(text)


async def embed_documents(texts: list[str]) -> list[list[float]]:
    return await get_embeddings().aembed_documents(texts)


def estimate_tokens(text: str, model: str | None = None) -> int:
    settings = get_settings()
    model_name = model or settings.openai_chat_model
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))
