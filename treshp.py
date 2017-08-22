#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Truck Routes Eexractor SHP

This script extracts New York City truck routes from official SHP files found
at http://www.nyc.gov/html/dot/html/about/datafeeds.shtml#truckroutes
and creates sets of KML files that can be easily imported into Google My Maps.
"""

import codecs
import sys
import re
import argparse
from bs4 import BeautifulSoup
from geopandas import GeoDataFrame
from fiona.errors import FionaValueError
import shapely
import pandas as pd


STYLES = {
    # Through
    #f768a1
    #ae017e
    'ThroughRoute': 'ffa168f7',
    'ThroughRouteRestricted': 'ff7e01ae',
    # Local
    #78c679
    #238443
    'LocalRoute': 'ff79c678',
    'LocalRouteRestricted': 'ff438423'
}


class Route(object):


    def __init__(self, Descriptio, Street, Restrictio, geometry):
        self.Descriptio = Descriptio
        self.Street = Street
        self.Restrictio = Restrictio
        self.geometry = geometry


class TruckRouteExtractor:

    def __init__(self, filename, routes, prefix, limit):
        self.filename = filename
        self.routes = routes
        self.prefix = prefix
        self.limit = limit
        self.soup = self.get_soup()
        self.data = self.get_data(filename)

    def get_soup(self):
        soup = BeautifulSoup('', 'lxml-xml')
        new_tag = soup.new_tag
        soup.append(new_tag('kml', xmlns="http://www.opengis.net/kml/2.2"))
        soup.kml.append(self.get_document_tag(soup))
        return soup

    def get_document_tag(self, soup):
        document = soup.new_tag('Document')
        document.append(soup.new_tag('name'))
        for style in STYLES:
            name = style
            color = STYLES[style]
            document.append(self.get_style_tag(soup, name, color))
        document.append(soup.new_tag('Folder'))
        return document

    def get_style_tag(self, soup, name, color):
        """
        """

        new_tag = soup.new_tag
        style = new_tag('Style', id=name)

        style.append(new_tag('LabelStyle'))
        style.LabelStyle.append(new_tag('color'))
        style.LabelStyle.color.string = '00000000'
        style.LabelStyle.append(new_tag('scale'))
        style.LabelStyle.scale.string = '0'

        style.append(new_tag('LineStyle'))
        style.LineStyle.append(new_tag('color'))
        style.LineStyle.color.string = color
        style.LineStyle.append(new_tag('width'))
        style.LineStyle.width.string = '1.5'

        style.append(new_tag('PolyStyle'))
        style.PolyStyle.append(new_tag('color'))
        style.PolyStyle.color.string = '00000000'
        style.PolyStyle.append(new_tag('outline'))
        style.PolyStyle.outline.string = '0'

        return style

    def get_data(self, filename):
        print "Preparing file '{}'...".format(filename)
        try:
            data = GeoDataFrame.from_file(filename)
            data = data[['Descriptio', 'Street', 'Restrictio', 'geometry']]
        except (IOError, FionaValueError) as error:
            print error
            sys.exit()
        print "File '{}' is ready".format(filename)
        return data

    def extract_routes(self):
        for route in self.routes:
            self.extract_route(route)

    def set_doc_metadata(self, route_name):
        document = self.soup.kml.Document
        document['id'] = route_name
        name = document.find('name')
        name.string = route_name


    def create_doc(self, route, file_no):
        route_name = route.replace(' ', '_') + 's_' + str(file_no)
        self.set_doc_metadata(route+'s')
        doc_content = self.soup.prettify(formatter='minimal')
        doc_name = '{}{}.kml'.format(self.prefix, route_name)

        codecs.open(doc_name, mode='w', encoding="utf-8").write(doc_content)
        print 'Created file: {}'.format(doc_name)
        self.soup.kml.Document.Folder.clear()

    def check_file_limit(self, total, limit, file_no, pattern):
        if limit == self.limit:
            limit = 0
            self.create_doc(pattern, file_no)
            return total + 1, limit, file_no + 1
        else:
            return total + 1, limit + 1, file_no

    def append_placemark(self, total, limit, file_no, route):
        folder = self.soup.kml.Document.Folder


    def get_routes(self, pattern):
        data =self.data
        re_pattern = re.compile(pattern)
        routes = data[data['Descriptio'].str.contains(re_pattern)]
        routes = routes.to_crs(epsg=4326)
        fields = ['Descriptio', 'Street', 'Restrictio']
        routes = routes.groupby(fields, as_index=False).agg(lambda x: shapely.ops.linemerge(x.values))
        return routes

    def extract_route(self, pattern):
        print 'Creating... : {}'.format(pattern)
        routes = self.get_routes(pattern)
        folder = self.soup.kml.Document.Folder
        total, limit, file_no = 0, 0, 1
        for index, route in routes.iterrows():
            if isinstance(route.geometry, shapely.geometry.linestring.LineString):
                folder.append(self.get_placemark(route))
                total, limit, file_no = self.check_file_limit(total, limit, file_no, pattern)
            else:
                for geom in route.geometry.geoms:
                    route.geometry = geom
                    folder.append(self.get_placemark(route))
                    total, limit, file_no = self.check_file_limit(total, limit, file_no, pattern)
        self.create_doc(pattern, file_no)
        print 'Total of %s placemarks' % total

    def get_placemark(self, route):
        """
        """
        new_tag = self.soup.new_tag
        coordinates = self.coords_to_str(route.geometry.coords)
        description = self.get_route_description(route)

        placemark = new_tag('Placemark')

        placemark.append(new_tag('name'))
        placemark.find('name').string = route.Street

        placemark.append(new_tag('description'))
        placemark.description.string = description

        placemark.append(new_tag('styleUrl'))
        placemark.styleUrl.string = self.get_route_style(route)

        placemark.append(new_tag('MultiGeometry'))
        placemark.MultiGeometry.append(new_tag('LineString'))
        linestring = placemark.MultiGeometry.LineString
        linestring.append(new_tag('tessellate'))
        linestring.tessellate.string = '1'
        linestring.append(new_tag('coordinates'))
        linestring.coordinates.string = coordinates
        return placemark

    def coords_to_str(self, coords):
        str_coords = ''
        for coord in coords:
            str_coords += '{},{},0 '.format(coord[0], coord[1])
        return str_coords

    def get_route_description(self, route):
        description = 'Description: {}\nRestriction: {}'.format(
            route.Descriptio, route.Restrictio
        )
        return description

    def get_route_style(self, route):
        restricted = ''
        if route.Restrictio != 'None':
            restricted = 'Restricted'
        route_type = 'Local'
        if route.Descriptio.find('Through') != -1:
            route_type = 'Through'
        style = '#{}Route{}'.format(route_type, restricted)
        # style = '#LocalRoute'
        return style


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
