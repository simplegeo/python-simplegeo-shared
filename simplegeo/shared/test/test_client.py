import unittest
from pyutil import jsonutil as json
from simplegeo.shared import Client, APIError, DecodeError

from decimal import Decimal as D

import mock

MY_OAUTH_KEY = 'MY_OAUTH_KEY'
MY_OAUTH_SECRET = 'MY_SECRET_KEY'
TESTING_LAYER = 'TESTING_LAYER'

API_VERSION = '1.0'
API_HOST = 'api.simplegeo.com'
API_PORT = 80

class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = Client(MY_OAUTH_KEY, MY_OAUTH_SECRET, API_VERSION, API_HOST, API_PORT)
        self.query_lat = D('37.8016')
        self.query_lon = D('-122.4783')

    def test_wrong_endpoint(self):
        self.assertRaises(Exception, self.client.endpoint, 'wrongwrong')

    def test_missing_argument(self):
        self.assertRaises(Exception, self.client.endpoint, 'feature')

    def test_get_feature(self):
        mockhttp = mock.Mock()
        mockhttp.request.return_value = ({'status': '200', 'content-type': 'application/json', }, EXAMPLE_BODY)
        self.client.http = mockhttp

        res = self.client.get_feature("abcdefghijklmnopqrstuvwyz")
        self.assertEqual(mockhttp.method_calls[0][0], 'request')
        self.assertEqual(mockhttp.method_calls[0][1][0], 'http://api.simplegeo.com:80/%s/feature/%s.json' % (API_VERSION, "abcdefghijklmnopqrstuvwyz"))
        self.assertEqual(mockhttp.method_calls[0][1][1], 'GET')
        # the code under test is required to have json-decoded this before handing it back
        self.failUnless(isinstance(res, dict), (repr(res), type(res)))

    def test_type_check_request(self):
        self.failUnlessRaises(TypeError, self.client._request, 'whatever', 'POST', {'bogus': "non string"})

    def test_get_feature_bad_json(self):
        mockhttp = mock.Mock()
        mockhttp.request.return_value = ({'status': '200', 'content-type': 'application/json', }, EXAMPLE_BODY + 'some crap')
        self.client.http = mockhttp

        try:
            self.client.get_feature("abcdefghijklmnopqrstuvwyz")
        except DecodeError, e:
            self.failUnlessEqual(e.code,None,repr(e.code))
            self.failUnless("Could not decode JSON" in e.msg, repr(e.msg))
            erepr = repr(e)
            self.failUnless('JSONDecodeError' in erepr, erepr)

        self.assertEqual(mockhttp.method_calls[0][0], 'request')
        self.assertEqual(mockhttp.method_calls[0][1][0], 'http://api.simplegeo.com:80/%s/feature/%s.json' % (API_VERSION, "abcdefghijklmnopqrstuvwyz"))
        self.assertEqual(mockhttp.method_calls[0][1][1], 'GET')

    def test_dont_json_decode_results(self):
        """ _request() is required to return the exact string that the HTTP
        server sent to it -- no transforming it, such as by json-decoding. """

        mockhttp = mock.Mock()
        mockhttp.request.return_value = ({'status': '200', 'content-type': 'application/json', }, '{ "Hello": "I am a string. \xe2\x9d\xa4" }'.decode('utf-8'))
        self.client.http = mockhttp
        res = self.client._request("http://thing", 'POST')[1]
        self.failUnlessEqual(res, '{ "Hello": "I am a string. \xe2\x9d\xa4" }'.decode('utf-8'))

    def test_dont_Recordify_results(self):
        """ _request() is required to return the exact string that the HTTP
        server sent to it -- no transforming it, such as by json-decoding and
        then constructing a Record. """

        EXAMPLE_RECORD_JSONSTR=json.dumps({ 'geometry' : { 'type' : 'Point', 'coordinates' : [D('10.0'), D('11.0')] }, 'id' : 'my_id', 'type' : 'Feature', 'properties' : { 'key' : 'value'  , 'type' : 'object' } })

        mockhttp = mock.Mock()
        mockhttp.request.return_value = ({'status': '200', 'content-type': 'application/json', }, EXAMPLE_RECORD_JSONSTR)
        self.client.http = mockhttp
        res = self.client._request("http://thing", 'POST')[1]
        self.failUnlessEqual(res, EXAMPLE_RECORD_JSONSTR)

    def test_get_feature_error(self):
        mockhttp = mock.Mock()
        mockhttp.request.return_value = ({'status': '500', 'content-type': 'application/json', }, '{"message": "help my web server is confuzzled"}')
        self.client.http = mockhttp

        try:
            self.client.get_feature("abcdefghijklmnopqrstuvwyz")
        except APIError, e:
            self.failUnlessEqual(e.code, 500, repr(e.code))
            self.failUnlessEqual(e.msg, '{"message": "help my web server is confuzzled"}', (type(e.msg), repr(e.msg)))

        self.assertEqual(mockhttp.method_calls[0][0], 'request')
        self.assertEqual(mockhttp.method_calls[0][1][0], 'http://api.simplegeo.com:80/%s/feature/%s.json' % (API_VERSION, "abcdefghijklmnopqrstuvwyz"))
        self.assertEqual(mockhttp.method_calls[0][1][1], 'GET')

    def test_APIError(self):
        e = APIError(500, 'whee', {'status': "500"})
        self.failUnlessEqual(e.code, 500)
        self.failUnlessEqual(e.msg, 'whee')
        repr(e)
        str(e)


