import flask
import json
import urllib2
import urllib
import base64
import re
import ConfigParser
import argparse
import traceback

app = flask.Flask(__name__)

timeout = 1
mailgun_url = ""
mailgun_api_key = ""
mandrill_url = ""
mandrill_api_key = ""

def parse_config(file):
    config = ConfigParser.ConfigParser()
    config.read(file)
    global mailgun_url
    mailgun_url = config.get("mailgun", "url")
    global mailgun_api_key
    mailgun_api_key = config.get("mailgun", "api_key")
    global mandrill_url
    mandrill_url = config.get("mandrill", "url")
    global mandrill_api_key
    mandrill_api_key = config.get("mandrill", "api_key")

def generate_json_response(status, content):
    response = flask.make_response(json.dumps(content), status)
    response.headers['Content-type'] = "application/json"
    return response

def is_valid_email_address(address):
    return re.match(r"[^@]*@[^\.]*\..*", address) is not None

def send_mailgun_request(json_data):
    mailgun_request = urllib2.Request(mailgun_url)
    mailgun_auth_string = base64.encodestring("api:%s" % mailgun_api_key).replace('\n', '')
    mailgun_request.add_header("Authorization", "Basic %s" % mailgun_auth_string)
    email_data = urllib.urlencode({
        "from": "%s <%s>" % (json_data["from_name"], json_data["from"]),
        "to": "%s <%s>" % (json_data["to_name"], json_data["to"]),
        "subject": json_data["subject"],
        "text": json_data['body']
    })
    mailgun_request.add_data(email_data)
    results = urllib2.urlopen(mailgun_request, timeout=timeout)
    response = results.read()
    return response

def send_mandrill_request(json_data):
    mandrill_request = urllib2.Request(mandrill_url)
    email_data = json.dumps({
        "key": mandrill_api_key,
        "message": {
            "from_email": json_data["from"],
            "from_name": json_data["from_name"],
            "to": [
                {
                    "email": json_data["to"],
                    "name": json_data["to_name"],
                    "type": "to"
                }
            ],
            "subject": json_data["subject"],
            "text":json_data["body"]
        }
    })
    mandrill_request.add_data(email_data)
    results = urllib2.urlopen(mandrill_request, timeout=timeout)
    response = results.read()
    return response

@app.route("/email", methods=["POST"])
def email():
    # parse input JSON
    try:
        json_obj = json.loads(flask.request.get_data())
    except ValueError, e:
        return generate_json_response(500, {
            "status": "ERROR",
            "reason": "Failed to parse input JSON: %s" % str(e)
        })
    # make sure we have all the parameters
    for key in ["to", "to_name", "from", "from_name", "subject", "body"]:
        if key not in json_obj:
            return generate_json_response(500, {
                "status": "ERROR",
                "reason": "Required JSON parameter [%s] is missing." % key
            })
    # validate email address
    if not is_valid_email_address(json_obj["to"]) or not is_valid_email_address(json_obj["from"]):
        return generate_json_response(500, {
            "status": "ERROR",
            "reason": "Either from or to email address is invalid. [from: '%s', to: '%s']" % (json_obj["from"], json_obj["to"])
        })
    # remove html tags from body
    json_obj["body"] = re.sub(r"\<\/?p\>", "\n", json_obj["body"])
    json_obj["body"] = re.sub(r"\<br[^\>]*\>", "\n", json_obj["body"])
    json_obj["body"] = re.sub(r"\<[^\>]*\>", "", json_obj["body"])

    try:
        mandrill_response = send_mandrill_request(json_obj)
        service_provider = "Mandrill"
        service_message = mandrill_response
    except Exception, e:
        print "Mandrill failed. Using Mailgun"
        traceback.print_exc()
        try:
            mailgun_response = send_mailgun_request(json_obj)
            service_provider = "Mailgun"
            service_message = mailgun_response
        except Exception, e2:
            print "Mailgun failed. Error."
            traceback.print_exc()
            return generate_json_response(500, {
                "status": "ERROR",
                "reason": str(e2)
            })
    return generate_json_response(200, {
        "status": "OK",
        "service_provider": service_provider,
        "service_message": service_message
    })

def main():
    parser = argparse.ArgumentParser(description="Email sender")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", help="Run server in debug mode")
    parser.add_argument("-c", "--config", dest="config_file", default="config.ini", help="Mailgun & Mandrill config file location")
    parser.add_argument("-t", "--timeout", dest="timeout", default=1.0, type=float, help="Timeout in seconds for Mandrill and Mailgun")
    parser.add_argument("-p", "--port", dest="port", default=5000, help="Start server on this port")
    args = parser.parse_args()
    global timeout
    timeout = args.timeout
    parse_config(args.config_file)
    if args.debug:
        print "Mandrill API URL [%s]" % mandrill_url
        print "Mandrill API Key [%s]" % mandrill_api_key
        print "Mailgun API URL [%s]" % mailgun_url
        print "Mailgun API Key [%s]" % mailgun_api_key
    app.debug = args.debug
    app.port = args.port
    app.run()

if __name__ == '__main__':
    main()