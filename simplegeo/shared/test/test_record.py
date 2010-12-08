import unittest
from simplegeo.shared import Feature, deep_swap
from decimal import Decimal as D

class FeatureTest(unittest.TestCase):

    def test_swapper(self):
        t1 = (2, 1)
        self.failUnlessEqual(deep_swap(t1), (1, 2))

        linestring1 = [(2, 1), (4, 3), (6, 5), (8, 7)]
        self.failUnlessEqual(
            deep_swap(linestring1),
            [(1, 2), (3, 4), (5, 6), (7, 8)]
            )

        multipolygon1 = [
            [[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]],
            [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]],
             [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2]]]
            ]

        self.failUnlessEqual(deep_swap(multipolygon1),
                             [[[(2.0, 102.0), (2.0, 103.0), (3.0, 103.0), (3.0, 102.0), (2.0, 102.0)]], [[(0.0, 100.0), (0.0, 101.0), (1.0, 101.0), (1.0, 100.0), (0.0, 100.0)], [(0.2, 100.2), (0.2, 100.8), (0.8, 100.8), (0.8, 100.2), (0.2, 100.2)]]]
                             )

    def test_record_constructor(self):
        self.failUnlessRaises(AssertionError, Feature, D('11.0'), D('10.0'), properties={'record_id': 'my_id'})

        # lat exceeds bound
        self.failUnlessRaises(AssertionError, Feature, (D('91.0'), D('10.1')), properties={'record_id': 'my_id'})

        # lon exceeds bound
        self.failUnlessRaises(AssertionError, Feature, (D('10.1'), D('180.1')), properties={'record_id': 'my_id'})

        record = Feature(coordinates=(D('11.0'), D('10.0')), properties={'record_id': 'my_id'})
        self.failUnlessEqual(record.properties.get('record_id'), 'my_id')
        self.failUnlessEqual(record.id, None)
        self.failUnlessEqual(record.geomtype, 'Point')
        self.failUnlessEqual(record.coordinates[0], D('11.0'))
        self.failUnlessEqual(record.coordinates[1], D('10.0'))

        record = Feature(coordinates=(D('11.0'), D('10.0')), simplegeohandle='SG_abcdefghijklmnopqrstuv')
        self.failUnlessEqual(record.properties.get('record_id'), None)
        self.failUnlessEqual(record.id, 'SG_abcdefghijklmnopqrstuv')

        record = Feature(coordinates=(D('11.0'), D('10.0')), properties={'record_id': 'my_id'}, simplegeohandle='SG_abcdefghijklmnopqrstuv')
        self.failUnlessEqual(record.properties.get('record_id'), 'my_id')
        self.failUnlessEqual(record.id, 'SG_abcdefghijklmnopqrstuv')

        record = Feature(coordinates=(D('11.0'), D('10.0')))
        self.failUnlessEqual(record.properties.get('record_id'), None)
        self.failUnlessEqual(record.id, None)

        record = Feature((D('11.0'), D('10.0')), properties={'record_id': 'my_id'})
        self.failUnlessEqual(record.properties.get('record_id'), 'my_id')

        record = Feature((11.0, 10.0), properties={'record_id': 'my_id'})
        self.failUnlessEqual(record.geomtype, 'Point')
        self.failUnlessEqual(record.coordinates[0], 11.0)
        self.failUnlessEqual(record.coordinates[1], 10.0)
        self.failUnlessEqual(record.properties.get('record_id'), 'my_id')

        record = Feature([[(11.0, 179.9), (12, -179.9)]], geomtype='Polygon')
        self.failUnlessEqual(record.geomtype, 'Polygon')
        self.failUnlessEqual(len(record.coordinates[0]), 2)
        self.failUnlessEqual(record.coordinates[0][0], (11.0, 179.9))

        jsondict = record.to_dict()
        self.failUnlessEqual(jsondict['geometry']['coordinates'][0][0], (179.9, 11.))

    def test_record_from_dict(self):
        record_dict = {
                     'geometry' : {
                                   'type' : 'Point',
                                   'coordinates' : [D('10.0'), D('11.0')]
                                   },
                     'type' : 'Feature',
                     'properties' : {
                                     'record_id' : 'my_id',
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Feature.from_dict(record_dict)
        self.assertEquals(record.coordinates[0], D('11.0'))
        self.assertEquals(record.coordinates[1], D('10.0'))
        self.assertEquals(record.properties.get('record_id'), 'my_id')
        self.assertEquals(record.properties['key'], 'value')
        self.assertEquals(record.properties['type'], 'object')

        record_dict = {
                     'geometry' : {
                                   'type' : 'Point',
                                   'coordinates' : [D('10.0'), D('11.0')]
                                   },
                     'id' : 'SG_abcdefghijklmnopqrstuv',
                     'type' : 'Feature',
                     'properties' : {
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Feature.from_dict(record_dict)
        self.assertEquals(record.properties.get('record_id'), None)
        self.assertEquals(record.id, 'SG_abcdefghijklmnopqrstuv')

        record_dict = {
                     'geometry' : {
                                   'type' : 'Point',
                                   'coordinates' : [D('10.0'), D('11.0')]
                                   },
                     'id' : 'SG_abcdefghijklmnopqrstuv',
                     'type' : 'Feature',
                     'properties' : {
                                     'record_id' : 'my_id',
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Feature.from_dict(record_dict)
        self.assertEquals(record.properties.get('record_id'), 'my_id')
        self.assertEquals(record.id, 'SG_abcdefghijklmnopqrstuv')

        record_dict = {
                     'geometry' : {
                                   'type' : 'Point',
                                   'coordinates' : [10.0, 11.0]
                                   },
                     'type' : 'Feature',
                     'properties' : {
                                     'record_id' : 'my_id',
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Feature.from_dict(record_dict)
        self.assertEquals(record.coordinates[0], 11.0)
        self.assertEquals(record.coordinates[1], 10.0)

    def test_record_to_dict_sets_id_correctly(self):
        handle = 'SG_abcdefghijklmnopqrstuv'
        record_id = 'this is my record #1. my first record. and it is mine'
        rec = Feature(coordinates=(D('11.03'), D('10.03')), simplegeohandle=handle, properties={'record_id': record_id})
        dic = rec.to_dict()
        self.failUnlessEqual(dic.get('id'), handle)
        self.failUnlessEqual(dic.get('properties', {}).get('record_id'), record_id)

        rec = Feature(coordinates=(D('11.03'), D('10.03')), simplegeohandle=handle, properties={'record_id': None})
        dic = rec.to_dict()
        self.failUnlessEqual(dic.get('id'), handle)
        self.failUnlessEqual(dic.get('properties', {}).get('record_id'), None)

        rec = Feature(coordinates=(D('11.03'), D('10.03')), simplegeohandle=handle, properties={'record_id': None})
        dic = rec.to_dict()
        self.failUnlessEqual(dic.get('id'), handle)
        self.failUnlessEqual(dic.get('properties', {}).get('record_id'), None)

        rec = Feature(coordinates=(D('11.03'), D('10.03')), simplegeohandle=None, properties={'record_id': None})
        dic = rec.to_dict()
        self.failUnlessEqual(dic.get('id'), None)
        self.failUnlessEqual(dic.get('properties', {}).get('record_id'), None)
