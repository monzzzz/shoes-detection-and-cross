import easyocr
import cv2
import numpy as np
import re

def easy_ocr(image, filename, prob=0.5):
    reader = easyocr.Reader(['th'])
    results = reader.readtext(image)
    shoes_dict = {"name": filename, "detail": []}
    for result in enumerate(results):
        check = True
        text = re.sub(r'\s+', '', result[1][1]).strip()
        for char in text:
            if ord(char) < 0x0E00 or ord(char) > 0x0E7F:
                check = False
                break
        if (result[1][2] > prob and check):
            shoes_dict["detail"].append({"name": filename ,"color": text, "prob": result[1][2]})
    return shoes_dict

def pre_process_image(image, invert=False, rescale=False, binarize=False, denoise=False, thin_font=False, thick_font=False):
    if invert:
        image = invert_image(image)
    if rescale:
        image = rescale_image(image)
    if binarize:
        image = binarize_image(image)
    if denoise:
        image = denoise_image(image)
    if thin_font:
        image = thin_font(image)
    if thick_font:
        image = thick_font(image)
    return image


def invert_image(image):
    inverted_image = cv2.bitwise_not(image)
    return inverted_image 

def rescale_image(image):
    width = image.shape[1]
    height = image.shape[0]
    resized_image = cv2.resize(image, ( width + 1000, height + 400))
    return resized_image

def binarize_image(image):
    converted =  cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    threshold, im_bw = cv2.threshold(converted, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) # adjust the color later
    return im_bw

def denoise_image(image):
    kernel = np.ones((2,2), np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    image= cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    image = cv2.blur(image, (2,2))
    return image

def thin_font(image): # thickening and thinning the fonts
    image = cv2.bitwise_not(image)
    kernel = np.ones((2,2), np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.bitwise_not(image)
    return image

def thick_font(image):
    image = cv2.bitwise_not(image)
    kernel = np.ones((2,2), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.bitwise_not(image)
    return image