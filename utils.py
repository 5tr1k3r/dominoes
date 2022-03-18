import time


def timeit(f):
    """ Timing decorator."""

    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print(f'Took {(te - ts):.3f}s')
        return result

    return timed
