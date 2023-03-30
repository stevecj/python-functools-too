#!/usr/bin env python3

from functools import wraps
import unittest

from functools_too import *


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
