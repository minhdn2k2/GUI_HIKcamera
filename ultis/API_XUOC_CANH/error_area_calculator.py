import cv2
import os
import shutil
import numpy as np

class ErrorAreaCalculator:
    def __init__(self):
        pass

    def calc_error_area_img(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        img_blur = cv2.GaussianBlur(img_gray,(3,3),0)

        ret, img_th = cv2.threshold(img_blur,0,255,cv2.THRESH_BINARY + 
                                            cv2.THRESH_OTSU)

        cnt_white = self.count_white_pixels(img_th)

        return img_th, cnt_white

    def calc_error_area_imgs(self, images_root):
        pass

    def enhance_contrast_img(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # clahe = cv2.createCLAHE()
        # img_contrast = clahe.apply(img_gray) + 60

        return cv2.equalizeHist(img_gray)
    
    def count_white_pixels(self, img):
        count = np.count_nonzero(img > 127)
        return count
    
    def count_pixel_difference(self, img_gray):
        cnt = 0
        for i in range(img_gray.shape[0]):
            for j in range(img_gray.shape[1]):
                # print(img_gray[i][j])
                if img_gray[i][j] not in [0, 255]:
                    cnt += 1

        return cnt
        