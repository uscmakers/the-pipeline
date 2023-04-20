import os
import requests
import logging
import time
import datetime
from dotenv import load_dotenv
from requests.api import get
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import time

load_dotenv()

# logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Initializes your app with your bot token and signing secret
app = App(token=os.environ["SLACK_BOT_TOKEN"])
user_app = App(token=os.environ["SLACK_USER_TOKEN"])

moonraker_url = os.environ["MOONRAKER_URL"]
webcam1_image_url = os.environ["WEBCAM1_IMAGE_URL"]
webcam2_image_url = os.environ["WEBCAM2_IMAGE_URL"]

def make_img_url():
  response1 = requests.get(webcam1_image_url)
  filename1 = "printer_image1.jpg"
  response2 = requests.get(webcam2_image_url)
  filename2 = "printer_image2.jpg"
  file = open(filename1, "wb")
  file.write(response1.content)
  file.close()
  file = open(filename2, "wb")
  file.write(response2.content)
  file.close()
  return filename1, filename2

def get_gcode_metadata(gcode_filename):
  response = requests.get(f"{moonraker_url}/server/database/item?namespace=gcode_metadata")
  json_data = response.json()["result"]["value"][gcode_filename]
  # logger.error(json_data)
  return json_data

def get_moonraker_status():
  response = requests.get(f"{moonraker_url}/printer/objects/query?gcode_move&toolhead&extruder=target,temperature&extruder1=target,temperature&display_status&mcu&heaters&system_stats&fan&extruder&extruder1&heater_bed&print_stats")
  json_data = response.json()["result"]["status"]
  # json_data["metadata"] = get_gcode_metadata(json_data['print_stats']['filename'])
  #logger.error(json_data)
  return json_data

@app.message("test")
def show_printer_status(client, message, say):
    response = requests.get(f"{moonraker_url}/printer/objects/list")
    print(response.json())
    block = [
        {
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "action_id": "sl_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Placeholder text for single-line input"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Label"
            },
            "hint": {
                "type": "plain_text",
                "text": "Hint text"
            }
        },
        {
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "action_id": "ml_input",
                "multiline": True,
                "placeholder": {
                    "type": "plain_text",
                    "text": "Placeholder text for multi-line input"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Label"
            },
            "hint": {
                "type": "plain_text",
                "text": "Hint text"
            }
        }
    ]
    
    client.chat_postMessage(
    channel=message["channel"],
    # thread_ts=message_ts,
    text="Printer actions",
    blocks=block
    # You could also use a blocks[] array to send richer content
    )

    # When a user shares a file triggers the message+file_share event. (https://api.slack.com/events/message/file_share)
@app.event({'type': 'message', 'subtype': 'file_share'})
def file_upload_detection(client, message, event, say):
    file_name = event["files"][0]["name"]
    # Check if the shared file is a G-code file
    if file_name.endswith(".gcode"):
        # # Send confirmation message with buttons
        # say({
        #     "text": "Do you want to confirm the print interface?",
        #     "attachments": [
        #         {
        #             "text": "",
        #             "fallback": "You are unable to confirm the print interface.",
        #             "callback_id": "print_interface",
        #             "color": "#3AA3E3",
        #             "attachment_type": "default",
        #             "actions": [
        #                 {
        #                     "name": "confirm",
        #                     "text": "Yes",
        #                     "type": "button",
        #                     "value": "confirm"
        #                 },
        #                 {
        #                     "name": "cancel",
        #                     "text": "No",
        #                     "type": "button",
        #                     "value": "cancel"
        #                 }
        #             ]
        #         }
        #     ]
        #})

        user_id = event["user"]
        #file_id = event["files"][0]["id"]

        # File type aimed to be binary, mime_type or media type should be "application/octet-stream"
        # Maybe add some if else statement in the future so it only responds to g code rather than any file
        file_type = event["files"][0]["filetype"]
        mime_type = event["files"][0]["mimetype"]


        file_name = event["files"][0]["name"]
        text = f"Hello <@{user_id}>! I see you uploaded a gcode file ({file_name}) 👀🎉."
        say(text)
        url_private_download = event["files"][0]["url_private_download"]
        # text = f"Download link for moonraker purposes?: <{url_private_download}>"
        # say(text)
        
        # Downloading and saving file from private link to temporary folder
        say(f"Downloading file and storing into gcode_storage")
        token = os.environ["SLACK_BOT_TOKEN"]
        response = requests.get(url_private_download, headers={'Authorization': 'Bearer %s' % token})
        #open(f'/home/pi/printer_data/gcodes/pipeline_storage/{file_name}', 'wb').write(response.content)
        open(f'/home/pi/printer_data/gcodes/{file_name}', 'wb').write(response.content)
        # Enqueue said file to printer
        # response = requests.post(f"{moonraker_url}/server/job_queue/job?filenames=pipeline_storage/{file_name}")
        response = requests.post(f"{moonraker_url}/server/job_queue/job?filenames={file_name}")
        say(f"Enqueued, current status: \n {response}")

