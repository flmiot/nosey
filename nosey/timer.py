import time
import nosey

# TODO: Could also go into the __init__
def timer(description):
    def wrapper(func):
        def startStop(*args, **kwargs):
            start       = time.time()
            result      = func(*args, **kwargs)
            took        = time.time() - start
            fmt = "{} [Took {:.5f} s]".format(description, took)
            nosey.Log.info(fmt)
            return result
        return startStop
    return wrapper
