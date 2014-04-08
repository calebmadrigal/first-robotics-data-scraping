#!/usr/bin/env python
#
# USAGE: python first_robotics_data.py

""" Data scrapes the FIRST robotics website for match results, standings, and awards. """

__author__ = "Caleb Madrigal"
__date__ = "2014-03-05"
__updated__ = "2014-04-07"
__version__  = "1.0.0"

import re
import csv
from urllib2 import urlopen
from bs4 import BeautifulSoup

YEAR = '2014'
EVENT_LIST_URL = 'https://my.usfirst.org/myarea/index.lasso?event_type=FRC&year=' + YEAR
URL_PREFIX = 'https://my.usfirst.org/myarea/index.lasso'
MATCH_RESULTS_HEADINGS = ['Time', 'Description', 'Match', 'Red 1', 'Red 2', 'Red 3',
                         'Blue 1', 'Blue 2', 'Blue 3', 'Red Score', 'Blue Score',
                         'Match Type', 'Event Name', 'Year']

def get_event_list():
    """ Returns the list of the event URLs that we want to crawl, filtering out the ones we
        don't want (which right now is just the championship). """

    html = urlopen(EVENT_LIST_URL)
    soup = BeautifulSoup(html)

    # Find all <a> tags which contain 'event_details' in their href; these are
    # the competition urls.
    events = soup.findAll('a', href=re.compile('event_details'))

    # Filter out championship
    desired_events = [link for link in events if link.text.lower().find('championship') == -1]

    # Get URLs from anchor tags
    url_list = [URL_PREFIX + link.get('href') for link in desired_events]
    return url_list

def get_event_details(event_url):
    """ Takes the event url and returns a dictionary in this format:
        { 'match_results': [...],
          'standings': [...],
          'awards': [...]
        } """

    html = urlopen(event_url)
    soup = BeautifulSoup(html)

    event_name = soup.find('td', text=re.compile('Event')).next_sibling.next_sibling.text
    print '\nGetting details for event:', event_name

    match_results_url = soup.find('a', href=re.compile('matchresults')).get('href')
    standings_url = soup.find('a', href=re.compile('matchresults')).get('href')
    awards_url = soup.find('a', href=re.compile('matchresults')).get('href')

    match_results = get_match_results(match_results_url, event_name)
    standings = get_standings(standings_url, event_name)
    awards = get_awards(awards_url, event_name)

    return {'match_results': match_results, 'standings': standings_url, 'awards': awards_url}

def get_match_results(match_results_url, event_name):
    """ Scrape match results and return them in a list of lists. """

    print '\tGetting match results for:', event_name, '(url:', match_results_url, ')'
    html = urlopen(match_results_url)
    soup = BeautifulSoup(html)

    # Find the qualifications table and the elimination table; it was emperically found
    # that the 2nd table is the qualifications table, and the 3rd table is the elimination table :)
    tables = soup.findAll('table')
    qual_table = tables[2]
    elim_table = tables[3]

    qual_rows = qual_table.findAll('tr')
    elim_rows = elim_table.findAll('tr')

    data = []

    for row in qual_rows[3:]:
        new_row = [td.text.strip() for td in row.findAll('td')]
        new_row.insert(1, '') # Insert empty description
        new_row = new_row + ['Qualification', event_name, YEAR]
        data.append(new_row)

    for row in elim_rows[3:]:
        new_row = [td.text for td in row.findAll('td')]
        new_row = new_row + ['Elimination', event_name, YEAR]
        data.append(new_row)

    return data

def get_standings(standings_url, event_name):
    """ Scrape match results and return them in a list of lists. """

    print '\tGetting standings for:', event_name
    html = urlopen(standings_url)
    soup = BeautifulSoup(html)

def get_awards(awards_url, event_name):
    """ Scrape match results and return them in a list of lists. """

    print '\tGetting awards for:', event_name
    html = urlopen(awards_url)
    soup = BeautifulSoup(html)

def write_csv_file(filename, data, column_headers):
    with open(filename, 'w') as match_results_file:
        csv_writer = csv.writer(match_results_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(column_headers)

        for line in data:
            csv_writer.writerow(line)

def main():
    match_results = []
    standings = []
    awards = []

    for url in get_event_list():
        results = get_event_details(url)
        match_results += results['match_results']

    write_csv_file('match_results.csv', match_results, MATCH_RESULTS_HEADINGS)

if __name__ == '__main__':
    main()

