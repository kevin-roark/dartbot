
import cv2 as cv
import frame_convert
import freenect
import numpy
import serial
import os, math, sys, time, random
import db_physics

########
### CONSTANTS
########

HORIZONTAL_VIEW_ANGLE = 58.0
VERTICAL_VIEW_ANGLE = 45.0
RGB_WIDTH = 640
RGB_HEIGHT = 480
FOCAL_LENGTH_X = RGB_WIDTH / (2 * math.tan(math.radians(HORIZONTAL_VIEW_ANGLE / 2)))
FOCAL_LENGTH_Y = RGB_HEIGHT / (2 * math.tan(math.radians(VERTICAL_VIEW_ANGLE / 2)))

DART_TEMPLATE_FILE = os.path.dirname(os.path.realpath(__file__)) + '/dartboard_template.png'
DARTBOARD_TEMPLATE = cv.imread(DART_TEMPLATE_FILE)

MATCHING_METHODS = [
    cv.TM_SQDIFF,
    cv.TM_SQDIFF_NORMED,
    cv.TM_CCORR,
    cv.TM_CCORR_NORMED,
    cv.TM_CCOEFF,
    cv.TM_CCOEFF_NORMED
]

BULLSEYE_COLOR_BOUNDARIES = ( (0, 0, 128), (255, 255, 255) ) # forgiving red

KINECT_RELEASE_Z_OFFSET = 0.3616 # distance (m) from kinect to where the dart is released

#########
#### COMPUTER VISION RESULT CLASSES
#########

class BullseyeResult(object):
    def __init__(self, corner1, center, corner2, supplementary_image=None):
        self.corner1 = corner1
        self.center = center
        self.corner2 = corner2
        self.supplementary_image = supplementary_image

        self.has_performed_vision = False

    def perform_vision_calculations(self):
        print 'performing vision calculations ...'
        self.pos = real_world_position(self.center)
        self.has_performed_vision = True

    def report(self):
        if not self.has_performed_vision:
            self.perform_vision_calculations()

        #print 'match point:', self.center
        print '3d match space:', self.pos[0]
        #print 'z_info:', self.pos[1]

class CircularBullseyeResult(BullseyeResult):
    def __init__(self, center, radius, supplementary_image=None):
        corner1 = (center[0] - radius, center[1] - radius)
        corner2 = (center[0] + radius, center[1] + radius)
        super(CircularBullseyeResult, self).__init__(corner1, center, corner2, supplementary_image)

#########
#### COMPUTER VISION FINDER CLASSES
#########

class BullseyeFinder(object):
    def __init__(self, draw=False, test_point=None):
        self.draw = draw
        self.test_point = test_point

    def run(self):
        print 'grabbing kinect rgb frame...'
        self.rgb_image = get_video() # grab image from kinect

        print 'converting to numpy ...'
        self.rgb_mat = numpy.asarray(self.rgb_image[:,:]) # make it numpy style

        print 'performing analysis ...'
        self.result = self.find_bullseye(self.rgb_image)

        self.draw_bullseye(self.rgb_mat)

    def report(self):
        self.report_bullseye(self.result)

    def find_bullseye(self, rgb_image):
        return None # help me out here

    def draw_bullseye(self, display_image):
        bullseye_result = self.result

        if self.draw:
            if self.test_point:
                cv.circle(display_image, self.test_point, 8, (255, 255, 0), 2, 8, 0)

            if bullseye_result is not None:
                cv.circle(display_image, bullseye_result.center, 10, (0, 0, 255), 2, 4, 0)
                cv.rectangle(display_image, bullseye_result.corner1, bullseye_result.corner2, 0, 2, 8, 0)

            # display results in window
            self.window_number = str(random.randint(0, 1000))
            kinect_window = 'kinect image ' + self.window_number
            cv.namedWindow(kinect_window, cv.WINDOW_AUTOSIZE)
            cv.imshow(kinect_window, display_image)

            if bullseye_result is not None and bullseye_result.supplementary_image is not None:
                supplementary_window = 'supplementary image ' + self.window_number
                cv.namedWindow(supplementary_window, cv.WINDOW_AUTOSIZE)
                cv.imshow(supplementary_window, bullseye_result.supplementary_image)

    def report_bullseye(self, bullseye_result):
        if bullseye_result is None:
            print 'failed to find bullseye!!!!'
        else:
            bullseye_result.report()

        if self.test_point:
            print 'test point / real world test loc:'
            print self.test_point
            print real_world_position(self.test_point)


