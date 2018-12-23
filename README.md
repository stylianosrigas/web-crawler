# Web Crawler
This is a Web Crawler app that returns the url mapping of a specified website.

## Solution explained
For the solution of this application a selection of tools was made to make things faster and more efficient. ***Python3*** language was used for coding, ***aiohttp*** package to handle the url connection and data extraction, as well as Python3 supported ***asyncio*** package for running tasks in an asynchronous way.

The idea is that when the app initially runs, it moves to the first depth layer of the website and creates a list of all the available links that are within the accepted format. Once this job is done if the depth value is set to a higher level than 1, a pool of available links is created that are picked asynchronously and each one of them is scanned for connected links. The same process is followed until the depth of scanning reaches the desired depth.

## Assumptions
- In the application a list of links already explored is created to avoid rescanning of urls. The main reason for that is that most websites have a list of links that are part of the base website structure and exist in all pages. These kind of links are included in the initial url crawl and not in every link connected to that. This leads to reduction of calculation time and map representation complexity
- For this Web Crawler application it is expected that the app will follow only internal links of the url examined. Therefore, email and social media connections are not followed.


## Parameterisation
Several parameters can be specified, while running the Web Crawler app.

* **--file** This parameter is not required to run the Web Crawler, but when specified with a file name the results will be exported in this file.
* **-url** This parameter is required to run the Web Crawler. It is used to specify the url that should be crawled.
* **--depth** This parameter is not required to run the Web Crawler but a default value will be applied in any case. It is used to specify the depth of crawling.
* **--tasks** This parameter is not required to run the Web Crawler but a default value of 120 tasks will be applied in any case. It is used to specify the number of tasks to run asynchronously.
* **--output** This parameter is not required to run the Web Crawler, but when specified as True the results will be exported in the terminal window.

## Run the code
The application is written in Python3, therefore it can be simply run by running:

  -> **python3 app/main.py --url <url_to_crawl>**

By running -> **python3 app/main.py --help** you can get all the available parameter options.

For example -> **python3 app/main.py --file 'results.txt' --url  https://bbc.com --depth 2 --output True** will crawl *bbc.com* and create a mapping of all links up to a depth of 2. The result will be output in both a file called results.txt, as well as the terminal that runs the application.

## Testing
***Pytest*** framework was used to write small simple tests for the Web Crawler. The application does not have 100% testing coverage, but basic testing is in place to cover the app logic. To run the tests the following command can be used:

-> **python3 -m pytest --cov-report term-missing --cov=app/ --capture=sys --verbose --color=yes**

## Improvements
- Basic app testing was covered as part of this code version. Future testing coverage expansion needed.
- Better error handling should be added in the future.
- At the moment a maximum tasks number is used to limit the number of asynchronous tasks running. This number is based on network connectivity and aiohttp limitations. Usage of another package for the connection or of a better try/error setup could solve this issue.
