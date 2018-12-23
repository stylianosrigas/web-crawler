import asyncio
import logging

from datetime import datetime

from web_crawler import Web_Crawler
from helpers import Helpers

logging.basicConfig(level=logging.INFO)


def main():
    """
    This the main function used to orchestrate the app run. Reads parsing
    arguments, initiates the assynchronous run and visualizes the results.
    """
    args = Helpers().argparser()
    loop = asyncio.get_event_loop()
    now = datetime.now()
    logging.info('************************* The Crawler *************************')
    logging.info('Initialization variables:\n URL -> %s\n MAX DEPTH -> %s\n MAX TASKS -> %s' %(args['url'], args['depth'], args['tasks']))
    map_object = loop.run_until_complete(Web_Crawler(args['url'], args['depth'], args['tasks']).web_crawler())
    loop.close()
    url_map = map_object[0]
    links_examined = map_object[1]
    if args['output']:
        Helpers().visualise_results_cli(url_map)
    total_time_needed = (datetime.now() - now).total_seconds()
    logging.info('The total number of links examined -> %s' % int(links_examined))
    logging.info('The total time needed for the analysis -> % seconds' % total_time_needed)
    if args['file']:
        f = open(args['file'], "w+")
        Helpers().visualise_results_file(url_map, f)
        f.close()

if __name__ == "__main__":
    main()