class TemplateMatcher(BullseyeFinder):
    def __init__(self, draw=False, test_point=None, matching_method=cv.TM_SQDIFF):
        super(TemplateMatcher, self).__init__(draw, test_point)
        self.matching_method = matching_method

    # override !
    def find_bullseye(self, rgb_image):
        # convert kinect rbg image to numpy matrix
        rgb_mat = numpy.asarray(rgb_image[:,:])

        # run the template matching
        match_result = TemplateMatcher.match_template(rgb_mat, DARTBOARD_TEMPLATE, self.matching_method)
        return match_result

    # override !
    def report_bullseye(self, bullseye_result, display_image):
        name = TemplateMatcher.matching_method_name(self.matching_method)
        print 'matching method:', self.matching_method, '(' + name + ')'

        super(TemplateMatcher, self).report_bullseye(bullseye_result, display_image)

    @staticmethod
    def matching_method_name(matching_method):
        if matching_method == cv.TM_SQDIFF:
            return 'squared diff'
        elif matching_method == cv.TM_SQDIFF_NORMED:
            return 'normalized squared diff'
        elif matching_method == cv.TM_CCORR:
            return 'correlation'
        elif matching_method == cv.TM_CCORR_NORMED:
            return 'normalized correlation'
        elif matching_method == cv.TM_CCOEFF:
            return 'correlation coefficient'
        elif matching_method == cv.TM_CCOEFF_NORMED:
            return 'normalized correlation coefficient'
        else:
            return 'UNKNOWN MATCHING_METHOD'

    @staticmethod
    def match_method_prefers_min(match_method):
        return (match_method == cv.TM_SQDIFF or match_method == cv.TM_SQDIFF_NORMED)

    @staticmethod
    def match_template(image, template, matching_method=cv.TM_SQDIFF):
        # run the template matching
        match_result = cv.matchTemplate(image, template, matching_method)

        # normalize matched result
        normalized_match_result = cv.normalize(match_result, alpha=0, beta=1, norm_type=cv.NORM_MINMAX, dtype=-1)

        # get that tasty min and max matches (localize the best result)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(normalized_match_result)
        match_loc = min_loc if TemplateMatcher.match_method_prefers_min(matching_method) else max_loc

        # calculate helpful match info
        match_center = (match_loc[0] + template.shape[0] / 2, match_loc[1] + template.shape[1] / 2)
        match_corner = (match_loc[0] + template.shape[0], match_loc[1] + template.shape[1])

        return BullseyeResult(match_loc, match_center, match_corner, normalized_match_result)


class ColorBasedFinder(BullseyeFinder):
    def __init__(self, draw=False, test_point=None, color_boundaries=BULLSEYE_COLOR_BOUNDARIES):
        super(ColorBasedFinder, self).__init__(draw, test_point)
        self.color_boundaries = color_boundaries
        self.lower, self.upper = self.color_boundaries

