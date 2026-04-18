from textwrap import dedent

import pytest

from beats2bars import beats2bars


@pytest.mark.parametrize(
    "input_data, start_beat, beats_per_bar, expected_output, expected_stats, span",
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
            ["3.0\t6.0\t1"],  # spans 3 → 6
            (1.0, 60.0),
            True,
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
                "0.5\t1.5\t1",
                "1.5\t2.5\t2",
            ],
            (0.5, 120.0),
            True,
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
                "2.0\t6.0\t1",
                "6.0\t10.0\t2",
            ],
            (2.0, 30.0),
            True,
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
                "1.0\t2.5\t1",
                "2.5\t5.0\t2",
            ],
            (1.0, 60.0),
            True,
        ),
    ],
)
def test_varied_beat_durations(
    input_data,
    start_beat,
    beats_per_bar,
    expected_output,
    expected_stats,
    span,
):
    """Test span-label (duration) mode across various beat spacings."""
    gen = beats2bars(
        iter(input_data),
        start_beat=start_beat,
        beats_per_bar=beats_per_bar,
        start=1,
        span=span,
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
# Additional tests: default event (zero-duration) mode
# ------------------------------


def test_event_mode_one_bar():
    """Default mode emits start=end timestamps at each downbeat."""
    input_data = ["1.0", "2.0", "3.0", "4.0"]

    gen = beats2bars(iter(input_data), 1, 2, 1)

    out = []
    try:
        while True:
            out.append(next(gen))
    except StopIteration:
        pass

    assert out == [
        "1.0\t1.0\t1",
        "3.0\t3.0\t2",
    ]


def test_event_mode_three_beats_per_bar():
    input_data = ["1.0", "2.0", "3.0", "4.0", "5.0", "6.0"]

    gen = beats2bars(iter(input_data), 1, 3, 1)

    out = []
    try:
        while True:
            out.append(next(gen))
    except StopIteration:
        pass

    assert out == [
        "1.0\t1.0\t1",
        "4.0\t4.0\t2",
    ]


# ------------------------------
# Dir-mode discovery tests
# ------------------------------


class TestDiscoverBeatsFile:
    """Find a unique beats_*.txt in a directory."""

    def test_finds_unique_beats_file(self, tmp_path):
        from beats2bars import _discover_beats_file

        beats = tmp_path / "beats_song.txt"
        beats.write_text("")
        (tmp_path / "bars_song.txt").write_text("")  # ignored
        (tmp_path / "other.txt").write_text("")

        assert _discover_beats_file(tmp_path) == beats

    def test_zero_beats_files_errors(self, tmp_path):
        from beats2bars import _discover_beats_file

        with pytest.raises(ValueError, match="no beats"):
            _discover_beats_file(tmp_path)

    def test_multiple_beats_files_errors(self, tmp_path):
        from beats2bars import _discover_beats_file

        (tmp_path / "beats_a.txt").write_text("")
        (tmp_path / "beats_b.txt").write_text("")
        with pytest.raises(ValueError, match="multiple beats"):
            _discover_beats_file(tmp_path)

    def test_stem_derived_from_beats_filename(self, tmp_path):
        from beats2bars import _beats_to_bars_path

        beats = tmp_path / "beats_blues_brothers_my_guy.txt"
        bars = _beats_to_bars_path(beats)
        assert bars == tmp_path / "bars_blues_brothers_my_guy.txt"


if __name__ == "__main__":
    pytest.main([__file__])
