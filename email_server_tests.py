import unittest
import argparse
import urllib2
import json

class TestEmailServer(unittest.TestCase):

    def send_request(self, data):
        request = urllib2.Request(server, data)
        try:
            results = urllib2.urlopen(request)
            response = results.read()
        except urllib2.HTTPError, error:
            response = error.read()
        return response

    def test_malformed_json(self):
        wrong_json = "{this, is [not even trying} to be a JSON string}"
        response = self.send_request(wrong_json)
        json_response = json.loads(response);
        self.assertEqual("ERROR", json_response["status"])
        self.assertTrue("Failed to parse input JSON" in json_response["reason"])

    def test_missing_json(self):
        data = json.dumps({
            "from": "test@example.com",
            "from_name": "John Doe",
            "subject": "Unknown",
            "body": "<p>Blah blah blah</p>"
        })
        response = self.send_request(data)
        json_response = json.loads(response);
        self.assertEqual("ERROR", json_response["status"])
        self.assertTrue("Required JSON parameter" in json_response["reason"])

    def test_wrong_email_address(self):
        data = json.dumps({
            "from": "this_is_not_an_email_address.com",
            "from_name": "John Doe",
            "to": "jjzhou01@gmail.com",
            "to_name": "JZ",
            "subject": "Unknown",
            "body": "<p>Blah blah blah</p>"
        })
        response = self.send_request(data)
        json_response = json.loads(response);
        self.assertEqual("ERROR", json_response["status"])
        self.assertTrue("email address is invalid" in json_response["reason"])

    def test_send_email(self):
        data = json.dumps({
            "from": "test@example.com",
            "from_name": "John Doe",
            "to": "jjzhou01@gmail.com",
            "to_name": "JZ",
            "subject": "Unknown",
            "body": "<p>Blah blah blah</p>"
        })
        response = self.send_request(data)
        json_response = json.loads(response);
        self.assertEqual("OK", json_response["status"])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Email sender test suite")
    parser.add_argument("-s", "--server", dest="server", default="http://localhost:5000/email", help="Email server end point.")
    args = parser.parse_args()
    global server
    server = args.server
    unittest.main(verbosity=2)