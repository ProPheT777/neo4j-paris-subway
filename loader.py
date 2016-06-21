#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import os.path

from neo4j.v1 import GraphDatabase, basic_auth
from geopy.geocoders import Nominatim

lines = ['1', '2', '3', '3b', '4', '5', '6', '7', '7b', '8', '9', '10', '11', '12', '13', '14']
metros = {}
geocode = os.path.isfile('geocode.csv')
locations = {}

for line in lines: metros[line] = []

with open('structure.csv', 'rb') as file, open('geocode.csv', 'a+') as geofile:
    geolocator = Nominatim()
    writer = csv.writer(geofile)

    for row in csv.reader(file, delimiter=';'):
        if len(row) == 1 or 'M' != list(row[0])[0]: continue

        relatedLine = row[0][1:]

        if relatedLine == '7 bis': relatedLine = '7b'
        if relatedLine == '3 bis': relatedLine = '3b'

        if row[1] not in metros[relatedLine]:
            metros[relatedLine].append(row[1])

            if False == geocode:
                location = geolocator.geocode('Paris, %s' % row[1])

                try:
                    writer.writerow([row[1], location.longitude, location.latitude])
                except AttributeError:
                    writer.writerow([row[1], 0.0, 0.0])

    for row in csv.reader(geofile):
        locations[row[0]] = {"longitude": row[1], "latitude": row[2]}

driver = GraphDatabase.driver('bolt://127.0.0.1', auth=basic_auth('neo4j', 'helene'))
session = driver.session()

for line, stations in metros.items():
    session.run("MERGE (:Line {name: {name} })", {"name": line})
    session.run("CREATE CONSTRAINT on (s:Station) ASSERT s.name IS UNIQUE")

    for index, station in enumerate(stations):
        session.run(
            "MERGE (s:Station {name: {name}}) ON CREATE SET s.latitude = {latitude}, s.longitude = {longitude}",
            {"name": station, "latitude": locations[station]['latitude'], "longitude": locations[station]['longitude']}
        )

        session.run(
            "MATCH (l:Line), (s:Station) WHERE l.name = {line} AND s.name = {station} MERGE (l)-[:HAVE_STATION]->(s)",
            {"line": line, "station": station}
        )

        try:
            nextStation = stations[index+1]

            session.run(
                "MATCH (s1:Station), (s2:Station) WHERE s1.name = {s1_name} AND s2.name = {s2_name} MERGE (s1)-[:NEXT_TO]->(s2) MERGE (s2)-[:NEXT_TO]->(s1)",
                {"s1_name": station, "s2_name": nextStation}
            )
        except IndexError:
            pass

session.close()