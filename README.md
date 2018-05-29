# MidiWrite by Cameron Terry

#### May 28, 2018

# Intro
MidiWrite makes turning a chord progression into a MIDI file a super simple process while lessening the time required needed to create a MIDI file based on a progression. It is intended for guitarists who wish to quickly create a MIDI file from chords; however, plans to make MidiWrite more flexible are in the works.

MidiWrite takes in a series of chords and creates a MIDI file in the directory MidiWrite was ran. It accepts chords of the following types:

* [chord*] : 5 string root
* [chord**] : 6 string root
* [eadgbe] : fret notation


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

Note that the prefix is unnecessary if a time signature of 4/4, tempo of 120 and key signature of Cmaj are desired.

To build the MIDI file, run from the command line as follows:

```sh
$ python midiwrite.py [markup file] [octave shift](optional)
```

MidiWrite then builds a MIDI file based on the metadata in the markup file.

Note that MidiWrite is *not* backwards compatible with earlier versions of Python; currently, MidiWrite works only with Python 3.6+ (due to type hinting).
However, removal of the type hinting should make MidiWrite compatible with all versions of Python 3.


# Planned Extensions
The following functions are planned to be incorporated into the markup language:

<command>'s additional flags:
* -a : arpeggiate chord
* -w : whole note
* -h : half note
* -q : quarter note
* -e : eighth note
* -s : sixteenth note
* -t : 32nd note

Individual note markup shorthands are also possible additional functions:

    <ea[d_1hd_2]gbe> for hammer-ons
    <ea[d_2pd_1]gbe> for pull-offs
    <eadgbe s eadgbe> for slides


Future plans for MidiWrite
==========================
Future extensions are planned, including:
    -note-length variability
    -individual note writing
    -scale writing
    -musical idea abstraction (e.g. 7th chords in cycle of 5ths for the key of Abmaj)
