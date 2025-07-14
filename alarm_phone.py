from telegram import Bot
import time
from telegram.ext import Updater, MessageHandler, Filters
import os
import io
import cv2
from PIL import Image
from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv
import pyautogui
import next_action

load_dotenv(dotenv_path="keys.env")  
API_TOKEN = os.getenv("API_TOKEN")
CHAT_ID = (os.getenv("CHAT_ID"))
bot = Bot(token=API_TOKEN)
UPDATE_FILE = "update_id.txt"
ai_file = "next_action.txt"
last = "nothing"

def write_new_ai(new):
    global ai_file
    with open(ai_file, "a") as file:
        file.write(f"{new}\n")
def make_and_send_photo():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cam.release()
    if not ret:
        alarm(message="can't make photo")
        return
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    buf = io.BytesIO()
    img_pil.save(buf, format="JPEG")
    buf.seek(0)
    alarm(buf=buf)
def alarm(message=None, buf=None):
    if buf is not None:
        bot.send_photo(chat_id=CHAT_ID, photo=buf)
    if message is not None:
        bot.send_message(chat_id=CHAT_ID, text=message)
def handle_message(update, context):
    print("Received message:", update.message.text)
    try:
        succes = True
        mess = update.message.text
        if mess == "Test":
            alarm(message="Test back!")
        elif mess == "Script/break":
            alarm(message="exit...")
            os._exit(0)
        elif mess == "Script/photo":
            with open("makephoto.txt", "w") as f:
                f.write("1")
            alarm(message="photo making started")
        elif mess == "Script/alarm":
            print("_ALARM_SOUND_")
            sound = AudioSegment.from_file("alarm.wav", format="wav")
            play(sound)
        elif mess == "Script/script":
            with open("alarm_phone.py", "r") as file:
                file_r = file.read()
                alarm(message=file_r)
        elif mess == "Script/music":
            sound = AudioSegment.from_file("alarm_music_wtf.wav", format="wav")
            play(sound)
        elif mess == "Script/light":
            for _ in range(100):
                pyautogui.press('capslock')
        elif "Script/exec/" in mess:
            mess = mess.replace("Script/exec/", "").strip()
            print(f"EXEC COMMAND- {mess}")
            alarm(message="executing command")
            try:
                result = eval(mess)
                print(result) 
                alarm(message=str(result))
            except Exception as e:
                print("Error:", e)
                alarm(message=f"Error: {e}")
                succes = False
        elif "A/" in mess and "A/new/" not in mess:
            mess = mess.replace("A/", "")
            mess = mess.replace("?", "")
            mess = mess.replace("!", "")
            mess = mess.replace(".", "").lower()
            print(mess)
            answer = next_action.main(vraag=mess)
            print(answer)
            alarm(message=answer)
            global ai_file
            with open(ai_file, "r") as file:
                f = file.read()
                #TODO: make memory AI in memory_Action.txt
                if mess not in f:
                    alarm(message="good message?\ntype A/new/last/")
                    global last
                    last = f"{mess}:{answer}"
        elif "A/new/" in mess:
            if "A/new/last/":
                print(f"{last} LAST IN TO FILE")
                write_new_ai(f"{last}")
            else:
                mess = mess.replace("A/new/", "")
                write_new_ai(mess) 
        else:
            succes = False
            alarm(message=f"'{mess}' is not a command")
        if succes:
            alarm("succes")
        else:
            alarm("failed")
    except KeyboardInterrupt:
        alarm(message="broke program by server user")
        print("quit")
        os._exit(0)
    except Exception as e:
        print(f"error {e}")
        alarm(message=f"error: {e}")
def run_handle():
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()