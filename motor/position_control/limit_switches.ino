
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
    activateLimitPin(proximalHomeOpticalLimitSwitch_pin);
    setProximalHome = true;
  }

  // distal home switch
  if (!setDistalHome && digitalRead(distalHomeOpticalLimitSwitch_pin) == HIGH) {
    activateLimitPin(distalHomeOpticalLimitSwitch_pin);
    setDistalHome = true;
  }

  // safety switches
  if (digitalRead(proximalSafetyLimitSwitch_pin) == LOW) {
    activateLimitPin(proximalSafetyLimitSwitch_pin);
  }
  if (digitalRead(distalSafetyLimitSwitch_pin) == LOW) {
    activateLimitPin(distalSafetyLimitSwitch_pin);
  }
}

void activateLimitPin(int pinNumber) {
  Serial.print("limit switch pressed: ");
  Serial.println(pinNumber);

  switch (pinNumber) {
    case proximalHomeOpticalLimitSwitch_pin:
      setMotorHome(1, true);
      break;

    case distalHomeOpticalLimitSwitch_pin:
      setMotorHome(2, true);
      break;

    case proximalSafetyLimitSwitch_pin:
    case distalSafetyLimitSwitch_pin:
      setEnabled(false);
      break;

    default:
      break;
  }

  safetyLimitPinWaitingForDepress = pinNumber;
}
