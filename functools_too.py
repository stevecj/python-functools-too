from functools import wraps
from inspect import signature
from weakref import ref, WeakKeyDictionary


def bind_call_params(func):
    """
    Transform a function to always receive its arguments in the same form
    (which are positional and which are keyword) even if its
    implementation is less strict than what is described by its
    signature.

    This is for use where where the form in which the parameters are passed
    may be significant to its decorator (e.g. '@functools.cache' or
    'functools.lru_cache').

    Example:
        from datetime import datetime
        from functools import cache
        from functools_too import bind_call_params

        @bind_call_params
        @cache
        def example(a, b='<b>', /, c='<c>', *, d='<d>'):
            return (datetime.now(), a, b, c, d)
    """
    sig = signature(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        return func(*bound.args, **bound.kwargs)

    return wrapper


# 'decorator' argument is keyword-only to prevent accidental attempt
# to use 'per_target_decorated_method' as a decorator rather than
# calling it as a function that returns a decorator.
def per_target_decorated_method(*, decorator):
    """
    Apply the given decorator to the method separately for each target
    (instance for an instance method or class for a class method).

    In the case of a class method, the base class and each of its
    subclasses are different targets.

    This is mainly for use with decorators that cache results (e.g.
    'functools.cache' or 'functools.lru_cache') so that they do not
    unnecessarily retain data for objects after the objects no longer
    exist.

    Note that each target must be hashable and weak-referenceable.

    Example:
        from datetime import datetime
        from functools import cache
        from functools_too import per_target_decorated_method

        class Example:
            @per_target_decorated_method(decorator=cache)
            def example(self, a):
                return (datetime.now(), id(self), a)
    """
    def inner_decorator(func):
        decorated_by_target = WeakKeyDictionary()

        @wraps(func)
        def wrapper(target, *args, **kwargs):
            try:
                decorated = decorated_by_target[target]

            except TypeError:
                # Target can't be used as a weak reference or is not
                # of a hashable type
                try:
                    ref(target)
                except TypeError:
                    raise TypeError(
                        f'cannot create weak reference to {type(target)!r}'
                        f' target object')

                # Target is not of a hashable type
                raise

            except KeyError:
                # Decorated function is not in dictionary yet for
                # current target
                decorated = decorator(func)
                decorated_by_target[target] = decorated

            return decorated(target, *args, **kwargs)

        return wrapper

    return inner_decorator
