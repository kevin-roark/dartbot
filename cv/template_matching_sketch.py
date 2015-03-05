
import cv2 as cv
import frame_convert
import freenect

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
dart_template = cv.imread('./dartboard_template.png')

# get rgb camera info
#rgb_info = rgb_camera_info()
#rgb_width = rgb_info.width
#rgb_height = rgb_info.height

# get the rgb image from kinect
rgb_image = get_video()

# copy rgb image to show in the window later
display_image = rgb_image.clone()

# run the template matching
matching_method = cv.TM_SQDIFF_NORMED
match_result = cv.matchTemplate(rgb_image, dart_template, matching_method)

# normalize matched result
normalized_match_result = cv.normalize(match_result, alpha=0, beta=1, norm_type=cv.NORM_MINMAX, dtype=-1)

# get that tasty min and max matches (localize the best result)
min_val, max_val, min_loc, max_loc = cv.minMaxLoc(normalized_match_result)

match_loc = min_loc if match_method_prefers_min(matching_method) else max_loc

# draw rectangle around the match area
match_point = cv.Point(match_loc.x + dart_template.cols, match_loc.y + dart_template.rows)
cv.rectangle(display_image, match_loc, match_point, cv.Scalar(0), 2, 8, 0)
cv.rectangle(normalized_match_result, match_loc, match_point, cv.Scalar(0), 2, 8, 0)

# display results in window
cv.imshow(kinect_window, display_image)
cv.imshow(result_window, normalized_match_result)
