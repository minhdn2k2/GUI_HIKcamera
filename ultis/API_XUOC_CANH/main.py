import cv2
import os
import shutil
from time import time
from display_error_detection import *
import warnings
warnings.filterwarnings("ignore") 

#display_error_detection_model = DisplayErrorModel(res_tile=200) # for restoration (low speed). decrease res_tile if out of memory
display_error_detection_model = DisplayErrorModel() # for not restoration (high speed)

image_path = os.path.join('datasets', 'test_data', 'anh2.png')
output_path = os.path.join('datasets', 'output')

if __name__ == '__main__':
    try:
        shutil.rmtree(output_path)
    except:
        pass
    os.mkdir(output_path)

    img = cv2.imread(image_path)

    img_result = display_error_detection_model.detect_error_end2end(img)

    cv2.imwrite(os.path.join(output_path, 'final_img.jpg'), img_result)
