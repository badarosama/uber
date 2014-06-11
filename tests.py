import unittest

from flask import json

import server
from server import app
app = app.test_client()


def dummy_fail_func(data):
  raise Exception(':(')


class ServerTest(unittest.TestCase):
  def test_message_format(self):
    # Check message to server if valid
    data = {
      'to': 'badarosama@gmail.com',
      'to_name':'Osama',
      'from':'noreply@uber.com',
      'from_name': 'Uber',
      'subject': 'A message from Uber',
      'body': '<h1>your bill</h1><p>$10</p>'
      }
    try:
      server.validate_request(data)
    except:
      self.fail()

  def test_message_format_missing_key(self):
    # Check for missing key in data
    data = {
      'to': 'badarosama@gmail.com',
      'from': 'noreply@uber.com',
      'from_name': 'Uber',
      'subject': 'A message from Uber', 
      'body':'<h1>your bill</h1><p>$10</p>'
      }
    try:
      server.validate_request(data)
      self.fail()
    except Exception, e:
      self.assertTrue('missing' in e.message)
      self.assertTrue('to_name' in e.message)
    
  def test_message_format_addtional_key(self):
    # Check for additional key in data
    data = {
      'key1': 'value1',
      'to': 'badarosama@gmail.com',
      'from': 'noreply@uber.com',
      'to_name': 'Osama',
      'from_name': 'Uber',
      'subject': 'A message from Uber',
      'body': '<h1>your bill</h1><p>$10</p>'
      }
    try:
      server.validate_request(data)
      self.fail()
    except Exception, e:
      self.assertTrue('unknown' in e.message)
      self.assertTrue('key1' in e.message)

  def test_message_format_null_value(self):
    # Check for null value
    data = {
      'to': '',
      'from': 'noreply@uber.com',
      'to_name': 'Osama',
      'from_name': 'Uber',
      'subject': 'A message from Uber',
      'body':'<h1>your bill</h1><p>$10</p>'
      }
    try:
      server.validate_request(data)
      self.fail()
    except Exception, e:
      self.assertTrue('to' in e.message)
      self.assertTrue('null' in e.message)

  def test_text_parsing(self):
    # Check for text to see if html removed.       
    self.assertEqual('your bill  $10',
                     server.parse_text('<h1>your bill</h1><p>$10</p>'))
    self.assertEqual('hello how are you',
                     server.parse_text('<h1><b>hello how are you</b></h1>'))
    self.assertEqual('lolcat', server.parse_text('lolcat'))
    
  def test_send_email_mailgun(self):
    # Send email through mailgun server.       
    data = {
      'to': 'badarosama@gmail.com',
      'from': 'noreply@uber.com',
      'to_name': 'Osama',
      'from_name': 'Uber',
      'subject': 'A message from Uber',
      'body': '<h1>your bill</h1><p>$10</p>'
      }
    try:
      server.send_email_mailgun(data)
    except Exception, e:
      self.fail('%s: %s' % (type(e), getattr(e, 'message', '')))

  def test_send_email_mandrill(self):
    # Send email through mandrill server.
    data = {
      'to': 'badarosama@gmail.com',
      'from': 'noreply@uber.com',
      'to_name': 'Osama',
      'from_name': 'Uber',
      'subject': 'A message from Uber',
      'body': '<h1>your bill</h1><p>$10</p>'
      }
    try:
      server.send_email_mandrill(data)
    except Exception, e:
      self.fail('%s: %s' % (type(e), getattr(e, 'message', '')))

  def test_send_email(self):
    # Send email.
    data = {
      'to': 'badarosama@gmail.com',
      'from': 'noreply@uber.com',
      'to_name': 'Osama',
      'from_name': 'Uber',
      'subject': 'A message from Uber',
      'body': '<h1>your bill</h1><p>$10</p>'
      }
    response = app.post('email', data=json.dumps(data))
    self.assertEqual(response.status, '200 OK')

  def test_send_email_one_service_down(self):
    # Send email through mandrill server.
    data = {
      'to': 'badarosama@gmail.com',
      'from': 'noreply@uber.com',
      'to_name': 'Osama',
      'from_name': 'Uber',
      'subject': 'A message from Uber',
      'body': '<h1>your bill</h1><p>$10</p>'
      }

    # Kill Mailgun.
    send_email_mailgun = server.send_email_mailgun
    server.send_email_mailgun = dummy_fail_func
    response = app.post('email', data=json.dumps(data))
    self.assertEqual(response.status, '200 OK')

    # Restore Mailgun.
    server.send_email_mailgun = send_email_mailgun

    # Kill Mandrill.
    send_email_mandrill = server.send_email_mandrill
    server.send_email_mandrill = dummy_fail_func
    response = app.post('email', data=json.dumps(data))
    self.assertEqual(response.status, '200 OK')

    # Restore Mandrill.
    server.send_email_mandrill = send_email_mandrill

  def test_send_email_both_services_down(self):
    # Send email through mandrill server.
    data = {
      'to': 'badarosama@gmail.com',
      'from': 'noreply@uber.com',
      'to_name': 'Osama',
      'from_name': 'Uber',
      'subject': 'A message from Uber',
      'body': '<h1>your bill</h1><p>$10</p>'
      }

    # Kill both Mailgun & Mandrill.
    send_email_mailgun = server.send_email_mailgun
    server.send_email_mailgun = dummy_fail_func
    send_email_mandrill = server.send_email_mandrill
    server.send_email_mandrill = dummy_fail_func

    response = app.post('email', data=json.dumps(data))
    self.assertEqual(response.status, '500 INTERNAL SERVER ERROR')

    # Restore both.
    server.send_email_mailgun = send_email_mailgun
    server.send_email_mandrill = send_email_mandrill


if __name__ == '__main__':
  unittest.main(verbosity=2)
