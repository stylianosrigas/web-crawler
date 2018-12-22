import asyncio
import json
from app.web_crawler import Web_Crawler


class Test_Web_Crawler(object):

    def setup_method(self):
        self.init = Web_Crawler("www.test.com", 1, 1)
        self.loop = asyncio.get_event_loop()

    def test_list_cleanup(self):
        assert self.init.list_cleanup([["Test"], None], []) == ["Test"]

    def test_remove_none_elements_from_list(self):
        assert self.init.remove_none_elements_from_list(["Test", None]) == ["Test"]

    def test_dynamic_speed(self):
        self.init.speed_factor = 2
        assert self.init.dynamic_speed(1) == 1
        assert self.init.dynamic_speed(500) == 250

    def test_check_url(self):
        self.init.initial_domain = "https://www.test_url.com"
        self.init.not_wanted = ['twitter', 'facebook', 'linkedin', 'mailto', 'url=']
        assert self.init.check_url(["www.test_url.com/test/init", "www.test_url.com/test/www.linkedin.com"], "www.test_url.com/test")

    def test_remote_list_duplicates(self):
        self.init.examined_links = ["www.test_url.com/test"]
        expected_links = ["www.test_url.com/test2"]
        assert self.init.remove_list_duplicates(["www.test_url.com/test", "www.test_url.com/test2"]) == expected_links

    def test_get_links(self):
        with open('tests/fixtures/html_data') as raw_html:
            expected_links = ["/test1.html", "https://www.test_url.com/test2"]
            links_extracted = self.loop.run_until_complete(self.init.get_links(raw_html))
            assert links_extracted == expected_links

    def test_real_functionality(self):
        url = "https://monzo.com"
        self.init = self.init = Web_Crawler(url, 1, 1)
        raw = self.loop.run_until_complete(self.init.get_raw_data(url))
        links = self.loop.run_until_complete(self.init.get_links(raw))
        urls = self.init.check_url(links, url)
        clean_list = self.init.remove_list_duplicates(urls)

        json_data = open("tests/fixtures/links.json").read()
        expected_links = json.loads(json_data)['links']
        assert (len(clean_list) == len(expected_links)) and \
            (sorted(clean_list)==sorted(expected_links))
