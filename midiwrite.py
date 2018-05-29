# markup file parser for MidiWrite

import sys
from midi_write import MidiWrite

if __name__ == "__main__":
    file = sys.argv[1]
    output_file = file[:-4] + ".midi"
    custom_file = None
    title = None
    time_sig = None
    key_sig = None
    command_listing = False
    commands = []

    if len(sys.argv) > 2:
        octave_shift = int(sys.argv[2])
    else:
        octave_shift = None

    with open(file, 'r') as f:
        first_line = True
        prefix = False
        for line in f:
            line = line.strip()[1:-1]
            if first_line:
                if not line.startswith("begin"):
                    print("Error: file does not start with 'begin'.")
                    exit(1)
                else:
                    title = line.split(" ")[1]

            if command_listing:
                if line == "/commands":
                    command_listing = False
                else:
                    commands += line.replace("\"", "").replace(" ", "").split(',')
                    if line.startswith("end"):
                        print("Error: Commands not finished.")

            if prefix:
                if line.startswith("time-sig"):
                    time_sig = line.split("=")[1]
                elif line.startswith("tempo"):
                    tempo = line.split("=")[1]
                elif line.startswith("key-sig"):
                    key_sig = line.split("=")[1]
                elif line == "/prefix":
                    if prefix:
                        prefix = False
                else:
                    print("Error: variable declaration outside of prefix.")
                    exit(1)
            else:
                if line.startswith("custom_file"):
                    custom_file = line.split("=")[1][1:-1]

                if line == "commands":
                    command_listing = True

            if line == "prefix":
                prefix = True

            first_line = False

    if octave_shift is not None:
        if octave_shift < 0:
            MidiWrite.octave_shift_down(octave_shift)
        else:
            MidiWrite.octave_shift_up(octave_shift)

    MidiWrite.set_custom_file(custom_file)
    MidiWrite.write_preqs(output_file)

    if time_sig is None:
        if tempo is not None and key_sig is None:
            MidiWrite.write_track(output_file, commands, title=title, tempo=tempo)
        elif tempo is None and key_sig is not None:
            MidiWrite.write_track(output_file, commands, title=title, key=key_sig)
    elif tempo is None:
        if key_sig is None:
            MidiWrite.write_track(output_file, commands, title=title, time=time_sig)
        else:
            MidiWrite.write_track(output_file, commands, title=title, time=time_sig, key=key_sig)
    elif key_sig is None:
        if tempo is None:
            MidiWrite.write_track(output_file, commands, title=title, time=time_sig, key=key_sig)
        else:
            MidiWrite.write_track(output_file, commands, title=title, time=time_sig, tempo=tempo)
    else:
        MidiWrite.write_track(output_file, commands, title=title, time=time_sig, tempo=tempo, key=key_sig)
