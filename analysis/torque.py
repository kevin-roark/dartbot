
from math import sin, cos, pi, sqrt
import operator, csv

# constants

#link lengths in (m)
#l1 = 0.2
#l2 = 0.2
MODEL_L1 = 0.1925
MODEL_L2 = 0.3025

#link / ee masses (in kg)
m1 = 0.48 # mass of link 1
m2 = 0.31 # mass of the coupler

def m3(l2): # mass of link 2
    #return .435483 * l2
    return 0.127

m4 = 0.25 # mass of end-effecter

target_distance = 2.5 # distance to the target in (m)

g = 9.81 # gravity
pi2 = 2 * pi # 2 PI

simulation_seconds = .5
step_granularity = 0.001
delta_t = 0.001

initial_theta1 = pi / 3
initial_theta2 = -pi / 3
initial_omega1 = 0
initial_omega2 = 0
initial_alpha1 = 0 # for test
initial_alpha2 = 0 # for test

release_theta1 = 5.0 * pi / 6
release_angle = pi - release_theta1  # angle with respect to the vertical from the arm release

log_steps = False # true if you wanna see the values at each individual step
log_debug = False
log_link_lengths = False

class BestLinkWrapper():
    def __init__(self, best=100000, lambda1=0, lambda2=0, l1=0, l2=0):
        self.best = best
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.l1 = l1
        self.l2 = l2

    def update(self, best, lambda1, lambda2, l1, l2):
        self.best = best
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.l1 = l1
        self.l2 = l2

    def __str__(self):
        return '{} // l1: {}, l2: {}, lambda1: {}, lambda2: {}'.format(
            self.best, self.l1, self.l2, self.lambda1, self.lambda2)

class LambdaWrapper():
    def __init__(self, time, value):
        self.time = time
        self.value = value

    def __str__(self):
        return '{} at {}s'.format(self.value, self.time)

def drange(start, stop, stepsize):
    r = start
    while r < stop:
        yield r
        r += stepsize

# smallest sum, minimizing max, smallest difference
def find_best_link_lengths():
    start_length = 0.1925
    end_length = 0.4
    granularity = 0.005

    smallest_sum = BestLinkWrapper()
    smallest_max = BestLinkWrapper()
    smallest_difference = BestLinkWrapper()

    for l1 in drange(start_length, end_length, granularity):
        for l2 in drange(start_length, end_length, granularity):
            if log_debug: print 'calculating for l1 = {}, l2 = {}'.format(l1, l2)
            lambda1, lambda2 = find_lambdas(l1, l2)

            summ = lambda1.value + lambda2.value
            if summ < smallest_sum.best:
                smallest_sum.update(summ, lambda1, lambda2, l1, l2)

            maxx = max(lambda1.value, lambda2.value)
            if maxx < smallest_max.best:
                smallest_max.update(maxx, lambda1, lambda2, l1, l2)

            diff = abs(lambda1.value - lambda2.value)
            if diff < smallest_difference.best:
                smallest_difference.update(diff, lambda1, lambda2, l1, l2)

    if log_link_lengths:
        print '\nsmallest sum: {}\n'.format(smallest_sum)
        print 'smallest max: {}\n'.format(smallest_max)
        print 'smallest_difference: {}\n'.format(smallest_difference)

# helper model that is passed around

class TorqueValues():
    def __init__(self, a1=None, a2=None):
        self.theta1 = initial_theta1
        self.theta2 = initial_theta2

        self.omega1 = initial_omega1
        self.omega2 = initial_omega2

        if a1:
            self.alpha1 = a1
        else:
            self.alpha1 = initial_alpha1

        if a2:
            self.alpha2 = a2
        else:
            self.alpha2 = initial_alpha2

        self.theta1s = []
        self.theta2s = []
        self.lambda1s = []
        self.lambda2s = []

# find them lambdas