# inspired by http://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/
class CircularColorBasedFinder(ColorBasedFinder):
    def __init__(self, draw=False,
                       test_point=None,
                       color_boundaries=BULLSEYE_COLOR_BOUNDARIES,
                       dp=1.2,
                       min_dist=100,
                       max_circles=4,
                       continue_after_success=False,
                       draw_supplementary=False):
        super(CircularColorBasedFinder, self).__init__(draw, test_point, color_boundaries)
        self.dp = dp
        self.min_dist = min_dist
        self.draw_supplementary = draw_supplementary
        self.continue_after_success = continue_after_success

    # override !
    def find_bullseye(self, rgb_image):
        # convert kinect rbg image to numpy matrix
        rgb_mat = self.rgb_mat

        # copy kinect rgb image for drawing
        drawing_image = None if not self.draw else rgb_mat.copy()

        # convert to grayscale
        gray_image = cv.cvtColor(rgb_mat, cv.COLOR_BGR2GRAY)

        # detect circles in the image
        print 'detecting circles ...'
        circles = cv.HoughCircles(gray_image, cv.cv.CV_HOUGH_GRADIENT, self.dp, self.min_dist)

        # here we will store what we think the bullseye is
        bullseye_circle = None

        # this was for testing (x,y) vs (y,x)
        # cv.circle(drawing_image, (400, 150), 6, (0, 0, 0), 4)
        #print rgb_mat.shape
        #print rgb_mat[150, 400]

        # ensure at least some circles were found
        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = numpy.round(circles[0, :]).astype("int")
            circles = circles[:4]

            # loop over the (x, y) coordinates and radius of the circles
            count = 0
            for (x, y, r) in circles:
                print 'circle number', count, 'alert:', x, y, r
                if not bullseye_circle:
                    if self.pixel_fits_bullseye_profile(rgb_mat[y, x]):
                        print 'circular success!'
                        bullseye_circle = (x, y, r)
                        if not self.continue_after_success:
                            break

                if self.draw and self.draw_supplementary:
                    # draw the circle in the output image, then draw a rectangle
                    # corresponding to the center of the circle
                    cv.circle(drawing_image, (x, y), r, (0, 255, 0), 4)
                    cv.rectangle(drawing_image, (x - 2, y - 2), (x + 2, y + 2), (0, 128, 255), -1)
                    cv.putText(drawing_image, str(count), (x - 5, y - 15), cv.FONT_HERSHEY_PLAIN, 2, (255, 255, 255))

                count += 1

            if bullseye_circle is None and len(circles) > 0:
                bullseye_circle = circles[0] # fallback in case we have circles but color detection is meh

        supp_img = drawing_image if (self.draw and self.draw_supplementary) else None

        if bullseye_circle is not None:
            center = (bullseye_circle[0], bullseye_circle[1])
            radius = bullseye_circle[2]
            return CircularBullseyeResult(center, radius, supp_img)
        else:
            return CircularBullseyeResult((0, 0), 1, supp_img)

    def pixel_fits_bullseye_profile(self, pixel):
        b, g, r = pixel
        lower_b, lower_g, lower_r = self.lower
        upper_b, upper_g, upper_r = self.upper
        print 'b, g, r:', pixel
        if b < lower_b or b > upper_b or \
           g < lower_g or g > upper_g or \
           r < lower_r or r > upper_r:
            return False
        return True

# Inspired by http://stackoverflow.com/questions/12943410/opencv-python-single-rather-than-multiple-blob-tracking
class BlobbyColorBasedFinder(ColorBasedFinder):
    # override !
    def find_bullseye(self, rgb_image):
        # smooth kinect rgb image
        smooth_image = cv.blur(rgb_image, (3,3))

        # convert upper and lower boundaries to numpy
        lower = numpy.array(self.lower, dytype="uint8")
        upper = numpy.array(self.upper, dtype="uint8")

        # find range of smoothed kinect image within color boundaries
        thresh_image = cv.inRange(smooth_image, lower, upper)
        supplementary_thresh = thresh_image.copy()

        # find contours in the threshold image
        contours, hierarchy = cv.findContours(thresh_image, cv.RETR_LIST,cv.CHAIN_APPROX_SIMPLE)

        # finding contour with maximum area and store it as best_cnt
        max_area, largest_contour = 0, None
        for cnt in contours:
            area = cv.contourArea(cnt)
            if area > max_area:
                max_area = area
                largest_contour = cnt

        if not largest_contour:
            return None

        # finding centroids of largest_contour and draw a circle there
        moments = cv.moments(largest_contour)
        cx, cy = int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])

        return CircularBullseyeResult((cx, cy), 5, supplementary_thresh)


########
### KINECT STUFF
########

def reset_kinect():
    print 'cleaning up the kinect ...'
    freenect.sync_get_depth()
    freenect.sync_get_video()

def real_world_position(screen_point):
    adjusted_screen_x = screen_point[0] - RGB_WIDTH / 2 # center x should be 0
    adjusted_screen_y = screen_point[1] - RGB_HEIGHT / 2 # center y should be 0

    # it is (Y, X) style ya dummy
    z_world_struct = get_z_world_depth()[screen_point[1]][screen_point[0]]
    z_world = z_world_struct[1]

    # focal method
    #x_world = z_world * adjusted_screen_x / FOCAL_LENGTH_X
    #y_world = z_world * adjusted_screen_y / FOCAL_LENGTH_Y

    # emperical method
    x_world = adjusted_screen_x * (z_world - 10) * .0021
    y_world = adjusted_screen_y * (z_world - 10) * .0021

    pos = (x_world, y_world, z_world)
    return (pos, z_world_struct)

def get_z_world_depth():
    depth_mat = freenect.sync_get_depth()[0]
    rows = len(depth_mat)
    columns = len(depth_mat[0])

    world_depth_mat = [None] * rows

    for r in range(rows):
        world_depth_row = [None] * columns
        for c in range(columns):
            raw_disparity = depth_mat[r][c]
            metered_depth = 0.1236 * math.tan(raw_disparity / 2842.5 + 1.1863) # http://openkinect.org/wiki/Imaging_Information#Depth_Camera
            #metered_depth = 100 / (-0.00307 * raw_disparity + 3.33)
            world_depth_row[c] = (raw_disparity, metered_depth)

        world_depth_mat[r] = world_depth_row

    return world_depth_mat

