import unittest
from simplegeo.shared import Feature
import mock
from decimal import Decimal as D

class FeatureTest(unittest.TestCase):

    def test_record_constructor(self):
        self.failUnlessRaises(AssertionError, Feature, D('11.0'), D('10.0'), properties={'record_id': 'my_id'})

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
        self.assertEquals(record.coordinates[0], D('10.0'))
        self.assertEquals(record.coordinates[1], D('11.0'))
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
        self.assertEquals(record.coordinates[0], 10.0)
        self.assertEquals(record.coordinates[1], 11.0)

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
