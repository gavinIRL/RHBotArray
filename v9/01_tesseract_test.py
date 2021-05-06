# This will be a test file for detecting words in the game window
# Initial usage is aimed at identifying loot to sell
# And also for automated levelling by identifying mission accepts, etc.
import pytesseract
from PIL import Image
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print(pytesseract.image_to_string('test.png'))
# print(pytesseract.image_to_string(Image.open('test.png')))
