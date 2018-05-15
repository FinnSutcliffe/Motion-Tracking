import cv2
import numpy as np

def main():

    cap = cv2.VideoCapture(0)


    def receive_frame(cap):
        ret, image = cap.read()
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Returns greyscale image


    def compare_frame(frame1, frame2):
        return abs(np.subtract(np.array(frame1,int),np.array(frame2,int)))  # Subtracts frame1 from frame2 (background)


    def threshold_frame(frame, threshold):
        frame = (frame > threshold)  # Returns an array of Bools
        frame = np.asarray(np.array(frame)*(-1),np.uint8 )  # Any frames of 1 become -1, which is converted to the uint8 max
        return frame


    def blur_frame(frame, radius):
        kernal = np.ones((radius, radius),np.float32)/(radius*radius)  # Defines area for averaging around pixel
        frame = cv2.filter2D(frame,-1, kernal)  # Averages frame


    def find_top_and_bottom(element, array):
        top = -1
        for y, row in enumerate(array):  # Returns index and list
            if element in row:
                bottom = y
                if top == -1:  # If top not already set
                    top = y  # Set top y coord
        if top == -1:  # If no element found at all
            return int(len(array[0])/2),int(len(array)/2)  # Return midpoint of frame
        return top, bottom


    def draw_box_and_coords(topleft, bottomright, coords, frame, colour):
        font = cv2.FONT_HERSHEY_SYMPLEX
        cv2.rectangle(frame, (topleft[0],topleft[1]),(bottomright[0],bottomright[1]),colour, 1)
        cv2.line(frame,(20,460),(90,460),0,20)  # Draws line to highlight text
        cv2.putText(frame,str(coords[0])+', '+str(coords[1]), (15,465), font, 0.5, colour, 1, cv2.LINE_AA)


    def identify_object(frame):
        class Coords():
            x = 0
            y = 0
            def __init__(self):
                x = Coords.x
                y = Coords.y


        tl = Coords(x=0,y=0)  # Top left
        br = Coords(x=0,y=0)  # Bottom right
        tl.y, br.y = find_top_and_bottom(255, frame)  # Finds Y coords of white pixel limits
        tl.x, br.x = find_top_and_bottom(255, np.rot90(frame, 3))  # Finds X coords of white pixel limits
        centre = Coords(x=int((tl.x+br.x)/2),y=int((tl.y+br.y)/2))  # Finds centre

        draw_box_and_coords([tl.x, tl.y],[br.x,br.y], [centre.x,centre.y], frame, (255,255,255))

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
            cv2.imshow(frame[0],frame[1])


    def nothing(a):
        pass


    flow = 1
    trackbars_created = False
    threshold = 50
    while True:
        key = press_key()
        if key == None or key == 1:
            flow = 1
        elif key == 2:
            flow = 2
        elif key == 0:
            break
        elif key == 3:
            background = receive_frame(cap)

        if flow == 1:  # Static background subtract
            base_frame = receive_frame(cap)
            compared_frame = compare_frame(base_frame,background)
            ########## EXPERIMENTAL ##########
            blurred_frame = blur_frame(compared_frame,25)
            thr_frame = threshold_frame(blurred_frame,threshold)
            ##################################


        elif flow == 2:  # Dynamic background subtract
            base_frame = receive_frame(cap)
            compared_frame = compare_frame(base_frame, background)
            ########## EXPERIMENTAL ##########
            blurred_frame = blur_frame(compared_frame, 25)
            thr_frame = threshold_frame(blurred_frame, threshold)
            ##################################
            background = base_frame

        centre = identify_object(thr_frame)

        draw_frames([['base_frame',base_frame],['compared_frame',compared_frame],['thr_frame',thr_frame]])

        if not trackbars_created:
            cv2.createTrackbar('T','thr_frame', threshold, 100, nothing)
            trackbars_created = True
        threshold = cv2.getTrackbarPos('T', 'thr_frame')
    cap.release()
    cap.destroyAllWindows()


main()