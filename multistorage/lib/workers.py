import threading
import Queue
import logging

_QUEUE = Queue.Queue()
_WORKERS = []

class Worker(threading.Thread):

    def __init__(self, *args, **kwargs):
        self.stop = True
        self.handled = 0
        super(Worker, self).__init__(*args, **kwargs)


    def run(self):
        logging.debug('%s running' % (self.name,))
        self.stop = False
        while not self.stop:
            try:
                fn = _QUEUE.get(timeout=0.2)
                logging.debug('%s callback found' % (self.name,))
                fn()
                self.handled += 1
            except Queue.Empty:
                pass
        logging.debug('%s going down. Handled %d jobs.' % (self.name,
                                                           self.handled))




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
        w.stop = True
    _WORKERS[:] = []


def stats():
    logging.info('Getting workers stats')
    res = {}
    for w in _WORKERS:
        logging.debug('%s handled %d jobs.' % (w.name, w.handled))
        res[w.name] = w.handled
    return res
