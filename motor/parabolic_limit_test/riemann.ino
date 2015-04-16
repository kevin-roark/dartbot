
/// State variables
float running_left_sum = 0;
float running_right_sum = 0;

float prev_value = 0;
float prev_ms = 0;

/// Private functions

float middleRiemannSum() {
  return (running_left_sum + running_right_sum) / 2;
}

/// API

float currentRiemannSum() {
  return middleRiemannSum(); 
}

void addRiemannPoint(float value, int ms) {  
  float ms_delta = ms - prev_ms;
  
  running_left_sum += (ms_delta * prev_value);
  running_right_sum += (ms_delta * value);
  
  prev_value = value;
  prev_ms = ms;
}

void resetRiemannSums() {
  prev_value = 0;
  running_left_sum = 0;
  running_right_sum = 0; 
}
