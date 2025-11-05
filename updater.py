import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ResultUpdater:
    @staticmethod
    def update_akt_response(
        cursor,
        akt_code: int,
        ai_response: str
    ) -> bool:

        query = """
            UPDATE dbai.mc_checkakt
            SET 
                airesponse = %s,
                airedate = %s,
                aire = 1
            WHERE code = %s
        """
        
        try:
            current_time = datetime.now()
            cursor.execute(query, (ai_response, current_time, akt_code))
            
            logger.info(f"Акт {akt_code} успешно обновлен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении акта {akt_code}: {e}")
            return False