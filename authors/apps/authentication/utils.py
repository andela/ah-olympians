import sendgrid
import os
from sendgrid.helpers.mail import *


def send_email(to_email, subject, message):
    """This function is used to send email.
    Takes in email_to, subject, message as parameters

    :param to_email: person to be sent email
    :param subject: subject of the email
    :param message: message of the email
    :return: a message, success or fail
    """
    sg = sendgrid.SendGridAPIClient(apikey=os.getenv("SENDGRID_API_KEY"))
    from_email = Email(os.getenv("EMAIL_FROM"))
    to_email = Email(to_email)
    subject = subject
    content = Content("text/plain", message)
    try:
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        # response code 202 ensures the message is sent
        if response.status_code is not 202:
            return "email not sent check your api key and email from"
        return "email sent"
    except Exception:
        return "There was an error sending"


def verify_message(name, token):
    message = "Thank you " + name + " for registering with us please verify your email\n" \
                                    " by clicking on the following link\n" \
              + os.getenv("URL") + "/verify/" + token + "\n Welcome"

    return message
