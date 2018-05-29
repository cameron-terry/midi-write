##-------------------------------------------------------------------------------------------------------------------##
# TODO: abstract musical ideas even further
#       e.g. add support for cycle of fifths, hammer-ons / pull-offs, and more
# TODO: add variability to note length
# TODO: add arpeggios! and markup file
#       arpeggios shouldn't be too hard. it's a matter of spacing out the notes in the chord (increasing delta-time)
##-------------------------------------------------------------------------------------------------------------------##
# MidiWrite by Cameron Terry
# May 28, 2018
#
# MidiWrite makes turning a chord progression into a MIDI file a super simple process while lessening the time
# required needed to create a MIDI file based on a progression.
##-------------------------------------------------------------------------------------------------------------------##

import array


class MidiWrite:
    # user defined file that contains additional chord mappings
    custom_write = None

    debug = False  # set in track_chunk

    # constant bytes
    mthd                = b'\x4d\x54\x68\x64'
    header_chunk_length = b'\x00\x00\x00\x06'

    mtrk                = b'\x4d\x54\x72\x6b'
    track_chunk_length  = b'\x00\x00\x00\x14'

    eof                 = b'\x00\xff\x2f\x00'

    # used to map notes to sound frequencies
    note_map = {
        "C": 60, "C#": 61, "Db": 61, "D": 62, "D#": 63, "Eb": 63, "E": 64, "F": 65, "F#": 66,
        "Gb": 66, "G": 67, "G#": 68, "Ab": 68, "A": 69, "A#": 70, "Bb": 70, "B": 71
    }

    # used for translating fret-based input
    guitar_map_standard_tuning = {
        "E": ["E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B", "C", "C#/Db", "D", "D#/Eb"],
        "A": ["A", "A#/Bb", "B", "C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab"],
        "D": ["D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B", "C", "C#/Db"],
        "G": ["G", "G#/Ab", "A", "A#/Bb", "B", "C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb"],
        "B": ["B", "C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb"],
        "E": ["E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B", "C", "C#/Db", "D", "D#/Eb"]
    }

    # used for translating chords to notes
    chord_dict = {
        "dim7**": [0, 9, 5, 18],
        "dim7*":  [0, 6, 10, 13, 19],
        "aug7**": [0, 11, 16, 20],
        "aug7*":  [0, 8, 11, 16],
        "dim**":  [0, 6, 12, 15],
        "dim*":   [0, 6, 9, 15],
        "aug**":  [0, 4, 8, 12, 16],
        "aug*":   [0, 4, 8, 12],
        "sus4**": [0, 7, 12, 17, 19, 24],
        "sus4*":  [0, 7, 12, 17, 19],
        "sus2**": [0, 14, 19, 24],
        "sus2*":  [0, 7, 12, 14, 19],
        "Mm7**":  [0, 11, 15, 19],
        "Mm7*":   [0, 7, 11, 15, 21],
        "m7b5**": [0, 10, 15, 18],
        "m7b5*":  [0, 6, 10, 15],
        "maj6**": [0, 9, 16, 19],
        "maj6*":  [0, 7, 12, 16, 21],
        "m6**":   [0, 9, 15, 19],
        "m6*":    [0, 7, 12, 15, 21],
        "maj7**": [0, 11, 16, 19],
        "maj7*":  [0, 7, 11, 16, 19],
        "maj**":  [0, 7, 12, 16, 19, 24],
        "maj*":   [0, 7, 12, 16, 19],
        "m7**":   [0, 10, 15, 19],
        "m7*":    [0, 7, 10, 15, 19],
        "m**":    [0, 7, 12, 15, 19, 24],
        "m*":     [0, 7, 12, 15, 19],
        "7**":    [0, 10, 15, 19],
        "7*":     [0, 7, 10, 16, 19],
        "13**":   [0, 10, 16, 21],
        "13*":    [0, 4, 10, 14, 21]
    }

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def set_custom_file(file: str):
        if file is not None:
            MidiWrite.custom_file = file

    @staticmethod
    def get_key(k: str):

        '''
        Returns the number of sharps / flats for a given key
        :param k: the key signature
        :return: the number of sharps / flats and if the key is major / minor
        '''

        major_keys = {
            'Cb': 7, 'Gb': 6, 'Db': 5, 'Ab': 4, 'Eb': 3, 'Bb': 2, 'F#': -6, 'C#': -7, 'F': 1, 
            'C': 0, 'G': -1, 'D': -2, 'A': -3, 'E': -4, 'B': -5
        }

        minor_keys = {
            'Ab': 7, 'Eb': 6, 'Bb': 5, 'F#': -3, 'C#': -4, 'G#': -5, 'D#': -6, 'A#': -7, 'F': 4,
            'C': 3, 'G': 2, 'D': 1, 'A': 0, 'E': -1,'B': -2
        }

        if "maj" in k:
            for element in major_keys:
                if element == k[:2]:
                    return major_keys[element], 1
            for element in major_keys:
                if element == k[0]:
                    return major_keys[element], 1
        elif "m" in k:
            for element in minor_keys:
                if element == k[:2]:
                    return minor_keys[element], 0
            for element in minor_keys:
                if element == k[0]:
                    return minor_keys[element], 0
        else:
            raise ValueError

    @staticmethod
    def octave_shift_down(n: int):
        '''
        Shifts all notes down n octaves
        :param n: number of octaves to shift down
        :return: none
        '''
        if n > 0:
            for key in MidiWrite.note_map:
                MidiWrite.note_map[key] -= n * 12

    @staticmethod
    def octave_shift_up(n: int):
        '''
        Shifts all notes up n octaves
        :param n: number of octaves to shift up
        :return: none
        '''
        if n > 0:
            for key in MidiWrite.note_map:
                MidiWrite.note_map[key] += n * 12

    # based on pseudo-code from http://midi.teragonaudio.com/tech/midifile/vari.htm
    @staticmethod
    def write_var_len(n: int) -> [int]:
        EIGHT_BIT_MAX = 256
        SEVEN_BIT_MAX = 128
        '''
        Transforms an integer into a variable-length quantity
        :param n: the integer to convert
        :return: variable-length quantity array of the integer
        '''
        byte_arr = [0 for _ in range(4)]
        count = 0

        while True:
            if n < SEVEN_BIT_MAX:
                byte_arr[count] = n & 0x7f
                count += 1
                break
            else:
                result = n
                byte_arr[count] = result & 0x7f | 0x80
                count += 1
                n >>= 7

        byte_arr = byte_arr[:count]
        byte_arr.reverse()

        r = True  # used for additional formatting
        for i in range(len(byte_arr)):
            if i < len(byte_arr) - 1:
                if byte_arr[i] + byte_arr[i + 1] < EIGHT_BIT_MAX:
                    byte_arr[i] = byte_arr[i] + byte_arr[i + 1]
                    byte_arr[i + 1] = 0
                    r = False

        if r:
            byte_arr.reverse()

        byte_arr = array.array('B', byte_arr).tostring()
        return byte_arr

    @staticmethod
    def read_var_len(n: [int]) -> int:
        '''
        converts a variable-length quantity to an integer.
        :param n: the variable-length quantity to convert
        :return: integer representation of the variable-length quantity
        '''
        result = 0
        for val in n:
            result <<= 7
            result |= (val & 0x7f)
            if not (val & 0x80 == 0x80):
                return result

    @staticmethod
    def write_preqs(file: str):
        '''
        write the pre-requisite headers to the midi file.
        :param file: the midi file to write to
        :return: none
        '''
        # check prefix
        if file[-5:] != ".midi":
            print("File not could be created.")
            exit(1)

        MidiWrite.write_header_chunk(file)
        MidiWrite.write_track_chunk(file)

    @staticmethod
    def write_header_chunk(file: str):
        '''
        write the header chunk to the midi file.
        :param file: the midi file to write to
        :return: none
        '''
        fmat         = b'\x00\x01' # multiple-track format
        track        = b'\x00\x02' # 1 track
        quart_length = b'\x00\x60' # quarter tick length

        with open(file, "wb") as f:
            f.write(MidiWrite.mthd)
            f.write(MidiWrite.header_chunk_length)
            f.write(fmat)
            f.write(track)
            f.write(quart_length)

    @staticmethod
    def write_track_chunk(file: str):
        '''
        write the track chunk to the midi file.
        :param file: the midi file to write to
        :return: none
        '''

        with open(file, "ab") as f:
            f.write(MidiWrite.mtrk)
            f.write(MidiWrite.track_chunk_length)

        MidiWrite.write_time_sig(file)

    @staticmethod
    def write_time_sig(file: str):
        '''
        write the time signature and other relevant meta tags to the midi file
        :param file: the midi file to write to
        :return: none
        '''
        time_sig = b'\x00\xff\x58\x04\x04\x02\x18\x08'
        tempo    = b'\x00\xff\x51\x03\x07\xa1\x20'
        eot      = b'\x83\x00\xff\x2f\x00'

        with open(file, "ab") as f:
            f.write(time_sig)
            f.write(tempo)
            f.write(eot)

    @staticmethod
    def write_track(file: str, commands: [bytes], title='Main', time="4/4", tempo=60, key='Cmaj', debug=False):
        if debug:
            MidiWrite.debug = True
        '''
        write the track data to the midi file
        :param file: the midi file to write to
        :param commands: the notes to write to the midi file
        :param title: the title of the track
        :param key: the key signature of the track
        :param debug: show progress on creating midi file
        :return:
        '''
        chunk_length = b'\x00\x00'
        preset = b'\x00\xc1' + bytes([24])
        chunk_title = b'\x00\xff\x03'
        key_sig = b'\x00\xff\x59\x02'
        time_sig = b'\x00\xff\x58\x04'
        time_sig_end_bytes = b'\x24\x08'

        chunk_title_length = bytes([len(title)])
        chunk_title += chunk_title_length
        for letter in title:
            chunk_title += bytes([ord(letter)])

        flats, major_minor = MidiWrite.get_key(key)

        ts_num = bytes([int(time.split("/")[0])])
        ts_denom = bytes([int(time.split("/")[1])])

        time_sig += ts_num + ts_denom + time_sig_end_bytes

        key_sig += bytes([flats])
        key_sig += bytes([major_minor])

        count = len(chunk_length) + len(MidiWrite.eof) + len(chunk_title) + len(key_sig) + len(time_sig)
        notes_list = []

        for chord in commands:
            notes = MidiWrite.find_notes(chord)
            for note in notes:
                count += len(note)
            notes_list.append(notes)

        b = MidiWrite.write_var_len(count + 1)
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
                    print("Writing \"%s\" to %s... " % (commands[i], file), end="", flush=True)
                for note in notes_list[i]:
                    f.write(note)
                if MidiWrite.debug:
                    print("Done.")

            f.write(MidiWrite.eof)

    @staticmethod
    def find_notes(chord, time: bytes= b'\x40') -> [bytes]:
        '''
        find the notes needed to play the chord
        :param chord: the chord to find the notes of
        :param time: time each note is held down
        :return: the midi representation of the chord / notes
        '''
        start_simul = b'\x00\x90'
        note_on     = time
        note_off    = b'\x00'
        delay       = b'\x81\x40'

        notes = MidiWrite.chord_shape(chord)
        note_arr = []

        if notes:
            for i in range(len(notes)):
                # means 0x90 - turn on - 0x?? - 60 + n (C#, 60 is C) -- 0x20 -- for a quarter?
                note_arr.append(start_simul + bytes(notes[i:i+1]) + note_on)

            note_arr.append(delay + bytes(notes[len(notes)-1:len(notes)]) + note_off)

            for j in range(len(notes) - 1, 0, -1):
                # delta times of simultaneous events are 0
                note_arr.append(b'\x00' + bytes(notes[j-1:j]) + note_off)

            return note_arr
        else:
            return [b'\x81\x40\x90\x4c\x20',
                    b'\x81\x40\x4c\x00']  # return single note

    @staticmethod
    def chord_shape(chord) -> [int]:
        '''
        determine the notes of the chord based on chord type / fret locations
        :param chord: the chord to find the notes of
        :return: the chord as a set of integer notes
        '''
        if isinstance(chord, str):
            # look for note and chord type in dictionaries
            for element in MidiWrite.note_map:
                if element in chord:
                    base = MidiWrite.note_map[element]
                    if '%' not in chord:
                        for c_shape in MidiWrite.chord_dict:
                            if c_shape in chord:
                                return [base + i for i in MidiWrite.chord_dict[c_shape]]
                    else:
                        # look for chord in separate custom file
                        # custom file defines chords like so: <chord> : <[notes]> or <chord>:<fret notation>
                        # TODO: currently can only define one type of custom chord, edit to allow multiple
                        # e.g. F7%, F7%%, etc
                        custom_dict = {}
                        if MidiWrite.custom_file is not None:
                            with open(MidiWrite.custom_file, 'r') as f:
                                for line in f:
                                    definition = line.split(":")

                                    if 'x' in definition[1][0]:  # fret-notation
                                        chord = definition[1]
                                        break

                                    definition[1] = [int(j) for j in definition[1].split(",")]
                                    custom_dict[definition[0]] = definition[1]
                            for custom_c_shape in custom_dict:
                                if custom_c_shape in chord:
                                    return [base + i for i in custom_dict[custom_c_shape]]

        # assume chord is in fret-notation
        notes = []
        if MidiWrite.is_number(chord[0]):
            notes.append(MidiWrite.guitar_map_standard_tuning["E"][int(chord[0]) % 12])  # octaves repeat
        else:
            if MidiWrite.debug and chord[0] != 'x':
                print("Invalid character found, is ignored.")
        if MidiWrite.is_number(chord[1]):
            notes.append(MidiWrite.guitar_map_standard_tuning["A"][int(chord[1]) % 12])
        else:
            if MidiWrite.debug and chord[1] != 'x':
                print("Invalid character found, is ignored.")
        if MidiWrite.is_number(chord[2]):
            notes.append(MidiWrite.guitar_map_standard_tuning["D"][int(chord[2]) % 12])
        else:
            if MidiWrite.debug and chord[2] != 'x':
                print("Invalid character found, is ignored.")
        if MidiWrite.is_number(chord[3]):
            notes.append(MidiWrite.guitar_map_standard_tuning["G"][int(chord[3]) % 12])
        else:
            if MidiWrite.debug and chord[3] != 'x':
                print("Invalid character found, is ignored.")
        if MidiWrite.is_number(chord[4]):
            notes.append(MidiWrite.guitar_map_standard_tuning["B"][int(chord[4]) % 12])
        else:
            if MidiWrite.debug and chord[4] != 'x':
                print("Invalid character found, is ignored.")
        if MidiWrite.is_number(chord[5]):
            notes.append(MidiWrite.guitar_map_standard_tuning["E"][int(chord[5]) % 12])
        else:
            if MidiWrite.debug and chord[5] != 'x':
                print("Invalid character found, is ignored.")

        for i in range(len(notes)):
            if len(notes[i]) > 2:
                notes[i] = notes[i][:2]
            for key, value in MidiWrite.note_map.items():
                if key == notes[i]:
                    notes[i] = MidiWrite.note_map[key]
                    break

        return notes
