import time
import logging
from scanner import ChecklistScanner
from collector import ChecklistDataCollector
from ai_analyzer import AIAnalyzer
from updater import ResultUpdater
from checksum_tracker import ChecksumTracker
from database import DatabaseConnection

logger = logging.getLogger(__name__)


class ChecklistAnalyzerService:

    def __init__(self, connection_string: str, poll_interval: int = 60):
        self.connection_string = connection_string
        self.poll_interval = poll_interval
        self.scanner = ChecklistScanner()
        self.collector = ChecklistDataCollector()
        self.analyzer = AIAnalyzer()
        self.updater = ResultUpdater()
        self.checksum_tracker = ChecksumTracker()
    
    def process_checklist(
        self,
        cursor,
        table_ending: str,
        checklist_code: int,
        akt_code: int
    ) -> bool:
        """
        Обрабатывает один чеклист: собирает данные, анализирует, обновляет
        
        Returns:
            True если успешно обработан, False иначе
        """
        logger.info(f"Обработка чеклиста {checklist_code} ({table_ending}), акт {akt_code}")
        
        current_checksum = self.checksum_tracker.calculate_checksum(
            cursor, table_ending, checklist_code
        )
        stored_checksum = self.checksum_tracker.get_stored_checksum(cursor, akt_code)
        
        if current_checksum == stored_checksum and stored_checksum is not None:
            logger.info(f"Чеклист {checklist_code} не изменился, пропускаем")
            return True
        
        if stored_checksum is not None:
            logger.info(f"Обнаружены изменения в чеклисте {checklist_code}, повторный анализ")
        
        # Собираем данные
        df = self.collector.collect_checklist_data(cursor, table_ending, checklist_code)
        if df is None or df.empty:
            logger.warning(f"Нет данных для анализа чеклиста {checklist_code}")
            return False
        
        # Анализируем через ИИ
        ai_response = self.analyzer.analyze(df)
        if ai_response is None:
            logger.error(f"Не удалось получить анализ для чеклиста {checklist_code}")
            return False
        
        # Обновляем результаты
        success = self.updater.update_akt_response(cursor, akt_code, ai_response)
        if not success:
            return False
        
        # Сохраняем контрольную сумму
        self.checksum_tracker.update_checksum(cursor, akt_code, current_checksum)
        
        logger.info(f"Чеклист {checklist_code} успешно обработан")
        return True
    
    def run_cycle(self):
        logger.info("=" * 60)
        logger.info("Начало цикла проверки")
        
        try:
            with DatabaseConnection(self.connection_string) as cursor:
                # Находим все чеклисты, требующие анализа
                pending = self.scanner.find_pending_checklists(cursor)
                
                if not pending:
                    logger.info("Нет чеклистов для обработки")
                    return
                
                logger.info(f"Найдено {len(pending)} чеклистов для обработки")
                
                # Обрабатываем каждый чеклист
                success_count = 0
                for table_ending, checklist_code, akt_code in pending:
                    if self.process_checklist(cursor, table_ending, checklist_code, akt_code):
                        success_count += 1
                
                logger.info(f"Успешно обработано: {success_count}/{len(pending)}")
                
        except Exception as e:
            logger.error(f"Критическая ошибка в цикле проверки: {e}", exc_info=True)
    
    def run_forever(self):
        """Запускает бесконечный цикл мониторинга"""
        logger.info("Запуск сервиса мониторинга чеклистов")
        logger.info(f"Интервал проверки: {self.poll_interval} секунд")
        
        while True:
            try:
                self.run_cycle()
                
            except KeyboardInterrupt:
                logger.info("Получен сигнал остановки, завершение работы")
                break
                
            except Exception as e:
                logger.error(f"Неожиданная ошибка: {e}", exc_info=True)
            
            logger.info(f"Ожидание {self.poll_interval} секунд до следующей проверки...")
            time.sleep(self.poll_interval)