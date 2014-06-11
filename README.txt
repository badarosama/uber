To Run:
Download flask.
From terminal run 'python server.py' to run the server. You can POST requests to server to verify the output. 
To run tests, type 'python tests.py'.

Server

1-/email accepts a POST request. It tries to send email through mailgun. Failing that it tries to send email through mandrill. If both servers fail to send email, it raises an exception.
2- email.conf stores the config variables such as API keys and url-links. 
3- each request to the server is first validated using validate_request(). Validate request takes in a dict of values
and checks to see if any key is missing or if there are more keys or whether the keys are formatted correctly. It also checks for null values and raises exceptions accordingly.
4- the exceptions are handled in the server and displayed on the browser with the correct response value.
5- parse_text(data) is used to remove the html tags from the body of the email. It uses a regex to get rid of tags.


Given more time.

1- parse_text() can be improved. Maybe an existing python library can be used to perform a better more robust job.
2- implemented one of the additional challenges - if one server fails,it send email through the other. could have implemented most of the other challenges.
3- use unit test.mock library for mock testing in my tests instead of creating dummy objects.

