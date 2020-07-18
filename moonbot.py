import os
from slack import RTMClient
from slack.errors import SlackApiError

# Below method is run any time a message event occurs
@RTMClient.run_on(event='message')
def say_hello(**payload):
    data = payload['data']
    web_client = payload['web_client']
    rtm_client = payload['rtm_client']
    # Parse the message for string 'Hello'
    if 'text' in data and 'Hello' in data.get('text', []):
        channel_id = data['channel']
        thread_ts = data['ts']
        user = data['user']

        try:
            # Sends a message (as bot).... we can put this anywhere.
            response = web_client.chat_postMessage(
                channel=channel_id,
                text=f"Hi <@{user}>!",
                thread_ts=thread_ts
            )
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")

# SLACK_BOT_TOKEN must be set from terminal using 'export SLACK_BOT_TOKEN='token'
rtm_client = RTMClient(token=os.environ["SLACK_BOT_TOKEN"])
rtm_client.start()
