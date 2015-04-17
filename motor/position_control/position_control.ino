
// constants
#define TIME_BEFORE_RELEASE 700

// state management
bool enabled = false;
bool motor_1_home = false;
bool motor_2_home = false;
unsigned long electromagnetReleaseTime = 0;

void setup() {
  Serial.begin(9600);

  setupMotorPins();
  setupLimitSwitches();
  setupElectromagnet();

  printStartMessage();
}

void loop() {
  checkLimitSwitches();
  
  if (electromagnetReleaseTime > 0 && millis() > electromagnetReleaseTime) {
    Serial.println("MAGNET");
    writeElectroMagnet(false);
    electromagnetReleaseTime = 0; 
  }
}

void setMotorHome(int motor, bool on) {
  if (!enabled) {
    return;
  }

  if (motor == 1) {
    motor_1_home = on;
    Serial.print("motor 1");
  } else if (motor == 2) {
    motor_2_home = on;
    Serial.print("motor 2");
  }

  Serial.print(" home is now ");
  printPinState(on);

  setMotorPinHome(motor, on? HIGH : LOW);
}

void goToA() {
//  if (!motor_1_home || !motor_2_home) {
//    return;
//  }

  Serial.println("sending motors home");
  writePositionPins(LOW);  
}

void goToB() {
//  if (!motor_1_home || !motor_2_home) {
//    return;
//  }

  Serial.println("sending motors to destination");
  writePositionPins(HIGH);
  
  electromagnetReleaseTime = millis() + TIME_BEFORE_RELEASE;
}
