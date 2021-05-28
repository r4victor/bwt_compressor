## Overview

<b>bwt_compressor</b> is a lossless compressor/decompressor based on Burrows–Wheeler transform (BWT). It can be used as a CLI-tool or as a Python library. 

The compression of data involves three major steps:

* [Burrows–Wheeler transform](https://en.wikipedia.org/wiki/Burrows%E2%80%93Wheeler_transform)
* [Distance coding](http://www.data-compression.info/Algorithms/DC/#:~:text=Distance%20Coding%20(DC)%20is%20an,by%20Edgar%20Binder%20in%202000.&text=DC%20is%20a%20replacement%20of,can%20be%20greater%20than%20255.)
* [Huffman coding](https://en.wikipedia.org/wiki/Hamming_distance)

<b>Warning:</b> This project is for educational purposes only. It is written in Python and hasn't been optimized for speed and memory consumption.

## Requirements

* Python (tested on 3.9)
* `numpy`
* [`pydivsufsort`](https://github.com/louisabraham/pydivsufsort)
* `pytest` (for tests only)
* `bitarray` (for tests only)

## Installation

1. Get the source code:

```
$ git clone https://github.com/r4victor/bwt_compressor && cd bwt_compressor
```

2. Install the requirements:
```
$ python -m pip install -r requirements.txt
```

3. Check that everything is ok by running tests:

```
$ python -m pytest tests/
```

## Troubleshooting

If you have problems installing the `pydivsufsort` library with `pip`, consider installing it from the source:

1. Get the source:
```
$ git clone https://github.com/louisabraham/pydivsufsort
```
2. Install from the source:
```
$ python -m pip install pydivsufsort/.
```

## Usage

The program reads the input data from stdin and outputs the result of the compression to stdout. Here's how you may use it:

```
$ cat resources/martin_eden.txt | python -m bwt_compressor > resources/martin_eden.bwt
```

To decompress the data, specify the `-d` option:

```
$ cat resources/martin_eden.bwt | python -m bwt_compressor -d > resources/martin_eden_decompressed.txt
```

## Limitations

At this moment the compressor works only with ASCII-texts that do not contain the null byte (`\x00`). This limitation can be lifted in the future.
