"""Multithreaded Downloader"""

import click
import pump.downloader as downloader
import pump.utils as utils
import sys
from typing import List

@click.command()
@click.argument("url", type=str)
@click.option("--csize", "-s", type=int, help="Chunk size to use, defaults to size/#chunks")
@click.option("--ccount", "-c", default=8, type=int, help="Number of Chunks to download concurrently")
@click.option("--output-path", "-o", type=str, help="Path to write the downloaded output file")
@click.option("--verbose", "-v", is_flag=True, default=True, help="Enable/Disable verbose")
@click.option("--force", "-f", is_flag=True, default=False, help="Supress confirmation for filename")
@click.option("--header", "-H", multiple=True, default=[], help="Pass each request header (as in curl)")
def main(url: str,
         ccount: int,
         csize: int,
         output_path: int,
         verbose: bool,
         force: bool,
         header: List[str]):
    """Multithreaded Downloader for concurrent downloads"""
    # parse headers
    try:
        headers = utils.parse_headers(header)
    except Exception as e:
        click.echo(e, err=True)
        sys.exit(-1)

    # initialize downloader
    download_handler = downloader.DownloadHandler(
         url,
         ccount,
         csize,
         verbose,
         headers
    )
    
    # confirm if non-parallel download is fine or not
    if not download_handler.is_parallel():
         click.secho(
              "Multithreaded download is not supported!", 
              fg="red"
         )
         allow = click.confirm(
              "Do you want a single threaded download?", 
               default=True,
               abort=True
         )
    
    # display and confirm name          
    filename = download_handler.get_filename()
    if output_path is not None:
        filename = output_path
        download_handler.set_filename(filename)
        force = True
    click.echo("File will be saved as " + click.style(filename, bold=True))
    if not force:
        change = click.confirm(
             "Do you want to change the name?",
             default=False
        )
        if change:
             filename = click.prompt("New filename")
             download_handler.set_filename(filename)

     # display size of file
    if verbose:
         size, unit = utils.format_bytes(download_handler.get_size())
         click.echo(f"Fetching {size:.2f} {unit}s in {ccount} chunks")
         
    # start download
    download_handler.start()
    click.secho(f"\rSuccess: {filename} downloaded", fg="green")
     
if __name__ == '__main__':
     main()
