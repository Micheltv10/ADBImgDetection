import cv2  # https://docs.opencv.org/4.x/
import numpy as np
import pyautogui
from time import sleep
from ppadb.client import Client as AdbClient

pyautogui.FAILSAFE = False
adb = AdbClient(host="127.0.0.1", port=5037)

# Get the connected devices
devices = adb.devices()

while len(devices) == 0:
    print("No device connected")
    devices = adb.devices()

device = devices[0]
max_results = 42

def click(x, y):
    device.shell(f"input tap {x} {y}")

def swipe(x1, y1, x2, y2, duration):
    device.shell(f"input swipe {x1} {y1} {x2} {y2} {duration}")

def getTemplatePos(
    template_image_path: str,
    device=device,
    threshold: float = 0.45,
    number_of_clicks: int = 1,
):
    template_image_path = "img/" + template_image_path
    print(f"{template_image_path} search")
    
    template_image = cv2.imread(template_image_path, cv2.IMREAD_COLOR)  # Load template image in color
    game_screenshot = device.screencap()  # Take a screenshot
    # Convert the screenshot to a format that OpenCV can use
    game_screenshot = cv2.imdecode(np.frombuffer(game_screenshot, np.uint8), -1)
    game_screenshot = cv2.cvtColor(game_screenshot, cv2.COLOR_BGR2RGB)
    game_screenshot = cv2.cvtColor(game_screenshot, cv2.COLOR_BGR2RGB)

    
    

    # Ensure both images have the same data type
    template_image = template_image.astype(np.uint8)
    # Ensure both images have the same number of color channels
    if len(template_image.shape) != len(game_screenshot.shape) or template_image.shape[2] != game_screenshot.shape[2]:
        raise ValueError("Template image and game screenshot have incompatible dimensions or number of channels")

    # https://docs.opencv.org/master/d4/dc6/tutorial_py_template_matching.html
    search_result = cv2.matchTemplate(
        game_screenshot, template_image, cv2.TM_CCOEFF_NORMED
    )

    
    locations = np.where(search_result >= threshold)
    locations = list(zip(*locations[::-1]))
    if not locations:
        print("No results found.")
        return game_screenshot, np.array([], dtype=np.int32).reshape(0, 4)

    rectangles = []

    for loc in locations:
        # get width and height
        rect = [int(loc[0]), int(loc[1])]
        rectangles.append(rect + [rect[0] + template_image.shape[1], rect[1] + template_image.shape[0]])    
    rectangles, weights = cv2.groupRectangles(rectangles, groupThreshold=1, eps=0.01)
    print(rectangles)

        # for performance reasons, return a limited number of results.
        # these aren't necessarily the best results.
    if len(rectangles) > max_results:
        print('Warning: too many results, raise the threshold.' + str(len(rectangles)))
        rectangles = rectangles[:max_results]
        # draw rectangles on the game screenshot
    for (startX, startY, endX, endY) in rectangles:
        cv2.rectangle(game_screenshot, (startX, startY), (endX, endY), (255, 255, 0), 2)
        # show the output image with the rectangle drawn on it
    return game_screenshot, rectangles


fields = [
    "1.png",
    "3.png",
    
]
frame_count = 0
while True:
    for field in fields:
        game_screenshot, rectpos = getTemplatePos(field)
        # resize 
        game_screenshot = cv2.resize(game_screenshot, (0, 0), fx=0.5, fy=0.5)
        cv2.imshow("Game Screenshot", game_screenshot)
        cv2.waitKey(1)
        if len(rectpos) > 0:
            # click(rectpos[0][0], rectpos[0][1])
            print("click")
            
        