def get_depth():
    return frame_convert.pretty_depth_cv(freenect.sync_get_depth()[0])

def get_video():
    # in ros:
    # bayered_image = rgb_image_raw()
    # rgb_image = cv.ctvColor(bayered_image, cv.CV_BAYERGR2RGB)

    # in straight python freenect:
    numpy_vid = freenect.sync_get_video()[0]
    return frame_convert.video_cv(numpy_vid)

def z_gain_for_target_z(z_dist):
    #y = -9.7428x6 + 103.21x5 - 448.41x4 + 1021.7x3 - 1286.3x2 + 847.51x - 226.85

    gain = -9.7428 * (z_dist ** 6) + \
            103.21 * (z_dist ** 5) - \
            448.41 * (z_dist ** 4) + \
            1021.7 * (z_dist ** 3) - \
            1286.3 * (z_dist ** 2) + \
            847.51 * (z_dist) - \
            226.85

    return gain

##########
#### ARDUINO COMMUNICATION
##########

arduinoSerial = None

def start_serial():
    global arduinoSerial
    try:
        arduinoSerial = serial.Serial('/dev/tty.usbmodem1421', 9600)
        print 'ok serial is connected good'
    except OSError as e:
        print 'failed to start serial: {}'.format(e)

def write_serial(text):
    global arduinoSerial

    if not arduinoSerial:
        return

    arduinoSerial.write(text)

##########
#### SCRIPT BEHAVIOR
##########

def template_matching_test(args):
    methods = len(MATCHING_METHODS)
    for i in range(methods):
        print '**** test run ', i, ' ****'
        method = MATCHING_METHODS[i]
        matcher = TemplateMatcher(matching_method=method)
        matcher.run()
        matcher.report()
        print ''

def serial_test(args):
    start_serial()
    write_serial('ok')
    print 'yeah i did it'

def find_bullseye_with_confirmation(args):
    bullseye_pos = None

    while not bullseye_pos:
        finder = CircularColorBasedFinder(draw=True, draw_supplementary=True, continue_after_success=True)
        finder.run()
        finder.report()

        user_confirmation = input('Does the reported bullseye position look good? ')
        if user_confirmation == 1:
            bullseye_pos = finder.result.center
            print 'sick!!!!!'
        else:
            cv.destroyAllWindows()

def find_centered_bullseye_with_confirmation(args):
    start_serial()

    target_x = RGB_WIDTH / 2
    target_y = RGB_HEIGHT / 2 # for now this is not used ...
    target_buffer = 15

    target_finder = None
    at_target = False

    while not at_target:
        finder = CircularColorBasedFinder(draw=True, draw_supplementary=False, continue_after_success=False)
        finder.run()

        if not finder.result:
            print 'could not find the dartbot ... '
            print 'abort!!!'
            at_target = True

        pos = finder.result.center
        dist_from_target = (pos[0] - target_x)
        print 'distance in x from center is {}'.format(dist_from_target)
        if abs(dist_from_target) <= target_buffer:
            print 'we like that!\n'
            at_target = True
            target_finder = finder
        else:
            print 'we dont like that ...'

            print 'lets turn the motor a bit...'
            serial_command = 'l' if dist_from_target < 0 else 'r'
            write_serial(serial_command)
            print 'waiting for the motor ...'
            time.sleep(1.3)

            cv.destroyAllWindows()

    if target_finder:
        target_finder.report()

        measured_z = target_finder.result.pos[0][2]

        true_z = measured_z + KINECT_RELEASE_Z_OFFSET # add the release offset (smart idea)

        gain = z_gain_for_target_z(true_z)
        print '...gaining by {}\n'.format(gain)
        motor_gained_z = gain * true_z

        print '\nmotor control parameters:'
        db_physics.arm_info_for_target_z(motor_gained_z) # print relevant info for motor controllers


def main():
    reset_kinect()

    functions = {
        'template_test': template_matching_test,
        'serial': serial_test,
        'find': find_bullseye_with_confirmation,
        'search': find_centered_bullseye_with_confirmation
    }

    fn = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in functions else 'template_test'

    functions[fn](sys.argv[2:])

if __name__ == '__main__':
    main()

    while 1:
        if cv.waitKey(10) == 27:
            break
