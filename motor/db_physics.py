
import sys
from math import sin, cos, pi, sqrt

l1 = 0.1925 # proximal length
l2 = 0.3025 # distal length

initial_theta1 = 0.8727
initial_theta2 = -0.698

release_theta1 = 5.0 * pi / 6
release_angle = pi - release_theta1  # angle with respect to the vertical from the arm release

release_theta2 = 5.0 * pi / 6

d_theta1 = release_theta1 - initial_theta1 # total theta 1 traveled
d_theta2 = release_theta2 - initial_theta2 

# assumes z dist in meters
def final_velocity_needed_for_z(z_dist):
    gravity_z = 9.81 * z_dist
    double_release_angle = 2 * release_angle
    v = sqrt(gravity_z / sin(double_release_angle))
    return v

def proximal_accel_with_final_v(v):
    v_sq = v * v
    total_l = l1 + l2

    big_eq = ((sqrt(d_theta1) * total_l) + sqrt(1 / d_theta1) * abs(initial_theta2) * l2)
    big_eq_squared = big_eq * big_eq

    return v_sq / (2 * big_eq)

def distal_accel_with_proximal_accel(proximal_accel):
    return (proximal_accel * abs(initial_theta2)) / d_theta1

def proximal_angular_velocity_with_accel(accel):
    omega = sqrt( 2 * accel * d_theta1)
    return omega

def distal_angular_velocity_with_accel(accel):
    omega = sqrt( 2 * accel * d_theta2)
    return omega

def arm_info_for_target_z(z_dist):
    final_v = final_velocity_needed_for_z(z_dist)
    a1 = proximal_accel_with_final_v(final_v)
    a2 = distal_accel_with_proximal_accel(a1)
    v1 = proximal_angular_velocity_with_accel(a1)
    v2 = distal_angular_velocity_with_accel(a2)

    print 'proximal accel: {}'.format(a1)
    print 'distal accel: {}'.format(a2)
    print 'proximal velocity: {}'.format(v1)
    print 'distal velocity: {}'.format(v2)

def main():
    args = sys.argv[1:]
    if len(args) < 1:
        print 'u have to give me a z dist'
        return

    z = float(args[0])
    arm_info_for_target_z(z)


if __name__ == '__main__':
    main()


