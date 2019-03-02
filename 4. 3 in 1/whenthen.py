class InvalidUsage(Exception):
    pass


def whenthen(func):

    list_of_conditions = []
    list_of_actions = []

    def new_func(*args):

        if len(list_of_conditions) != len(list_of_actions):
            raise InvalidUsage

        for condition, action in zip(list_of_conditions, list_of_actions):
            if condition(*args):
                return action(*args)

        return func(*args)

    def when(func1):
        if len(list_of_conditions) == len(list_of_actions):
            list_of_conditions.append(func1)
        else:
            raise InvalidUsage
        return new_func

    def then(func2):
        if len(list_of_conditions) - 1 == len(list_of_actions):
            list_of_actions.append(func2)
        else:
            raise InvalidUsage
        return new_func

    new_func.when = when
    new_func.then = then

    return new_func


@whenthen
def fract(x):
    return x * fract(x - 1)


@fract.when
def fract(x):
    return x == 0


@fract.then
def fract(x):
    return 1


@fract.when
def fract(x):
    return x > 5


@fract.then
def fract(x):
    return x * (x - 1) * (x - 2) * (x - 3) * (x - 4) * fract(x - 5)



print(fract(4))
