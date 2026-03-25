from openai import OpenAI
import openai 
from shared.core.exceptions import OpenaiException


class OpenaiService:
    def __init__(self):
        self.client = OpenAI()

    def embed_text(self, chunks: list[str]) -> list[list[float]]:
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=chunks
            )
            return [item.embedding for item in response.data]
        except openai.AuthenticationError:
            raise OpenaiException(operation="embed_text", detail="invalid API Key")
        except openai.RateLimitError:
            raise OpenaiException(operation="embed_text", detail="Rate Limit")
        except openai.APIConnectionError:
            raise OpenaiException(operation="embed_text", detail="connection error")
        except openai.APIError as e:
            raise OpenaiException(operation="embed_text", detail=str(e))