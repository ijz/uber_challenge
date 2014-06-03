from flask import Flask
from flask import request
import json
import urllib2
import urllib
import base64

app = Flask(__name__)

mailgun_url = "https://api.mailgun.net/v2/sandbox6820aebf3fa44b15a0f38e7943ed6471.mailgun.org/messages"
mailgun_api_key = "key-4pu1uxt38wn5e34i4jn74yvchg30jv82"
mandrill_url = "https://mandrillapp.com/api/1.0/messages/send.json"
mandrill_key = "fXmpLQuUhIuLwcNuw0H2jg"

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
    results = urllib2.urlopen(mailgun_request, timeout=1)
    response = results.read()
    return response
    
def send_mandrill_request(json_data):
    mandrill_request = urllib2.Request(mandrill_url)
    mandrill_request.add_header("User-agent", "Mandrill-Curl/1.0")
    email_data = json.dumps({
        "key": mandrill_key,
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
            "text":json_data['body']
        }
    })
    mandrill_request.add_data(email_data)
    results = urllib2.urlopen(mandrill_request, timeout=1)
    response = results.read()
    return response

@app.route("/")
def index():
    return "index"
    
@app.route("/email", methods=["POST"])
def email():
    json_obj = json.loads(request.data)
    try:
        mandrill_response = send_mandrill_request(json_obj)
        return mandrill_response
    except Exception, e:
        print "Mandrill failed. Using Mailgun"
        print e
        try:
            mailgun_response = send_mailgun_request(json_obj)
            return mailgun_response
        except urllib2.URLError as e2:
            print "Mailgun failed. Error."
            print e2
    
if __name__ == '__main__':
    app.debug = True
    app.run()