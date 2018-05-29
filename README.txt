MidiWrite by Cameron Terry
May 28, 2018

Intro
=====

MidiWrite makes turning a chord progression into a midi file a super simple process while lessening the time required needed to create a midi file based on a progression.
It is intended for guitarists who wish to quickly write guitar chords into a midi file; however, plans to generalize MidiWrite are in the works.

MidiWrite takes in a series of chords and creates a midi file in the directory MidiWrite was ran. It accepts chords of the following type:

[chord*] -> 5 string root
[chord**] -> 6 string root
[eadgbe] -> fret notation


Future plans
===========

Future extensions are planned, including:
    -arpeggios
    -note-length variability
    -custom defined chord names
 
And most importantly, a markup file which will run MidiWrite. The markup file would like something of the following:

   <begin [title]>
       <prefix>
           <time-sig=[time_sig]> (not a necessary tag, default is 4/4)
           <tempo=[tempo]> (not a necessary tag, default is 120
           <key_sig=[key_sig]> (not a necessary tag, default is Cmaj)
       </prefix>
       <commands>
           [<command1> <command2> ... ]
       </commands>
   <end [title]>

with <command> having the following flags:
    -a : arpeggiate chord
    -w : whole note
    -h : half note
    -q : quarter note
    -e : eighth note
    -s : sixteenth note
    -t : 32th note

Individual note markup shorthands are also possible extensions:
    - <ea[d_1hd_2]gbe> for hammer-ons
    - <ea[d_2pd_1]gbe> for pull-offs
    - <eadgbe s eadgbe> for slides


The markup file will abstract the MidiWrite code so that the user can save progressions in a markup file which will be processed by MidiWrite.
