# Pump
## Concurrent file downloader written in Python

Downloads file in parts using multiple concurrent threads

## Installation
_Recommended to be used in a python virtual environment._
- Create a python virtualenv and activate it.
```
$ python3 -m venv env
$ source env/bin/activate
```
- Install the tool using pip
```
(env)$ pip install .
```
## Usage
- Use as `cowin-notifier` through shell
```
Usage: pump [OPTIONS] URL

  Multithreaded Downloader for concurrent downloads

Options:
  -s, --csize INTEGER     Chunk size to use, defaults to size/#chunks
  -c, --ccount INTEGER    Number of Chunks to download concurrently
  -o, --output-path TEXT  Path to write the downloaded output file
  -v, --verbose           Enable/Disable verbose
  -f, --force             Supress confirmation for filename
  --help                  Show this message and exit.
```

## Example
```
$ pump https://i.stack.imgur.com/Bhpd8.jpg -f
File will be saved as Bhpd8.jpg
Fetching 494.19 kiBs in 8 chunks
Success: Bhpd8.jpg downloaded
```
