import logging
from typing import Optional
import pandas as pd
from openai_client import call_openai
from config import ABBREVIATIONS, LEVELS

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Анализатор чеклистов через ИИ"""
    
    @staticmethod
    def build_prompt(df: pd.DataFrame) -> str:
        rows_text = "\n".join(
            f"- Категория: {row['category_name']} (код {row['charcode']}), "
            f"Оценка: {row['grade']}"
            for _, row in df.iterrows()
        )

        return f"""
Ты эксперт по авиационной безопасности, проверяющий авиакомпании.
Используй следующие расшифровки:

{ABBREVIATIONS}

Уровни соответствия / несоответствия:
{LEVELS}

Вот результаты конкретной проверки (чеклист):

{rows_text}

Твоя задача:
1. Дай конкретные рекомендации по устранению несоответствий для этой проверки.
2. Проанализируй тенденции по выявленным позициям (если они повторяются или связаны).
3. Составь сводный вывод о состоянии авиационной безопасности объекта по разделам.

ВАЖНО: Форматируй ответ БЕЗ markdown разметки. Используй только обычный текст, разделенный на параграфы. 
Не используй символы *, #, **, _, и другие markdown элементы. 
Структурируй текст через переносы строк и отступы.
"""
    
    @staticmethod
    def analyze(df: pd.DataFrame) -> Optional[str]:
        try:
            prompt = AIAnalyzer.build_prompt(df)
            messages = [{"role": "user", "content": prompt}]
            response = call_openai(messages)
            
            logger.info("Анализ успешно получен от ИИ")
            return response
            
        except Exception as e:
            logger.error(f"Ошибка при анализе через ИИ: {e}")
            return None