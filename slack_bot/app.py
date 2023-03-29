import os
import requests
import logging
import time
from dotenv import load_dotenv
from requests.api import get
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Initializes your app with your bot token and signing secret
app = App(token=os.environ["SLACK_BOT_TOKEN"])

moonraker_url = os.environ["MOONRAKER_URL"]
#webcam_image_url = os.environ["WEBCAM_IMAGE_URL"]

@app.message("test")
def show_printer_status(client, message, say):
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
def file_upload_detection(event, say):
    user_id = event["user"]
    #file_id = event["files"][0]["id"]

    # File type aimed to be binary, mime_type or media type should be "application/octet-stream"
    # Maybe add some if else statement in the future so it only responds to g code rather than any file
    file_type = event["files"][0]["filetype"]
    mime_type = event["files"][0]["mimetype"]

    file_name = event["files"][0]["name"]
    text = f"Hello <@{user_id}>! I see you uploaded a file ({file_name}) 👀🎉."
    say(text)
    url_private = event["files"][0]["url_private"]
    text = f"Download link for moonraker purposes?: <{url_private}>"
    say(text)

    # Downloading and saving file from private link to temporary folder
    say(f"Downloading file and storing into gcode_storage")
    token = os.environ["SLACK_BOT_TOKEN"]
    response = requests.get(url_private, headers={'Authorization': 'Bearer %s' % token})
    #open(f'/home/pi/printer_data/gcodes/pipeline_storage/{file_name}', 'wb').write(response.content)
    open(f'/home/pi/printer_data/gcodes/{file_name}', 'wb').write(response.content)
    # Enqueue said file to printer
    # response = requests.post(f"{moonraker_url}/server/job_queue/job?filenames=pipeline_storage/{file_name}")
    response = requests.post(f"{moonraker_url}/server/job_queue/job?filenames={file_name}")
    say(f"Enqueued, current status: \n {response}")

#"url_private":"https:\/\/files.slack.com\/files-pri\/TRYE87KQB-F04P57VAP9T\/russell_dummy.gcode",
#"url_private_download":"https:\/\/files.slack.com\/files-pri\/TRYE87KQB-F04P57VAP9T\/download\/russell_dummy.gcode"
#"permalink":"https:\/\/uscmakers.slack.com\/files\/U031E28HTL1\/F04P57VAP9T\/russell_dummy.gcode"
#"permalink_public":"https:\/\/slack-files.com\/TRYE87KQB-F04P57VAP9T-5eea892378"

# Prints the job queue status
@app.message("status")
def call_status(client, message, say):
    response = requests.get(f"{moonraker_url}/server/job_queue/status")
    json_data = response.json()
    say(f"{json_data}")


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


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
