import threading


from emotinsDetect import Camera_progress

class CameraSet:
    def __init__(self,filename,emotions, img_queue,true_emotions):
        Camera_Thread = threading.Thread(target=Camera_progress, args=(emotions, img_queue,true_emotions, filename))
        Camera_Thread.start()