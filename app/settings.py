from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from typing import Optional
from langchain_openai import ChatOpenAI

class PublisherSettings(BaseSettings):
    MODEL_NAME: str
    OPENROUTER_TOKEN: str
    PROVIDER: str
    AWS_REGION: str
    SQS_QUEUE_URL: str
    SERVICE_2_URL: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    llm: Optional[ChatOpenAI] = None

    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "./../.env"), extra="ignore")

    def get_key_provider(self) -> str:
        return self.PROVIDER
    
    def get_llm_name(self) -> str:
        return self.MODEL_NAME

    def get_llm_token(self) -> str:
        return self.OPENROUTER_TOKEN

    def get_aws_region(self) -> str:
        return self.AWS_REGION
    
    def get_sqs_url(self) -> str:
        return self.SQS_QUEUE_URL
    
    def get_service2_url(self) -> str:
        return self.SERVICE_2_URL
    
    def get_access_key_id(self):
        return self.AWS_ACCESS_KEY_ID
    
    def get_access_secret_key(self):
        return self.AWS_SECRET_ACCESS_KEY

settings = PublisherSettings()