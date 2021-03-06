Uber Coding Challenge
==============

### Installing Application
* Install Flask framework
* Edit `config.ini`, which is in the same directory as `email_server.py`. You can use a different file by specifing `-c|--config` when starting the server
* Update `config.ini` with the correct Mandrill and Mailgun API URL as well as API key
* You can see all command line options by running `python email_server.py --help`
* Start the server by running `python email_server.py`. This will use `config.ini` in the same directory as the script
* The server should be running with the following output: `* Running on http://127.0.0.1:5000/`

### Language and Framework
I chose to use Python + Flask because they were the first suggestions.

### Trade-offs
I simple removed all HTML tags and replaced `<p> </p> <br />` with new lines in 'body'. Given more time, I would try to preserve the structure of 'body' and maybe explore sending HTML emails.

### Running Tests
Run `python email_server_tests.py`. By default, the test script assumes the API end point is http://localhost:5000/email. You can change that by specifying `-s|--server http://your_server_address:port/email`. Four tests are run. Three of them are to test validation and error checking, and one is to send a valid request and should resolve in sending and receiving an email.

### Additional Features
My server will attempt to send emails via Mandrill first. If it fails for any reason, it will attempt to send using Mailgun. No configuration or restart is needed to failover.