import os



TMP_DIR = '/home/orangepi/tmp'
TMP_IMAGE_DIR = TMP_DIR + '/images'
TMP_IMAGE_PATH = TMP_IMAGE_DIR + '/tmp.jpg'
if not os.path.exists(TMP_IMAGE_DIR): os.makedirs(TMP_IMAGE_DIR)