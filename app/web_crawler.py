import asyncio
import itertools
import time
import logging
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

############################################################################################
class Mapping:
    """
    This is the Class used to set up the links between parent and child nodes.
    In the first run the url that is analyzed is used and is the one that has no parent.
    """
    def __init__(self, value, parent=None):
        self.value = value
        # self.next_links = set()
        self.next_nodes = set()
        self.parent_node = parent

    # def add_next_links(self, link_list):
    #     """
    #     This function adds to the current node object the links to be examined
    #     :param link_list: The list of links to be examined for a specific node
    #     """
    #     self.next_links = self.next_links.union(set(link_list))

    def add_next_nodes(self, node_list):
        """
        This function adds to the current node the nodes to be examined
        :param node_list: The list of nodes that will be child to the current node
        """
        self.next_nodes = self.next_nodes.union(set(node_list))


############################################################################################
class Web_Crawler():
    """
    This class is the engine of the Web Crawler.
    """
    def __init__(self, search_url, depth, speed):
        """
        Init function for Web_Crawler Class. This is the main class that includes
        all the methods that will be used to build the mapping of a specific url
        """
        self.initial_domain = search_url

        #Creating the first object of the Mapping
        self.tree_object = Mapping(search_url)

        #This list will be used as a queue system for faster analysis
        self.links_to_visit = [self.tree_object]

        #This list of links will be used to avoid rescaning of the same entries
        self.examined_links = []

        self.speed_factor = speed

        self.max_depth = depth

        #This list includes keywords of links not to follow
        self.not_wanted = ['twitter', 'facebook', 'linkedin', 'mailto', 'url=']


    def list_cleanup(self, multitask_results, results):
        """
        This function cleans the multitask list fron nontype entries and adds
        all lists in a single list.
        :param multitask_results: Multi level nested list.
        :param results: List to be appended with new entries
        :return results: Returns the results witn new updated entries
        """
        multitask_results = self.remove_none_elements_from_list(multitask_results)
        for entries in multitask_results:
            for single_entry in entries:
                results.append(single_entry)
        return results

    def remove_none_elements_from_list(self, list):
        """
        This function removes nontype entries from a lists
        :param list: The list to be cleaned
        :return: The clean list
        """
        return [e for e in list if e != None]

    def dynamic_speed(self, size):
        """
        This function defines the number of tasks that will run assynchronously.
        Due to the limits of aiohttp the speed factor needs to be defined based
        on the depth of analysing.
        :param size: The size of the links to be examined.
        :return: The number of tasks
        """
        if size == 1:
            return size
        else:
            return round(size/self.speed_factor)


    def check_url(self, links, url_to_analyze):
        """
        This function checks if links are within the accepted links
        :param links: The links that need to be checked
        :param url_to_analyze: The url that is examined at this step.
        :return urls: URLs that passed the check
        """
        urls = []
        for link in links:
            if (link != None) and (not link == url_to_analyze):
                if (link.startswith('/')) and (link != '/') and (not link.startswith('/-')) and (not 'email' in link):
                    link = self.initial_domain + link
                    urls.append(link)
                elif self.initial_domain.split("//")[1] in link:
                    check = True
                    for check_value in self.not_wanted:
                        if check_value in link:
                            check = False
                            break
                    if check:
                        urls.append(link)
        return urls


    def remove_list_duplicates(self, list_d):
        """
        This function makes a comparison of the new links to be examined with the
        already examined links, in order to avoid double rescaning.
        :param list_d: List of new links:
        :return new_list: List of links that are examined already
        """
        new_list = []
        for item in list_d:
            if item not in self.examined_links:
                new_list.append(item)
        new_list = list(set(new_list))
        return new_list


    async def get_raw_data(self, url):
        """
        This function returns the raw html page
        :param url: The url to get the raw page for
        :return: The raw html page
        """
        async with aiohttp.ClientSession() as aio_session:
            async with aio_session.get(url) as response:
                if response.status == 200:
                    return await response.read()

    async def get_links(self, data):
        """
        This function returns the links included in the raw html page
        :param data: This is the raw page
        :return new_links: All links got from the raw page
        """
        new_links = []
        soup = BeautifulSoup(data, 'html.parser')
        links = soup.find_all('a')
        for link in links:
            new_links.append(link.get('href'))
        return new_links

    async def analyze_node(self, node):
        """
        This function includes the core functionality of the app. It gets the
        object that needs to be examined and gets new links, creates new objects
        and returns the new entries.
        :param node: The node to be analysed
        :return new_entries: Entries to be examined next
        """
        url_to_analyze = node.value
        logging.debug('Analyzing node -> %s' %url_to_analyze )
        raw_html = await self.get_raw_data(url_to_analyze)
        if raw_html:
            logging.debug('Succesfully got raw html page for url -> %s' %url_to_analyze)
            logging.debug('Getting new links from url -> %s' %url_to_analyze)
            new_links_to_visit = await self.get_links(raw_html)

            if new_links_to_visit:
                logging.debug('Validating links and turning links into useful urls...')
                new_links_to_visit = self.check_url(new_links_to_visit, url_to_analyze)

                logging.debug('Removing URL duplicates...')
                new_links_to_visit = self.remove_list_duplicates(new_links_to_visit)

                # logging.debug('Updating parent node with all new links to visit...')
                # node.add_next_links(new_links_to_visit)

                logging.debug('Setting up new links in tree and setting the parental link...')
                new_entries = await self.tree_update(new_links_to_visit, node)

                logging.debug('Setting link between parent and child nodes...')
                node.add_next_nodes(new_entries)

                logging.debug('Adding new examined links in Global link list...')
                self.examined_links.extend(new_links_to_visit)
                return new_entries


    async def tree_update(self, links, parent_node):
        """
        This function creates objects from links and returns a list of objects
        to be examined next.
        :param links: URL values of links to be examined next.
        :param parent_node: The parent node of this child links.
        :return: List of link objects.
        """
        entries = []
        for link in links:
            entries.append(Mapping(value=link, parent=parent_node))
        return entries


    async def web_crawler(self):
        """
        This function is the main class function. It orchestrates the web crawling
        based on depth and queue of lists to examined. It stops running, when
        maximum depth is reached and all links are examined.
        :return: The object mapping.
        """
        logging.info("Initializing the Crawler...")
        logging.debug("Setting Crawler status to True to initialize crawling...")
        crawler_status = True
        #Initializing current depth variable
        depth = 0
        while crawler_status:
            results = []
            logging.info('Links to analyze -> %s in depth -> %s' % (len(self.links_to_visit), depth))
            while len(self.links_to_visit) > 0:
                speed = self.dynamic_speed(len(self.links_to_visit))
                tasks = [self.analyze_node(self.links_to_visit.pop()) for task in range(speed)]
                multitask_results = (await asyncio.gather(*tasks))
                results = self.list_cleanup(multitask_results, results)
            depth = depth + 1
            logging.info('Current crawling depth is -> %s' % depth)
            if depth == self.max_depth:
                logging.info('Reached maximum depth...')
                crawler_status = False
                return (self.tree_object, len(self.examined_links))
            else:
                self.links_to_visit.extend(results)
