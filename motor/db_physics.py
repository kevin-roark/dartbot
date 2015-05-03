
import sys
from math import sin, cos, pi, sqrt

l1 = 0.1925 # proximal length
l2 = 0.3025 # distal length

initial_theta1 = 0.8727 #pi / 3
initial_theta2 = -0.698 #-pi / 3

release_theta1 = 5.0 * pi / 6
release_angle = pi - release_theta1  # angle with respect to the vertical from the arm release

d_theta1 = release_theta1 - initial_theta1 # total theta 1 travelled

# assumes z dist in meters
def velocity_needed_for_z(z_dist):
    gravity_z = 9.81 * z_dist
    double_release_angle = 2 * release_angle
    v = sqrt(gravity_z / sin(double_release_angle))
    return v

def proximal_accel_with_v(v):
    v_sq = v * v
    total_l = l1 + l2

    big_eq = ((sqrt(d_theta1) * total_l) + sqrt(1 / d_theta1) * abs(initial_theta2) * l2)
    big_eq_squared = big_eq * big_eq

    return v_sq / (2 * big_eq)

def distal_accel_with_proximal_accel(proximal_accel):
    return (proximal_accel * abs(initial_theta2)) / d_theta1

def arm_info_for_target_z(z_dist):
    vel = velocity_needed_for_z(z_dist)
    a1 = proximal_accel_with_v(vel)
    a2 = distal_accel_with_proximal_accel(a1)

    print 'velocity: {}'.format(vel)
    print 'proximal accel: {}'.format(a1)
    print 'distal accel: {}'.format(a2)

def main():
    args = sys.argv[1:]
    if len(args) < 1:
        print 'u have to give me a z dist'
        return

    z = float(args[0])
    arm_info_for_target_z(z)


if __name__ == '__main__':
    main()


