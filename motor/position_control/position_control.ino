
// state management
bool enabled = false;
bool motor_1_home = false;
bool motor_2_home = false;

void setup() {
  Serial.begin(9600);

  setupMotorPins();
  setupLimitSwitches();

  printStartMessage();
}

void loop() {
  checkLimitSwitches();
}

void setMotorHome(int motor, bool home) {
  if (!enabled) {
    return;
  }

  if (motor == 1) {
    motor_1_home = home;
    Serial.print("motor 1");
  } else if (motor == 2) {
    motor_2_home = home;
    Serial.print("motor 2");
  }

  Serial.print(" home is now ");
  printPinState(home);

  setMotorPinHome(motor, home? HIGH : LOW);
}

void goToA() {
  if (!motor_1_home || !motor_2_home) {
    return;
  }

  Serial.println("sending motors home");
  writePositionPins(LOW);
}

void goToB() {
  if (!motor_1_home || !motor_2_home) {
    return;
  }

  Serial.println("sending motors to destination");
  writePositionPins(HIGH);
}
