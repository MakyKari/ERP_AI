import sys
import logging
import argparse
from service import ChecklistAnalyzerService
from config import POLL_INTERVAL

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('checklist_analyzer.log')
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='AI Checklist Analyzer Service для мониторинга авиационных чеклистов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py "postgresql://user:pass@localhost:5432/new_air_inc_db"
  python main.py "postgresql://user:pass@localhost/new_air_inc_db" --interval 120
  python main.py "postgresql://user:pass@localhost/new_air_inc_db" --once
        """
    )
    
    parser.add_argument(
        'connection_string',
        type=str,
        help='PostgreSQL connection string (postgresql://user:password@host:port/dbname)'
    )
    
    parser.add_argument(
        '-i', '--interval',
        type=int,
        default=POLL_INTERVAL,
        help=f'Интервал проверки в секундах (по умолчанию: {POLL_INTERVAL})'
    )
    
    parser.add_argument(
        '--once',
        action='store_true',
        help='Выполнить один цикл проверки и завершить работу'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Детальный вывод (DEBUG уровень)'
    )
    
    return parser.parse_args()


def main():
    args = parse_arguments()
    
    # Настройка уровня логирования
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Включен DEBUG режим")
    
    logger.info("=" * 60)
    logger.info("AI Checklist Analyzer Service")
    logger.info("=" * 60)
    logger.info(f"Connection string: {args.connection_string}")
    logger.info(f"Poll interval: {args.interval} секунд")
    logger.info(f"Mode: {'одиночный запуск' if args.once else 'постоянный мониторинг'}")
    logger.info("=" * 60)
    
    try:
        service = ChecklistAnalyzerService(
            connection_string=args.connection_string,
            poll_interval=args.interval
        )
        
        if args.once:
            logger.info("Запуск одиночного цикла проверки...")
            service.run_cycle()
            logger.info("Одиночный цикл завершен")
        else:
            logger.info("Запуск в режиме постоянного мониторинга...")
            service.run_forever()
            
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки (Ctrl+C)")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
