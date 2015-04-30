
// optical limit switch config:
// anode (orange) should wire to a 250 ohm resistor, the other end of the resistor to a arduino output pin.
// cathode (green) should wire to a arduino ground pin.
// collector (white) should wire to pullup digital input.
// emitter (blue) wires to arduino ground pin.

/// Configuration
#define proximalHomeOpticalLimitSwitch_pin 12
#define proximalSafetyLimitSwitch_pin 13
#define distalHomeOpticalLimitSwitch_pin 8
#define distalSafetyLimitSwitch_pin 7

/// State management
bool setProximalHome = false;
bool setDistalHome = false;

/// API
void setupLimitSwitches() {
  pinMode(proximalHomeOpticalLimitSwitch_pin, INPUT);
  pinMode(distalHomeOpticalLimitSwitch_pin, INPUT);

  pinMode(proximalSafetyLimitSwitch_pin, INPUT_PULLUP);
  pinMode(distalSafetyLimitSwitch_pin, INPUT_PULLUP);
}

void checkLimitSwitches() {
  // proximal home switch
  if (!setProximalHome && digitalRead(proximalHomeOpticalLimitSwitch_pin) == HIGH) {
    setMotorHome(1, true);
    Serial.println("proximal motor is home");
    setProximalHome = true;
  }

  // distal home switch
  if (!setDistalHome && digitalRead(distalHomeOpticalLimitSwitch_pin) == HIGH) {
    setMotorHome(2, true);
    Serial.println("distal motor is home");
    setDistalHome = true;
  }

  // proximal safety switch
  if (digitalRead(proximalSafetyLimitSwitch_pin) == LOW) {
    setEnabled(false);
    Serial.print("SAFETY LIMIT SWITCH HIT: ");
    Serial.println(proximalSafetyLimitSwitch_pin);
  }

  // distal safety switch
  if (digitalRead(distalSafetyLimitSwitch_pin) == LOW) {
    setEnabled(false);
    Serial.print("SAFETY LIMIT SWITCH HIT: ");
    Serial.println(distalSafetyLimitSwitch_pin);
  }
}
