from hvac.duration import (
    parse_duration,
    format_duration,
    DAY,
    HOUR,
    MINUTE,
    SECOND,
    MILLISECOND,
    MICROSECOND,
    NANOSECOND,
)

from unittest import TestCase
from parameterized import parameterized, param


class TestDuration(TestCase):
    @parameterized.expand(
        [
            param(dur=""),
            param(dur=" "),
            param(dur="-"),
            param(dur="+"),
            param(dur="0-"),
            param(dur="0+"),
            param(dur="d7"),
            param(dur="h24"),
            param(dur="ms"),
            param(dur="-d"),
            param(dur="+h"),
            param(dur="-ms"),
            param(dur="1d 1h"),
            param(dur="1 h1m1s"),
            param(dur="17."),
            param(dur="17.s"),
            param(dur="1.0.10s"),
        ]
    )
    def test_invalid_duration_strings(self, dur):
        with self.assertRaises(ValueError):
            parse_duration(dur)

    @parameterized.expand(
        [
            param(dur="1y"),
            param(dur="-1w"),
            param(dur="+1mm"),
            param(dur="1.5dh"),
            param(dur="1hs"),
            param(dur="1hm45mss"),
        ]
    )
    def test_invalid_units(self, dur):
        with self.assertRaises(ValueError):
            parse_duration(dur)

    # @parameterized.expand([])
    # def test_invalid_values(self, dur):
    #     with self.assertRaises(ValueError):
    #         parse_duration(dur)

    @parameterized.expand(
        [
            param(dur=" 0", expect=0),
            param(dur="-0", expect=0),
            param(dur="+0", expect=0),
            param(dur="0ns", expect=0),
            param(dur="1ns", expect=1),
            param(dur="999ns", expect=999),
            param(dur="1000ns", expect=1000),
            param(dur="1001ns", expect=1001),
            param(dur="-0ns", expect=0),
            param(dur="-1ns", expect=-1),
            param(dur="-999ns", expect=-999),
            param(dur="-1000ns", expect=-1000),
            param(dur="-1001ns", expect=-1001),
            param(dur="1001µs589ns", expect=1001 * MICROSECOND + 589 * NANOSECOND),
        ]
    )
    def test_valid_integer_conversions(self, dur, expect):
        result = parse_duration(dur)
        self.assertEqual(result, expect)

    @parameterized.expand(
        [
            param(dur="0.0", expect=0),
            param(dur="-0.0", expect=0),
            param(dur="+0.0", expect=0),
            param(dur=".0ns", expect=0),
            param(dur=".1ns", expect=0),
            param(dur="0.1ns", expect=0),
            param(dur="1.1ns", expect=1),
            param(dur="1.1001ms", expect=1100100),
            param(dur="0.900us", expect=0.9 * MICROSECOND),
            param(dur="0.900ms", expect=0.9 * MILLISECOND),
            param(dur=".9s.1ms", expect=0.9 * SECOND + 0.1 * MILLISECOND),
            param(dur="01.001us", expect=round(1.001 * MICROSECOND)),
            param(dur="01.001ms", expect=round(1.001 * MILLISECOND)),
            param(dur="1.5d4h6d", expect=1.5 * DAY + 4 * HOUR + 6 * DAY),
            param(
                dur="28h17s9.001ms",
                expect=28 * HOUR + 17 * SECOND + 9.001 * MILLISECOND,
            ),
            param(
                dur="7d8.9h17.78m1ns",
                expect=7 * DAY + 8.9 * HOUR + 17.78 * MINUTE + 1 * NANOSECOND,
            ),
        ]
    )
    def test_valid_float_conversions(self, dur, expect):
        result = parse_duration(dur)
        self.assertEqual(result, expect)

    @parameterized.expand(
        [
            param(dur=0, expect="0s"),
            param(dur=1, expect="1ns"),
            param(dur=999, expect="999ns"),
            param(dur=1000, expect="1µs"),
            param(dur=1001, expect="1.001µs"),
            param(dur=-1, expect="-1ns"),
            param(dur=-999, expect="-999ns"),
            param(dur=-1000, expect="-1µs"),
            param(dur=-1001, expect="-1.001µs"),
            param(dur=-1001000, expect="-1.001ms"),
            param(dur=-1000000000, expect="-1s"),
            param(dur=-60000000000, expect="-1m0s"),
            param(dur=-3600000000000, expect="-1h0m0s"),
            param(dur=-86400000000000, expect="-1d0h0m0s"),
        ]
    )
    def test_duration_formatting(self, dur, expect):
        result = format_duration(dur)
        self.assertEqual(result, expect)
