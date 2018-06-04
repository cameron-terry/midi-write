# markup file parser for MidiWrite

import sys
from midi_writer import MidiWrite

if __name__ == "__main__":
    file = sys.argv[1]
    output_file = file[:-4] + ".midi"
    custom_file = None
    mode = "cn_mode"
    title = None
    ppq = 96
    tempo = 120
    time_sig = "4/4"
    key_sig = "Cmaj"
    command_listing = False
    commands = []

    was_prefix = False

    if len(sys.argv) > 2:
        octave_shift = int(sys.argv[2])
    else:
        octave_shift = None

    i = 0
    with open(file, 'r') as f:
        first_line = True
        prefix = False
        for line in f:
            line = line.strip()[1:-1]
            if first_line:
                if not line.startswith("begin"):
                    print("Error in [%s]: file does not start with 'begin' [line: %d]" % (file, i + 1))
                    exit(1)
                else:
                    title = line.split(" ")[1]

            if command_listing:
                if line == "/commands":
                    command_listing = False
                else:
                    commands += line.replace("\"", "").replace(" ", "").split(',')
                    if line.startswith("end"):
                        print("Error in [%s]: Commands not finished [line: %d]" % (file, i + 1))

            if prefix:
                if line.startswith("time-sig"):
                    time_sig = line.split("=")[1]
                elif line.startswith("tempo"):
                    tempo = int(line.split("=")[1])
                elif line.startswith("key-sig"):
                    key_sig = line.split("=")[1]
                elif line.startswith("mode"):
                    mode = line.split("=")[1]
                elif line.startswith("ppq"):
                    ppq = line.split("=")[1]
                elif line == "/prefix":
                    if prefix:
                        prefix = False
                else:
                    print("Error in [%s]: variable declaration outside of prefix [line: %d]" % (file, i + 1))
                    exit(1)
            else:
                if line.startswith("custom_file"):
                    custom_file = line.split("=")[1][1:-1]

                if line == "commands":
                    command_listing = True

            if line == "prefix":
                prefix = True
                was_prefix = True

            first_line = False

            if line.startswith("end"):
                if title != line.split(" ")[1]:
                    print("Error in [%s]: beginning and end tags do not match titles [line: %d]" % (file, i + 1))
                    exit(1)

            i += 1

    MidiWrite.set_custom_file(custom_file)

    MidiWrite.write_preqs(output_file, time=time_sig, tempo=tempo, ppq=ppq)

    if time_sig is None:
        if tempo is not None and key_sig is None:
            MidiWrite.write_track(output_file, commands, title=title, shift=octave_shift, mode=mode)
        elif tempo is None and key_sig is not None:
            MidiWrite.write_track(output_file, commands, title=title, key=key_sig, shift=octave_shift, mode=mode)
    elif tempo is None:
        if key_sig is None:
            MidiWrite.write_track(output_file, commands, title=title, shift=octave_shift, mode=mode)
        else:
            MidiWrite.write_track(output_file, commands, title=title, key=key_sig, shift=octave_shift, mode=mode)
    elif key_sig is None:
        if tempo is None:
            MidiWrite.write_track(output_file, commands, title=title, key=key_sig, shift=octave_shift, mode=mode)
        else:
            MidiWrite.write_track(output_file, commands, title=title, shift=octave_shift, mode=mode)
    else:
        MidiWrite.write_track(output_file, commands, title=title, key=key_sig, shift=octave_shift, mode=mode)
