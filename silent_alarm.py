import cv2
import pygame
import alarm_phone
import time
import io
from PIL import Image
import threading
import os

pygame.mixer.init()
last_alarm_time = 0 
cooldown = 5       
pending_alarm = False
alarm_trigger_time = 0
frames_folder = "frames"
video_filename = "output.avi"
frame_count_limit = 3
fps = 1

cam = cv2.VideoCapture(0)
ret, frame1 = cam.read()
frame1_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
frame1_gray = cv2.GaussianBlur(frame1_gray, (21, 21), 0)
stop_event = threading.Event()
thread_messages = threading.Thread(target=alarm_phone.run_handle)
thread_messages.start()

def get_times():
    t = time.localtime()
    return f"month: {t.tm_mon}\nday: {t.tm_mday}\nhour: {t.tm_hour}\nminute: {t.tm_min}\nsecond: {t.tm_sec}"
def send_snapshot(frame):
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    buf = io.BytesIO()
    img_pil.save(buf, format="JPEG")
    buf.seek(0)
    alarm_phone.alarm(buf=buf)
for _ in range(999999999999999999999999999):
    ret, frame2 = cam.read()
    if not ret:
        break
    frame2_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    frame2_gray = cv2.GaussianBlur(frame2_gray, (21, 21), 0)
    diff = cv2.absdiff(frame1_gray, frame2_gray)
    thresh = cv2.threshold(diff, 15, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    movement_detected = any(cv2.contourArea(c) >= 1000 for c in contours)
    for contour in contours:
        if cv2.contourArea(contour) < 1000:
            continue
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame2, (x, y), (x + w, y + h), (0, 255, 0), 2)
    current_time = time.time()
    if movement_detected and (current_time - last_alarm_time) > cooldown and not pending_alarm:
        alarm_trigger_time = current_time + 0.5
        pending_alarm = True
        print("|0.5", end="|", flush=True)
    elif pending_alarm and current_time >= alarm_trigger_time:
        times_now = get_times()
        print(f"_ALARM_{times_now}", end="_", flush=True)
        alarm_phone.alarm(times_now)
        send_snapshot(display_frame)
        last_alarm_time = current_time
        pending_alarm = False
    elif movement_detected:
        print("|C", end="|", flush=True)
    t = time.localtime()
    night_mode = t.tm_hour >= 22
    display_frame = frame2.copy()
    if night_mode:
        display_frame = cv2.convertScaleAbs(display_frame, alpha=4.5, beta=99)
        cv2.putText(display_frame, "NIGHT MODE", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    gray_display = cv2.cvtColor(display_frame, cv2.COLOR_BGR2GRAY)
    gray_display = cv2.equalizeHist(gray_display)
    cv2.imshow("alarm camera", gray_display)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break
    frame1_gray = frame2_gray.copy()
    if os.path.exists("makephoto.txt"):
        os.remove("makephoto.txt")  
        send_snapshot(display_frame)
        alarm_phone.alarm("made photo")
stop_event.set()
thread_messages.join()
cam.release()
cv2.destroyAllWindows()