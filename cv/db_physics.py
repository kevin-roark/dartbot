
import sys
from math import sin, cos, pi, sqrt

l1 = 0.1925 # proximal length
l2 = 0.3025 # distal length
g = 9.81

initial_theta1 = 0.8727

release_angle = pi / 6  # with respect to vertical

d_theta1 = 1.7148 # 98.25 degrees
d_theta2 = 0.698 # 40 degrees

# assumes z dist in meters
def final_velocity_needed_for_z(z_dist, yZero):
    gravity_z = g * z_dist
    cos_release_angle = cos(release_angle)

    numerator = gravity_z * gravity_z

    denominator = (cos_release_angle * cos_release_angle) * \
                  (2 * gravity_z * sin(release_angle) / cos_release_angle + \
                   2 * g * yZero)

    v = sqrt(numerator / denominator)

    return v

def proximal_accel_with_final_v(v):
    v_sq = v * v
    total_l = l1 + l2

    big_eq = ((sqrt(d_theta1) * total_l) + sqrt(1 / d_theta1) * abs(d_theta2) * l2)
    big_eq_squared = big_eq * big_eq

    return v_sq / (2 * big_eq)

def distal_accel_with_proximal_accel(proximal_accel):
    return (proximal_accel * abs(d_theta2)) / d_theta1

def proximal_angular_velocity_with_accel(accel):
    omega = sqrt( 2 * accel * d_theta1)
    return omega

def distal_angular_velocity_with_accel(accel):
    omega = sqrt( 2 * accel * d_theta2)
    return omega

def electromagnet_release_time(a1, omega1):
    f = 1.1
    calc_time = ( (1 / f) * sqrt(2 * d_theta1 / a1) ) + ( ((1 - 1 / f) * d_theta1) / omega1 )
    boosted_time = calc_time * 1.36
    return boosted_time

def rads_to_rpm(a):
    return a * 30 / pi

def boost_accel(a):
    return a * 1.1

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

def arm_info_for_target_z(z_dist, height=0.0):
    gain = z_gain_for_target_z(z_dist)
    print '...gaining given z by {}\n'.format(gain)
    gained_z_dist = gain * z_dist

    final_v = final_velocity_needed_for_z(gained_z_dist, height)

    angular_a1 = proximal_accel_with_final_v(final_v)
    angular_a2 = distal_accel_with_proximal_accel(angular_a1)
    angular_v1 = proximal_angular_velocity_with_accel(angular_a1)
    angular_v2 = distal_angular_velocity_with_accel(angular_a2)

    electromagnet_release = electromagnet_release_time(angular_a1, angular_v1)

    a1 = rads_to_rpm(angular_a1)
    v1 = rads_to_rpm(angular_v1)
    a2 = rads_to_rpm(angular_a2)
    v2 = rads_to_rpm(angular_v2)

    boosted_a1 = boost_accel(a1)
    boosted_a2 = boost_accel(a2)

    reduced_a1 = boosted_a1 * 4.024
    reduced_v1 = v1 * 4.024
    reduced_magnet_release = electromagnet_release # should reduce?
    reduced_a2 = boosted_a2 * 5 + boosted_a1
    reduced_v2 = v2 * 5 + v1

    print 'proximal:::'
    print 'accel (with boost): {}'.format(reduced_a1)
    print 'velocity: {}\n'.format(reduced_v1)
    print 'distal:::'
    print 'accel (with boost): {}'.format(reduced_a2)
    print 'velocity: {}\n'.format(reduced_v2)
    print 'electromagnet release time: {}'.format(reduced_magnet_release)

def main():
    args = sys.argv[1:]
    if len(args) < 1:
        print 'u have to give me a z dist'
        return

    z = float(args[0])
    height = float(args[1]) if len(args) > 1 else 0.0

    arm_info_for_target_z(z, height)


if __name__ == '__main__':
    main()
