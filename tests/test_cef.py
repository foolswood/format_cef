from unittest import TestCase
from datetime import datetime

from format_cef import cef


class TestCef(TestCase):
    def test_escaping(self):
        escape = cef.escaper('|=')
        self.assertEqual(
            escape(r'|some|really\nasty\\things\|to=try\='),
            r'\|some\|really\\nasty\\things\|to\=try\=')

    def test_unbounded_str_sanitisation(self):
        sanitise = cef.str_sanitiser('banana')
        self.assertEqual(sanitise('banana', 'label'), 'banana')
        self.assertRaises(ValueError, sanitise, 'apple', 'label')

    def test_bounded_str_sanitisation(self):
        sanitise = cef.str_sanitiser(
            '[banana]*', min_len=3, max_len=6, escape_chars='b')
        self.assertRaises(ValueError, sanitise, 'an', 'label')
        self.assertEqual(sanitise('ba', 'label'), r'\ba')
        self.assertEqual(sanitise('banan', 'label'), r'\banan')
        # Escaping makes string too long:
        self.assertRaisesRegexp(
            ValueError, 'range', sanitise, 'banana', 'label')
        self.assertRaises(ValueError, sanitise, 'apple', 'label')
        self.assertRaises(TypeError, sanitise, 3, 'label')

    def test_int_stanitisation(self):
        sanitise = cef.int_sanitiser(32)
        self.assertEqual(sanitise(0, 'label'), '0')
        self.assertEqual(sanitise(32, 'label'), '32')
        self.assertRaises(ValueError, sanitise, -1, 'label')
        self.assertRaises(ValueError, sanitise, 33, 'label')
        self.assertRaises(TypeError, sanitise, 'moo', 'label')

    def test_datetime_sanitisation(self):
        sanitise = cef.datetime_sanitiser()
        d = datetime(2017, 4, 10, 1, 2, 3)
        expected = 'Apr 10 2017 01:02:03'
        self.assertEqual(sanitise(d, 'label'), expected)
        self.assertRaises(TypeError, sanitise, expected, 'label')

    def test_format_cef(self):
        args = (
            'acme corp', 'TNT', '1.0', '404 | not found',
            'Explosives not found', 10)
        self.assertEqual(
            cef.format_cef(*args, extensions={'deviceAction': 'explode = !'}),
            r'CEF:0|acme corp|TNT|1.0|404 \| not found|Explosives not found|'
            r'10|act=explode \= !')
