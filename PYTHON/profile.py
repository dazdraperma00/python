import inspect
import time


def sub_profile(func, name):

    def new_func(*args, **kwargs):
        print('{!r} started'.format(name))
        start = time.perf_counter()

        result = func(*args, **kwargs)

        end = time.perf_counter()
        print('{!r} ended in {}s'.format(name, round(float(end - start), 5)))
        return result

    return new_func


def profile(obj):

    if inspect.isfunction(obj):

        new_func = sub_profile(obj, obj.__name__)
        return new_func

    if inspect.isclass(obj):
        methods_names = [method_name for method_name, code in obj.__dict__.items() if
                         inspect.isfunction(code)]
        for method_name in methods_names:
            method = getattr(obj, method_name)
            name = '.'.join([obj.__name__, method_name])
            setattr(obj, method_name, sub_profile(method, name))
        return obj


@profile
def foo(x):
    return x*x


@profile
def hello(msg):
    return "Hello! " + msg


@profile
class Number:
    def __init__(self, value):
        self._value = value

    def sqr(self):
        return type(self)(self._value * self._value)

    def half(self):
        return type(self)(self._value // 2)

    def __repr__(self):
        return 'Number({value})'.format(value=self._value)


hello('Python')
foo(10)

n = Number(10)
n.sqr()
n.half()
repr(n)
