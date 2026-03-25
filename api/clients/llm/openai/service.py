from openai import AsyncOpenAI
import openai 
from shared.core.exceptions import OpenaiException
from api.clients.llm.base_service import BaseLLMService
from typing import AsyncGenerator


class OpenaiService(BaseLLMService):
    def __init__(self):
        self.client = AsyncOpenAI()

    async def embed_text(self, text:str) ->list[float]:
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except openai.AuthenticationError:
            raise OpenaiException(operation="embed_text", detail="invalid API Key")
        except openai.RateLimitError:
            raise OpenaiException(operation="embed_text", detail="Rate Limit")
        except openai.APIConnectionError:
            raise OpenaiException(operation="embed_text", detail="connection error")
        except openai.APIError as e:
            raise OpenaiException(operation="embed_text", detail=str(e))
        
    async def create_message(self, texts:list[str], user_input:str) ->AsyncGenerator[str , None]:
        try:
            input_string = "\n\n".join(texts)
            stream = await self.client.responses.create(
                model="gpt-5.4-nano",
                stream= True,
                input= [
                {
                    "role": "user",
                    "content": f"Create a response and primarily focus on information from this string: {input_string}. If the string is empty or simply no relevant information to the message are given, answer the question with all your basic knowledge and do not rely on the information string. The user message or input is: {user_input}"
                }
                ]
            )
            async for event in stream:
                if event.type == "response.output_text.delta":
                    yield event.delta
        except openai.AuthenticationError:
            raise OpenaiException(operation="create_message", detail="invalid API Key")
        except openai.RateLimitError:
            raise OpenaiException(operation="create_message", detail="Rate Limit")
        except openai.APIConnectionError:
            raise OpenaiException(operation="create_message", detail="connection error")
        except openai.APIError as e:
            raise OpenaiException(operation="create_message", detail=str(e))
        