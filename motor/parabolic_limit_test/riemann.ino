
/// Help
#define MS_NORMALIZER 0.001

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

void addRiemannPoint(float vel, int ms) {  
  float ms_delta = ms - prev_ms;
  
  running_left_sum += (ms_delta * MS_NORMALIZER * prev_vel);
  running_right_sum += (ms_delta * MS_NORMALIZER * vel);
  
  prev_vel = vel;
  prev_ms = ms;
}

void resetRiemannSums() {
  prev_vel = 0;
  running_left_sum = 0;
  running_right_sum = 0; 
}
