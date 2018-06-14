import cv2
import numpy as np
from scipy import stats
import time

def main():
    cap = cv2.VideoCapture(0)
    WIDTH = 40
    HEIGHT = 30

    def receive_frame(cap):
        ret, image = cap.read()
        image = cv2.resize(image, (WIDTH,HEIGHT))
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Returns grayscale image

    def compare_frame(frame1, frame2):
        return abs(np.subtract(np.array(frame1, int), np.array(background, int)))  # Subtracts frame1 from frame2 (background)

    def threshold_frame(frame, threshold):
        frame = (frame > threshold)  # Returns an array of Bools
        frame = np.asarray(np.array(frame) * (-1),np.uint8)  # Any frames of 1 become -1, which is converted to the uint8 max
        return frame

    def blur_frame(frame, radius):
        kernal = np.ones((radius, radius), np.float32) / (radius * radius)  # Defines area for averaging around pixel
        frame = cv2.filter2D(np.array(frame,dtype='float32'), -1, kernal)  # Averages frame
        return frame

    def draw_box_and_coords(topleft, bottomright, coords, frame, colour):
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.rectangle(frame, (topleft[0], topleft[1]), (bottomright[0], bottomright[1]), colour, 1)
        cv2.line(frame, (20, 460), (90, 460), 0, 20)  # Draws line to highlight text
        cv2.putText(frame, str(coords[0]) + ', ' + str(coords[1]), (15, 465), font, 0.5, colour, 1, cv2.LINE_AA)

    def identify_object(frame):
        
        _,frame1 = cv2.connectedComponents(frame)
        if np.amax(frame1)!=0:
            mode = stats.mode(frame1[frame1!=0], axis=None)[0][0]
        else:
            mode = 1
        
        frame1 = np.asarray(frame1,np.uint8)
        frame1[frame1 != mode] = 0
        x,y,w,h = cv2.boundingRect(frame1)
        tl = [x, y]
        br = [x+w, y+h]  # Bottom right
        centre = [int((tl[0] + br[0]) / 2), int((tl[1] + br[1]) / 2)]  # Finds centre
        draw_box_and_coords([tl[0], tl[1]], [br[0], br[1]], [centre[0], centre[1]], frame, (255, 255, 255))
        return centre

    def press_key():
        keypress = cv2.waitKey(1) & 0xFF
        if keypress == ord("q"):
            return 0
        elif keypress == ord("1"):
            return 1
        elif keypress == ord("2"):
            return 2
        elif keypress == ord("r"):
            return 3

    def draw_frames(list1):  # List of [['title',frame]...]
        for frame in list1:
            cv2.imshow(frame[0], np.asarray((frame[1]), np.uint8))

    def calculate_angles(centre):
        # tan(theta/2) = dimension/2 * tan(63/2)/(diagonal/2)
        # e.g. horizontal: tan(theta/2) = 320*tan(31.5)/400
        # Angle from centre to edge of webcam (horizontal) = 26.1 degrees, 0.377 rad
        # Angle from centre to edge of webcam (vertical) = 20.2 degrees, 0.353 rad
        # tan(thetad)/tan(thetat) = dist/total
        dx = centre[0] - 320
        dy = centre[1] - 240
        angle = np.arctan([np.tan(0.377) * dx / 320, np.tan(0.353) * dy / 240]) + np.pi / 2
        return np.asarray(np.degrees(angle), int)

    def write_to_servos():
        pass

    def nothing(a):
        pass

    flow = 1
    trackbars_created = False
    threshold = 20
    background = receive_frame(cap)
    while True:
        t1= time.time()
        key = press_key()
        if key == 1:
            flow = 1
        elif key == 2:
            flow = 2
            timer = 0
        elif key == 0:
            break
        elif key == 3:
            background = receive_frame(cap)
        print "Keypresses", time.time()-t1
        t1 = time.time()
        if flow == 1:  # Static background subtract
            base_frame = receive_frame(cap)
            print "Receive frame", time.time()-t1
            t1 = time.time()
            compared_frame = compare_frame(base_frame, background)
            print "Compare frame", time.time()-t1
            t1 = time.time()
            blurred_frame = blur_frame(compared_frame, 3)
            print "Blur frame", time.time()-t1
            t1 = time.time()
            thr_frame = threshold_frame(blurred_frame, threshold)
            print "Thr frame", time.time()-t1
            t1 = time.time()

        elif flow == 2:  # Dynamic background subtract
            timer += 1
            base_frame = receive_frame(cap)
            compared_frame = compare_frame(base_frame, background)
            blurred_frame = blur_frame(compared_frame, 3)
            thr_frame = threshold_frame(blurred_frame, threshold)
            if timer == 1:
                background = base_frame
                timer = 0

        base_frame = cv2.resize(base_frame, (640,480))
        print "Resize base", time.time()-t1
        t1 = time.time()
        #blurred_frame = cv2.resize(np.asarray(blurred_frame,np.uint8), (640,480))
        thr_frame = cv2.resize(thr_frame, (640,480))
        print "Resize thr", time.time()-t1
        t1 = time.time()
        
        centre = identify_object(thr_frame)
        print "Find centre", time.time()-t1
        t1 = time.time()
        draw_frames([['base_frame', base_frame],['thr_frame', thr_frame]])#[['base_frame', base_frame], ['blurred_frame', blurred_frame], ['thr_frame', thr_frame]])
        print "Draw frames", time.time()-t1
        t1 = time.time()
        if not trackbars_created:
            cv2.createTrackbar('T', 'thr_frame', threshold, 100, nothing)
            trackbars_created = True
        threshold = cv2.getTrackbarPos('T', 'thr_frame')
        print "Trackbars", time.time()-t1
        print
        print
        print

    cap.release()
    cv2.destroyAllWindows()


main()