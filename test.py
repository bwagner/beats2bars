from textwrap import dedent

import pytest

from beats2bars import beats2bars


@pytest.mark.parametrize(
    "input_data, start_beat, beats_per_bar, expected_output, expected_stats, instant",
    [
        # Case 0: Consistent beat intervals (1 sec → 60 BPM)
        (
            dedent(
                """
                1.0
                2.0
                3.0
                4.0
                5.0
                6.0
            """
            )
            .strip()
            .split("\n"),
            3,
            3,
            ["3.0\t6.0\tT 1"],  # spans 3 → 6
            (1.0, 60.0),
            False,
        ),
        # Case 1: Faster beats (0.5 sec → 120 BPM)
        (
            dedent(
                """
                0.5
                1.0
                1.5
                2.0
                2.5
                3.0
            """
            )
            .strip()
            .split("\n"),
            1,
            2,
            [
                "0.5\t1.5\tT 1",
                "1.5\t2.5\tT 2",
            ],
            (0.5, 120.0),
            False,
        ),
        # Case 2: Slower beats (2 sec → 30 BPM)
        (
            dedent(
                """
                2.0
                4.0
                6.0
                8.0
                10.0
            """
            )
            .strip()
            .split("\n"),
            1,
            2,
            [
                "2.0\t6.0\tT 1",
                "6.0\t10.0\tT 2",
            ],
            (2.0, 30.0),
            False,
        ),
        # Case 3: Mixed beat intervals → average 1 sec → 60 BPM
        (
            dedent(
                """
                1.0
                1.5
                2.5
                4.0
                5.0
            """
            )
            .strip()
            .split("\n"),
            1,
            2,
            [
                "1.0\t2.5\tT 1",
                "2.5\t5.0\tT 2",
            ],
            (1.0, 60.0),
            False,
        ),
    ],
)
def test_varied_beat_durations(
    input_data,
    start_beat,
    beats_per_bar,
    expected_output,
    expected_stats,
    instant,
):
    """Test default spanning-label behavior."""
    gen = beats2bars(
        iter(input_data),
        start_beat=start_beat,
        beats_per_bar=beats_per_bar,
        start=1,
        instant=instant,
    )

    output = []
    try:
        while True:
            output.append(next(gen))
    except StopIteration as e:
        stats = e.value

    assert output == expected_output
    assert stats == pytest.approx(expected_stats, rel=1e-2)


# ------------------------------
# Additional tests: instant mode
# ------------------------------


def test_instant_mode_one_bar():
    """Ensure old behavior works (start=end timestamps)."""
    input_data = ["1.0", "2.0", "3.0", "4.0"]

    gen = beats2bars(iter(input_data), 1, 2, 1, instant=True)

    out = []
    try:
        while True:
            out.append(next(gen))
    except StopIteration:
        pass

    assert out == [
        "1.0\t1.0\tT 1",
        "3.0\t3.0\tT 2",
    ]


def test_instant_mode_three_beats_per_bar():
    input_data = ["1.0", "2.0", "3.0", "4.0", "5.0", "6.0"]

    gen = beats2bars(iter(input_data), 1, 3, 1, instant=True)

    out = []
    try:
        while True:
            out.append(next(gen))
    except StopIteration:
        pass

    assert out == [
        "1.0\t1.0\tT 1",
        "4.0\t4.0\tT 2",
    ]


if __name__ == "__main__":
    pytest.main([__file__])
