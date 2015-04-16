
// Ramp cycles as percentage between 0 -> 255 for uni mode
// 0 is max clockwise, 127 zero, 255 max ccw for bi mode
#define ZERO_DUTY 127.0
#define SLOW_CW_DUTY 122
#define SLOW_CCW_DUTY 132

// configuration
#define MOTOR_MAX_VEL 300.0 // in rps
#define POS_LIMIT 0.2 // something close to radians

// state management
boolean enabled = false;
boolean inhibited = false;
boolean clockwise = true;

int count = 0;
boolean resting = false;
unsigned long zeroTime = 0;

void setup() {
  Serial.begin(9600);
  
  setupMotorPins();
  setupLimitSwitches();
  
  printStartMessage();
}

void loop() {
  //checkLimitSwitches();
  
  if (resting) {
    writeToMotor(1, ZERO_DUTY);
    writeToMotor(2, ZERO_DUTY);
    if (millis() - zeroTime > 300) {
      resting = false; 
    }
    return;
  }

  int duty_cycle = clockwise? SLOW_CW_DUTY : SLOW_CCW_DUTY; 
  writeToMotor(1, duty_cycle);
  writeToMotor(2, duty_cycle);
  
  if (enabled) {
    float ms = millis();
    float current_vel = ((ZERO_DUTY - duty_cycle) / ZERO_DUTY) * MOTOR_MAX_VEL;
//    Serial.print("current vel: ");
//    Serial.println(current_vel);
    addRiemannPoint(current_vel, ms, 1);
    
    float currentSum = currentRiemannSum();
    
    count += 1;
    
    Serial.print("sum: ");
    Serial.print(currentSum);
    Serial.print("     /     time: ");
    Serial.println(ms);
    
    if (abs(currentSum) >= POS_LIMIT) {
      clockwise = !clockwise;
      resetRiemannSums();
      count = 0;
      zeroTime = millis();
      resting = true;
    }
  }
}

