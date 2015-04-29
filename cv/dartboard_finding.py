
import cv2 as cv
import frame_convert
import freenect
import numpy
import os, math, sys, time, random

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

#########
#### COMPUTER VISION CLASSES
#########

class BullseyeResult(object):
    def __init__(self, corner1, center, corner2, supplementary_image=None):
        self.corner1 = corner1
        self.center = center
        self.corner2 = corner2
        self.pos = real_world_position(center)
        self.required_v = velocity_needed_for_z(self.pos[0][2])
        self.supplementary_image = supplementary_image

class CircularBullseyeResult(BullseyeResult):
    def __init__(self, center, radius, supplementary_image=None):
        corner1 = (center[0] - radius, center[1] - radius)
        corner2 = (center[0] + radius, center[1] + radius) 
        super(CircularBullseyeResult, self).__init__(corner1, center, corner2, supplementary_image)

class BullseyeFinder(object):
    def __init__(self, draw=False, test_point=None):
        self.draw = draw
        self.test_point = test_point

    def run(self):
        rgb_image = get_video() # grab image from kinect
        self.result = self.find_bullseye(rgb_image)

        rgb_mat = numpy.asarray(rgb_image[:,:]) # make it numpy style
        self.report_bullseye(self.result, rgb_mat)

    def find_bullseye(self, rgb_image):
        return None # help me out here 

    def report_bullseye(self, bullseye_result, display_image):
        if bullseye_result is None:
            print 'failed to find bullseye!!!!'
        else:
            print 'match point:', bullseye_result.center
            print '3d match space:', bullseye_result.pos[0]
            print 'z_info:', bullseye_result.pos[1]
            print 'required velocity:' + bullseye_result.required_v

        if self.test_point:  
            print 'test point / real world test loc:'
            print self.test_point
            print real_world_position(self.test_point)

            if draw:
                cv.circle(display_image, self.test_point, 8, (255, 255, 0), 2, 8, 0)

        if self.draw:
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
    def __init__(self, draw=False, test_point=None, color_boundaries=BULLSEYE_COLOR_BOUNDARIES, dp=1.2, min_dist=100):
        super(CircularColorBasedFinder, self).__init__(draw, test_point, color_boundaries)
        self.dp = dp
        self.min_dist = min_dist

    # override !
    def find_bullseye(self, rgb_image):
        # convert kinect rbg image to numpy matrix
        rgb_mat = numpy.asarray(rgb_image[:,:])

        # copy kinect rgb image for drawing
        drawing_image = rgb_mat.copy()

        # convert to grayscale
        gray_image = cv.cvtColor(rgb_mat, cv.COLOR_BGR2GRAY)

        # detect circles in the image
        circles = cv.HoughCircles(gray_image, cv.cv.CV_HOUGH_GRADIENT, self.dp, self.min_dist)

        # here we will store what we think the bullseye is
        bullseye_circle = None

        cv.circle(drawing_image, (400, 150), 6, (0, 0, 0), 4)
        print rgb_mat.shape
        print rgb_mat[150, 400]

        # ensure at least some circles were found
        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = numpy.round(circles[0, :]).astype("int")

            # loop over the (x, y) coordinates and radius of the circles
            count = 0
            for (x, y, r) in circles:
                print 'circle number', count, 'alert:', x, y, r
                if not bullseye_circle:
                    if self.pixel_fits_bullseye_profile(rgb_mat[y, x]):
                        print 'circular success!'
                        bullseye_circle = (x, y, r)

                if self.draw:
                    # draw the circle in the output image, then draw a rectangle
                    # corresponding to the center of the circle
                    cv.circle(drawing_image, (x, y), r, (0, 255, 0), 4)
                    cv.rectangle(drawing_image, (x - 2, y - 2), (x + 2, y + 2), (0, 128, 255), -1)
                    cv.putText(drawing_image, str(count), (x - 5, y - 15), cv.FONT_HERSHEY_PLAIN, 2, (255, 255, 255))

                count += 1

        if bullseye_circle:
            center = (bullseye_circle[0], bullseye_circle[1])
            radius = bullseye_circle[2]
            return CircularBullseyeResult(center, radius, drawing_image)
        else:
            return CircularBullseyeResult((0, 0), 1, drawing_image)

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
    freenect.sync_get_depth()
    freenect.sync_get_video()

# assumes z dist in meters
def velocity_needed_for_z(z_dist):
    gravity_z = - 9.81 * z_dist
    double_release_angle = 2 * (3.14 / 6) # TODO: update release angle
    v = sqrt(gravity_z / sin(double_release_angle))
    return v

def real_world_position(screen_point):
    adjusted_screen_x = screen_point[0] - RGB_WIDTH / 2 # center x should be 0
    adjusted_screen_y = screen_point[1] - RGB_HEIGHT / 2 # center y should be 0

    # TODO: determine if shohuld do (x, y) or (r, x)
    z_world_struct = get_z_world_depth()[screen_point[0]][screen_point[1]]
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
        print ''

def find_bullseye_with_confirmation(args):
    bullseye_pos = None

    while not bullseye_pos:
        finder = CircularColorBasedFinder(draw=True)
        finder.run()

        user_confirmation = input('Does the reported bullseye position look good? ')
        if user_confirmation == 'lgtm':
            bullseye_pos = finder.result.center
            print 'sick!!!!!'
        else:
            cv.destroyAllWindows()

    # TODO: report bullseye_pos to robot

def main():
    reset_kinect()

    functions = {
        'template_test': template_matching_test,
        'find': find_bullseye_with_confirmation
    }

    fn = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in functions else 'template_test'

    functions[fn](sys.argv[2:])

if __name__ == '__main__':
    main()

    while 1:
        if cv.waitKey(10) == 27:
            break

