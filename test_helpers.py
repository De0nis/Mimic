import pyautogui
import os
from PIL import Image, ImageChops
import cv2

def make_screenshot(screenshot_no,x,y):
        screenshot = pyautogui.screenshot(region=((x-50),(y-50), 100, 100))
        screenshot.save(f'./screenshots/{screenshot_no}_.png')
        sample = os.path.abspath(f"./screenshots/{screenshot_no}.png")
        img1 = Image.open(f'./screenshots/{screenshot_no}_.png')
        img2 = Image.open(sample)
        if img1.mode != img2.mode:
                img2 = img2.convert(img1.mode)
        diff = ImageChops.difference(img1, img2)
        diff.save(f'./screenshots/{screenshot_no}_diff.png')
        img = cv2.imread(f'./screenshots/{screenshot_no}_diff.png')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        sum_diff_area=0
        for cnt in contours:
                sum_diff_area+=cv2.contourArea(cnt)
        return sum_diff_area
