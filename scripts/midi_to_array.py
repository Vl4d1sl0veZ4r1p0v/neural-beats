import argparse
import os

import mido
from mido import MidiFile
import numpy as np

from midi_util import midi_to_array, quantize

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Save a directory of MIDI files as arrays.')
    parser.add_argument('path', help='Input path')
    parser.add_argument(
        '--use-cached',
        dest='use_cached',
        action='store_true',
        help='Overwrite existing files.')
    parser.add_argument(
        '--quantization',
        default=5,
        help='Defines a 1/2**quantization note quantization grid')
    parser.set_defaults(use_cached=False)
    args = parser.parse_args()

    path_prefix, path_suffix = os.path.split(args.path)
    # Handle case where a trailing / requires two splits.
    if len(path_suffix) == 0:
        path_prefix, path_suffix = os.path.split(path_prefix)
    base_path_out = os.path.join(path_prefix, 'array')

    for root, dirs, files in os.walk(args.path):
        for file in files:
            print os.path.join(root, file)
            if file.split('.')[-1] == 'mid':
                # Get output file path
                suffix = root.split(args.path)[-1]
                out_dir = base_path_out + '/' + suffix
                out_file = '{}.npy'.format(os.path.join(out_dir, file))
                if os.path.exists(out_file) and args.use_cached == True:
                    continue

                mid = quantize(MidiFile(os.path.join(root,file)),
                               quantization=args.quantization)
                time_sig_msgs = [ msg for msg in mid.tracks[0] if msg.type == 'time_signature' ]
                if len(time_sig_msgs) == 1:
                    time_sig = time_sig_msgs[0]
                    if not (time_sig.numerator == 4 and time_sig.denominator == 4):
                        print 'Time signature not 4/4. Skipping...'
                        continue
                else:
                    print 'No time signature. Skipping...'
                    continue

                array = midi_to_array(mid, int(args.quantization))
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                #print 'Saving', out_file
                np.save(out_file, array)
