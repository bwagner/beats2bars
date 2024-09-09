from textwrap import dedent

import pytest

from beats2bars import beats2bars


@pytest.mark.parametrize(
    "input_data, start_beat, beats_per_bar, expected_output, expected_stats",
    [
        # Case 0: Consistent beat intervals (1 second between beats, leading to 60 BPM)
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
            ).split("\n"),
            3,
            3,
            ["3.0\t3.0\tT 1", "6.0\t6.0\tT 2"],
            (1.0, 60.0),
        ),
        # Case 1: Faster beats (0.5 second intervals, leading to 120 BPM)
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
            ).split("\n"),
            1,
            2,
            ["0.5\t0.5\tT 1", "1.5\t1.5\tT 2", "2.5\t2.5\tT 3"],
            (0.5, 120.0),
        ),
        # Case 2: Slower beats (2 second intervals, leading to 30 BPM)
        (
            dedent(
                """
                2.0
                4.0
                6.0
                8.0
                10.0
                """
            ).split("\n"),
            1,
            2,
            ["2.0\t2.0\tT 1", "6.0\t6.0\tT 2", "10.0\t10.0\tT 3"],
            (2.0, 30.0),
        ),
        # Case 3: Mixed beat intervals (inconsistent intervals, calculate avg BPM)
        (
            dedent(
                """
                1.0
                1.5
                2.5
                4.0
                5.0
                """
            ).split("\n"),
            1,
            2,
            ["1.0\t1.0\tT 1", "2.5\t2.5\tT 2", "5.0\t5.0\tT 3"],
            (1.0, 60.0),  # avg duration is 1.0, BPM is 60
        ),
    ],
)
def test_varied_beat_durations(
    input_data, start_beat, beats_per_bar, expected_output, expected_stats
):
    gen = beats2bars(
        iter(input_data), start_beat=start_beat, beats_per_bar=beats_per_bar, start=1
    )

    output = []
    try:
        while True:
            output.append(next(gen))
    except StopIteration as e:
        stats = e.value

    assert output == expected_output
    assert stats == pytest.approx(expected_stats, rel=1e-2)


if __name__ == "__main__":
    pytest.main([__file__])
