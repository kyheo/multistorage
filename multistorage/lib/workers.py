import threading
import Queue
import logging

_QUEUE = Queue.Queue()
_WORKERS = []

class Worker(threading.Thread):

    def __init__(self, *args, **kwargs):
        self._running = False
        super(Worker, self).__init__(*args, **kwargs)


    def stop(self):
        self._running = False


    def run(self):
        logging.debug('%s running' % (self.name,))
        self._running = True
        while self._running:
            try:
                fn = _QUEUE.get(timeout=0.2)
                logging.debug('%s callback found' % (self.name,))
                fn()
            except Queue.Empty:
                if not self._running:
                    break
        logging.debug('%s going down' % (self.name,))




def add(callback):
    _QUEUE.put_nowait(callback)


def start(qty=1):
    logging.info('Starting %d worker(s)' % (qty,))
    for i in range(qty):
        w = Worker(name='Worker %d' % (i,))
        w.start()
        _WORKERS.append(w)


def stop():
    logging.info('Stopping workers')
    for w in _WORKERS:
        w.stop()
    _WORKERS[:] = []
