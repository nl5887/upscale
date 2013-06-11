import threading

class periodic_task(object):
    def __init__(self, interval):
        self.interval=interval

    def __call__(self, f):
        stopped = threading.Event()

        def loop(): # executed in another thread
                while not stopped.wait(self.interval): # until stopped
                        f()

        t = threading.Thread(target=loop)
        t.daemon = True # stop if the program exits
        t.start()

