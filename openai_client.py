import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    logger.error("OPENAI_API_KEY не установлен в переменных окружения!")
    raise ValueError("OPENAI_API_KEY is required")

client = OpenAI(api_key=api_key)


def call_openai(messages, model="gpt-4o-mini", max_tokens=10000):
    """
    Вызов OpenAI API
    
    Args:
        messages: Список сообщений для чата
        model: Модель GPT (по умолчанию gpt-4o-mini)
        max_tokens: Максимальное количество токенов в ответе
        
    Returns:
        Текст ответа от GPT или сообщение об ошибке
    """
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error("OpenAI error: %s", e)
        return f"[OpenAI error: {e}]"
