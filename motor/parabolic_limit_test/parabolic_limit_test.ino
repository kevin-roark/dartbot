
// Ramp cycles as percentage between 0 -> 255 for uni mode
// 0 is max clockwise, 127 zero, 255 max ccw for bi mode
#define ZERO_DUTY 127.5
#define SLOW_CW_DUTY 122
#define SLOW_CCW_DUTY 132

// configuration
#define MOTOR_MAX_VEL 100.0 // in rps

// state management
boolean enabled = false;
boolean inhibited = false;
boolean clockwise = true;

void setup() {
  setupMotorPins();
  setupLimitSwitches();

  Serial.begin(4800);
  
  printStartMessage();
}

void loop() {
  checkLimitSwitches();

  int duty_cycle = clockwise? SLOW_CW_DUTY : SLOW_CCW_DUTY;
  writeToMotor(1, duty_cycle);
  writeToMotor(2, duty_cycle);
  
  float current_vel = ((ZERO_DUTY - duty_cycle) / ZERO_DUTY) * MOTOR_MAX_VEL;
  addRiemannPoint(current_vel, millis());
  Serial.print("sum: ");
  Serial.print(currentRiemannSum());
  Serial.print("     /     time: ");
  Serial.println(millis());
}

