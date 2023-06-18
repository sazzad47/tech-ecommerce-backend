from django.core.mail import EmailMultiAlternatives
import os


class Util:
    @staticmethod
    def send_email(data):
        subject = data['subject']
        body = data['body']
        html_body = data['html_body']  # Retrieve the HTML content
        to_email = data['to_email']
        from_email = os.environ.get('EMAIL_FROM')  # Remove the trailing comma

        # Create an EmailMultiAlternatives object
        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        email_message.attach_alternative(html_body, 'text/html')  # Attach the HTML content

        # Send the email
        email_message.send()
