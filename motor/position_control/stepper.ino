//////////////////////////////////////////////////////////////////
//DARTBot Stepper Test
//EasyStepper
//use rotate and/or rotateDeg to controll stepper motor
//speed is any number from .01 -> 1 with 1 being fastest -
//Slower Speed == Stronger movement
/////////////////////////////////////////////////////////////////

/// Pins

#define dirPin A1
#define stepPin A2

/// API

void setupStepper() {
  pinMode(dirPin, OUTPUT);
  pinMode(stepPin, OUTPUT);

  digitalWrite(stepPin, LOW);  
}

void moveStepperLeft() {
  stepperRotateDeg(-1.5, 0.01);
}

void moveStepperRight() {
  stepperRotateDeg(1.5, 0.01);
}

void stepperRotate(int steps, float speed) {
  //rotate a specific number of microsteps (8 microsteps per step) - (negitive for reverse movement)
  //speed is any number from .01 -> 1 with 1 being fastest - Slower is stronger
  int dir = (steps > 0)? HIGH:LOW;
  steps = abs(steps);

  digitalWrite(dirPin,dir);

  float usDelay = (1/speed) * 210;

  for(int i=0; i < steps; i++){
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(usDelay);

    digitalWrite(stepPin, LOW);
    delayMicroseconds(usDelay);
  }
}

void stepperRotateDeg(float deg, float speed) {
  //rotate a specific number of degrees (negitive for reverse movement)
  //speed is any number from .01 -> 1 with 1 being fastest - Slower is stronger
  int dir = (deg > 0)? HIGH:LOW;
  digitalWrite(dirPin,dir);

  int steps = abs(deg)*(1/0.225);
  float usDelay = (1/speed) * 210;

  for(int i=0; i < steps; i++){
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(usDelay);

    digitalWrite(stepPin, LOW);
    delayMicroseconds(usDelay);
  }
}
