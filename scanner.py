import logging
from typing import List, Tuple
from config import CHECKLIST_TABLES

logger = logging.getLogger(__name__)


class ChecklistScanner:
    """Сканер чеклистов для поиска непроанализированных записей"""
    
    @staticmethod
    def find_pending_checklists(cursor) -> List[Tuple[str, int, int]]:
        """
        Находит чеклисты, ожидающие анализа
        
        Returns:
            List[Tuple[table_ending, checklist_code, akt_code]]
        """
        pending = []
        
        for table_ending in CHECKLIST_TABLES:
            query = f"""
                SELECT 
                    m.code as checklist_code,
                    m.aktcode,
                    a.aito
                FROM dbai.m_checklist_{table_ending} m
                JOIN dbai.mc_checkakt a ON m.aktcode = a.code
                WHERE m.aktcode != 0 
                  AND a.aito = 1
            """
            
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                
                for row in results:
                    pending.append((
                        table_ending,
                        row['checklist_code'],
                        row['aktcode']
                    ))
                    
                if results:
                    logger.info(f"Найдено {len(results)} записей в m_checklist_{table_ending}")
                
            except Exception as e:
                logger.error(f"Ошибка при сканировании m_checklist_{table_ending}: {e}")
        
        return pending