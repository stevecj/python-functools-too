#!/usr/bin env python3

from functools import wraps
import unittest

from functools_too import *


class TestBindCallParams(unittest.TestCase):

    def setUp(self):

        def capture_the_params_signature(a, b='<b>', /, c='<c>', *, d='<d>'):
            pass

        @bind_call_params
        # Decorate with 'wraps' so that the function signature seen by
        # 'bind_call_params' is that of `capture_the_params_signature',
        # even though the function capturing params as '*args' and
        # '**kwargs'.
        @wraps(capture_the_params_signature)
        def capture_the_params(*args, **kwargs):
            self.captured_params = {'args': args, 'kwargs': kwargs}

        self.capture_the_params = capture_the_params

    def test_converts_passed_params_to_a_consistent_form(self):
        expected_captured_params = {
            'args': ('<a>', '<b>', '<c>'), 'kwargs': {'d': '<d>'}}

        self.capture_the_params('<a>')
        self.assertEqual(expected_captured_params, self.captured_params)

        self.capture_the_params('<a>', '<b>')
        self.assertEqual(expected_captured_params, self.captured_params)

        self.capture_the_params('<a>', '<b>', '<c>')
        self.assertEqual(expected_captured_params, self.captured_params)

        self.capture_the_params('<a>', '<b>', c='<c>')
        self.assertEqual(expected_captured_params, self.captured_params)

        self.capture_the_params('<a>', '<b>', '<c>', d='<d>')
        self.assertEqual(expected_captured_params, self.captured_params)

        self.capture_the_params('<a>', '<b>', c='<c>', d='<d>')
        self.assertEqual(expected_captured_params, self.captured_params)

    def test_preserves_passed_non_default_param_values(self):
        # Technically, this is just indirectly testing the behavior
        # of 'inspect.BoundArguments#apply_defaults()', but it feels
        # good to have as a sanity check.
        self.capture_the_params('<a>', '<b2>', '<c2>', d='<d2>')
        self.assertEqual({
            'args': ('<a>', '<b2>', '<c2>'), 'kwargs': {'d': '<d2>'}},
            self.captured_params)


class TestPerTargetDecoratedMethod(unittest.TestCase):

    def setUp(self):

        self.example_decorator_call_count = 0
        self.example_decorated_call_count = 0

        def example_decorator(func):
            self.example_decorator_call_count += 1

            @wraps(func)
            def wrapped(*args, **kwargs):
                self.example_decorated_call_count += 1
                func(*args, **kwargs)

            return wrapped

        class Example:
            @per_target_decorated_method(decorator=example_decorator)
            def an_instance_method(self):
                pass

            @classmethod
            @per_target_decorated_method(decorator=example_decorator)
            def a_class_method(self):
                pass

        class ExampleSub(Example):
            pass

        self.Example    = Example
        self.ExampleSub = ExampleSub

        # Sanity check
        self.assertEqual(0, self.example_decorator_call_count)

    def test_calls_decorator_separately_per_separate_instance_target(self):
        example_inst_a = self.Example()
        example_inst_b = self.Example()

        # Sanity check
        self.assertEqual(0, self.example_decorator_call_count)

        example_inst_a.an_instance_method()
        example_inst_b.an_instance_method()
        self.assertEqual(2, self.example_decorator_call_count)

    def test_calls_decorator_once_per_instance_target(self):
        example_inst_a = self.Example()

        # Sanity check
        self.assertEqual(0, self.example_decorator_call_count)

        example_inst_a.an_instance_method()
        example_inst_a.an_instance_method()
        self.assertEqual(1, self.example_decorator_call_count)

    def test_calls_decorator_separately_per_separate_class_target(self):
        self.Example.a_class_method()
        self.ExampleSub.a_class_method()
        self.assertEqual(2, self.example_decorator_call_count)

    def test_calls_decorator_once_per_class_target(self):
        self.Example.a_class_method()
        self.Example.a_class_method()
        self.assertEqual(1, self.example_decorator_call_count)
