from queue import Queue


class CandleQueue:

    def __init__(self, maxsize=1000):
        self.queue = Queue(maxsize=maxsize)

    def put(self, candle):
        self.queue.put(candle)

    def get(self, timeout=None):
        return self.queue.get(timeout=timeout)

    def task_done(self):
        self.queue.task_done()