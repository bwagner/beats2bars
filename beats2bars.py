#!/usr/bin/env python


def beats2bars(input_generator, start_beat: int, beats_per_bar: int, start: int):
    """
    Processes the input from a generator, converting a sequence of beat timestamps
    into labeled bars based on the specified start_beat and beats per bar ready for
    import into Audacity.

    Args:
        input_generator (generator): A generator that yields lines of input.
        start_beat (int): The beat number to start labeling from. Beats before this
                      are skipped.
        beats_per_bar (int): The number of beats per bar. Labels are placed at every
                             Nth beat, where N is the number of beats per bar, aka
                             time signature.
        start (int): The starting label number. This is the number of the first labeled bar.

    Yields:
        str: A formatted string in the format `<start_time>\t<start_time>\tT <label_number>`
    """
    ERR = 0.03  # +/- error allowance for bpm
    DDMAX = 0.1  # Max difference between consecutive time differences
    UNSET = -1  # Constant to represent unset variables

    lbl_counter = 0
    lbl_no = start
    BPB = beats_per_bar

    pd = UNSET  # Previous delta between times
    pv = UNSET  # Previous value

    beat_index = 1

    for line in input_generator:
        line = line.strip()
        if not line:
            continue

        columns = line.split()
        if len(columns) == 0:
            continue

        # Handle the case where the input is a single column of floats
        if len(columns) == 1:
            current_time = float(columns[0])
        else:
            # Handle the Audacity label format (two or three columns)
            current_time = float(columns[0])  # First column is the time

        if beat_index >= start_beat:
            if (lbl_counter % BPB) == 0:
                yield f"{current_time}\t{current_time}\tT {lbl_no}"
                lbl_no += 1

            lbl_counter += 1

            if pv != UNSET:
                d = current_time - pv
                dd = d - pd  # Delta of deltas
                if pd != UNSET and dd > DDMAX:
                    sys.stderr.write(
                        f"# diff = {dd} @ {current_time} T {lbl_no - 1} pd = {pd} d = {d}\n"
                    )
                    bpm = 60 / pd
                    sys.stderr.write(
                        f"# (guessed bpm: {bpm}) rerun DBNBeatTracker with --min_bpm {(1 - ERR) * bpm} --max_bpm {(1 + ERR) * bpm}\n"
                    )
                pd = d

            pv = current_time  # Set the previous value to the current time

        beat_index += 1  # Increment the beat index


if __name__ == "__main__":

    import sys

    import typer

    app = typer.Typer(add_completion=False)

    def inv(text: str) -> str:
        """Inverts the color of text using ANSI escape codes."""
        INV = "\033[7m"
        NRM = "\033[0m"
        return f"{INV}{text}{NRM}"

    @app.command()
    def main(
        start_beat: int = typer.Argument(0, help="how many beats to skip before starting"),
        beats_per_bar: int = typer.Argument(
            4, help='how many beats per bar, aka "time signature"'
        ),
        start: int = typer.Argument(1, help="how to start numbering"),
        input_file: str = typer.Argument("-"),
    ):
        """
        Converts a text file with times in a column or Audacity style labels
        (two columns + optional label) to Audacity style labels and writes them to stdout.
        """
        prg = sys.argv[0]

        sys.stderr.write(
            f"{prg} using OFS {inv(str(start_beat))} BPB {inv(str(beats_per_bar))} STA {inv(str(start))}\n"
        )
        sys.stderr.write(
            "If this is not what you intended, make sure to add a blank after the parameters before redirecting >\n"
        )

        if input_file == "-":
            input_gen = (line for line in sys.stdin)
            for output_line in beats2bars(input_gen, start_beat, beats_per_bar, start):
                print(output_line)
        else:
            with open(input_file, "r") as f:
                input_gen = (line for line in f)
                for output_line in beats2bars(input_gen, start_beat, beats_per_bar, start):
                    print(output_line)

    app()
