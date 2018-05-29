# MidiWrite by Cameron Terry

#### May 28, 2018

# Intro
MidiWrite makes turning a chord progression into a MIDI file a simple process while lessening the time required needed to create a MIDI file based on a progression. It is intended for guitarists who wish to quickly create a MIDI file from chords; however, plans to make MidiWrite more flexible are in the works.

MidiWrite takes in a series of chords and creates a MIDI file in the directory MidiWrite was ran. It accepts chords of the following types:

|  command  | type of chord |
|:---------:|:-------------:|
|  [chord*] | 5 string root |
| [chord**] | 6 string root |
|  [eadgbe] | fret notation |

# Custom Files
MidiWrite can be pointed to a text file containing definitions of user-defined chords.
A user-defined chord looks like the following:

    <chord>%:<[notes]> or <chord>%<[fret notation]>

The **%** denotes a user-defined chord.


# Markup Language
MidiWrite uses a markup language to abstract writing code to convert the chords into a midi file.
A sample markup file is shown below.

    <begin [title]>
        <prefix>
            <time-sig=[time_sig]> (not a necessary tag, default is 4/4)
            <tempo=[tempo]> (not a necessary tag, default is 120)
            <key_sig=[key_sig]> (not a necessary tag, default is Cmaj)
        </prefix>
        <commands>
            [<command1> <command2> ... ]
        </commands>
    <end [title]>

where commands is a comma-separated list of chords *(see my_prog.mwm).*

## Command flags

Each command can have optional flags denoting additional parameters:

| flag |           command           |
|:----:|:---------------------------:|
|  -a  |       arpeggiate chord      |
|  -ar | arpeggiate chord in reverse |
|  -w  |          whole note         |
|  -h  |     half note (default)     |
|  -q  |         quarter note        |
|  -e  |         eighth note         |
|  -s  |        sixteenth note       |
|  -t  |          32nd note          |

Note that the prefix is unnecessary if a time signature of 4/4, tempo of 120 and key signature of Cmaj are desired.

## Building the file

To build the MIDI file, run from the command line as follows:

```sh
$ python midiwrite.py [markup file] [octave shift](optional)
```

MidiWrite then builds a MIDI file based on the metadata in the markup file.

Note that MidiWrite is *not* backwards compatible with earlier versions of Python; currently, MidiWrite works only with Python 3.6+ (due to type hinting).
However, removal of the type hinting should make MidiWrite compatible with all versions of Python 3.


# Planned Extensions
The following functions are planned to be incorporated into the markup language:
* Single note and scale support
* Individual note markup shorthands

    |       command      | type of chord |
    |:------------------:|:-------------:|
    | <ea[d_1 h d_2]gbe> |   hammer-on   |
    | <ea[d_2 h d_1]gbe> |    pull-off   |
    |  <[eadgbe] s [eadgbe]> | fret notation |

# Future plans for MidiWrite
Future extensions are planned, including:
* single-note and scale writing
* note-length variability
* multiple track writing
* musical idea abstraction (e.g. 7th chords in cycle of 5ths for the key of Abmaj)
