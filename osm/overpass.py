"""
The module provides named queries against Overpass API, i.e., for entities in
OpenStreetMap using Overpass Query Language:
https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL
"""
import socket
from itertools import chain

import jsonlines
import overpy
from tqdm import tqdm


class Overpass:

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def way2dict(self, way):
        return {
            'type': 'way',
            'id': way.id
        }

    def relation2dict(self, relation):
        return {
            'type': 'relation',
            'id': relation.id
        }

    def node2dict(self, node):
        return {
            'type': 'node',
            'id': node.id,
            'name': node.tags.get('name', None),  # name is an optional tag
            'lat': float(node.lat),
            'lon': float(node.lon),
        }

    def save(self, results, areas_ids, fpath):
        """

        :param results: nodes returned by Overpass API
        :param areas_ids: OpenStreetMap IDs of areas.
        :param fpath: file to save
        :return:
        """
        with jsonlines.open(fpath, 'w') as f:
            for area_id, result in zip(areas_ids, results):
                nodes = [self.node2dict(node) for node in result.nodes]
                ways = [self.way2dict(way) for way in result.ways]
                relations = [self.relation2dict(relation)
                             for relation
                             in result.relations]
                for element in chain(nodes, ways, relations):
                    element['osmAreaId'] = area_id
                    f.write(element)

    def fetch(self, areas_ids, query, fpath):
        """
        Saves results of a given query in JSON lines format.
        :param areas_ids: OpenStreetMap IDs of areas.
        :param query: Overpass API query.
        :param fpath: path to file to store results.
        :return:
        """

        ip = socket.gethostbyname(self.host)
        api = overpy.Overpass(url=f'http://{ip}:{self.port}/api/interpreter')
        results = (api.query(query(area_id))
                   for area_id
                   in tqdm(areas_ids,
                           desc=f'Querying Overpass for {query.__name__}...'))
        self.save(results, areas_ids, fpath)
