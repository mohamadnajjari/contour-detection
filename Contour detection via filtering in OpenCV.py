import requests 
from io import BytesIO
from PIL import Image
import cv2 as cv
import numpy as np

response = requests.get('https://i.stack.imgur.com/ukOkD.jpg')
image = np.asarray(Image.open(BytesIO(response.content)))
image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

sobelx = np.array([[-1,0,1],[-2,0,2],[-1,0,1]])
sobely = np.array([[-1,-2,-1],[0,0,0],[1,2,1]])

vertical_edge = cv.filter2D(image_gray, -1, sobelx)
horizontal_edge = cv.filter2D(image_gray, -1, sobely)

image_adth = cv.adaptiveThreshold(vertical_edge, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 9,2)
image_blur = cv.medianBlur(image_adth, 25)

ret, image_gray = cv.threshold(image_blur, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)

def function(image_gray,image, horizontal_edge):
      
    contours, _ = cv.findContours(image_gray, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    
    new_counters = []
    for i, c in enumerate(contours):
        area = cv.contourArea(c)
        if area>3500 and area<6000:
            new_counters.append(c)
                   
    contours_poly = [None]*len(new_counters)
    boundRect = [None]*len(new_counters)
    lines = [False]*len(new_counters)
    for i, c in enumerate(new_counters):
        epsilon = 0.01 * cv.arcLength(c, True)  
        contours_poly[i] = cv.approxPolyDP(c, epsilon, True)
        boundRect[i] = cv.boundingRect(contours_poly[i])
        
        x, y, width, height = boundRect[i]
        
        extracted_region = horizontal_edge[ y:y+height, x:x+width]
        _, extracted_region = cv.threshold(extracted_region, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)

        contours, _ = cv.findContours(extracted_region, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        for _, cc in enumerate(contours):
            area = cv.contourArea(cc)
            print(area)
            if area>50:# and area<6000:
                lines[i] = True
                
    for i in range(len(new_counters)):
        red = (0, 0, 255)
        green = (0, 255, 0)
        if lines[i]:
            cv.rectangle(image, (int(boundRect[i][0]), int(boundRect[i][1])), \
            (int(boundRect[i][0]+boundRect[i][2]), int(boundRect[i][1]+boundRect[i][3])), green, 2)
            
        else:
            cv.rectangle(image, (int(boundRect[i][0]), int(boundRect[i][1])), \
            (int(boundRect[i][0]+boundRect[i][2]), int(boundRect[i][1]+boundRect[i][3])), red, 2)
                
    cv.imshow('Contours', image)
    
window = 'Source'
cv.namedWindow(window)
cv.imshow(window, image)
function(image_gray,image,horizontal_edge)
cv.waitKey(0)  
cv.destroyAllWindows()  