
/// Configuration
#define motor1BacksideLimitSwitch_pin 12
#define motor1NearsideLimitSwitch_pin 13
#define motor2BacksideLimitSwitch_pin A1
#define motor2NearsideLimitSwitch_pin A2

#define minDepressionTime 200

/// State management
int limitPinWaitingForDepress = 0;
unsigned long lastLimitSwitchTime = 0;

/// API
void setupLimitSwitches() {
  pinMode(motor1BacksideLimitSwitch_pin, INPUT_PULLUP);
  pinMode(motor1NearsideLimitSwitch_pin, INPUT_PULLUP);
  pinMode(motor2BacksideLimitSwitch_pin, INPUT_PULLUP);
  pinMode(motor2NearsideLimitSwitch_pin, INPUT_PULLUP);
}

void checkLimitSwitches() {
  if (limitPinWaitingForDepress == 0) {
    if (digitalRead(motor1BacksideLimitSwitch_pin) == LOW) {
      activateLimitPin(motor1BacksideLimitSwitch_pin);
    }
    else if (digitalRead(motor1NearsideLimitSwitch_pin) == LOW) {
      activateLimitPin(motor1NearsideLimitSwitch_pin);
    }
    else if (digitalRead(motor2BacksideLimitSwitch_pin) == LOW) {
      activateLimitPin(motor2BacksideLimitSwitch_pin);
    }
    else if (digitalRead(motor2NearsideLimitSwitch_pin) == LOW) {
      activateLimitPin(motor2NearsideLimitSwitch_pin);
    }
  }
  else if (digitalRead(limitPinWaitingForDepress) == HIGH && millis() - lastLimitSwitchTime > minDepressionTime) {
    deactivateLimitPin();
  }
}

void activateLimitPin(int pinNumber) {
  Serial.print("limit switch pressed: ");
  Serial.println(pinNumber);

  limitPinWaitingForDepress = pinNumber;
  clockwise = !clockwise;
  resetRiemannSums();

  lastLimitSwitchTime = millis();
}

void deactivateLimitPin() {
  limitPinWaitingForDepress = 0;
  Serial.println("i am depressed!!");
}
