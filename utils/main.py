import os

TMP_DIR = '/home/orangepi/tmp'
CFG_DIR = os.path.join(TMP_DIR, 'cfg')
if not os.path.exists(CFG_DIR): os.mkdir(CFG_DIR)

IMAGE_DIR = os.path.join(TMP_DIR, 'image')
if not os.path.exists(IMAGE_DIR): os.mkdir(IMAGE_DIR)

VIDEO_DIR = os.path.join(TMP_DIR, 'video')
if not os.path.exists(VIDEO_DIR): os.mkdir(VIDEO_DIR)