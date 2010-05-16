#
# Controlling an RC car via webcam (well, so far, just tracking it...)
#
# Requires OpenCV 2.0 and Python 2.6
#

import cv


def find_car(image):
    """ Finds red blob (hopefully only one, the rc car) in an image
    """
    size = cv.GetSize(image)

    #prepare memory
    car = cv.CreateImage(size, 8, 1)
    red = cv.CreateImage(size, 8, 1)
    hsv = cv.CreateImage(size, 8, 3)
    sat = cv.CreateImage(size, 8, 1)

    #split image into hsv, grab the sat
    cv.CvtColor(image, hsv, cv.CV_BGR2HSV)
    cv.Split(hsv, None, sat, None, None)

    #split image into rgb
    cv.Split(image, None, None, red, None)

    #find the car by looking for red, with high saturation
    cv.Threshold(red, red, 128, 255, cv.CV_THRESH_BINARY)
    cv.Threshold(sat, sat, 128, 255, cv.CV_THRESH_BINARY)

    #AND the two thresholds, finding the car
    cv.Mul(red, sat, car)

    #remove noise, highlighting the car
    cv.Erode(car, car, iterations=2)
    cv.Dilate(car, car, iterations=5)

    #return a bounding box
    return cv.BoundingRect(car)


points = []
capture = cv.CaptureFromCAM(0)
if not capture:
    print "Error opening capture device"
    sys.exit(1)

cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH, 640)
cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT, 480)

#writer = cv.CreateVideoWriter('test.avi', cv.CV_FOURCC('F','M','P','4'), 30, (640, 480))

while 1:

    original = cv.QueryFrame(capture)

    car_rect = find_car(original)

    middle = (car_rect[0] + (car_rect[2] / 2), car_rect[1] + (car_rect[3]/2))
    if points == []:
        points.append(middle)
    else:
        if abs(points[-1][0] - middle[0]) > 5 and abs(points[-1][1] - middle[1]) > 10:
            points.append(middle)

    cv.Rectangle(original,
                 (car_rect[0], car_rect[1]),
                 (car_rect[0] + car_rect[2], car_rect[1] + car_rect[3]),
                 (255, 0, 0),
                 2,
                 8,
                 0)

    for point in points:
        cv.Circle(original,
                  point,
                  3,
                 (0, 0, 255),
                 -1,
                 8,
                 0)

    #cv.WriteFrame(writer, original)

    cv.ShowImage('Analysed', original)
    k = cv.WaitKey(33)
