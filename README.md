# python-functools-too
Additional higher-order functions and operations on callable objects for Python

Note: This project is not yet built as a package or uploaded to PyPi,
so if you want to use it now, you should do so by copying its code
into your project.

Decorators
==========

`@bind_call_params`
---------------------------------

Transform a function to always receive its arguments in the same form
(which are positional and which are keyword) even if its
implementation is less strict than what is described by its
signature.

This is for use where where the form in which the parameters are passed
may be significant to its decorator (e.g. '@functools.cache' or
'functools.lru\_cache').

Example:

    from datetime import datetime
    from functools import cache
    from functools_too import bind_call_params

    @bind_call_params
    @cache
    def example(a, b='<b>', /, c='<c>', *, d='<d>'):
        return (datetime.now(), a, b, c, d)

`@per_target_decorated_method(decorator=<decorator>)`
-----------------------------------------------------

Apply the given decorator to the method separately for each target
(instance for an instance method or class for a class method).

In the case of a class method, the base class and each of its
subclasses are different targets.

This is mainly for use with decorators that cache results (e.g.
'functools.cache' or 'functools.lru\_cache') so that they do not
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
