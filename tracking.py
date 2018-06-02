import cv2
import numpy as np
from scipy import stats

def main():
    cap = cv2.VideoCapture(0)

    def receive_frame(cap):
        ret, image = cap.read()
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Returns grayscale image

    def compare_frame(frame1, frame2):
        return abs(np.subtract(np.array(frame1, int), np.array(background, int)))  # Subtracts frame1 from frame2 (background)

    def threshold_frame(frame, threshold):
        frame = (frame > threshold)  # Returns an array of Bools
        frame = np.asarray(np.array(frame) * (-1),np.uint8)  # Any frames of 1 become -1, which is converted to the uint8 max
        return frame

    def blur_frame(frame, radius):
        kernal = np.ones((radius, radius), np.float32) / (radius * radius)  # Defines area for averaging around pixel
        frame = cv2.filter2D(frame, -1, kernal)  # Averages frame
        return frame

    def find_top_and_bottom(element, array):
        top = -1
        for y, row in enumerate(array):  # Returns index and list
            if element in row:
                bottom = y
                if top == -1:  # If top not already set
                    top = y  # Set top y coord
        if top == -1:  # If no element found at all
            return int(len(array) / 2), int(len(array) / 2)  # Return midpoint of frame
        return top, bottom

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
        
        tl = [0, 0]  # Top left
        br = [0, 0]  # Bottom right
        tl[1], br[1] = find_top_and_bottom(mode, frame1)  # Finds Y coords of white pixel limits
        tl[0], br[0] = find_top_and_bottom(mode, np.rot90(frame1, 3))  # Finds X coords of white pixel limits
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

    def draw_frames(list):  # List of [['title',frame]...]
        for frame in list:
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

        if flow == 1:  # Static background subtract
            base_frame = receive_frame(cap)
            compared_frame = compare_frame(base_frame, background)
            blurred_frame = blur_frame(compared_frame, 25)
            thr_frame = threshold_frame(blurred_frame, threshold)

            # thr1_frame = threshold_frame(compared_frame,threshold)
            # blurred2_frame = blur_frame(thr1_frame, 25)
            # thr3_frame = threshold_frame(blurred2_frame,threshold)


        elif flow == 2:  # Dynamic background subtract
            timer += 1
            base_frame = receive_frame(cap)
            compared_frame = compare_frame(base_frame, background)
            blurred_frame = blur_frame(compared_frame, 25)
            thr_frame = threshold_frame(blurred_frame, threshold)
            if timer == 1:
                background = base_frame
                timer = 0

        centre = identify_object(thr_frame)

        draw_frames([['base_frame', base_frame], ['blurred_frame', blurred_frame], ['thr_frame', thr_frame]])

        if not trackbars_created:
            cv2.createTrackbar('T', 'thr_frame', threshold, 100, nothing)
            trackbars_created = True
        threshold = cv2.getTrackbarPos('T', 'thr_frame')


    cap.release()
    cv2.destroyAllWindows()


main()