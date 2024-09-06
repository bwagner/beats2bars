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

    assert (
        list(beats2bars(iter(input_data), start_beat=3, beats_per_bar=3, start=1))
        == expected_output
    )


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

    assert (
        list(beats2bars(iter(input_data), start_beat=3, beats_per_bar=3, start=1))
        == expected_output
    )


def test_empty_input():
    input_data = []
    expected_output = []

    assert (
        list(beats2bars(iter(input_data), start_beat=2, beats_per_bar=3, start=1))
        == expected_output
    )


def test_non_numeric_input():
    input_data = dedent(
        """
        not_a_number
        2.0
        3.0
    """
    ).split("\n")

    with pytest.raises(ValueError):
        list(beats2bars(iter(input_data), start_beat=1, beats_per_bar=2, start=1))


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

    assert (
        list(beats2bars(iter(input_data), start_beat=4, beats_per_bar=2, start=1))
        == expected_output
    )


if __name__ == "__main__":
    pytest.main([__file__])
