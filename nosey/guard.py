import time
import nosey

def updateGuard(func):
    def check(*args, manual = False, **kwargs):
        if nosey.gui.actionUpdate_automatically.isChecked() or manual:
            return func(*args, **kwargs)
    return check


def timer(description):
    def wrapper(func):
        def startStop(*args, **kwargs):
            start       = time.time()
            result      = func(*args, **kwargs)
            took        = time.time() - start
            fmt = "{} [Took {:.5f} s]".format(description, took)
            nosey.Log.debug(fmt)
            return result
        return startStop
    return wrapper
