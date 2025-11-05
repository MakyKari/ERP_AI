import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ChecksumTracker:
    """Отслеживает изменения в чеклистах для повторного анализа"""
    
    @staticmethod
    def calculate_checksum(cursor, table_ending: str, checklist_code: int) -> Optional[str]:
        query = f"""
            SELECT 
                STRING_AGG(
                    CONCAT(charcode, ':', grade), 
                    '|' ORDER BY charcode
                ) as checksum
            FROM dbai.mc_checkpart_{table_ending}
            WHERE checkcode = %s
        """
        
        try:
            cursor.execute(query, (checklist_code,))
            result = cursor.fetchone()
            return result['checksum'] if result else None
            
        except Exception as e:
            logger.error(f"Ошибка при вычислении контрольной суммы: {e}")
            return None
    
    @staticmethod
    def get_stored_checksum(cursor, akt_code: int) -> Optional[str]:
        query = """
            SELECT aichecksum
            FROM dbai.mc_checkakt
            WHERE code = %s
        """
        
        try:
            cursor.execute(query, (akt_code,))
            result = cursor.fetchone()
            return result['aichecksum'] if result and result['aichecksum'] else None
            
        except Exception as e:
            logger.error(f"Ошибка при получении контрольной суммы: {e}")
            return None
    
    @staticmethod
    def update_checksum(cursor, akt_code: int, checksum: str) -> bool:
        query = """
            UPDATE dbai.mc_checkakt
            SET aichecksum = %s
            WHERE code = %s
        """
        
        try:
            cursor.execute(query, (checksum, akt_code))
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении контрольной суммы: {e}")
            return False