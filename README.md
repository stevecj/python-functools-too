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
(which are positional and which are keyword) even if its implementation
is less strict than what is described by its signature.

This is for use where where the form in which the parameters are passed
may be significant to its decorator (e.g. '@functools.cache' or
'functools.lru\_cache') and we want that form to be determined by the
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


`@cached_static_method`
---------------------------------

Transform a method to a static-method cache, optionally based on
parameters in bound-argument form (see `@bind_call_params`),

When used as a decorator, transforms the method into a static method
that caches results for parameters in the form in which they are given
(which are positional vs keyword).

When called as a function, returns a decorator that transforms a method
into a static method that caches results for parameters, either in
their given form (default or 'bind\_args=False') or in their bound form
('bind\_args=True').


`@cached_class_method`
----------------------

Transform a method to a class-method cache, optionally based on
parameters in bound-argument form (see `@bind_call_params`),

When used as a decorator, transforms the method into a class method
that caches results for the combination of target class and passed
parameters in the form in which they are given (which of then are
passed as positional vs keyword).

When called as a function, returns a decorator that transforms a method
into a class method that caches results for the combination of target
class and passed parameters, either in their given form (default or
'bind\_args=False') or in their bound form ('bind\_args=True').


`@cached_class_property`
------------------------

Transform a method of a class into a property whose value is computed
once and then cached separately for the class and each subclass.


`@cached_static_property`
-------------------------

Transform a method of a class into a property whose value is computed
once and then cached statically.

Whether the property is first accessed through the base class or an
inheriting class, the computed value is cached once for the base class
and all of its descendants.


`@class_property`
-----------------

Transform a method into a class property.

A convenience decorator that behaves the same as decorating with
'@classmethod' followed by '@property' but without having to remember
which comes first.


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
