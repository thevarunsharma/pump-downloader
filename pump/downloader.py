import os
import requests
import sys
import threading
import tqdm
import pump.utils as utils
import uuid

from math import ceil
from time import sleep
from typing import IO, Dict
from urllib.parse import urlparse

GLOBAL_THREAD_LOCK = threading.Lock()


class Downloader(threading.Thread):
    """Downloader for single chunk"""
    
    MAX_WRITE_SIZE = 1024 * 256      # chunk size for download
    
    def __init__(self, 
                 url: str, 
                 start: int, 
                 end: int,
                 file: IO,
                 tqdm_handler: tqdm.tqdm = None,
                 headers: Dict[str, str] = None):
        """Instantiate a downloader for a single chunk
        
        Parameters
        ----------
        url: str:
            URL for teh downloadable resource
        start: int
            start byte for resource
        end: int
            end byte for resource
        file: IO
            file IO object for output to file 
        tqdm_handler: tqdm.tqdm
            a ``tqdm`` progress bar object to be updated as download progresses.
            Defaults to ``None``, which means no progress bar will be displayed.
        headers: Dict[str, str]
            optional headers to be passed with the http requests
        """
        super().__init__()
        # resource URL
        self.__url = url
        # start byte
        self.__start = start
        # end byte
        self.__end = end
        # status bar
        self.__status_bar = tqdm_handler
        # file write head
        self.__fh = file
        # write pointer position
        self.__wpos = self.__start
        # optional headers
        self.__headers = headers

    def __store(self,
                response: requests.Response):
        # method writes the response content to a temp file
        for chunk in response.iter_content(chunk_size=Downloader.MAX_WRITE_SIZE):
            with GLOBAL_THREAD_LOCK:
                # seek to position in file
                self.__fh.seek(self.__wpos)
                # write a chunk to file
                self.__fh.write(chunk)
                # update write position
                self.__wpos += len(chunk)
            
            # update status bar
            if self.__status_bar:
                self.__status_bar.update()
                
        # update and close status bar
        if self.__status_bar:
            self.__status_bar.update()
            self.__status_bar.close()
            

    def run(self):
        headers = {
            "Range" : f"bytes={self.__start}-{self.__end}",
            **self.__headers
        }
        response = requests.get(
            self.__url,
            headers=headers,
            stream=True
        )
        response.raise_for_status()
        # store the response
        self.__store(response)
        

class DownloadHandler:
    """Setting up download threads and finally compiling content to single output path"""
    
    def __init__(self,
                 url: str,
                 chunk_count: int = 8,
                 chunk_size: int = None,
                 verbose: bool = True,
                 headers: dict[str, str] = None):
        """Instantiate a download handler
        
        Parameters
        ----------
        url: str
            URL for the downloadable resource.
        chunk_count: int
            Desired number of parallel connections for concurrent downloads
            of parts. 
            Defaults to 8 in case parallel download is supported.
            If parallel download is not supported then set to 1.
        chunk_size: int
            Desired size of single chunk to be downloaded.
            By default calculated based on file ``size`` and ``chunk_count`` provided.
            This parameter will take precedence over the ``chunk_count`` value in case both
            are available, to decide on the effective ``chunk_size``.
        verbose: bool
            Whether to enable or disable verbose, progress bars, etc.
            Defaults to ``True``.
        headers: dict
            Optional headers for the HTTP request
        """
        # resource URL
        self.__url = url
        # optional headers to the HTTP requests
        self.__headers = headers
        # whether to display status bar
        self.__verbose = verbose
        # base filename derived form ``url``
        self.__filename = utils.get_available_path(utils.get_base_filename(url))
        # if Parallel download is supported for the resource
        self.__parallel = self.__supports_partial()
        # size of download in bytes
        self.__size = self.__get_content_length()
        # count and size of chunks to be downloaded
        self.__chunk_count, self.__chunk_size = self.__calculate_chunks(chunk_count, chunk_size)
        # thread-threads
        self.__downloaders = []
    
    def get_url(self) -> str:
        """Get resource URL"""
        return self.__url
    
    def set_url(self, 
                url: str):
        """Set resource URL"""
        self.__url = url
    
    def get_filename(self) -> str:
        """Get filename"""
        return self.__filename
    
    def set_filename(self, 
                     filename: str):
        """Set filename"""
        self.__filename = filename
        
    def is_parallel(self) -> bool:
        """Is parallel download supported"""
        return self.__parallel
    
    def get_size(self) -> int:
        """Get file size in bytes"""
        return self.__size
    
    def get_chunk_count(self) -> int:
        """Get number of chunks for downloads"""
        return self.__chunk_count
    
    def get_chunk_size(self) -> int:
        """Get chunk size for  downloads in bytes"""
        return self.__chunk_size
    
    def is_verbose_enabled(self) -> bool:
        """Check whether verbose is enables"""
        return self.__verbose
    
    def toggle_verbose(self):
        """Toggle verbose status"""
        self.__verbose = not self.__verbose

    def get_headers(self):
        """Returns request headers"""
        return { **self.__headers }
    
    def __get_content_length(self) -> int:
        """Fetches content length and checks partial download suppot
        using a HEAD request"""
        # send a HEAD request to fetch 'Content-Length' and 'Accept-Ranges' arguments
        response = requests.head(
            self.__url,
            headers=self.__headers
        )
        response.raise_for_status()
        size = response.headers.get("Content-Length")
        return int(size)

    def __supports_partial(self) -> bool:
        """Returns whether partial content download is supported"""
        # sends an empty range GET request to check for partial download support
        headers = {
            "Range" : f"bytes=0-0",
            **self.__headers
        }
        response = requests.get(
            self.__url,
            headers=headers
        )
        response.raise_for_status()
        # 206 means range header was honored and partial content was returned
        return response.status_code == 206

    def __calculate_chunks(self, 
                           chunk_count: int, 
                           chunk_size: int) -> (int, int):
        # method to calculate chunk size and count based on passed arguments
        # if parallel downloads are not supported
        assert chunk_count != 0, "chunk count can't be zero"
        assert chunk_size !=0, "chunk size can't be zero"
        if not self.__parallel:
            return 1, self.__size
        if chunk_size is None:
            return chunk_count, ceil(self.__size / chunk_count)
        chunk_count = ceil(self.__size / chunk_size)
        return chunk_count, chunk_size
    
    def __dispatch(self):
        """Prepare and dispatch threads"""
        # iterate through trhead counts
        with open(self.__filename, "wb") as fh:
            for i in range(self.__chunk_count):
                start = i * self.__chunk_size
                end = min((i+1) * self.__chunk_size, self.__size)-1
                # initialize status bar
                if self.__verbose:
                    status_bar = tqdm.trange(
                        ceil((end - start + 1 ) / Downloader.MAX_WRITE_SIZE),
                        position=i,
                        leave=False,
                        desc=f"Chunk {i+1}"
                        )
                else:
                    status_bar = None
                        
                downloader = Downloader(
                    self.__url,
                    start,
                    end,
                    fh,
                    status_bar,
                    self.__headers
                )
                self.__downloaders.append(downloader)
                downloader.start()
                
            # join threads
            for downloader in self.__downloaders:
                downloader.join()
        # join and halt for a second
        sleep(1)       
    
    def start(self):
        """Run Downloader"""
        self.__dispatch()
