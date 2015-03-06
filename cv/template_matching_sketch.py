
import cv2 as cv
import frame_convert
import freenect
import numpy
import os
import math

HORIZONTAL_VIEW_ANGLE = 57.0
VERTICAL_VIEW_ANGLE = 43.0
RGB_WIDTH = 640
RGB_HEIGHT = 480
FOCAL_LENGTH_X = RGB_WIDTH / (2 * math.tan(math.radians(HORIZONTAL_VIEW_ANGLE / 2)))
FOCAL_LENGTH_Y = RGB_HEIGHT / (2 * math.tan(math.radians(VERTICAL_VIEW_ANGLE / 2)))

def real_world_position(screen_point):
    adjusted_screen_x = screen_point[0] - RGB_WIDTH / 2 # center x should be 0
    adjusted_screen_y = screen_point[1] - RGB_HEIGHT / 2 # center y should be 0

    z_world = get_z_world_depth()[screen_point[0]][screen_point[1]]

    x_world = z_world * adjusted_screen_x / FOCAL_LENGTH_X
    y_world = z_world * adjusted_screen_y / FOCAL_LENGTH_Y
    return (x_world, y_world, z_world)

def get_z_world_depth():
    depth_mat = freenect.sync_get_depth()[0]
    print depth_mat # TODO: this function
    return depth_mat

def match_method_prefers_min(match_method):
    return match_method == cv.TM_SQDIFF or match_method == cv.TM_SQDIFF_NORMED

def get_depth():
    return frame_convert.pretty_depth_cv(freenect.sync_get_depth()[0])

def get_video():
    # in ros:
    # bayered_image = rgb_image_raw()
    # rgb_image = cv.ctvColor(bayered_image, cv.CV_BAYERGR2RGB)

    # in straight python freenect:
    return frame_convert.video_cv(freenect.sync_get_video()[0])

# UI windows
kinect_window = 'kinect image'
result_window = 'result image'
cv.namedWindow(kinect_window, cv.WINDOW_AUTOSIZE)
cv.namedWindow(result_window, cv.WINDOW_AUTOSIZE)

# load the dart template
template_file = os.path.dirname(os.path.realpath(__file__)) + '/dartboard_template.png'
dart_template = cv.imread(template_file)

# get the rgb image from kinect
rgb_image = get_video()

# convert rbg image to numpy matrix
rgb_mat = numpy.asarray(rgb_image[:,:])

# copy rgb image to show in the window later
display_image = rgb_mat # do i need to clone?

# run the template matching
matching_method = cv.TM_SQDIFF_NORMED
match_result = cv.matchTemplate(rgb_mat, dart_template, matching_method)

# normalize matched result
normalized_match_result = cv.normalize(match_result, alpha=0, beta=1, norm_type=cv.NORM_MINMAX, dtype=-1)

# get that tasty min and max matches (localize the best result)
min_val, max_val, min_loc, max_loc = cv.minMaxLoc(normalized_match_result)

match_loc = min_loc if match_method_prefers_min(matching_method) else max_loc

# draw rectangle around the match area
match_point = (match_loc[0] + dart_template.shape[0], match_loc[1] + dart_template.shape[1]) # outside of python use cv.Point, rows, and cols
cv.rectangle(display_image, match_loc, match_point, 0, 2, 8, 0)
cv.rectangle(normalized_match_result, match_loc, match_point, 0, 2, 8, 0)

# get real world position of match_loc for fun
real_world_match_loc = real_world_position(match_loc)
print real_world_match_loc

# display results in window
cv.imshow(kinect_window, display_image)
cv.imshow(result_window, normalized_match_result)

while 1:
  if cv.waitKey(10) == 27:
        break
