import logging

logger = logging.getLogger("Factorial")
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class Cache(object):

    def __init__(self):
        self._cache = {}

    def get(self, key):
        logger.debug("Factorial({}) was received from cache.".format(key))
        return self._cache.get(key)

    def put(self, key, value):
        logger.debug("Factorial({}) was put to cache.".format(key))
        self._cache[key] = value


cache = Cache()


def cached_factorial(_factorial):
    def _cached_factorial(n):
        if cache.get(n) is None:
            cache.put(n, _factorial(n))
        else:
            logger.info("Cache hit for number {}".format(n))

        return cache.get(n)

    return _cached_factorial


@cached_factorial
def factorial(n):
    if n < 2:
        return 1
    return factorial(n - 1) * n
