# Example use of MidiWrite
# * = 5 string root
# ** = 6 string root


from midi_write import MidiWrite

file = "my_prog.midi"

commands = ["Dbmaj7*", "x8786x", "Bbm7**", "Am7**",
            "Abm7**", "Db7*", "Gbmaj7**", "x2222x",
            "Dbmaj7*", "Bbm7**", "Ebm7*", "Ab13**",
            "Dbmaj7*", "Bbm7**", "Ebm7*", "Ab13**"]

MidiWrite.octave_shift_down(1)
MidiWrite.write_preqs(file)
MidiWrite.write_track(file, commands, title="My Progression", debug=True)
