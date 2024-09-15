#!/usr/bin/env python

import sys
from pathlib import Path
from statistics import mean
from typing import Generator, Iterator, Tuple


def beats2bars(
    input_generator: Iterator[str],
    start_beat: int,
    beats_per_bar: int,
    start: int,
    numbers: bool = True,
    prefix: str = "T ",
) -> Generator[str, None, Tuple[float, float]]:
    """
    Processes the input from a generator, converting a sequence of beat timestamps
    into labeled bars based on the specified start_beat and beats_per_bar, ready for
    import into Audacity.

    Args:
        input_generator (Iterator[str]): A generator or iterator that yields lines of input.
        start_beat (int): The beat number to start labeling from. Beats before this
                          are skipped.
        beats_per_bar (int): The number of beats per bar. Labels are placed at every
                             Nth beat, where N is the number of beats per bar (i.e., time signature).
        start (int): The starting label number. This is the number of the first labeled bar.
        numbers (bool): Whether to include numbering in the labels.
        prefix (str): The prefix for the labels (default is "T ").

    Yields:
        str: The beat labels as formatted strings.

    Returns:
        tuple[float, float]: The average bar duration and average BPM as a final result when the generator finishes.
    """
    ERR = 0.03  # +/- error allowance for bpm
    DDMAX = 0.1  # Max difference between consecutive time differences

    lbl_counter = 0
    lbl_no = start

    ptd = None  # Previous delta between times
    prev_time = None

    beat_index = 1
    prefix = prefix or ""

    durations = []  # Store beat durations to calculate average duration and BPM

    for line in input_generator:
        line = line.strip()
        if not line:
            continue

        if len(columns := line.split()) == 0:
            continue

        current_time = float(columns[0])

        if beat_index >= start_beat:
            if (lbl_counter % beats_per_bar) == 0:
                lbl = f"{prefix}{lbl_no}" if numbers else prefix
                yield f"{current_time}\t{current_time}\t{lbl}"
                lbl_no += 1

            lbl_counter += 1

            if prev_time is not None:
                d = current_time - prev_time
                durations.append(d)
                if ptd is not None:
                    dd = d - ptd  # Delta of deltas
                    if dd > DDMAX:
                        sys.stderr.write(
                            f"# diff = {dd} @ {current_time} T {lbl_no - 1} ptd = {ptd} d = {d}\n"
                        )
                        bpm = 60 / ptd
                        sys.stderr.write(
                            f"# (guessed bpm: {bpm}) rerun DBNBeatTracker with --min_bpm {(1 - ERR) * bpm} --max_bpm {(1 + ERR) * bpm}\n"
                        )
                ptd = d

            prev_time = current_time

        beat_index += 1

    # Calc avg duration and BPM upon generator exhaustion
    avg_duration = mean(durations) if durations else 0
    avg_bpm = 60 / avg_duration if durations else 0
    return avg_duration, avg_bpm


def process(gen):
    try:
        while True:
            print(next(gen))
    except StopIteration as e:
        avg_duration, avg_bpm = e.value
        sys.stderr.write(f"Average bar duration: {avg_duration:.2f} seconds\n")
        sys.stderr.write(f"Average BPM: {avg_bpm:.2f}\n")


if __name__ == "__main__":
    import typer

    app = typer.Typer(add_completion=False)

    def inv(text: str) -> str:
        """Inverts the color of text using ANSI escape codes."""
        INV = "\033[7m"
        NRM = "\033[0m"
        return f"{INV}{text}{NRM}"

    @app.command()
    def main(
        start_beat: int = typer.Argument(
            1,
            help="The beat number to start labeling from. Beats before this are skipped.",
        ),
        beats_per_bar: int = typer.Argument(
            4, help='How many beats per bar, aka "time signature"'
        ),
        start: int = typer.Argument(1, help="Where to start numbering"),
        input_file: str = typer.Argument("-"),
        prefix: str = typer.Option("T ", help="Prefix for labels"),
        numbers: bool = typer.Option(True, help="Include numbering in labels"),
    ):
        """
        Converts a text file with times in a column or Audacity style labels
        (two columns + optional label) to Audacity style labels and writes them to stdout.
        """
        prg = Path(__file__).name

        sys.stderr.write(
            f"{prg} using start beat {inv(str(start_beat))} beats per bar {inv(str(beats_per_bar))} start number {inv(str(start))}\n"
        )
        sys.stderr.write(
            "If this is not what you intended, make sure to add a blank after the parameters before redirecting >\n"
        )

        if input_file == "-":
            input_gen = (line for line in sys.stdin)
            gen = beats2bars(
                input_gen, start_beat, beats_per_bar, start, numbers, prefix
            )
            process(gen)
        else:
            with open(input_file, "r") as f:
                input_gen = (line for line in f)
                gen = beats2bars(
                    iter(input_gen), start_beat, beats_per_bar, start, numbers, prefix
                )
                process(gen)

    app()
