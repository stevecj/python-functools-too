from functools import cache, wraps
from inspect import signature
from weakref import ref, WeakKeyDictionary

__all__ = [
    'bind_call_params', 'cached_static_method', 'cached_class_method',
    'cached_class_property', 'cached_static_property', 'class_property',
    'per_target_decorated_method']


def class_property(func):
    """
    Transform a method into a class property.

    A convenience decorator that behaves the same as decorating with
    '@classmethod' followed by '@property' but without having to remember
    which comes first.
    """
    return classmethod(property(func))


def bind_call_params(func):
    """
    Transform a function to always receive its arguments in the same form
    (which are positional and which are keyword) even if its implementation
    is less strict than what is described by its signature.

    This is for use where where the form in which the parameters are passed
    may be significant to its decorator (e.g. '@functools.cache' or
    'functools.lru_cache') and we want that form to be determined by the
    signature of the called function and not how they are given by the
    caller.

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


def cached_static_method(func=None, /, *, bind_args=False):
    """
    Transform a method to a static-method cache, optionally based on
    parameters in bound-argument form (see `@bind_call_params`),

    When used as a decorator, transforms the method into a static method
    that caches results for parameters in the form in which they are given
    (which are positional vs keyword).

    When called as a function, returns a decorator that transforms a method
    into a static method that caches results for parameters, either in
    their given form (default or 'bind_args=False') or in their bound form
    ('bind_args=True').
    """
    if func:
        # Called as decorator w/o binding of args.
        return staticmethod(cache(func))

    else:
        if bind_args:
            # return decorator with binding of args.
            def decorator(func):
                return staticmethod(
                    bind_call_params(cache(func)))
        else:
            # return decorator without binding of args.
            def decorator(func):
                return staticmethod(cache(func))

        return decorator


def cached_class_method(func=None, /, *, bind_args=False):
    """
    Transform a method to a class-method cache, optionally based on
    parameters in bound-argument form (see `@bind_call_params`),

    When used as a decorator, transforms the method into a class method
    that caches results for the combination of target class and passed
    parameters in the form in which they are given (which of them are
    passed as positional vs keyword).

    When called as a function, returns a decorator that transforms a method
    into a class method that caches results for the combination of target
    class and passed parameters, either in their given form (default or
    'bind_args=False') or in their bound form ('bind_args=True').
    """
    if func:
        # Called as decorator w/o binding of args.
        return classmethod(
            per_target_decorated_method(decorator=cache)(func))

    else:
        if bind_args:
            # return decorator with binding of args.
            def decorator(func):
                def cached_with_bound_args(func):
                    return bind_call_params(cache(func))

                return classmethod(
                    per_target_decorated_method(
                        decorator=cached_with_bound_args)(func))
        else:
            # return decorator without binding of args.
            def decorator(func):
                return classmethod(
                    per_target_decorated_method(decorator=cache)(func))

        return decorator


class cached_static_property:
    """
    Transform a method of a class into a property whose value is computed
    once and then cached statically.

    Whether the property is first accessed through the base class or an
    inheriting class, the computed value is cached once for the base class
    and all of its descendants.
    """
    def __init__(self, func):
        self.func = func
        self.cache = []

    def __get__(self, obj, objtype=None):
        if self.cache:
            return self.cache[0]
        else:
            value = self.func()
            self.cache.append(value)
            return value


def cached_class_property(func):
    """
    Transform a method of a class into a property whose value is computed
    once and then cached separately for the class and each subclass.
    """
    def per_target_caching_deco(func):
        cache = []

        @wraps(func)
        def wrapper(cls):
            if cache:
                return cache[0]
            else:
                value = func(cls)
                cache.append(value)
                return value

        return wrapper

    @class_property
    @per_target_decorated_method(decorator=per_target_caching_deco)
    def wrapper(cls):
        return func(cls)

    return wrapper
