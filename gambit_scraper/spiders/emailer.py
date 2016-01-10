import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os

from pprint import pprint

from pathlib import Path



import httplib2
from apiclient import discovery, errors
import oauth2client
from oauth2client import client
from oauth2client import tools




class Emailer:

    # try:
    #     import argparse
    #     flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    # except ImportError:
    flags = None

    SCOPES = 'https://www.googleapis.com/auth/gmail'
    CLIENT_SECRET_FILE = 'credentials.json'
    APPLICATION_NAME = 'Gambit Web Scraper'

    def __init__(self):
        self.service = self.main()

    def main(self):
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http)
        return service

    @classmethod
    def get_credentials(cls):

        path_to_parent_directory = Path(__file__).parents[1]

        print(path_to_parent_directory)

        credential_path = str(path_to_parent_directory) + '/credentials.json'

        store = oauth2client.file.Storage(credential_path)

        pprint(store)

        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(cls.CLIENT_SECRET_FILE, cls.SCOPES)
            flow.user_agent = cls.APPLICATION_NAME
            if cls.flags:
                credentials = tools.run_flow(flow, store, cls.flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)

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


