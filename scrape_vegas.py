import urllib.request
from bs4 import BeautifulSoup
from pathlib import Path
import csv
import re

def parse_rows(rows):
    """ Get data from rows """
    results = []
    alpha_num = re.compile(r'[a-z]')
    for row in rows:
        table_headers = row.find_all('th')
        if table_headers:
            results.append([headers.get_text() for headers in table_headers])

        table_data = row.find_all('td')
        if table_data:
            new_row = []
            to_strip = " .,;\""
            for data in table_data:
                raw_data = data.get_text().strip(to_strip).lower()
                if alpha_num.match(raw_data):
                    school = raw_data.split(' ')
                    for i in range(len(school)):
                        school[i] = school[i].strip(to_strip)
                        formatted = "-".join(school)
                else:
                    formatted = raw_data
                new_row.append(formatted)
            results.append(new_row)
    return results


def scraper(url, identifier1, identifier1type="table", identifier2=None):
    # Make soup
    try:
        resp = urllib.request.urlopen(url)
    except urllib.request.URLError as e:
        print('An error occured fetching %s \n %s' % (url, e.reason))
        return 1
    soup = BeautifulSoup(resp.read(), "html.parser")

    # Get table
    try:
        if identifier2:
            table = soup.find(identifier1type, identifier1).find("table", identifier2)
        else:
            table = soup.find("table", identifier1)
    except AttributeError as e:
        print('No tables found, exiting')
        return 1

    # Get rows
    try:
        rows = table.find_all('tr')
    except AttributeError as e:
        print('No table rows found, exiting')
        return 1

    # Get data
    table_data = parse_rows(rows)

    # Save data
    count = 0
    webr = re.compile(r'www\.(\w+)\.com')
    urlID = webr.search(url)
    websiteID = urlID.group(1)
    print(websiteID)

    while True:
        my_file = Path("./data/" + websiteID + str(count) + ".csv")
        if my_file.is_file():
            # file exists
            count += 1
        else:
            # write it
            with open("./data/" + websiteID + str(count) + ".csv", 'w') as csvfile:
                writer = csv.writer(csvfile)
                [writer.writerow(r) for r in table_data]
            break


# scraper("http://www.vegasinsider.com/college-basketball/odds/futures/",
#         {"style":"background-color:#FCF5E5; margin: 0 auto; clear: both;"},
#         identifier2={"class":"table-wrapper cellTextNorm"})

scraper("https://www.oddsshark.com/ncaab/odds/futures",
        {"style":"background-color:#FCF5E5; margin: 0 auto; clear: both;"},
        identifier2={"class":"table-wrapper cellTextNorm"})

