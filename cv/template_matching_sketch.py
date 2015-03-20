
import cv2 as cv
import frame_convert
import freenect
import numpy
import os, math, sys, time, random

HORIZONTAL_VIEW_ANGLE = 58.0
VERTICAL_VIEW_ANGLE = 45.0
RGB_WIDTH = 640
RGB_HEIGHT = 480
FOCAL_LENGTH_X = RGB_WIDTH / (2 * math.tan(math.radians(HORIZONTAL_VIEW_ANGLE / 2)))
FOCAL_LENGTH_Y = RGB_HEIGHT / (2 * math.tan(math.radians(VERTICAL_VIEW_ANGLE / 2)))
DART_TEMPLATE_FILE = os.path.dirname(os.path.realpath(__file__)) + '/dartboard_template.png'
DARTBOARD_TEMPLATE = cv.imread(DART_TEMPLATE_FILE)

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

def match_method_prefers_min(match_method):
    return (match_method == cv.TM_SQDIFF or match_method == cv.TM_SQDIFF_NORMED)

def get_depth():
    return frame_convert.pretty_depth_cv(freenect.sync_get_depth()[0])

def get_video():
    # in ros:
    # bayered_image = rgb_image_raw()
    # rgb_image = cv.ctvColor(bayered_image, cv.CV_BAYERGR2RGB)

    # in straight python freenect:
    numpy_vid = freenect.sync_get_video()[0]
    return frame_convert.video_cv(numpy_vid)

class MatchTemplateResult():
    def __init__(self, corner1, center, corner2, pos, normalized_image):
        self.corner1 = corner1
        self.center = center
        self.corner2 = corner2
        self.pos = pos
        self.normalized_image = normalized_image

def match_template(image, template, matching_method=cv.TM_SQDIFF):
    # run the template matching
    match_result = cv.matchTemplate(image, template, matching_method)

    # normalize matched result
    normalized_match_result = cv.normalize(match_result, alpha=0, beta=1, norm_type=cv.NORM_MINMAX, dtype=-1)

    # get that tasty min and max matches (localize the best result)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(normalized_match_result)
    match_loc = min_loc if match_method_prefers_min(matching_method) else max_loc

    # calculate helpful match info
    match_center = (match_loc[0] + template.shape[0] / 2, match_loc[1] + template.shape[1] / 2)
    match_corner = (match_loc[0] + template.shape[0], match_loc[1] + template.shape[1])

    # get real world position of match_loc for fun
    match_center_pos = real_world_position(match_center)

    return MatchTemplateResult(match_loc, match_center, match_corner, match_center_pos, normalized_match_result)

def match_dartboard(draw=False, test_point=None):
    # get the rgb image from kinect
    rgb_image = get_video()

    # convert rbg image to numpy matrix
    rgb_mat = numpy.asarray(rgb_image[:,:])

    # run the template matching
    matching_method = cv.TM_SQDIFF
    match_result = match_template(rgb_mat, DARTBOARD_TEMPLATE, matching_method)

    print 'matching method: ', matching_method
    print 'match point: ', match_result.center
    print '3d match space: ', match_result.pos[0]
    print 'z_info: ', match_result.pos[1]

    display_image = rgb_mat
    if test_point:  
        print 'test point / real world test loc:'
        print test_point
        print real_world_position(test_point)

        if draw:
            cv.circle(display_image, test_point, 8, (255, 255, 0), 2, 8, 0)

    if draw:
        cv.circle(display_image, match_result.center, 10, (0, 0, 255), 2, 4, 0)
        cv.rectangle(display_image, match_result.corner1, match_result.corner2, 0, 2, 8, 0)
      
        # display results in window
        r = str(random.randint(1000))
        kinect_window = 'kinect image ' + r
        result_window = 'template matching image ' + r
        cv.namedWindow(kinect_window, cv.WINDOW_AUTOSIZE)
        cv.namedWindow(result_window, cv.WINDOW_AUTOSIZE)
        cv.imshow(kinect_window, display_image)
        cv.imshow(result_window, match_result.normalized_image)

def main():
    reset_kinect()

    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 5

    for i in range(runs):
        print '**** test run ', i, ' ****'
        match_dartboard()
        print ''

if __name__ == '__main__':
    main()

    while 1:
        if cv.waitKey(10) == 27:
            break

