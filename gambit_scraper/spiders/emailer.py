import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os


import httplib2
from apiclient import discovery, errors
import oauth2client
from oauth2client import client
from oauth2client import tools


class Emailer:

    def __init__(self):
        self.service = self.main()

    def main(self):
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http)
        return service

    @classmethod
    def get_credentials(cls):
        parent_directory = os.path.dirname(os.path.abspath(__file__))
        credentials_directory_path  = parent_directory + 'credentials.json'

        store = oauth2client.file.Storage(credentials_directory_path)

        credentials = store.get()
        return credentials

    @classmethod
    def create_message(cls, sender, to, subject, message_text):
        """Create a message for an email.

        Args:
          sender: Email address of the sender.
          to: Email address of the receiver.
          subject: The subject of the email message.
          message_text: The text of the email message.

        Returns:
          An object containing a base64url encoded email object.
        """
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_string())}

    def create_draft(self, user_id, message_body):
        """Create and insert a draft email. Print the returned draft's message and id.

        Args:
          service: Authorized Gmail API service instance.
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          message_body: The body of the email message, including headers.

        Returns:
          Draft object, including draft id and message meta data.
        """
        try:
            message = {'message': message_body}
            draft = self.service.users().drafts().create(userId=user_id, body=message).execute()

            print 'Draft id: %s\nDraft message: %s' % (draft['id'], draft['message'])

            return draft

        except errors.HttpError, error:
            print 'An error occurred: %s' % error
            return None


