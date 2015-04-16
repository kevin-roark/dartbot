
/// Help
#define TIME_NORMALIZER (0.001 * 0.1047) // ms and rpm -> rps
#define MOTOR1_REDUCTION_RATIO 0.25
#define MOTOR2_REDUCTION_RATIO 0.2

/// State variables
float running_left_sum = 0;
float running_right_sum = 0;

float prev_vel = 0;
float prev_ms = 0;

/// Private functions
float middleRiemannSum() {
  return (running_left_sum + running_right_sum) / 2;
}

/// API
float currentRiemannSum() {
  return middleRiemannSum(); 
}

void addRiemannPoint(float vel, int ms, int motor) {  
  float ms_delta = ms - prev_ms;
  float rr = motor == 1 ? MOTOR1_REDUCTION_RATIO : MOTOR2_REDUCTION_RATIO;
  
  running_left_sum += (ms_delta * TIME_NORMALIZER * prev_vel * rr);
  running_right_sum += (ms_delta * TIME_NORMALIZER * vel * rr);
  
  prev_vel = vel;
  prev_ms = ms;
}

void resetRiemannSums() {
  running_left_sum = 0;
  running_right_sum = 0; 
}
