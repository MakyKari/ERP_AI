import logging
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)


class ChecklistDataCollector:

    @staticmethod
    def collect_checklist_data(
        cursor, 
        table_ending: str, 
        checklist_code: int
    ) -> Optional[pd.DataFrame]:

        query = f"""
            SELECT 
                m.code as checklist_code,
                m.stdate,
                m.endate,
                p.charcode,
                p.grade,
                n.name as category_name
            FROM dbai.m_checklist_{table_ending} m
            JOIN dbai.mc_checkpart_{table_ending} p ON m.code = p.checkcode
            JOIN dbai.rep_char c ON p.charcode = c.code
            JOIN dbai.rep_names n ON c.namecode = n.code AND n.langid = 1049
            WHERE m.code = %s
            ORDER BY p.charcode;
        """
        
        try:
            cursor.execute(query, (checklist_code,))
            results = cursor.fetchall()
            
            if not results:
                logger.warning(f"Нет данных для чеклиста {checklist_code} ({table_ending})")
                return None
            
            df = pd.DataFrame(results)
            logger.info(f"Собрано {len(df)} записей для чеклиста {checklist_code}")
            return df
            
        except Exception as e:
            logger.error(f"Ошибка при сборе данных чеклиста {checklist_code}: {e}")
            return None