def find_lambdas(l1, l2, log_lambda_values=False, return_torque_values=False):
    num_steps = int(simulation_seconds / step_granularity)

    if log_lambda_values:
        #print '\n\nstarting {} second simulation with {} second step granularity'.format(simulation_seconds, step_granularity)
        #print 'calculation will take {} steps'.format(num_steps)
        #print 'starting now ...\n\n'
        pass

    # calculate desired accelerations
    d_theta1 = release_theta1 - initial_theta1 # total theta 1 travelled
    v = sqrt((target_distance * g) / (sin(2 * release_angle))) # velocity needed to acheive bullseye
    avg_a1 = (v * v) / (2 * ((sqrt(d_theta1) * (l1 + l2)) + sqrt(1 / d_theta1) * abs(initial_theta2) * l2) ** 2)
    avg_a2 = (avg_a1 * abs(initial_theta2)) / d_theta1

    if log_debug: print 'v_release: ' + str(v)
    if log_debug: print 'Desired angular acceleration 1: {}'.format(avg_a1)
    if log_debug: print 'Desired angular acceleration 2: {}'.format(avg_a2)
    if log_lambda_values: pass# print_sep()

    main_values = TorqueValues(avg_a1, avg_a2)

    for i in range(num_steps + 1):
        t = i * step_granularity
        step(main_values, t, l1, l2)

        if t == 0 and log_debug:
            print 'step 0:'
            print 'theta1 = ' + str(main_values.theta1)
            print 'omega1 = ' + str(main_values.omega1)
            print 'theta2 = ' + str(main_values.theta2)
            print 'omega2 = ' + str(main_values.omega2)

        if log_debug:
            if abs(main_values.theta2) < .005:
                print 'theta2 is {}'.format(main_values.theta2)
                print 'omega1: {} / omega2: {}'.format(main_values.omega1, main_values.omega2)

        if log_steps:
            print 'step {} ({}s): lambda1 = {} / lambda2 = {}'.format(i, t, main_values.lambda1s[i], main_values.lambda2s[i])

    if log_steps:
        print_sep()

    max_lambda1_index, max_lambda1_value = max(enumerate(main_values.lambda1s), key=operator.itemgetter(1))
    max_lambda2_index, max_lambda2_value = max(enumerate(main_values.lambda2s), key=operator.itemgetter(1))

    lambda1_time = max_lambda1_index * step_granularity
    lambda2_time = max_lambda2_index * step_granularity

    if log_lambda_values:
        print 'Found maximum lambda1 at {}s: {}'.format(lambda1_time, max_lambda1_value)
        print 'Found maximum lambda2 at {}s: {}'.format(lambda2_time, max_lambda2_value)

    if return_torque_values:
        return main_values
    else:
        return LambdaWrapper(lambda1_time, max_lambda1_value),  LambdaWrapper(lambda2_time, max_lambda2_value)

def print_sep():
    #print '\n\n#############\n\n'
    pass

