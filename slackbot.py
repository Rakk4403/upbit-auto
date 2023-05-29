from slack_bolt import App
import os

class MySlackBot():
    def __init__(self, token = None, signing_secret = None):
        if token is None:
            token = os.environ['SLACK_BOT_TOKEN']
        if signing_secret is None:
            signing_secret = os.environ['SLACK_SIGNING_SECRET']
        self.app = App(token=token, signing_secret=signing_secret)
        self.client = self.app.client

    def send_message(self, channel, text):
        self.client.chat_postMessage(channel=channel, text=text)
