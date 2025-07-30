import aioboto3
import httpx
from .settings import settings
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse

from langchain_openai import ChatOpenAI

from .llm_integration import check_honesty, check_response
from  .schemas import UserInput
from .logging import logger

session = aioboto3.Session()

# sqs_client = boto3.client(
#     "sqs",
#     region_name=settings.get_aws_region(),
#     aws_access_key_id=settings.get_access_key_id(),
#     aws_secret_access_key=settings.get_access_secret_key()
# )

def get_llm_client():
    llm = ChatOpenAI(
        model = settings.get_llm_name(),
        api_key = settings.get_llm_token(),
        base_url= settings.get_key_provider()
    )
    settings.llm = llm
    return llm

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_llm_client()
    yield

publisher_app = FastAPI(lifespan=lifespan)

@publisher_app.get("/")
async def root():
    return RedirectResponse(url="/send/", status_code=307)

@publisher_app.post("/send/")
async def send(user_input: UserInput):
    result = await check_honesty(user_input)
    is_honest = await check_response(result)
    logger.debug(f"Message passed check: {is_honest}")
    if not is_honest:
        raise HTTPException(status_code=400, detail="Input is not valid.")
    async with session.client(
        "sqs",
        region_name=settings.get_aws_region(),
        aws_access_key_id=settings.get_access_key_id(),
        aws_secret_access_key=settings.get_access_secret_key()
    ) as sqs_client:
        try:
            logger.debug("start sending to queque")
            message_body = user_input.model_dump_json()
            await sqs_client.send_message(
                QueueUrl=settings.get_sqs_url(),
                MessageBody=message_body
            )
            logger.debug("end sending to queque")
            timeout = httpx.Timeout(60.0) 
            async with httpx.AsyncClient(timeout=timeout) as client:
                response_from_service2 = await client.post(settings.get_service2_url(), json=user_input.model_dump())
                response_from_service2.raise_for_status()
                logger.debug(f"letter wrote. Inside: {response_from_service2}")
                return JSONResponse(
                        status_code=202, 
                        content=response_from_service2.json()
                    )
        except Exception as e:
            logger.error(f"Failed to send message to SQS: {e}")
            raise HTTPException(status_code=500, detail="Failed to send message to queue.")
    # try:
        # timeout = httpx.Timeout(60.0) 
        # async with httpx.AsyncClient(timeout=timeout) as client:
        #     response_from_service2 = await client.post(settings.get_service2_url(), json=user_input.model_dump())
        #     response_from_service2.raise_for_status()
        #     logger.debug(f"letter wrote. Inside: {response_from_service2}")
        #     return JSONResponse(
        #             status_code=202, 
        #             content=response_from_service2.json()
        #         )
    # except Exception as e:
    #     logger.error(f"Message was sent to SQS, but failed to call Service 2: {e}")
    #     raise HTTPException(status_code=503, detail="Service 2 is unavailable.")
