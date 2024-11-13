
import os
import string
import random
from io import BytesIO

import numpy
import pytesseract
from PIL import Image
from PIL import ImageFilter
from scipy.ndimage import gaussian_filter

if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Define base image folders
F_PATH = os.path.dirname(__file__)
IMG_PATH = os.path.join(F_PATH, "..", "temp")
IMG_UNIQUE_ID = "".join(random.choices(string.digits, k=6))
IMG_ORIGINAL_PATH = os.path.join(IMG_PATH, f"original_{IMG_UNIQUE_ID}.png")
IMG_FILTERED_PATH = os.path.join(IMG_PATH, f"filtered_{IMG_UNIQUE_ID}.png")
IMG_FINAL_PATH = os.path.join(IMG_PATH, f"final_{IMG_UNIQUE_ID}.png")
if not os.path.exists(IMG_PATH): os.mkdir(IMG_PATH)


def solve_captcha_local(image_path):
    th1 = 156
    th2 = 120  # threshold after blurring
    sig = 1.5  # the blurring sigma

    original = Image.open(image_path)  
    original.save(IMG_ORIGINAL_PATH)  

    black_and_white = original.convert("L")  # converting to black and white
    first_threshold = black_and_white.point(lambda p: p > th1 and 255)
    blur = numpy.array(first_threshold)  # create an image array
    blurred = gaussian_filter(blur, sigma=sig)
    blurred = Image.fromarray(blurred)
    final = blurred.point(lambda p: p > th2 and 255)
    final = final.filter(ImageFilter.EDGE_ENHANCE_MORE)
    final = final.filter(ImageFilter.SHARPEN)
    final.save(IMG_FILTERED_PATH)

    blur2 = numpy.array(final)  # create an image array
    blurred2 = gaussian_filter(blur2, sigma=sig*0.7)
    blurred2 = Image.fromarray(blurred2)
    final2 = blurred2.point(lambda p: p > th2 and 255)
    final2 = final2.resize((3000,900))
    final2 = final2.filter(ImageFilter.EDGE_ENHANCE_MORE)
    final2 = final2.filter(ImageFilter.SHARPEN)
    final2.save(IMG_FINAL_PATH)

    ocr_config = '--psm 11 --oem 3 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvxwyz'
    number = pytesseract.image_to_string(Image.open(IMG_FINAL_PATH), config=ocr_config)
    number = number.strip().lstrip().rstrip().replace(chr(32), "").replace("\n", "")

    if len(number) != 6:
        number = pytesseract.image_to_string(Image.open(IMG_FILTERED_PATH), config=ocr_config)
        number = number.strip().lstrip().rstrip().replace(chr(32), "").replace("\n", "")

    return number


if __name__ == "__main__":
    solve_captcha_local("teste.png")