EXAMPLE_BODY="""
{
   "weather": {
    "message" : "'NoneType' object has no attribute 'properties'",
    "code" : 400
    },
   "features": [
    {
     "name" : "06075013000",
     "type" : "Census Tract",
     "bounds": [
      -122.437326,
      37.795016,
      -122.42360099999999,
      37.799485
     ],
     "href" : "http://api.simplegeo.com/0.1/boundary/Census_Tract%3A06075013000%3A9q8zn0.json"
     },
     {
     "name" : "94123",
     "type" : "Postal",
     "bounds": [
      -122.452966,
      37.792787,
      -122.42360099999999,
      37.810798999999996
     ],
     "href" : "http://api.simplegeo.com/0.1/boundary/Postal%3A94123%3A9q8zjc.json"
     },
     {
     "name" : "San Francisco",
     "type" : "County",
     "bounds": [
      -123.173825,
      37.639829999999996,
      -122.28178,
      37.929823999999996
     ],
     "href" : "http://api.simplegeo.com/0.1/boundary/County%3ASan_Francisco%3A9q8yvv.json"
     },
     {
     "name" : "San Francisco",
     "type" : "City",
     "bounds": [
      -123.173825,
      37.639829999999996,
      -122.28178,
      37.929823999999996
     ],
     "href" : "http://api.simplegeo.com/0.1/boundary/City%3ASan_Francisco%3A9q8yvv.json"
     },
     {
     "name" : "Congressional District 8",
     "type" : "Congressional District",
     "bounds": [
      -122.612285,
      37.708131,
      -122.28178,
      37.929823999999996
     ],
     "href" : "http://api.simplegeo.com/0.1/boundary/Congressional_District%3ACongressional_Di%3A9q8yyn.json"
     },
     {
     "name" : "United States of America",
     "type" : "Country",
     "bounds": [
      -179.14247147726383,
      18.930137634111077,
      179.78114994357418,
      71.41217966730892
     ],
     "href" : "http://api.simplegeo.com/0.1/boundary/Country%3AUnited_States_of%3A9z12zg.json"
     },
     {
     "name" : "Pacific Heights",
     "type" : "Neighborhood",
     "bounds": [
      -122.446782,
      37.787529,
      -122.422182,
      37.797728
     ],
     "href" : "http://api.simplegeo.com/0.1/boundary/Neighborhood%3APacific_Heights%3A9q8yvz.json"
     },
     {
     "name" : "San Francisco1",
     "type" : "Urban Area",
     "bounds": [
      -122.51666666668193,
      37.19166666662851,
      -121.73333333334497,
      38.04166666664091
     ],
     "href" : "http://api.simplegeo.com/0.1/boundary/Urban_Area%3ASan_Francisco1%3A9q9jsg.json"
     },
     {
     "name" : "California",
     "type" : "Province",
     "bounds": [
      -124.48200299999999,
      32.528832,
      -114.131211,
      42.009516999999995
     ],
     "href" : "http://api.simplegeo.com/0.1/boundary/Province%3ACA%3A9qdguu.json"
     }
   ],
   "demographics": {
    "metro_score" : "10"
    }
   }
"""
