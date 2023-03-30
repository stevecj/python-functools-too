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
        # even though the function is capturing params as '*args' and
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
