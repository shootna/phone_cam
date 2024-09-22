import cv2
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk


class CameraApp:
    def __init__(self, master):
        self.master = master
        self.master.title("监控程序")
        self.label = Label(master)
        self.label.pack()

        self.capture = cv2.VideoCapture("http://<phone_ip>:<port>/video")  # 替换为你的URL
        if not self.capture.isOpened():
            print("无法打开视频流")
            return

        self.update()

    def update(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)
        else:
            print("无法读取视频帧")
        self.master.after(10, self.update)

    def __del__(self):
        if self.capture.isOpened():
            self.capture.release()


if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
