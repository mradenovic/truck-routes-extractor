# Truck Route EXTractor

A tool to extract New York City truck routes from the official [NYC DOT datafeeds](http://www.nyc.gov/html/dot/html/about/datafeeds.shtml#truckroutes)
and create sets of KML files that can be easily imported into [Google My Maps](https://www.google.com/maps/about/mymaps/).

## Example Map

[NYC Truck Routes](https://drive.google.com/open?id=1yFhMLCQjZBGUjrPud8s7ciljPlg&usp=sharing)

## Prerequisites
* [Python 2.7](https://www.python.org/downloads/)
* [GeoPandas](http://geopandas.org/install.html)
* Download and extract [SHP files](http://www.nyc.gov/html/dot/downloads/misc/all_truck_routes_nyc.zip)

## Quick Start
* clone the repo: `git clone https://github.com/mradenovic/truck-routes-extractor.git`
* cd to newly created directory: `cd truck-routes-extractor`
* install python requirements: `sudo pip install -r requirements.txt`
* run command: `python trext.py -r "Local Truck Route" "Through Truck Route" -p All_ all_truck_routes_nyc/All_Truck_Routes_NYC_Lion14A.shp`

Resulting KML files can be imported into [Google My Maps](https://www.google.com/maps/about/mymaps/).
