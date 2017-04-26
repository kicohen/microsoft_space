def event_request_email(name, organization, contact, email, start_date, end_date, location, notes):
	body = '''We have recieved your request.

	--------------------------------------------------
	Event Name: %s
	Organization: %s
	Contact: %s
	Email: %s
	Start Date and Time: %s
	End Date and Time: %s
	Location: %s
	Notes: %s
	--------------------------------------------------

	We will review your request and contact you as soon as possible.
	To provide additional information, please respond to this message.

	Thank you,
	Microsoft Space Staff''' % (name, organization, contact, email, start_date, end_date, location, notes)
	return body

def event_confirmed():
	body = '''Your space request to use the Microsoft Space has been granted. 

In order to access the space, you must pick up an access card from the space. The space has open hours every day except for Friday. These hours can be found on our website or a typical week will have the following hours:
Monday - Thursday: 7:00pm - 11:00pm
Saturday - Sunday: 1:00pm - 7:00pm

Please see the Microsoft Space employee at the Space to pick up your key. After your event is over, please leave the key in the key box in the main room of the space.

If you have any questions or concerns, please contact us by replying to this email. 

Thank you,
Microsoft Space Staff'''
	return body


def event_declined():
	body = '''We are sorry to infrom you that your space request to use the Microsoft Space has been declined. 
This can be for many reasons including:
- The space is already booked
- The event is for non-Carnegie Mellon non-Microsoft use.
- The event is within 24 hours of when it was requested.

We encourage you to reach out to us for more information. 

Thank you,
Microsoft Space Staff'''
	return body
