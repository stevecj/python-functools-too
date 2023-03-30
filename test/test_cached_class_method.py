#!/usr/bin env python3

from functools import wraps
from inspect import signature
import unittest

from functools_too import *


class CommonCases:

    def test_applies_correct_method_properties(self):
        cls_qualname = self.Example.__qualname__
        method = self.Example.example_method

        self.assertEqual('example_method', method.__name__)
        self.assertEqual(f'{cls_qualname}.example_method', method.__qualname__)
        self.assertEqual('Hello from example_method!', method.__doc__)
        self.assertEqual(
            ['a', 'b'],
            [param_key for param_key in signature(method).parameters])

    def test_does_not_cache_for_different_args(self):
        self.assertEqual((1, 1, 1), self.Example.example_method(1, 1))
        self.assertEqual((2, 1, 2), self.Example.example_method(1, 2))

    def test_does_not_cache_for_same_args_to_base_class_and_subclass_method(
            self):
        self.assertEqual((1, 1, 1), self.Example.example_method(1, 1))
        self.assertEqual((2, 1, 1), self.ExampleSub.example_method(1, 1))

    def test_caches_for_same_args_to_base_class_method(self):
        self.assertEqual((1, 1, 1), self.Example.example_method(1, 1))
        self.assertEqual((1, 1, 1), self.Example.example_method(1, 1))

    def test_caches_for_same_args_to_subclass_method(self):
        self.assertEqual((1, 1, 1), self.ExampleSub.example_method(1, 1))
        self.assertEqual((1, 1, 1), self.ExampleSub.example_method(1, 1))


class MethodWithoutArgsBindingCases(CommonCases):

    def test_does_not_cache_for_same_args_in_different_form(self):
        self.assertEqual((1, 1, 1), self.Example.example_method(1, 1))
        self.assertEqual((2, 1, 1), self.Example.example_method(1, b=1))


class MethodWithArgsBindingCases(CommonCases):

    def test_caches_for_same_args_in_different_form(self):
        self.assertEqual((1, 1, 1), self.Example.example_method(1, 1))
        self.assertEqual((1, 1, 1), self.Example.example_method(1, b=1))


class TestCachedClassMethodAsDecorator(
        MethodWithoutArgsBindingCases, unittest.TestCase):

    def setUp(self):
        self.call_count = 0

        class Example:
            @cached_class_method
            def example_method(cls, a, b):
                """Hello from example_method!"""
                Example.test_instance.call_count += 1
                return (Example.test_instance.call_count, a, b)

        Example.test_instance = self

        class ExampleSub(Example):
            pass

        self.Example = Example
        self.ExampleSub = ExampleSub


class TestCachedClassMethodAsFunctionWithoutArgsBinding(
        MethodWithoutArgsBindingCases, unittest.TestCase):

    def setUp(self):
        self.call_count = 0

        class Example:
            @cached_class_method()
            def example_method(cls, a, b):
                """Hello from example_method!"""
                Example.test_instance.call_count += 1
                return (Example.test_instance.call_count, a, b)

        Example.test_instance = self

        class ExampleSub(Example):
            pass

        self.Example = Example
        self.ExampleSub = ExampleSub


class TestCachedClassMethodAsFunctionWithArgsBinding(
        MethodWithArgsBindingCases, unittest.TestCase):

    def setUp(self):
        self.call_count = 0

        class Example:
            @cached_class_method(bind_args=True)
            def example_method(cls, a, b):
                """Hello from example_method!"""
                Example.test_instance.call_count += 1
                return (Example.test_instance.call_count, a, b)

        Example.test_instance = self

        class ExampleSub(Example):
            pass

        self.Example = Example
        self.ExampleSub = ExampleSub
