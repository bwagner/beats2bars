from textwrap import dedent

import pytest

from beats2bars import beats2bars


def test_single_column_input():
    input_data = dedent(
        """
        1.0
        2.0
        3.0
        4.0
        5.0
        6.0
    """
    ).split("\n")
    expected_output = (
        dedent(
            """
        3.0\t3.0\tT 1
        6.0\t6.0\tT 2
    """
        )
        .strip()
        .split("\n")
    )

    gen = beats2bars(iter(input_data), start_beat=3, beats_per_bar=3, start=1)

    output = []
    try:
        while True:
            output.append(next(gen))
    except StopIteration as e:
        stats = e.value

    assert output == expected_output
    assert stats == (1.0, 60.0)  # Average duration, Average BPM


def test_two_column_input():
    input_data = dedent(
        """
        1.0 1.5
        2.0 2.5
        3.0 3.5
        4.0 4.5
        5.0 5.5
        6.0 6.5
    """
    ).split("\n")
    expected_output = (
        dedent(
            """
        3.0\t3.0\tT 1
        6.0\t6.0\tT 2
    """
        )
        .strip()
        .split("\n")
    )

    gen = beats2bars(iter(input_data), start_beat=3, beats_per_bar=3, start=1)

    output = []
    try:
        while True:
            output.append(next(gen))
    except StopIteration as e:
        stats = e.value

    assert output == expected_output
    assert stats == (1.0, 60.0)


def test_empty_input():
    input_data = []
    expected_output = []

    gen = beats2bars(iter(input_data), start_beat=2, beats_per_bar=3, start=1)

    output = []
    try:
        while True:
            output.append(next(gen))
    except StopIteration as e:
        stats = e.value

    assert output == expected_output
    assert stats == (0.0, 0.0)  # No valid durations, so stats should be zero


def test_non_numeric_input():
    input_data = dedent(
        """
        not_a_number
        2.0
        3.0
    """
    ).split("\n")

    gen = beats2bars(iter(input_data), start_beat=1, beats_per_bar=2, start=1)

    with pytest.raises(ValueError):
        list(gen)  # Attempt to consume the generator


def test_start_beat_skips_beats():
    input_data = dedent(
        """
        1.0
        2.0
        3.0
        4.0
        5.0
    """
    ).split("\n")
    expected_output = ["4.0\t4.0\tT 1"]

    gen = beats2bars(iter(input_data), start_beat=4, beats_per_bar=2, start=1)

    output = []
    try:
        while True:
            output.append(next(gen))
    except StopIteration as e:
        stats = e.value

    assert output == expected_output
    assert stats == (1.0, 60.0)


def test_start_beat_skips_beats_no_prefix():
    input_data = dedent(
        """
        1.0
        2.0
        3.0
        4.0
        5.0
    """
    ).split("\n")
    expected_output = ["4.0\t4.0\t1"]

    gen = beats2bars(
        iter(input_data), start_beat=4, beats_per_bar=2, start=1, prefix=""
    )

    output = []
    try:
        while True:
            output.append(next(gen))
    except StopIteration as e:
        stats = e.value

    assert output == expected_output
    assert stats == (1.0, 60.0)


def test_start_beat_skips_beats_no_num():
    input_data = dedent(
        """
        1.0
        2.0
        3.0
        4.0
        5.0
    """
    ).split("\n")
    expected_output = ["4.0\t4.0\tT "]

    gen = beats2bars(
        iter(input_data), start_beat=4, beats_per_bar=2, start=1, numbers=False
    )

    output = []
    try:
        while True:
            output.append(next(gen))
    except StopIteration as e:
        stats = e.value

    assert output == expected_output
    assert stats == (1.0, 60.0)


def test_start_beat_skips_beats_no_prefix_no_num():
    input_data = dedent(
        """
        1.0
        2.0
        3.0
        4.0
        5.0
    """
    ).split("\n")
    expected_output = ["4.0\t4.0\t"]

    gen = beats2bars(
        iter(input_data),
        start_beat=4,
        beats_per_bar=2,
        start=1,
        numbers=False,
        prefix=None,
    )

    output = []
    try:
        while True:
            output.append(next(gen))
    except StopIteration as e:
        stats = e.value

    assert output == expected_output
    assert stats == (1.0, 60.0)


if __name__ == "__main__":
    pytest.main([__file__])
