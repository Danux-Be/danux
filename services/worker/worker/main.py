import logging
import signal

from worker.config import settings
from worker.jobs import WorkerJobs

logging.basicConfig(level=settings.log_level, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

RUNNING = True


def _handle_stop(signum: int, _frame: object) -> None:
    global RUNNING
    logger.info('worker shutdown signal received', extra={'signal': signum})
    RUNNING = False


def main() -> None:
    signal.signal(signal.SIGTERM, _handle_stop)
    signal.signal(signal.SIGINT, _handle_stop)

    jobs = WorkerJobs()
    logger.info('worker started', extra={'queue': 'workflow_runs'})
    while RUNNING:
        jobs.poll_once(timeout_seconds=1)
    logger.info('worker stopped')


if __name__ == '__main__':
    main()
