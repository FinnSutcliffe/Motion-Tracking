import cv2
from time import sleep
import simplecv

cap = cv2.VideoCapture(0)

while True:
    ret,img = cap.read()
    cv2.imshow("img",img)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    
cap.release()
cv2.destroyAllWindows()