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
$ pip install pump-downloader
```
## Usage
- Use as `pump` through shell
```
$ pump --help
Usage: pump [OPTIONS] URL

  Multithreaded Downloader for concurrent downloads

Options:
  -s, --csize INTEGER     Chunk size to use, defaults to size/#chunks
  -c, --ccount INTEGER    Number of Chunks to download concurrently
  -o, --output-path TEXT  Path to write the downloaded output file
  -v, --verbose           Enable/Disable verbose
  -f, --force             Supress confirmation for filename
  -H, --header TEXT       Pass each request header (as in curl)
  --help                  Show this message and exit.
```

## Example
```
$ pump 'https://storage.googleapis.com/kaggle-data-sets/705300/1231826/compressed/multinli_1.0_train.txt.zip' \
-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0' \
-H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8' \
-H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' \
-H 'Referer: https://www.kaggle.com/' -H 'Alt-Used: storage.googleapis.com' \
-H 'Connection: keep-alive' -H 'Upgrade-Insecure-Requests: 1' -H 'Sec-Fetch-Dest: document' \
-H 'Sec-Fetch-Mode: navigate' -H 'Sec-Fetch-Site: cross-site' -H 'Sec-Fetch-User: ?1' \
-H 'Pragma: no-cache' -H 'Cache-Control: no-cache'
File will be saved as multinli_1.0_train.txt.zip
Do you want to change the name? [y/N]: n
Fetching 102.88 MiBs in 8 chunks
```