@app.message("demo")
def slack_demo(client, message, say):
    requests.post(f"{moonraker_url}/printer/gcode/script?script=DEMO")
    say(":printer: Demo Initiated!")

    url = moonraker_url
    myobj = {
    "jsonrpc": "2.0",
    "method": "printer.gcode.script",
    "params": {
        "script": "demo"
    },
    "id": 7125}

    x = requests.post(url, json = myobj)
    say(":printer: POST request sent")

@app.message("estop")
def emergency_stop(client, message, say):
    requests.post(f"{moonraker_url}/printer/emergency_stop")
    say(":printer: :octagonal_sign:   Print Stopped")

@app.action("printer_action_pause")
def approve_request(ack, say):
    # Acknowledge action request
    ack()
    requests.post(f"{moonraker_url}/printer/print/pause")
    say(":printer: :double_vertical_bar:  Print Paused")

@app.action("printer_action_resume")
def approve_request(ack, say):
    # Acknowledge action request
    ack()
    requests.post(f"{moonraker_url}/printer/print/resume")
    say(":printer: :black_right_pointing_triangle_with_double_vertical_bar: Print Resumed")

@app.action("printer_action_cancel")
def approve_request(ack, say):
    # Acknowledge action request
    ack()
    requests.post(f"{moonraker_url}/printer/print/cancel")
    say(":printer: :x:   Print Cancelled")

@app.action("printer_action_stop")
def approve_request(ack, say):
    # Acknowledge action request
    ack()
    requests.post(f"{moonraker_url}/printer/emergency_stop")
    say(":printer: :octagonal_sign:   Print Stopped")

@app.message("status")
def show_printer_status(client, message, say):

    pd = get_moonraker_status()
    print_time = time.strftime('%-H:%M', time.gmtime(pd["print_stats"]["print_duration"]))
    actual_time = time.strftime('%-H:%M', time.gmtime(pd["print_stats"]["total_duration"]))
    # total_time = time.strftime('%-H:%M', time.gmtime(pd["metadata"]["estimated_time"]))
    # remaining_time = time.strftime('%-H:%M', time.gmtime(pd["metadata"]["estimated_time"] - pd["print_stats"]["print_duration"]))
    percent_complete = int(100 * pd['display_status']['progress'])


def home_block():
  # body of the view
  status = get_moonraker_status()
  queue = requests.get(f"{moonraker_url}/server/job_queue/status").json()
  queue_state = queue["result"]["queue_state"]
  named_tuple = time.localtime() # get struct_time
  time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
  block = [
    {
			"type": "section",
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Refresh"
				},
				"value": "Refresh",
				"action_id": "refresh-home"
			},
			"text": {
				"type": "mrkdwn",
				"text": f"Last refresh: {time_string}"
			}
		},
    {
      "type": "divider"
    },
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "Job queue:"
      }
    },
    {
      "type": "divider"
    },
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "Status:"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f":syringe::thermometer:Left Extruder Temperature   : {round(status['extruder']['temperature'])}°"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f":syringe::thermometer:Right Extruder Temperature : {round(status['extruder1']['temperature'])}°"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f":bed::thermometer:Bed Temperature                   : {round(status['heater_bed']['temperature'])}°"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f":round_pushpin:Position                                        : x:{round(status['toolhead']['position'][0])} y:{round(status['toolhead']['position'][1])} z:{round(status['toolhead']['position'][2],3)}mm"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": ":clock3:Time Remaining                           : "
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": ":cyclone:Fan Speed:                                    : "
      }
    },
    {
      "type": "divider"
    }
  ]

  for x in reversed(range(len(queue['result']['queued_jobs']))):
    time_added = time.localtime(queue['result']['queued_jobs'][x]['time_added'])
    time_formatted = time.strftime("%Y-%m-%d %H:%M:%S", time_added)
    filename = queue['result']['queued_jobs'][x]['filename']
    # job_id exists for future comparisons
    job = {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"Filename: {filename}\nTime_added: {time_formatted}"
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "❌"
				},
				"value": "click_me_123",
				"action_id": "button-action"
			}
		}
    block.insert(3,job)
  
  return block

@app.action("refresh-home")
def update_home_tab(client, body, ack):
  try:
    ack()
    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
      # the user that opened your app's app home
      user_id=body["user"]["id"],
      # the view object that appears in the app home
      view={
        "type": "home",
        "callback_id": "home_view",
        "blocks": home_block(),
      }
    )
  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")

@app.event("app_home_opened")
def update_home_tab(client, event, logger):
  try:
    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
      # the user that opened your app's app home
      user_id=event["user"],
      # the view object that appears in the app home
      view={
        "type": "home",
        "callback_id": "home_view",
        "blocks": home_block(),
      }
    )
  
  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
