##-------------------------------------------------------------------------------------------------------------------##
# note: currenty musescore does not open these kinds of .midi files, unexpected eof
# TODO: check support for arpeggio patterns e.g. "4/4:1;[03-1-2-03-1-2]"
#       for now patterns are dotted eighths
#       user can point to a custom defined file
# TODO: add support for single notes, scales and other musical ideas including common progressions
#       e.g. add support for hammer-ons / pull-offs, and more
# TODO: improve debug functionality
#       give more feedback on different areas of the program
##-------------------------------------------------------------------------------------------------------------------##
# MidiWrite by Cameron Terry
# May 28, 2018
#
# MidiWrite makes turning a chord progression into a MIDI file a super simple process while lessening the time
# required needed to create a MIDI file based on a progression.
##-------------------------------------------------------------------------------------------------------------------##

import array
import struct
import math
import re
from ToneHelper import ToneHelper


# class for helper functions
class Misc:
    """
    Checks input to see if it is a number.
    """
    @staticmethod
    def is_number(s):
        try:
            int(s)
            return True
        except ValueError:
            return False


class MidiWrite:
    note_map = ToneHelper.note_map
    ppq = None
    key_signature = None

    # user defined file that contains additional chord mappings
    custom_file = None

    debug = False  # set in track_chunk

    # constant bytes
    mthd                = b'\x4d\x54\x68\x64'
    header_chunk_length = b'\x00\x00\x00\x06'

    mtrk                = b'\x4d\x54\x72\x6b'
    track_chunk_length  = b'\x00\x00\x00\x14'

    eof                 = b'\x01\xff\x2f\x00'

    @staticmethod
    def set_custom_file(file: str):
        """
        Sets a pointer to the custom file.
        :param file: the custom file
        :return: none
        """
        if file is not None:
            MidiWrite.custom_file = file

    @staticmethod
    def octave_shift_down(n: int):
        """
        Shifts all notes down n octaves.
        :param n: number of octaves to shift down
        :return: none
        """
        if n > 0:
            for key in MidiWrite.note_map:
                MidiWrite.note_map[key] -= n * 12

    @staticmethod
    def octave_shift_up(n: int):
        """
        Shifts all notes up n octaves.
        :param n: number of octaves to shift up
        :return: none
        """
        if n > 0:
            for key in MidiWrite.note_map:
                MidiWrite.note_map[key] += n * 12

    # based on pseudo-code from http://midi.teragonaudio.com/tech/midifile/vari.htm
    # and http://need12648430.github.io/tinysmf/docs/
    @staticmethod
    def write_var_len(n: int) -> [int]:
        """
        Transforms an integer into a variable-length quantity.
        :param n: the integer to convert
        :return: variable-length quantity array of the integer
        """
        original = n
        byte_arr = [0 for _ in range(4)]

        c = n & 0x7F
        i = 0
        n >>= 7
        byte_arr[i] = c
        i += 1

        while n > 0:
            c = 0x80 | (n & 0x7F)
            n >>= 7
            byte_arr[i] = c
            i += 1

        byte_arr = byte_arr[:i]
        byte_arr.reverse()

        if i == 1:
            byte_arr = [0] + byte_arr

        if MidiWrite.debug:
            statement = "Convert {} [{}] to variable-length quantity".format(original, hex(original))
            print(statement)
            print("="*len(statement))
            print("Byte transfer started...")
            for i in range(len(byte_arr)):
                print("Original: {}, sending byte {}: {}".format(original, i+1, hex(byte_arr[i])))
            print("Done sending.\n")

        byte_arr = array.array('B', byte_arr).tostring()
        return byte_arr

    @staticmethod
    def read_var_len(n: [int]) -> int:
        """
        Converts a variable-length quantity to an integer.
        :param n: the variable-length quantity to convert
        :return: integer representation of the variable-length quantity
        """
        i = 0
        c = n[i]
        q = c & 0x7f

        while c & 0x80:
            i += 1
            c = n[i]
            q = (q << 7) | (c & 0x7f)

        if len(n) > 0 and q == 0:
            q = n[1]

        return q

    @staticmethod
    def write_preqs(file: str, time: str="4/4", tempo: int=120, ppq: int=96):
        """
        Writes the pre-requisite headers to the midi file.
        :param file: the midi file to write to
        :param time: the time signature
        :param tempo: the bpm
        :param ppq: the parts per quarter (ticks per quarter note)
        :return: none
        """
        # check prefix
        if file[-5:] != ".midi":
            print("File not could be created.")
            exit(1)

        MidiWrite.ppq = MidiWrite.write_var_len(ppq)

        MidiWrite.write_header_chunk(file)
        MidiWrite.write_track_chunk(file, time, tempo)

    @staticmethod
    def write_header_chunk(file: str):
        """
        Writes the header chunk to the midi file.
        :param file: the midi file to write to
        :return: none
        """
        fmat         = MidiWrite.write_var_len(1)  # multiple-track format (0 is single)
        track        = MidiWrite.write_var_len(2)  # 2 tracks (header, track)
        quart_length = MidiWrite.ppq  # quarter tick length

        with open(file, "wb") as f:
            f.write(MidiWrite.mthd)
            f.write(MidiWrite.header_chunk_length)
            f.write(fmat)
            f.write(track)
            f.write(quart_length)

    @staticmethod
    def write_track_chunk(file: str, time, tempo):
        """
        Writes the track chunk to the midi file.
        :param file: the midi file to write to
        :param time: the time signature as a string
        :param tempo: the tempo of the progression as an integer
        :return: none
        """

        with open(file, "ab") as f:
            f.write(MidiWrite.mtrk)
            f.write(MidiWrite.track_chunk_length)

        MidiWrite.write_time_sig(file, time, tempo)

    @staticmethod
    def write_time_sig(file: str, time: str, tempo: int):
        """
        Writes the time signature and other relevant meta tags to the midi file.
        :param file: the midi file to write to
        :param time: the time signature as a string
        :param tempo: the tempo of the progression as an integer
        :return: none
        """
        tempo_bytes = b'\x00\xff\x51\x03'
        eot         = b'\x83\x00\xff\x2f\x00'

        time_sig = b'\x00\xff\x58\x04'
        time_sig_end_bytes = b'\x24\x08'

        # to convert bpm to tempo, use 60_000_000 / tempo
        tempo_hex = hex(int(60_000_000 / tempo))  # number of microseconds in a minute

        if len(tempo_hex) % 2 == 1:
            byte_1 = int(tempo_hex[:2] + '0' + tempo_hex[2], 0)
            byte_2 = int(tempo_hex[:2] + tempo_hex[3:5], 0)
            byte_3 = int(tempo_hex[:2] + tempo_hex[5:], 0)
            tempo_bytes += struct.pack("BBB", byte_1, byte_2, byte_3)

        ts_num = bytes([int(time.split("/")[0])])
        ts_denom = bytes([int(math.log(int(time.split("/")[1]), 2))])

        time_sig += ts_num + ts_denom + time_sig_end_bytes

        with open(file, "ab") as f:
            f.write(time_sig)
            f.write(tempo_bytes)
            f.write(eot)

    @staticmethod
    def write_track(file: str, commands: [bytes], title='Main', key='Cmaj', mode="cn_mode", shift=0, debug=False, arpeggiate=False):
        """
               Writes the track data to the midi file.
               :param file: the midi file to write to
               :param commands: the notes to write to the midi file
               :param title: the title of the track
               :param key: the key signature of the track
               :param mode: the type of chords entered
               :param shift: octave shift up / down
               :param debug: show progress on creating midi file
               :param arpeggiate: arpeggiate every chord
               :return: none
        """
        MidiWrite.key_signature = key

        if shift is None:
            shift = 0

        if shift != 0:
            if shift < 0:
                MidiWrite.octave_shift_down(abs(shift))
            else:
                MidiWrite.octave_shift_up(shift)

        if debug:
            MidiWrite.debug = True

        chunk_length = b'\x00\x00'  # TODO: what is this used for?
        preset = b'\x00\xc1' + bytes([24])  # guitar
        chunk_title = b'\x00\xff\x03'
        key_sig = b'\x00\xff\x59\x02'

        chunk_title_length = bytes([len(title)])
        chunk_title += chunk_title_length
        for letter in title:
            chunk_title += bytes([ord(letter)])

        flats, major_minor = ToneHelper.get_key(key)

        key_sig += bytes([flats if flats > 0 else 256 + flats])  # two's complement if negative
        key_sig += bytes([major_minor])

        # not sure why count is 1 less than it needs to be
        count = 1 + len(chunk_length) + len(chunk_title) + len(key_sig) + len(preset) + len(MidiWrite.eof)
        notes_list = []

        flip = False
        for chord in commands:
            if arpeggiate:
                notes = MidiWrite.find_notes(chord, flip=flip, mode=mode)
            else:
                notes = MidiWrite.find_notes(chord, mode=mode)
            for note in notes:
                count += len(note)
            notes_list.append(notes)
            if arpeggiate:
                flip = not flip

        b = MidiWrite.write_var_len(count)
        chunk_length += b

        # just a check to make sure number is formatted correctly
        if len(chunk_length) < 4:
            chunk_length = chunk_length[0:2] + b'\x00' + chunk_length[2:]

        with open(file, "ab") as f:
            f.write(MidiWrite.mtrk)
            f.write(chunk_length)
            f.write(chunk_title)
            f.write(key_sig)
            f.write(preset)

            for i in range(len(notes_list)):
                if MidiWrite.debug:
                    statement = "Write {} to {}".format(commands[i], file)
                    print(statement)
                    print("=" * len(statement))
                    print("Writing \"{}\" to {}... ".format(commands[i], file), end="")
                for note in notes_list[i]:
                    f.write(note)
                if MidiWrite.debug:
                    print("Done.\n")

            f.write(MidiWrite.eof)

    @staticmethod
    def find_notes(chord, flip=False, mode="cn_mode") -> [bytes]:
        """
        find the notes needed to play the chord
        :param chord: the chord to find the notes of
        :return: the midi representation of the chord / notes
        """
        start_simul       = b'\x00\x90'
        note_on           = b'\x40'
        note_off          = b'\x00'
        delay             = MidiWrite.write_var_len(MidiWrite.read_var_len(MidiWrite.ppq) * 2)  # half note default
        time_arp_delay    = bytes([MidiWrite.ppq[1] // 2])  # 1/2 of b'\x60', the quarter note length

        notes, arpeggiate, arp_rev, note_type, pattern = MidiWrite.chord_shape(chord, mode=mode)

        if arp_rev:
            flip = not flip

        # TODO: test all delays and finish patterns
        if note_type == 'o':
            if pattern is not None:  # triplet version
                delay = MidiWrite.write_var_len(int(MidiWrite.read_var_len(MidiWrite.ppq) * 2.67))
                time_arp_delay = MidiWrite.write_var_len(int(MidiWrite.read_var_len(MidiWrite.ppq) * 1.335))
            else:
                delay = MidiWrite.write_var_len(MidiWrite.read_var_len(MidiWrite.ppq) * 8)
                time_arp_delay = MidiWrite.write_var_len(MidiWrite.read_var_len(MidiWrite.ppq) * 4)
        elif note_type == '.w':
            if pattern is not None:
                delay = MidiWrite.write_var_len(MidiWrite.read_var_len(MidiWrite.ppq) * 4)
                time_arp_delay = MidiWrite.write_var_len(MidiWrite.read_var_len(MidiWrite.ppq) * 2)
            else:
                delay = MidiWrite.write_var_len(MidiWrite.read_var_len(MidiWrite.ppq) * 6)
                time_arp_delay = MidiWrite.write_var_len(MidiWrite.read_var_len(MidiWrite.ppq) * 3)
        elif note_type == 'w':
            if pattern is not None:
                delay = MidiWrite.write_var_len(int(MidiWrite.read_var_len(MidiWrite.ppq) * 2.67))
                time_arp_delay = MidiWrite.write_var_len(int(MidiWrite.read_var_len(MidiWrite.ppq) * 1.335))
            else:
                delay = MidiWrite.write_var_len(MidiWrite.read_var_len(MidiWrite.ppq) * 4)
                time_arp_delay = MidiWrite.write_var_len(MidiWrite.read_var_len(MidiWrite.ppq) * 2)
        elif note_type == '.h':  # divide by 1.5
            if pattern is not None:
                delay = MidiWrite.write_var_len(int(MidiWrite.read_var_len(MidiWrite.ppq) * 2))
                time_arp_delay = MidiWrite.write_var_len(int(MidiWrite.read_var_len(MidiWrite.ppq) * 1))
            else:
                delay = MidiWrite.write_var_len(MidiWrite.read_var_len(MidiWrite.ppq) * 3)
                time_arp_delay = MidiWrite.write_var_len(int(MidiWrite.read_var_len(MidiWrite.ppq) * 1.5))
        elif note_type == 'h':
            if pattern is not None:
                delay = MidiWrite.write_var_len(int(MidiWrite.read_var_len(MidiWrite.ppq) * 1.34))
                time_arp_delay = MidiWrite.write_var_len(int(MidiWrite.read_var_len(MidiWrite.ppq) * 0.665))
            else:
                pass
        elif note_type == '.q':
            delay = MidiWrite.write_var_len(int(MidiWrite.read_var_len(MidiWrite.ppq) * 1.5))
            time_arp_delay = MidiWrite.write_var_len(int(MidiWrite.read_var_len(MidiWrite.ppq) * 0.75))
        elif note_type == 'q':  # works
            delay = bytes([MidiWrite.ppq[1]])  # don't send the /x00 (trial & error)
            time_arp_delay = bytes([MidiWrite.ppq[1] // 2])
        elif note_type == '.e':
            delay = bytes([int(MidiWrite.ppq[1] * 0.75)])
            time_arp_delay = bytes([int(MidiWrite.ppq[1] * 0.375)])
        elif note_type == 'e':  # works
            delay = bytes([MidiWrite.ppq[1] // 2])
            time_arp_delay = bytes([MidiWrite.ppq[1] // 4])
        elif note_type == '.s':
            delay = bytes([int(MidiWrite.ppq[1] * 0.375)])
            time_arp_delay = bytes([int(MidiWrite.ppq[1] * 0.1875)])
        elif note_type == 's':
            delay = bytes([MidiWrite.ppq[1] // 4])
            time_arp_delay = bytes([MidiWrite.ppq[1] // 8])
        elif note_type == '.t':
            delay = bytes([int(MidiWrite.ppq[1] * 0.1875)])
            time_arp_delay = bytes([int(MidiWrite.ppq[1] * 0.09375)])
        elif note_type == 't':
            delay = bytes([MidiWrite.ppq[1] // 8])
            time_arp_delay = bytes([MidiWrite.ppq[1] // 16])

        note_arr = []

        if notes:
            # TODO: make num_notes variable
            num_notes = 4 if len(notes) >= 4 else len(notes)
            if not arpeggiate:
                if pattern is not None:
                    pattern = pattern.split("-")
                    for seg in pattern:
                        value = 0
                        for i in range(len(seg)):
                            value = int(seg[i])

                            # means 0x90 - turn on - 0x?? - 60 + n (C#, 60 is C) -- 0x40
                            note_arr.append(start_simul + bytes(notes[value:value+1]) + note_on)
                            if MidiWrite.debug:
                                statement = "Note on"
                                print(statement)
                                print("="*len(statement))
                                print("{} on".format(notes[value:value+1]))

                        note_arr.append(delay + bytes(notes[value:value+1]) + note_off)
                        if MidiWrite.debug:
                            statement = "Note off"
                            print(statement)
                            print("=" * len(statement))
                            print("{} off".format(notes[value:value+1]))

                        for i in range(len(seg) - 1):
                            value = int(seg[i])
                            note_arr.append(b'\x00' + bytes(notes[value:value+1]) + note_off)
                            if MidiWrite.debug:
                                statement = "Note off"
                                print(statement)
                                print("=" * len(statement))
                                print("{} off".format(notes[value:value+1]))

                else:
                    for i in range(len(notes)):
                        # means 0x90 - turn on - 0x?? - 60 + n (C#, 60 is C) -- 0x40
                        note_arr.append(start_simul + bytes(notes[i:i+1]) + note_on)

                    note_arr.append(delay + bytes(notes[len(notes)-1:len(notes)]) + note_off)

                    for j in range(len(notes) - 1, 0, -1):
                        # turn off all at same time
                        note_arr.append(b'\x00' + bytes(notes[j-1:j]) + note_off)
            else:
                if not flip:
                    for i in range(num_notes):
                        # means 0x90 - turn on - 0x?? - 60 + n (C#, 60 is C) -- 0x40
                        note_arr.append(start_simul + bytes(notes[i:i+1]) + note_on)
                        # means 0x90 - turn off - 0x?? - 60 + n (C#, 60 is C) -- 0x00 after time_arp_delay
                        note_arr.append(time_arp_delay + bytes(notes[i:i+1]) + note_off)
                else:
                    for i in range(num_notes, 0, -1):
                        note_arr.append(start_simul + bytes(notes[i-1:i]) + note_on)
                        note_arr.append(time_arp_delay + bytes(notes[i-1:i]) + note_off)

            return note_arr
        else:
            failed_note = 'C'
            return [b'\x81\x40\x90' + bytes([ToneHelper.note_map[failed_note]]) + b'\x20',
                    b'\x81\x40' + bytes([ToneHelper.note_map[failed_note]]) + b'\x00']  # return single failed note

    @staticmethod
    def chord_shape(chord, mode="cn_mode") -> [int]:
        """
        determine the notes of the chord based on chord type / fret locations
        :param chord: the chord to find the notes of
        :param mode: the type of chords entered (normal / roman numeral)
        :return: the chord as a set of integer notes
        """
        arpeggiate = False
        pattern = None
        arp_rev = False
        found_flags = False
        search_chord = chord
        note_type = 'd'
        
        if isinstance(chord, str):
            # TODO: make sure pattern time sig matches given time sig
            # check for pattern signal
            for pat in ToneHelper.patterns:
                if pat in chord:
                    pattern = ToneHelper.patterns[pat]
                    if pattern is None and MidiWrite.custom_file is not None:
                        if MidiWrite.debug:
                            print("Pattern not found in default, searching {}...".format(MidiWrite.custom_file))
                        with open(MidiWrite.custom_file, 'r') as f:
                            custom_pattern_dict = {}
                            for line in f:
                                line = line.split(";")
                                if len(line) > 1:
                                    custom_pattern_dict[line[0]] = line[1]  # is a str?
                            for c_pat in custom_pattern_dict:
                                if c_pat in chord:
                                    pattern = custom_pattern_dict[c_pat]
                    else:
                        if MidiWrite.debug:
                            print("pattern found: {}".format(pattern))
                        search_chord = search_chord.replace(pat, "")

            # check for arpeggio flags
            if "-a" in chord:
                arpeggiate = True
                if "-ar" in chord:
                    arp_rev = True
                    search_chord = search_chord.replace('-ar', '')
                else:
                    search_chord = search_chord.replace('-a', '')

            time_flags = ['-o', '-.w', '-w', '-.h', '-h', '-.q', '-q', '-.e', '-e', '-.s', '-s', '-.t', '-t']

            # check to make sure only one time flag is selected
            for _ in range(2):
                for flag in time_flags:
                    if flag in search_chord and not found_flags:
                        found_flags = True
                        note_type = flag[1:]
                        search_chord = search_chord.replace(flag, '')
                    elif flag in search_chord and found_flags:
                        print(search_chord)
                        print("Error: time flag already selected: -" + note_type)
                        exit(1)

            if mode == 'rn_mode':
                base = None
                secondary_chord = False

                sfs = ["bb", "b", "#", "##"]

                for element in ToneHelper.scale_dict:
                    if element in MidiWrite.key_signature:
                        base = element
                        break

                for value in ToneHelper.rn_scale:
                    if value in search_chord.lower():
                        acc = None
                        if "/" in search_chord:  # secondary chord
                            secondary_chord = True
                            # first, replace all *'s
                            secondary_value = re.sub(r'[*]+', r'', search_chord.split("/")[1]).lower()
                            primary_value = search_chord.split("/")[0][:-1].lower()

                            search_chord = search_chord.replace(str("/" + secondary_value.upper()), "")
                            search_chord = search_chord.replace(str("/" + secondary_value), "")

                            for accidentals in sfs:
                                if accidentals in primary_value:
                                    acc = accidentals
                                    primary_value = primary_value.replace(accidentals, "")
                                    search_chord = search_chord.replace(accidentals, "")

                            adjust = ToneHelper.shift_to_scale(primary_value, base)

                            if acc is not None:
                                adjust = ToneHelper.sharp_flat_shifted_note(acc, secondary_value, adjust)
                            else:
                                adjust = ToneHelper.shift_to_scale(secondary_value, adjust)
                        else:
                            primary_value = None
                            for accidentals in sfs:
                                if accidentals in search_chord:
                                    acc = accidentals
                                    primary_value = value.replace(accidentals, "")
                                    search_chord = search_chord.replace(accidentals, "")

                            if acc is not None:
                                adjust = ToneHelper.sharp_flat_shifted_note(acc, primary_value, base)
                            else:
                                adjust = ToneHelper.shift_to_scale(value, base)

                        if value.upper() in search_chord:
                            search_chord = search_chord.replace(value.upper(), adjust + "maj")

                        else:
                            search_chord = search_chord.replace(value.lower(), adjust + "m")

                        if "7" in search_chord and secondary_chord:
                            search_chord = search_chord.replace("maj", "").replace("m", "")
                        elif "13" in search_chord:
                            search_chord = search_chord.replace("maj", "").replace("m", "")

                        if MidiWrite.debug:
                            statement = "Convert roman numeral to chord name"
                            print(statement)
                            print("="*len(statement))
                            print("[{}] resolved to [{}].\n".format(chord, search_chord))

                        break

            # look for note and chord type in dictionaries
            for element in MidiWrite.note_map:
                if element in search_chord:
                    base = MidiWrite.note_map[element]
                    if '%' not in search_chord:
                        for c_shape in ToneHelper.chord_dict:
                            if c_shape in search_chord:
                                if "***" in search_chord:
                                    if MidiWrite.debug:
                                        statement = "Found chord"
                                        print(statement)
                                        print("=" * len(statement))
                                        print("Chord [{}] found: [{}]\n".format(search_chord, str(c_shape + "**")))
                                    return [24 + base + i for i in ToneHelper.chord_dict[c_shape]], arpeggiate, arp_rev, note_type, pattern
                                elif "**" in search_chord:
                                    if MidiWrite.debug:
                                        statement = "Found chord"
                                        print(statement)
                                        print("=" * len(statement))
                                        print("Chord [{}] found: [{}]\n".format(search_chord, str(c_shape + "*")))
                                    return [12 + base + i for i in ToneHelper.chord_dict[c_shape]], arpeggiate, arp_rev, note_type, pattern
                                elif "*" in search_chord:
                                    if MidiWrite.debug:
                                        statement = "Found chord"
                                        print(statement)
                                        print("=" * len(statement))
                                        print("Chord [{}] found: [{}]\n".format(search_chord, str(c_shape)))
                                    return [base + i for i in ToneHelper.chord_dict[c_shape]], arpeggiate, arp_rev, note_type, pattern
                    else:
                        # look for chord in separate custom file
                        # custom file defines chords like so: <chord> : <[notes]> or <chord>:<fret notation>
                        # e.g. F7%, F7%[2], etc
                        custom_dict = {}
                        if MidiWrite.custom_file is not None:
                            with open(MidiWrite.custom_file, 'r') as f:
                                for line in f:
                                    definition = line.split(":")

                                    # fret-notation
                                    if 'x' in definition[1] or any(char.isdigit() for char in definition[1]):
                                        search_chord = definition[1]
                                        break

                                    definition_edit = [int(j) for j in definition[1].split(",")]

                                    if definition[0].split("%")[1] != "":
                                        chord_name = definition[0].split("%")[0]
                                        def_no     = definition[0].split("%")[1]
                                        custom_dict[str(chord_name + def_no)] = definition_edit
                                    else:
                                        custom_dict[definition[0]] = definition_edit

                            for custom_c_shape in custom_dict:
                                if custom_c_shape in search_chord:
                                    return [base + int(i) for i in custom_dict[custom_c_shape]], arpeggiate, arp_rev, note_type, pattern

        # assume chord is in fret-notation
        if 'x' not in search_chord and not any(char.isdigit() for char in search_chord):
            print("Chord " + search_chord + " not found. Either chord has not been added or chord is incorrectly typed.")
            return [0], False, False, note_type

        if MidiWrite.debug:
            print("Assuming [{}] to be in fret notation.\n".format(search_chord))

        notes = []
        octaves = [0, 0, 0, 0, 0, 0]
        if Misc.is_number(search_chord[0]):
            shift = int(search_chord[0]) // 12
            octaves[0] = shift
            notes.append(ToneHelper.guitar_map_standard_tuning["E"][int(search_chord[0]) % 12])  # octaves repeat
        else:
            if MidiWrite.debug and search_chord[0] != 'x':
                print("Invalid character found, is ignored.")
        if Misc.is_number(search_chord[1]):
            shift = int(search_chord[1]) // 12
            octaves[1] = shift
            notes.append(ToneHelper.guitar_map_standard_tuning["A"][int(search_chord[1]) % 12])
        else:
            if MidiWrite.debug and search_chord[1] != 'x':
                print("Invalid character found, is ignored.")
        if Misc.is_number(search_chord[2]):
            shift = int(search_chord[2]) // 12
            octaves[2] = shift
            notes.append(ToneHelper.guitar_map_standard_tuning["D"][int(search_chord[2]) % 12])
        else:
            if MidiWrite.debug and search_chord[2] != 'x':
                print("Invalid character found, is ignored.")
        if Misc.is_number(search_chord[3]):
            shift = int(search_chord[3]) // 12
            octaves[3] = shift
            notes.append(ToneHelper.guitar_map_standard_tuning["G"][int(search_chord[3]) % 12])
        else:
            if MidiWrite.debug and search_chord[3] != 'x':
                print("Invalid character found, is ignored.")
        if Misc.is_number(search_chord[4]):
            shift = int(search_chord[4]) // 12
            octaves[4] = shift
            notes.append(ToneHelper.guitar_map_standard_tuning["B"][int(search_chord[4]) % 12])
        else:
            if MidiWrite.debug and search_chord[4] != 'x':
                print("Invalid character found, is ignored.")
        if Misc.is_number(search_chord[5]):
            shift = int(search_chord[5]) // 12
            octaves[5] = shift
            notes.append(ToneHelper.guitar_map_standard_tuning["E"][int(search_chord[5]) % 12])
        else:
            if MidiWrite.debug and search_chord[5] != 'x':
                print("Invalid character found, is ignored.")

        for i in range(len(notes)):
            if len(notes[i]) > 2:
                notes[i] = notes[i][:2]
            for key, value in MidiWrite.note_map.items():
                if key in notes[i]:
                    notes[i] = MidiWrite.note_map[key] + (12 * (1 + octaves[i]))
                    break

        if MidiWrite.debug:
            print("Fret notation chord [{}] created.\n".format(search_chord))

        return notes, arpeggiate, arp_rev, note_type, pattern

    @staticmethod
    def get_chords(c_type: str) -> [str]:
        """
        Returns requested chords.
        :param c_type: type of chord
        :return: all chords matching the request
        """

        return [entry for entry in ToneHelper.chord_dict if c_type in entry]

    @staticmethod
    def build_base_chords(bases: [str], c_type: str) -> [str]:
        """
        Return a list of base chords built from a type and base notes.
        :param bases: list of bases
        :param c_type: type of chord
        :return: chords built from the following prerequisite variables
        """
        return [[base + chord for chord in MidiWrite.get_chords(c_type)] for base in bases]
