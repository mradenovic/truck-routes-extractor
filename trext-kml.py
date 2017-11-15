#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Truck Routes EXTractor

This script extracts New York City truck routes from official KML files found
at http://www.nyc.gov/html/dot/html/about/datafeeds.shtml#truckroutes
and creates sets of KML files that can be easily imported into Google My Maps.
"""

import codecs
import sys
import re
import argparse
from bs4 import BeautifulSoup

class TruckRouteExtractor:


    def __init__(self, filename, routes, prefix, limit):
        self.filename = filename
        self.routes = routes
        self.prefix = prefix
        self.limit = limit
        self.soup = self.get_soup(filename)
        self.placemarks = self.soup.kml.Document.Folder('Placemark')

    def get_soup(self, filename):
        inputfile = self.get_inputfile(filename)
        print 'Preparing file {}...'.format(filename)
        soup = BeautifulSoup(inputfile, 'lxml-xml')
        print 'File {} is ready'.format(filename)
        return soup

    def get_inputfile(self, filename):
        try:
            inputfile = open(filename).read()
            if not self.is_valid_file(inputfile):
                raise IOError("File '{}' does not contain truck routes.".format(filename))
        except IOError as error:
            print error
            sys.exit()
        return inputfile

    def is_valid_file(self, inputfile):
        if ( inputfile.find('Truck Route') == -1):
            return False
        else:
            return True

    def extract_routes(self):
        self.soup.kml.Document.Folder.extract()
        folder = self.soup.new_tag('Folder')
        self.soup.kml.Document.append(folder)
        for route in self.routes:
            self.extract_route(route)

    def set_doc_metadata(self, route_name):
        document = self.soup.kml.Document
        document['id'] = route_name
        name = document.find('name')
        name.string = route_name


    def create_doc(self, route, doc_no):
        route_name = route.replace(' ', '_') + 's_' + str(doc_no)
        self.set_doc_metadata(route_name)
        doc_content = self.soup.prettify(formatter='minimal')
        doc_name = '{}{}.kml'.format(self.prefix, route_name)

        codecs.open(doc_name, mode='w', encoding="utf-8").write(doc_content)
        print 'Created file: {}'.format(doc_name)
        self.soup.kml.Document.Folder.clear()


    def extract_route(self, route):
        print 'Creating... : {}'.format(route)
        pattern = re.compile(route)
        document = self.soup.kml.Document
        folder = document.Folder
        doc_no = 1
        counter = 0
        total = 0
        # length = len(placemarks)
        for placemark in self.placemarks:
            # print '\r{}/{}'.format(i, len(placemarks)),
            found = placemark.find('description', string=pattern)
            if found:
                total += 1
                folder.append(placemark)
                counter += 1
                if counter == self.limit:
                    counter = 0
                    self.create_doc(route, doc_no)
                    doc_no += 1
        self.create_doc(route, doc_no)
        print 'Total of %s placemarks' % total


def main():
    parser = argparse.ArgumentParser(
        description="Extract truck routes from NYC DOT geodata")
    parser.add_argument('-v', '--version', action='version',
        version='%(prog)s 0.0.1')
    parser.add_argument('filename',
        help='input file to extract routes from')
    parser.add_argument('-r', '--routes', nargs='+', required=True, metavar='regexp',
        help='regular expression of routes to extract')
    parser.add_argument('-p', '--prefix', default='',
        help='prefix for files created')
    parser.add_argument('-l', '--limit', type=int, metavar='N', default='1999',
        help='limit number of placemarks per file')

    args = parser.parse_args()
    tre = TruckRouteExtractor(**vars(args))
    tre.extract_routes()


if __name__ == "__main__":
    main()
