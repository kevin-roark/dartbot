#define PWM_ZERO_VEL 127
#define PWM_MAX_CW_VEL 0
#define PWM_MAX_CCW_VEL 255

// pin configuration
#define motorPin 9
#define enablePin 2
#define inhibitPin 4

// behavior configuration
int rampTime = 2000; // ms
int sustainTime = 5000; // ms
int timeBetweenLoops = 2000; //ms
#define clockwise false
#define shouldLoop true
#define shouldPrint true
#define enabled false

// state management
int rampStepDelay = rampTime / PWM_ZERO_VEL;
int cyclesCompleted = 0;

void setup() {
  pinMode(motorPin, OUTPUT);
  pinMode(enablePin, OUTPUT);
  pinMode(inhibitPin, OUTPUT);
  
  digitalWrite(enablePin, enabled? HIGH : LOW);
  
  Serial.begin(4800);
}

void loop() {  
  if (!shouldLoop && cyclesCompleted > 0) {
    return; // get out of here! 
  }
  
  int pwm = PWM_ZERO_VEL;
  
  // ramp from 0 -> max velocity
  int rampUpIncrement = clockwise? -1 : +1;
  int rampUpLimit = clockwise? PWM_MAX_CW_VEL : PWM_MAX_CCW_VEL;
  while (true) {
    analogWrite(motorPin, pwm);
    printRampingUp(pwm);
    delay(rampStepDelay);
    
    pwm += rampUpIncrement;
    if (pwm == rampUpLimit) {
      break; 
    }
  }
  
  pwm -= rampUpIncrement; // we never want to actually be at the limits
  
  // sustain
  if (shouldPrint) {
    Serial.print("sustaining with pwm ");
    Serial.println(pwm);
  }
  delay(sustainTime);
  
  // ramp from max velocity -> 0
  int rampDownIncrement = clockwise ? +1 : -1;
  while (true) {
    analogWrite(motorPin, pwm);
    if (shouldPrint) {
      Serial.print("ramping down: ");
      Serial.println(pwm);
    }
    delay(rampStepDelay);
    
    pwm += rampDownIncrement;
    if (pwm == PWM_ZERO_VEL) {
      break; 
    }
  }
  
  analogWrite(motorPin, PWM_ZERO_VEL);
  cyclesCompleted += 1;
  delay(timeBetweenLoops);
}

void printRampingUp(int val) {
  if (shouldPrint) {
    Serial.print("ramping up: ");
    Serial.println(val);
  }
}

