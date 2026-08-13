from queue import Queue, Empty

from package.database import Database
from package.logger import get_logger


class DatabaseWorker:
    #TODO FUTURE:
    #   def __init_(self, queue, db, ...): 
    #       pass
    #   jab sqlite ki jagah mysql ya postgresql database ka use karunga

    def __init__(self, queue: Queue,  batch_size: int = 10, batch_timeout: int = 2): 
        self.queue = queue
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout

        self.logger = get_logger(__name__)

    def run(self):
        self.logger.info("Database worker started")

        db = Database()
        batch = []

        try:
            while True:

                try:
                    tick = self.queue.get(
                        timeout=self.batch_timeout
                    )

                    batch.append(tick)

                    if len(batch) >= self.batch_size:
                        self._save_batch(db, batch)

                    self.queue.task_done()

                except Empty:

                    if batch:
                        self._save_batch(db, batch)

        finally:
            if batch:
                self._save_batch(db, batch)

            db.close()

            self.logger.info(
                "Database worker stopped"
            )

    def _save_batch(self, db, batch):

        try:
            db.insert_ticks(batch)

            self.logger.debug(
                f"Database batch saved: {len(batch)} ticks"
            )

            batch.clear()

        except Exception:
            self.logger.exception(
                "Database batch insert failed"
            )