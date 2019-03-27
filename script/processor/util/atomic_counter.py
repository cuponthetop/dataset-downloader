from multiprocessing import Lock, Value


class Counter(object):
    def __init__(self):
        self.val = Value('i', 0)
        self.lock = Lock()

    def increment(self):
        with self.lock:
            self.val.value += 1

    @property
    def value(self):
        return self.val.value
