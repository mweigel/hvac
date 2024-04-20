import re

from collections import OrderedDict

NANOSECOND = 1
MICROSECOND = 1000 * NANOSECOND
MILLISECOND = 1000 * MICROSECOND
SECOND = 1000 * MILLISECOND
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR

_duration_units = OrderedDict(
    [
        ("d", DAY),
        ("h", HOUR),
        ("m", MINUTE),
        ("s", SECOND),
        ("ms", MILLISECOND),
        ("us", MICROSECOND),
        ("µs", MICROSECOND),
        ("ns", NANOSECOND),
    ]
)

_duration_float_re = re.compile(r"^\d*(\.\d+)?$")
_duration_split_re = re.compile(r"(ns|us|µs|ms|s|m|h|d)")


def parse_duration(duration: str) -> int:
    """A duration string is a possibly signed sequence of decimal numbers,
    each with an optional fraction and a unit suffix, such as "300ms", "-1.5h"
    or "2h45m". If no unit is given, the number is interpreted as seconds.
    Valid time units are: "ns", "us" (or "µs"), "ms", "s", "m", "h", "d".

    :param duration: Duration.
    :type duration: str
    :return: Duration in nanoseconds.
    :rtype: int
    """
    duration = _normalise(duration)

    sign = 1
    if duration[0] == "-":
        sign = -1
        duration = duration[1:]

    result = 0
    tokens = _split(duration)
    for val, unit in zip(tokens[0::2], tokens[1::2]):
        _validate(val, unit)
        result += float(val) * _duration_units[unit]

    return round(sign * result)


def format_duration(duration: int) -> str:
    """Returns a string representing the duration in the form "3d2h3m0.5s".
    Leading zero units are omitted. As a special case, durations less than one
    second format use a smaller unit (milli-, micro-, or nanoseconds) to ensure
    that the leading digit is non-zero. The zero duration formats as 0s.

    :param duration: Duration.
    :type duration: int
    :return: Duration string.
    :rtype: str
    """
    if duration == 0:
        return "0s"

    sign = "-" if duration < 0 else ""
    duration = abs(duration)

    result = ""
    if duration < SECOND:
        result = _format_small_num(duration)
    else:
        result = _format_large_num(duration)

    return f"{sign}{result}"


def _normalise(duration: str) -> str:
    duration = duration.strip()

    if not any(c.isdigit() for c in duration):
        raise ValueError(f'Invalid duration "{duration}"')

    if duration[0] == "+":
        duration = duration[1:]

    if duration[-1].isdigit():
        duration += "s"

    return duration


def _split(duration: str) -> list:
    tokens = _duration_split_re.split(duration)

    if len(tokens) < 2:
        raise ValueError("Invalid duration string")

    return tokens


def _validate(val: str, unit: str):
    if not _duration_float_re.match(val):
        raise ValueError(f'Invalid value "{val}" in duration')

    if not unit in _duration_units:
        raise ValueError(f'Unknown unit "{unit}" in duration')


def _format_small_num(duration) -> str:
    if duration < MICROSECOND:
        return f"{duration:d}ns"
    elif duration < MILLISECOND:
        return _strip_fract(f"{duration / MICROSECOND:.3f}") + "µs"
    else:
        return _strip_fract(f"{duration / MILLISECOND:.6f}") + "ms"


def _format_large_num(duration) -> str:
    result = ""
    for unit, val in _duration_units.items():
        if unit == "s":
            result = _strip_fract(f"{result}{duration / SECOND:.9f}") + "s"
            break

        if duration >= val:
            floor, duration = divmod(duration, val)
            result += f"{floor}{unit}"
        else:
            result += f"0{unit}" if result else ""

    return result


def _strip_fract(result: str) -> str:
    return result.rstrip("0").rstrip(".")
