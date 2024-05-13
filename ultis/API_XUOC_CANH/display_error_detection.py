import cv2
import os
import shutil
from time import time
import numpy as np
from ultralytics import YOLO
from tqdm import tqdm
from libs.API_XUOC_CANH.error_area_calculator import *
from libs.API_XUOC_CANH.params import MASH_POINTS



class DisplayErrorModel:
    def __init__(self):
        self.error_area_calculator = ErrorAreaCalculator()
        self.error_detection_model = YOLO('libs/API_XUOC_CANH/detect_model/best_norm_n.pt')
        self.device = 'cpu'
        self.ignore_tiles = [5, 6, 9, 10]

    def restoration_img(self, img):
        img_restoration = self.restoration_model.restotation_card_end2end(img)
        return img_restoration
    
    def resize_img(self, img, scale=2):
        img = cv2.resize(img, (img.shape[1]*2, img.shape[0]*2))
        return img

    def crop_tiles_img(self, img):
        height, width = img.shape[:2]

        # Calculate the amount of padding needed to make the width and height divisible by 640
        pad_bottom = int((640 - height % 640)/2)
        pad_right = int((640 - width % 640)/2)

        # Create a black image of size (height + pad_bottom, width + pad_right)
        padded_img = cv2.copyMakeBorder(img, pad_bottom, pad_bottom, pad_right, pad_right, cv2.BORDER_CONSTANT, value=(0, 0, 0))

        # Get the height and width of the padded image
        height, width = padded_img.shape[:2]

        # Define the size of the tiles
        tile_size = 640

        tiles = []

        # Loop through the padded image and split it into tiles
        for i in tqdm(range(0, height, tile_size)):
            for j in range(0, width, tile_size):
                tile = padded_img[i:i+tile_size, j:j+tile_size]
                tiles.append(tile)

        return tiles
    
    def infer_detect_error(self, tiles, area):
        tiles_predicted = []
        num = 0
        for i, tile in enumerate(tqdm(tiles)):
            if i not in self.ignore_tiles:
                results = self.error_detection_model(tile, imgsz=640, conf=0.4, iou=0.9, device=self.device, max_det=2000, verbose=False)
                boxes = results[0].boxes.xyxy.cpu().numpy().tolist()
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box)

                    box_error = tile[y1:y2, x1:x2]
                    _, cnt_white = self.error_area_calculator.calc_error_area_img(box_error)

                    if cnt_white > area:
                        tile = cv2.rectangle(tile, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        num+=1

            tiles_predicted.append(tile)
        return tiles_predicted, num

    def merge_tiles(self, tiles):
        cnt = 0

        total_img = np.zeros((0, 2560, 3), dtype=np.uint8)
        for i in tqdm(range(0, 1920 + 640, 640)):
            row_img = np.zeros((640, 0, 3), dtype=np.uint8)
            for j in range(0, 1920 + 640, 640):
                img = tiles[cnt]
                row_img = cv2.hconcat([row_img, img])
                cnt += 1
            total_img = cv2.vconcat([total_img, row_img])

        return total_img

    
    def detect_error_end2end(self, img, area):
        
        tiles = self.crop_tiles_img(img)
        tiles_predicted, num = self.infer_detect_error(tiles, area)
        img_result = self.merge_tiles(tiles_predicted)
        img_final = img_result[256:2304, 56:2504]

        return img_final, num
    
    
