import cv2
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
import os
import datetime


class CameraApp:
    def __init__(self, master):
        self.master = master
        self.master.title("监控程序")
        self.label = Label(master)
        self.label.pack()

        self.capture = cv2.VideoCapture("http://192.168.0.105:8080/video")  # 替换为你的URL
        if not self.capture.isOpened():
            print("无法打开视频流")
            return

        self.is_recording = False
        self.output = None

        Button(master, text="拍照", command=self.take_photo).pack()
        Button(master, text="开始录像", command=self.start_recording).pack()
        Button(master, text="停止录像", command=self.stop_recording).pack()

        self.update()

    def update(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)

            if self.is_recording and self.output is not None:
                self.output.write(frame)

        self.master.after(10, self.update)

    def take_photo(self):
        ret, frame = self.capture.read()
        if ret:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            photo_path = f"photo_{timestamp}.jpg"
            cv2.imwrite(photo_path, frame)
            print(f"拍照成功，保存为 {photo_path}")

    def start_recording(self):
        if not self.is_recording:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            video_path = f"video_{timestamp}.avi"
            self.output = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))
            self.is_recording = True
            print(f"开始录像，保存为 {video_path}")

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.output.release()
            self.output = None
            print("停止录像")

    def __del__(self):
        if self.capture.isOpened():
            self.capture.release()
        if self.is_recording and self.output is not None:
            self.output.release()


if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
