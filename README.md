# MidiWrite by Cameron Terry

#### May 28, 2018

# Intro
MidiWrite makes turning a chord progression into a MIDI file a simple process while lessening the time required needed to create a MIDI file based on a progression. It is intended for guitarists who wish to quickly create a MIDI file from chords; however, plans to make MidiWrite more flexible are in the works.

MidiWrite takes in a series of chords and creates a MIDI file in the directory MidiWrite was ran. It accepts chords of the following types:

|      Command     | Type of chord |
|:----------------:|:-------------:|
|  ```[chord*]```  | 6 string root |
|  ```[chord**]``` | 5 string root |
| ```[chord***]``` | 4 string root |
|  ```[eadgbe]```  | fret notation |

# Custom Files
MidiWrite can be pointed to a text file containing definitions of user-defined chords.
A user-defined chord looks like the following:

    <chord>%:<[notes]> or <chord>%<[fret notation]>

The **%** denotes a user-defined chord.

To specify multiple user-defined transpositions of the same chord, use ```<chord>%[i]``` to refer to a specific transposition.
  


# Markup Language
MidiWrite uses a markup language to abstract writing code for converting chords into a MIDI file.
A sample markup file is shown below.

    <begin [title]>
        <prefix>
            <time-sig=[time_sig]> (not a necessary tag, default is 4/4)
            <tempo=[tempo]> (not a necessary tag, default is 120)
            <key_sig=[key_sig]> (not a necessary tag, default is Cmaj)
            <ppq=[ppq]> (not a necessary tag, default is 96)
        </prefix>
        <custom_file=[custom_file]> (optional)
        <mode=[mode]> (optional)
        <commands>
            [<command1> <command2> ... ]
        </commands>
    <end [title]>

where ```ppq``` is the parts per quarter (or ticks per quarter note), and  ```<commands>``` contains a comma-separated list of chords *(see my_prog.mwm).*
Note that ```<prefix>``` is unnecessary if a time signature of *4/4*, tempo of *120*, key signature of *Cmaj*, and ```ppq``` of *96* are desired.

MidiWrite supports two modes of chord entry: *chord name mode* and *roman numeral mode*.

|     Mode      |       Type         |
|:-------------:|:------------------:|
| ```cn_mode``` |   chord name mode  |
| ```rn_mode``` | roman numeral mode |

Root string specifications are the same as chord name mode.

## Command flags

Each command can have optional flags denoting additional parameters:

|    Flag   |        Command        |
|:---------:|:---------------------:|
|  ```-a``` |    chord name mode    |
| ```-ar``` |   roman numeral mode  |
|  ```-o``` |   double whole note   |
| ```-.w``` |   dotted whole note   |
|  ```-w``` |       whole note      |
| ```-.h``` |    dotted half note   |
|  ```-h``` |  half note (default)  |
| ```-.q``` |  dotted quarter note  |
|  ```-q``` |      quarter note     |
| ```-.e``` |   dotted eighth note  |
|  ```-e``` |      eighth note      |
| ```-.s``` | dotted sixteenth note |
|  ```-s``` |     sixteenth note    |
| ```-.t``` |    dotted 32nd note   |
|  ```-t``` |       32nd note       |

## Patterns
MidiWrite also accepts a pattern denoting the time signature and pattern composition.
Specify the pattern in the command as follows:

    <"[time_sig]":"[pattern_no]" ... [command]>
    
If the pattern is not found in MidiWrite, it will search in a custom file (if provided).

The syntax for specifying a custom pattern is ```"[time_sig]:[pattern_no]";"[pattern]"```.

Characters ```0, 1, 2, 3, 4, 5``` correspond to *Low E, A, D, G, B, High E*, respectively.

## Additional Functionalities
MidiWrite also offers basic musical idea abstraction tools to quickly create progressions.
For example, to find cycle of fifths 7 chords for the key of Abmaj, use
   
   ```MidiWrite.build_base_chords(MidiWrite.cycle_of_mths('Ab', 3), "7")```

to return a list containing all possible chords (in respective order) to build a cycle of fifths progression around Abmaj (to three iterations).

Further extensions are planned, including building in common progressions such as:

* I -> IV -> V
* I -> vi -> IV -> V
* ii -> V -> I

and others.
## Building the file

To build the MIDI file, run from the command line as follows:

```sh
$ python midiwrite.py [markup file] [octave shift](optional)
```

MidiWrite then builds a MIDI file based on the metadata in the markup file.

Note that MidiWrite is *not* backwards compatible with earlier versions of Python; currently, MidiWrite works only with Python 3.6+ (due to type hinting). However, removal of type hinting should make MidiWrite compatible with all versions of Python 3.

# Planned Extensions
The following functions are planned to be incorporated into the markup language:
* Single note and scale support
* Individual note markup shorthands

    |        Command              | Type of Chord |
    |:---------------------------:|:-------------:|
    |   ```<ea[d_1 h d_2]gbe>```  |   hammer-on   |
    |   ```<ea[d_2 h d_1]gbe>```  |    pull-off   |
    | ```<[eadgbe] s [eadgbe]>``` |     slide     |

# Future plans for MidiWrite
Future extensions are planned, including:
* single-note and scale writing
* multiple track writing
