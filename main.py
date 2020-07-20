import math
from objects import *
import os
from slack import RTMClient
from slack.errors import SlackApiError

def runMockMission():
  #operator command testing
  #moonRanger.push_waypoint(10,20,2,"far east")
  #moonRanger.push_waypoint(18,2,2,"southern region")
  #moonRanger.drive_trek()
  #moonRanger.map.printMap(moonRanger.map.driveRecord)
  #moonRanger.get_telemetry_log()
  #moonRanger.get_nss_data()
  #print(moonRanger.checkSolarEff())
  #moonRanger.get_solar_status()
  #moonRanger.get_battery_status()
  #print(moonRanger.get_comm_status())

  # SLACK_BOT_TOKEN must be set from terminal using 'export SLACK_BOT_TOKEN='token'
  # Start slack bot client
  rtm_client = RTMClient(token=os.environ["SLACK_BOT_TOKEN"])
  rtm_client.start()

# Below method is run any time a message event occurs
@RTMClient.run_on(event='message')
def parse_command(**payload):
    data = payload['data']
    web_client = payload['web_client']
    rtm_client = payload['rtm_client']
    # Parse the message for string 'Hello'
    if 'text' in data:
        channel_id = data['channel']
        user = data['user']
        if 'get_comm_status' in data.get('text', []):
            response = moonRanger.get_comm_status()
        elif 'get_nss_data' in data.get('text', []):
            response = moonRanger.get_nss_data()
        elif 'get_telemetry_log' in data.get('text', []):
            response = moonRanger.get_telemetry_log()
        elif 'get_solar_status' in data.get('text', []):
            response = moonRanger.get_solar_status()
        elif 'get_battery_status' in data.get('text', []):
            response = moonRanger.get_battery_status()
        elif 'push_waypoint' in data.get('text', []):
            params = data.get('text', []).split()
            response = moonRanger.push_waypoint(int(params[1]), int(params[2]), int(params[3]), params[4])
        elif 'clear_trek' in data.get('text', []):
            response = moonRanger.clear_trek()
        elif 'charge_to_full' in data.get('text', []):
            response = moonRanger.charge_to_full()
        elif 'charge_to_percent' in data.get('text', []):
            params = data.get('text', []).split()
            response = moonRanger.charge_to_percent(int(params[1]))
        elif 'drive_trek' in data.get('text', []):
            response = moonRanger.drive_trek()

        try:
            # Sends a message (as bot).... we can put this anywhere.
            response = web_client.chat_postMessage(
                channel=channel_id,
                text=response,
            )
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")

#create a lander, rover, NSS
moonRanger = Rover()
nss = NSS()
x1 = Lander()
testMap = Map()
testMap.sunAngle = 135
moonRanger.nSystem = nss
moonRanger.lander = x1
moonRanger.map = testMap
#just combines the path driven view with the obstacle view
moonRanger.map.addObstaclesToRecord() 

runMockMission()
