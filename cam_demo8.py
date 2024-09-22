import cv2
import tkinter as tk
from tkinter import Label, Button, Entry, StringVar, scrolledtext, filedialog
from PIL import Image, ImageTk
import os
import datetime
import pyaudio
import wave
import threading


class CameraApp:
    def __init__(self, master):
        self.master = master
        self.master.title("监控程序")

        # IP地址输入
        # self.ip_var = StringVar(value="http://<your_phone_ip>:<port>/video")  # 默认IP地址
        # self.ip_label = Label(master, text="摄像头 IP 地址:")
        # self.ip_label.pack()
        # self.ip_entry = Entry(master, textvariable=self.ip_var)
        # self.ip_entry.pack()

        # IP地址和端口输入
        self.ip_var = StringVar(value="192.168.0.105")  # 默认IP地址（调试用）
        self.port_var = StringVar(value="8080")  # 默认端口

        self.ip_label = Label(master, text="摄像头 IP 地址:")
        self.ip_label.pack()
        self.ip_entry = Entry(master, textvariable=self.ip_var)
        self.ip_entry.pack()

        self.port_label = Label(master, text="端口:")
        self.port_label.pack()
        self.port_entry = Entry(master, textvariable=self.port_var)
        self.port_entry.pack()

        # 时间戳显示
        self.timestamp_var = StringVar()
        self.timestamp_label = Label(master, textvariable=self.timestamp_var)
        self.timestamp_label.pack()

        self.label = Label(master)
        self.label.pack()

        # 日志显示框
        #
        self.log_text = scrolledtext.ScrolledText(master, height=5, width=60,font=("Arial", 10),bg="lightblue",fg="blue") # 设置字体
        # self.log_text = scrolledtext.ScrolledText(master, height=5, width=60,font=("Arial", 10),bg="lightblue",fg="blue")
        self.log_text.pack()
        self.log_text.insert(tk.END, "日志记录:\n")

        # 默认参数
        self.recording_duration = 300  # 默认300秒
        self.max_files = 30  # 最多保存30个文件
        self.max_size = 4 * 1024 * 1024 * 1024  # 4GB
        self.video_folder = os.getcwd()  # 默认为当前工作路径
        self.video_folder_label = Label(master, text="视频保存路径:")
        self.video_folder_label.pack()
        self.video_folder_entry = Entry(master, width=50)   # 设置宽度
        self.video_folder_entry.pack()
        self.video_folder_entry.insert(0, self.video_folder)

        Button(master, text="选择路径", command=self.select_folder).pack()

        # 输入框和按钮
        self.duration_label = Label(master, text="录像时长（秒）：")
        self.duration_label.pack()
        self.duration_entry = Entry(master)
        self.duration_entry.pack()
        self.duration_entry.insert(0, f"{self.recording_duration}")

        button_frame = tk.Frame(master)
        button_frame.pack()

        Button(button_frame, text="拍照", command=self.take_photo).pack(side=tk.LEFT)
        Button(button_frame, text="开始录像", command=self.start_recording).pack(side=tk.LEFT)
        Button(button_frame, text="停止录像", command=self.stop_recording).pack(side=tk.LEFT)
        Button(button_frame, text="开始录音", command=self.start_audio_recording).pack(side=tk.LEFT)
        Button(button_frame, text="停止录音", command=self.stop_audio_recording).pack(side=tk.LEFT)
        Button(button_frame, text="双向通话", command=self.start_voice_call).pack(side=tk.LEFT)

        self.capture = None
        self.is_recording = False
        self.output = None
        self.audio_thread = None
        self.audio_recording = False

        self.update_timestamp()
        self.update()

    # 更新摄像头画面

    def update(self):

        if self.capture is not None:
            ret, frame = self.capture.read()
            if ret:
                # frame = cv2.resize(frame, (640, 480))  # 调整大小
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.label.imgtk = imgtk
                self.label.configure(image=imgtk, width=320, height=240)

                # 录制时将帧写入文件
                if self.is_recording and self.output is not None:
                    self.output.write(frame)

        self.master.after(10, self.update) # 每10毫秒更新一次

    def take_photo(self):
        if self.capture is not None:
            ret, frame = self.capture.read()
            if ret:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                photo_path = os.path.join(self.video_folder, f"photo_{timestamp}.jpg")
                cv2.imwrite(photo_path, frame)
                self.log(f"拍照成功，保存为 {photo_path}")

    def manage_files(self):
        """管理视频文件，检查数量和大小"""
        files = [f for f in os.listdir(self.video_folder) if f.endswith('.avi')]
        if len(files) >= self.max_files or self.get_folder_size() >= self.max_size:
            files.sort(key=lambda f: os.path.getctime(os.path.join(self.video_folder, f)))
            os.remove(os.path.join(self.video_folder, files[0]))  # 删除最旧文件
            self.log("已删除旧录像文件")

    def get_folder_size(self):
        """获取视频文件夹的总大小"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.video_folder):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def start_recording(self):
        """开始录像"""
        if not self.is_recording:
            # 获取用户输入的录像时长
            try:
                self.recording_duration = int(self.duration_entry.get())
            except ValueError:
                self.log("请输入有效的录像时长")
                return
                # 获取IP地址和端口
            ip_address = self.ip_var.get()  # 获取IP地址
            port = self.port_var.get()  # 获取端口
            url = f"http://{ip_address}:{port}/video"   # 视频流地址
            # 获取IP地址并打开视频流
            self.capture = cv2.VideoCapture(url)    # 打开视频流
            if not self.capture.isOpened():
                self.log("无法打开视频流")
                return

            self.is_recording = True
            self.start_new_recording()  # 开始新的录像

    def start_new_recording(self):
        """启动新一段录像"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = os.path.join(self.video_folder, f"video_{timestamp}.avi")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')

        try:
            self.output = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480)) # 20.0 fps
            self.log(f"开始录像，保存为 {video_path}")

        except Exception as e:
            self.log(f"无法开始录像: {e}")
            self.is_recording = False
            return

        # 启动定时器管理录像
        threading.Timer(self.recording_duration, self.finish_recording).start()

    def finish_recording(self):
        """结束当前录像并自动开始下一个"""
        if self.is_recording:
            self.output.release()
            self.output = None
            self.log("当前录像结束")

            self.manage_files()  # 检查文件管理

            # 继续下一个录像
            self.start_new_recording()

    def stop_recording(self):
        """停止录像"""
        if self.is_recording:
            self.is_recording = False
            if self.output is not None:
                self.output.release()
                self.output = None
            # self.capture.release()  # 释放摄像头

            # self.capture = None # 关闭视频流
            self.log("停止录像")

    def start_audio_recording(self):
        """开始录音"""
        if not self.audio_recording:
            self.audio_recording = True
            self.audio_thread = threading.Thread(target=self.record_audio)
            self.audio_thread.start()
            self.log("开始录音")

    def stop_audio_recording(self):
        """停止录音"""
        self.audio_recording = False
        self.log("停止录音")

    def record_audio(self):
        """录音功能"""
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        WAVE_OUTPUT_FILENAME = os.path.join(self.video_folder,
                                            f"audio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")

        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        frames = []

        while self.audio_recording:
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        self.log(f"音频保存为 {WAVE_OUTPUT_FILENAME}")

    def select_folder(self):
        """选择视频保存路径"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.video_folder = folder_selected
            self.video_folder_entry.delete(0, tk.END)
            self.video_folder_entry.insert(0, self.video_folder)
            self.log(f"已选择视频保存路径: {self.video_folder}")

    def start_voice_call(self):
        """双向通话功能，待实现"""
        self.log("双向通话功能需要额外配置")

    def update_timestamp(self):
        """更新时间戳"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_var.set(current_time)
        self.master.after(1000, self.update_timestamp)  # 每秒更新一次

    def log(self, message):
        """记录日志信息"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"{current_time}: {message}\n")
        self.log_text.yview(tk.END)  # 滚动到最新的日志

    def __del__(self):
        """清理资源"""
        if self.capture.isOpened():
            self.capture.release()
        if self.is_recording and self.output is not None:
            self.output.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
