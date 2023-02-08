

class Stream:

    def __init__(self, iterable) -> None:
        self._iterable = iterable

    def __iter__(self):
        return self._iterable

    def __next__(self):
        return next(self._iterable)

    def create(iterable):
        return Stream(iterable)

    def map(self, func):
        return Stream(map(func, self._iterable))

    def pipe(self, func):
        return Stream(func(self._iterable))


class StreamFunction:

    def __init__(self, func) -> None:
        self._func = func
        self.counter = 0
        self.pct = 0.0

    def exec(self, *args, **kwargs):
        res = self._func(*args, **kwargs)
        if type(res) is dict and 'pct' in res:
            self.pct = res['pct']
            return res['value']
        return res

    @property
    def func(self):
        self.counter += 1
        return self._func