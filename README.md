# beats2bars

I use `DBNBeatTracker` to identify beats in a track:
(`DBNBeatTracker` gets installed when you `pip install` [madmom](https://github.com/CPJKU/madmom))
```console
DBNBeatTracker single music.m4a > beats.txt
```
The resulting beats are a single column of seconds as decimals, e.g.
```console
0.240
0.690
1.130
1.590
2.030
2.490
2.920
...
```
To make them available in [Audacity](https://www.audacityteam.org/) as labels, they need to be of the form of _two_ columns with an optional label. In addition, I'd like to have bar numbers as labels in Audacity. That's where this script comes in.
```console
 Usage: beats2bars.py [OPTIONS] [START_BEAT] [BEATS_PER_BAR] [START]
                      [INPUT_FILE]

 Converts a text file with times in a column or Audacity style labels (two
 columns + optional label) to Audacity style labels and writes them to stdout.

 Usage: beats2bars.py [OPTIONS] [START_BEAT] [BEATS_PER_BAR] [START]
                      [INPUT_FILE]

 Converts a text file with times in a column or Audacity style labels (two
 columns + optional label) to Audacity style labels and writes them to stdout.
 BPM are reported to stderr at the end.

╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│   start_beat         [START_BEAT]     The beat number to start labeling      │
│                                       from. Beats before this are skipped.   │
│                                       [default: 1]                           │
│   beats_per_bar      [BEATS_PER_BAR]  how many beats per bar, aka "time      │
│                                       signature"                             │
│                                       [default: 4]                           │
│   start              [START]          where to start numbering [default: 1]  │
│   input_file         [INPUT_FILE]     [default: -]                           │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
```
Example invocation (I want to count 4/4 bars starting at beat 3)
```console
beats2bars.py 3 4 1 beats.txt > audacity_bars.txt
```
[rebuildap](https://github.com/bwagner/rebuildap), [shift_labels](https://github.com/bwagner/shift_labels), [pyaudacity](https://github.com/bwagner/pyaudacity)
