import argparse

class Helpers():

    def __init__(self):
        pass

    def argparser(self):
        """
        """
        parser = argparse.ArgumentParser(description='Welcome to Web Crawler')
        parser.add_argument('-f','--file', help='Specify this argument if you want to export the map in a file', required=False)
        parser.add_argument('-u','--url', help='Specify this argument to define the url that should be crawled', required=True)
        parser.add_argument('-d','--depth', help='Specify this argument to define the depth to be examined', required=False, type=int, default=3)
        parser.add_argument('-s','--speed', help='Specify this argument to define the speed factor to be used', required=False, type=float, default=3.7)
        parser.add_argument('-o','--cli_output', help='Specify this argument to define if cli output should be included for mapping', required=False, default=False)
        args = vars(parser.parse_args())
        return args

    def visualise_results_cli(self, url_map, level = 0):
        """
        """
        if level == 0:
            print('%s' % url_map.value)
            self.visualise_results_cli(url_map, 1)
        else:
            for node in url_map.next_nodes:
                print('%s|---%s' % (level*'\t', node.value))
                self.visualise_results_cli(node, level + 1)

    def visualise_results_file(self, url_map, file, level = 0):
        """
        """
        if level == 0:
            file.write('%s\n' % url_map.value)
            self.visualise_results_file(url_map, file, 1)
        else:
            for node in url_map.next_nodes:
                file.write('%s|---%s\n' % (level*3*'\t', node.value))
                self.visualise_results_file(node, file, level + 1)
