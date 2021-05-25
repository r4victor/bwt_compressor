import argparse
import sys

from bwt_compressor.compressor import compress, decompress


parser = argparse.ArgumentParser(
    prog='python3 -m bwt_compressor',
    description='The program reads data from stdin, '
    'compresses/decompresses it using the BWT-based compressor '
    'and writes the result to the stdout.'
)
parser.add_argument('-d', action='store_true', help='decompress mode')
args = parser.parse_args()


if args.d:
    compressed_text = sys.stdin.buffer.read()
    print(decompress(compressed_text))
else:
    text = sys.stdin.read()
    sys.stdout.buffer.write(compress(text))




