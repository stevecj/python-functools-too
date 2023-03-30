#!/usr/bin env python3

from functools import wraps
import unittest

from functools_too import *


class CommonCases:

    def test_does_not_cache_for_different_args(self):
        self.assertEqual((1, 1, 1), self.Example.example_method(1, 1))
        self.assertEqual((2, 1, 2), self.Example.example_method(1, 2))

    def test_caches_for_same_args_to_base_class_method(self):
        self.assertEqual((1, 1, 1), self.Example.example_method(1, 1))
        self.assertEqual((1, 1, 1), self.Example.example_method(1, 1))

    def test_caches_for_same_args_to_base_class_and_subclass_method(self):
        self.assertEqual((1, 1, 1), self.Example.example_method(1, 1))
        self.assertEqual((1, 1, 1), self.ExampleSub.example_method(1, 1))


class MethodWithoutArgsBindingCases(CommonCases):

    def test_does_not_cache_for_same_args_in_different_form(self):
        self.assertEqual((1, 1, 1), self.Example.example_method(1, 1))
        self.assertEqual((2, 1, 1), self.Example.example_method(1, b=1))


class MethodWithArgsBindingCases(CommonCases):

    def test_caches_for_same_args_in_different_form(self):
        self.assertEqual((1, 1, 1), self.Example.example_method(1, 1))
        self.assertEqual((1, 1, 1), self.Example.example_method(1, b=1))


class TestCachedStaticMethodAsDecorator(
        MethodWithoutArgsBindingCases, unittest.TestCase):

    def setUp(self):
        self.call_count = 0

        class Example:
            @cached_static_method
            def example_method(a, b):
                Example.test_instance.call_count += 1
                return (Example.test_instance.call_count, a, b)

        Example.test_instance = self

        class ExampleSub(Example):
            pass

        self.Example = Example
        self.ExampleSub = ExampleSub


class TestCachedStaticMethodAsFunctionWithoutArgsBinding(
        MethodWithoutArgsBindingCases, unittest.TestCase):

    def setUp(self):
        self.call_count = 0

        class Example:
            @cached_static_method()
            def example_method(a, b):
                Example.test_instance.call_count += 1
                return (Example.test_instance.call_count, a, b)

        Example.test_instance = self

        class ExampleSub(Example):
            pass

        self.Example = Example
        self.ExampleSub = ExampleSub


class TestCachedStaticMethodAsFunctionWithArgsBinding(
        MethodWithArgsBindingCases, unittest.TestCase):

    def setUp(self):
        self.call_count = 0

        class Example:
            @cached_static_method(bind_args=True)
            def example_method(a, b):
                Example.test_instance.call_count += 1
                return (Example.test_instance.call_count, a, b)

        Example.test_instance = self

        class ExampleSub(Example):
            pass

        self.Example = Example
        self.ExampleSub = ExampleSub
