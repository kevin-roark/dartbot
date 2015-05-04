
/// notes
///
/// 1140 encoder counts to get proximal from home (limit-switch defined) to 90 degrees
/// 800 encoder counts per revolution. 0.45 degrees per count
/// 1750 encoder counts for desired proximal end-position (873 to get to release position)
/// 1200 encoder counts for desired distal end-position (685 to get to release position)

// constants
float TIME_BEFORE_RELEASE = 961;

// state management
bool motor_1_enabled = false;
bool motor_2_enabled = false;
bool motor_1_home = false;
bool motor_2_home = false;
unsigned long electromagnetReleaseTime = 0;

void setup() {
  Serial.begin(9600);

  setupMotorPins();
  setupLimitSwitches();
  setupElectromagnet();
  setupStepper();

  printStartMessage();
}

void loop() {
  checkLimitSwitches();

  if (electromagnetReleaseTime > 0 && millis() >= electromagnetReleaseTime) {
    Serial.println("MAGNET");
    writeElectroMagnet(false);
    electromagnetReleaseTime = 0;
  }
}

void setMotorHome(int motor, bool on) {
  if (motor == 1 && !motor_1_enabled) {
    return;
  }

  if (motor == 2 && !motor_2_enabled) {
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

  if (motor_1_home && motor_2_home) {
    writeElectroMagnet(true);
  }
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
