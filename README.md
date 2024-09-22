# phone_cam
简单的ip摄像头监控程序，包含简单GUI，将手机当作ip监控摄像头使用，手机只作为摄像头方式使用，其他操作pc端完成，达到废旧手机二次利用  
cam_demo、cam_demo2为最原始版本，cam_demo8为比较完善的版本  
使用前提：安卓手机安装《ip Webcam》程序，运行准备调用：下载链接：https://apkpure.com/ip-webcam/com.pas.webcam/downloading  
水果手机自行下载《ip摄像头lite》，因为代码设定问题，需要把分辨率改成640*480.可后续修改代码，提高清晰度！！！  
或者其他方式调用手机摄像头，自行探索。  
可通过代码直接运行，已经打包好的程序演示地址：链接: https://pan.baidu.com/s/14J0o2zkUJ86GYrsbwJ43-A?pwd=CV67 提取码: CV67   
# 环境  
python==3.8  
opencv-python==4.10.0.84  
pillow==10.3.0  
PyAudio==0.2.14  
# 使用方法
同一局域网下，更改自己手机的IP，端口一般默认8080.  
对文件覆盖做了控制：  
self.recording_duration = 300  # 默认300秒  
self.max_files = 30  # 最多保存30个文件  
self.max_size = 4 * 1024 * 1024 * 1024  # 4GB  
![image](https://github.com/user-attachments/assets/3ebd43f6-e846-47da-bfc9-4f038ff6c621)
