
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

#########
#### COMPUTER VISION CLASSES
#########

class BullseyeResult(object):
    def __init__(self, corner1, center, corner2, pos):
        self.corner1 = corner1
        self.center = center
        self.corner2 = corner2
        self.pos = pos

class MatchTemplateResult(BullseyeResult):
    def __init__(self, corner1, center, corner2, pos, normalized_image):
        super(MatchTemplateResult, self).__init__(corner1, center, corner2, pos) 
        self.normalized_image = normalized_image


class BullseyeFinder(object):
    def __init__(self, draw=False, test_point=None):
        self.draw = draw
        self.test_point = test_point

    def run(self):
        self.result = self.find_bullseye()
        self.report_bullseye(self.result)

    def find_bullseye(self):
        return None # help me out here 

    def report_bullseye(self, bullseye_result):
        print 'match point:', bullseye_result.center
        print '3d match space:', bullseye_result.pos[0]
        print 'z_info:', bullseye_result.pos[1]

        display_image = rgb_mat
        if self.test_point:  
            print 'test point / real world test loc:'
            print self.test_point
            print real_world_position(self.test_point)

            if draw:
                cv.circle(display_image, self.test_point, 8, (255, 255, 0), 2, 8, 0)

        if self.draw:
            cv.circle(display_image, bullseye_result.center, 10, (0, 0, 255), 2, 4, 0)
            cv.rectangle(display_image, bullseye_result.corner1, bullseye_result.corner2, 0, 2, 8, 0)
 
            # display results in window
            self.window_number = str(random.randint(1000))
            kinect_window = 'kinect image ' + self.window_number
            cv.namedWindow(kinect_window, cv.WINDOW_AUTOSIZE)
            cv.imshow(kinect_window, display_image)


class TemplateMatcher(BullseyeFinder):
    def __init__(self, draw=False, test_point=None, matching_method=cv.TM_SQDIFF):
        super(TemplateMatcher, self).__init__(draw, test_point)
        self.matching_method = matching_method

    # override !
    def find_bullseye(self):
        # get the rgb image from kinect
        rgb_image = get_video()

        # convert rbg image to numpy matrix
        rgb_mat = numpy.asarray(rgb_image[:,:])

        # run the template matching
        match_result = TemplateMatcher.match_template(rgb_mat, DARTBOARD_TEMPLATE, self.matching_method)
        return match_result

    # override !
    def report_bullseye(self, bullseye_result):
        name = TemplateMatcher.matching_method_name(self.matching_method)
        print 'matching method:', self.matching_method, '(' + name + ')'

        super(TemplateMatcher, self).report_bullseye(bullseye_result)

        if self.draw:
            result_window = 'template matching image ' + self.window_number
            cv.namedWindow(result_window, cv.WINDOW_AUTOSIZE)
            cv.imshow(result_window, bullseye_result.normalized_image)

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

        # get real world position of match_loc for fun
        match_center_pos = real_world_position(match_center)

        return MatchTemplateResult(match_loc, match_center, match_corner, match_center_pos, normalized_match_result)

########
### KINECT STUFF
########

def reset_kinect():
    freenect.sync_get_depth()
    freenect.sync_get_video()

def real_world_position(screen_point):
    adjusted_screen_x = screen_point[0] - RGB_WIDTH / 2 # center x should be 0
    adjusted_screen_y = screen_point[1] - RGB_HEIGHT / 2 # center y should be 0

    z_world_struct = get_z_world_depth()[screen_point[0]][screen_point[1]]
    z_world = z_world_struct[1]

    x_world = z_world * adjusted_screen_x / FOCAL_LENGTH_X
    y_world = z_world * adjusted_screen_y / FOCAL_LENGTH_Y
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

def template_matching_test():
    methods = len(MATCHING_METHODS)
    for i in range(methods):
        print '**** test run ', i, ' ****'
        method = MATCHING_METHODS[i] 
        matcher = TemplateMatcher(matching_method=method)
        matcher.run()
        print ''


def main():
    reset_kinect()

    functions = {
        'template_test': template_matching_test
    }

    fn = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in functions else 'template_test'

    functions[fn]()

if __name__ == '__main__':
    main()

    while 1:
        if cv.waitKey(10) == 27:
            break