def step(t_values, t, l1, l2):
    # update the angles
    if t > 0:
        theta1_0 = t_values.theta1
        omega1_0 = t_values.omega1
        omega2_0 = t_values.omega2
        theta2_0 = t_values.theta2

        if log_debug: print 't = ' + str(t)

        t_values.theta1 = (theta1_0 + (t_values.omega1 * delta_t) + (0.5 * t_values.alpha1 * delta_t * delta_t)) % pi2
        if log_debug: print 'theta1 = ' + str(t_values.theta1)


        t_values.omega1 = omega1_0 + (t_values.alpha1 * delta_t)
        if log_debug: print 'omega1_0 = ' + str(omega1_0)
        if log_debug: print 'omega1 = ' + str(t_values.omega1)


        if theta2_0 > pi2:
            t_values.theta2 = (theta2_0 + (omega2_0 * delta_t) + (0.5 * t_values.alpha2 * delta_t * delta_t)) % pi2
        else:
            t_values.theta2 = (theta2_0 + (omega2_0 * delta_t) + (0.5 * t_values.alpha2 * delta_t * delta_t))
        if log_debug: print 'theta2 = ' + str(t_values.theta2)

        t_values.omega2 = omega2_0 + (t_values.alpha2 * delta_t)
        if log_debug: print 'omega2 = ' + str(t_values.omega2)


    # convenient accessors
    a1 = t_values.alpha1
    a2 = t_values.alpha2
    t1 = t_values.theta1
    t2 = t_values.theta2
    o1 = t_values.omega1
    o2 = t_values.omega2

    # calculate lambdas

    #print 'a1 constant is: ' + str(( l1 * l1 * (7.0 / 12 * m1 + 2 * m2 + m3 + m4 ) +  l1 * l2 * (m3 + 2 * m4) * cos(t2) + m3 * (l1 * l1 + 7.0 / 12 * l2 * l2 ) + m4 * (l1 * l1 + 2 * l2 * l2) ))
    #print 'a2 constant is: ' + str(( l1 * l2 * (0.5 * m3 + m4) * cos(t2) + m3 * (l1 * l1 + 7.0 / 12 * l2 * l2) + m4 * (l1 * l1 + 2 * l2 * l2) ))
    #print 'g constant is: ' + str(l1 * sin(t1) * (0.5 * m1 + m2 + m3 + m4) + l2 * sin(t1 + t2) * (0.5 * m3 + m4))

    #print 'alpha 1 iz ' + str(a1)
    #print 'alpha 2 iz ' + str(a2)

    lambda1 = a1 * ( l1 * l1 * (7.0 / 12 * m1 + 2 * m2 + m3(l2)+ m4 ) +  l1 * l2 * (m3(l2) + 2 * m4) * cos(t2) + m3(l2) * (l1 * l1 + 7.0 / 12 * l2 * l2 ) + m4 * (l1 * l1 + 2 * l2 * l2) ) + \
          a2 * ( l1 * l2 * (0.5 * m3(l2) + m4) * cos(t2) + m3(l2) * (l1 * l1 + 7.0 / 12 * l2 * l2) + m4 * (l1 * l1 + 2 * l2 * l2) ) + \
          o1 * ( -l1 * l2 * (m3(l2) + 2 * m4) * sin(t2) ) + \
          o2 * ( -l1 * l2 * (0.5 * m3(l2) + m4) * sin(t2) ) + \
          g * ( l1 * sin(t1) * (0.5 * m1 + m2 + m3(l2) + m4) + l2 * sin(t1 + t2) * (0.5 * m3(l2) + m4) )

    lambda2 = a1 * ( l1 * l2 * (0.5 * m3(l2) + m4) * cos(t2) + m3(l2) * (l1 * l1 + 7.0 / 12 * l2 * l2) + m4 * (l1 * l1 + 2 * l2 * l2) ) + \
          a2 * ( m3(l2) * (l1 * l1 + 7.0 / 12 * l2 * l2) + m4 * (l1 * l1 + 2 * l2 * l2) ) + \
          o1 * ( -l1 * l2 * (0.5 * m3(l2) + m4) * sin(t2)  ) + \
          o1 * o1 * ( l1 * l2 * (0.5 * m3(l2) + m4) * sin(t2) ) + \
          o1 * o2 * ( l1 * l2 * (0.5 * m3(l2) + m4) * sin(t2) ) + \
          g * ( l2 * (0.5 * m3(l2) + m4) * sin(t1 + t2) )

    if log_debug: print 'lambda 1: ' + str(lambda1)
    if log_debug: print 'lambda 2: ' + str(lambda2)

    t_values.theta1s.append(t_values.theta1)
    t_values.theta2s.append(t_values.theta2)
    t_values.lambda1s.append(lambda1)
    t_values.lambda2s.append(lambda2)

def write_csv(data, filename='out.csv'):
    with open(filename, 'w') as fp:
        csv_writer = csv.writer(fp, delimiter=',')
        csv_writer.writerows(data)

def make_l2_vs_lambda_data():
    csv_data = []
    for l2 in drange(.15, .45, .005):
        lambda1_wrapper, lambda2_wrapper = find_lambdas(MODEL_L1, l2)
        row = [l2, lambda1_wrapper.value, lambda2_wrapper.value]
        csv_data.append(row)
        print 'l2, lambda1, lambda2 = {}'.format(row)
    write_csv(csv_data, 'lambdas.csv')

def make_ideal_link_lambda_theta_data():
    torque_history_values = find_lambdas(MODEL_L1, MODEL_L1, return_torque_values=True)

    csv_data = [['Theta1', 'Theta2', 'Lambda1', 'Lambda2']]
    for i in range(len(torque_history_values.theta1s)):
        t1 = torque_history_values.theta1s[i]
        t2 = torque_history_values.theta2s[i]
        lambda1 = torque_history_values.lambda1s[i]
        lambda2 = torque_history_values.lambda2s[i]
        row = [t1, t2, lambda1, lambda2]
        print 'theta1, theta2, lambda1, lambda2 = {}'.format(row)
        csv_data.append(row)
    write_csv(csv_data, 'lambda_theta.csv')

def main():
    # this finds link lengths and logs them based on different heuristics
    #find_best_link_lengths()

    # this makes l2 vs lambdas csv
    #make_l2_vs_lambda_data()

    # this makes theta vs lambda csv
    #make_ideal_link_lambda_theta_data()

    # this logs the max lambdas at model links
    #find_lambdas(MODEL_L1, MODEL_L2, log_lambda_values=True)

    pass

if __name__ == '__main__':
    main()
