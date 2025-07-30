from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
import re
from .settings import settings
from .schemas import UserInput
from .logging import logger

qa_prompt_template = """
Respond with only a single word: TRUE or FALSE.
Analyze the text for swear words or obscene language.
If the text contains any swear words, answer FALSE.
If the text is clean, answer TRUE.


Text: {question}
Answer:
"""

prompt = PromptTemplate(
    input_variables=["question"],
    template=qa_prompt_template
)

async def check_honesty(user_message: UserInput) -> dict:
    logger.info("check_honesty function")
    user_message = f"Name of recipient: {user_message.name}, reason of message: {user_message.reason}"
    logger.debug(user_message)
    formatted_prompt = prompt.format(question=user_message)
    logger.debug(formatted_prompt)
    try: 
        messages = [HumanMessage(content=formatted_prompt)]
        result = await settings.llm.ainvoke(messages)
        return {
            "result": result.content if hasattr(result, "content") else str(result)
        }
    except Exception as e:
        raise  


async def check_response(result: dict):
    logger.debug(f"result dict: {result}, {result['result'].lower()}")
    raw_text = result.get('result', '')
    found = re.findall(r'\b(TRUE|FALSE)\b', raw_text, re.IGNORECASE)
    if found:
        last_match = found[-1].upper()
        return last_match == "TRUE"
    return False
