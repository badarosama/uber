import re
import requests

from flask import json
from flask import Flask
from flask import request
from flask import Response

app = Flask(__name__)
app.config.from_pyfile(__name__.rstrip('.py') + '.conf')
settings = app.config


def response(_dict={}, status=200):
  """" _dict: JSON dict to return.
       status: HTTP status code.
       returns a Flask Response object.
  """
  _dict = _dict.copy()
  _dict['success'] = status == 200
  return Response(json.dumps(_dict), status=status, mimetype='application/json')


def parse_text(data):    
  """ data:the Body of email as string.
      returns string with html removed.
  """
  return re.compile(r'<.*?>').sub(' ', data).strip()


def validate_request(_dict):
  """ _dict:dict of url parameters.
      checks for missing keys.
      checks for unknown keys.
      checks for null values.
      raise Exceptions if input not correctly formtted.
  """
  request_keys = set(_dict)
  missing_keys = settings['REQUIRED_KEYS'] - request_keys
  unknown_keys = request_keys - settings['REQUIRED_KEYS']
  if missing_keys:
    raise Exception('These required keys are missing in the request: %s.' %
                    list(missing_keys))
  if unknown_keys:
    raise Exception('These unknown keys are present in the request: %s.' %  
                    list(unknown_keys))
  for key, value in _dict.iteritems():
    if not value:
      raise Exception('%s key has a null (%s) value.' % (key, value))


@app.route('/email', methods=['POST'])
def email():
  """ checks input data is valid
      sends email on mailgun server.
      if mailgun fails, send email on mandrill server.
      if both fail to send, raise an exception.
  """
  try:
    data = json.loads(request.data)
  except ValueError:
    return response({'error': 'Request body is not valid JSON.'},
                    status=400)
  try:
    validate_request(data)
  except Exception, e:
    return response({'error': e.message},
                    status=400)
  try:
    send_email_mailgun(data)
    return response()
  except:
    pass
  try:
    send_email_mandrill(data)
    return response()
  except:
    return response({'error': 'Mail servers are down. Please try again shortly.'},
                    status=500)


def send_email_mailgun(data):
  """ make a post request on mailgun server.
  """
  from_info = data['from_name'] + ' <' + data['from'] + '>'
  to = data['to_name'] + ' <' + data['to'] + '>'
  subject = data['subject']
  text = parse_text(data['body'])
  
  r = requests.post(settings['MAILGUN_HOST'],
                    auth=('API', settings['API_KEY_MAILGUN']),
                    data={'from': from_info,
                          'to': to,
                          'subject':subject ,
                          'text': text}
                    )
  if r.status_code != 200:
    raise Exception(r.text)


def send_email_mandrill(data):
  """ make a post request on mandrill server.
  """
  from_name = data['from_name']
  from_email = data['from']
  to_name = data['to_name']
  to_email = data['to']
  subject = data['subject']
  text = parse_text(data['body'])
  
  payload = {
    'key': settings['API_KEY_MANDRILL'],
    'message': {
      'text': text,
      'subject': subject,
      'from_email': from_email,
      'from_name': from_name,
      'to': [
        {
          'email': to_email,
          'name': to_name,
          'type': 'to'
          }
        ]
      }
    }
  
  r = requests.post(settings['MANDRILL_HOST'],
                    data=json.dumps(payload))
  if r.status_code != 200:
    raise Exception(r.text)


if __name__ == '__main__':
  app.run()
