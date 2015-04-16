
/// Configuration
#define firstLimitSwitch_pin 13
#define secondLimitSwitch_pin 12
#define minDepressionTime 200

/// State management
int limitPinWaitingForDepress = 0;
unsigned long lastLimitSwitchTime = 0;

/// API
void setupLimitSwitches() {
  pinMode(firstLimitSwitch_pin, INPUT_PULLUP);
  pinMode(secondLimitSwitch_pin, INPUT_PULLUP);
}

void checkLimitSwitches() {  
  int firstLimit = digitalRead(firstLimitSwitch_pin);
  int secondLimit = digitalRead(secondLimitSwitch_pin);
  int waitingForDepressLimit = (limitPinWaitingForDepress == firstLimitSwitch_pin ? firstLimit : secondLimit);
  
  if (limitPinWaitingForDepress == 0) {
    if (firstLimit == LOW) {
      activateLimitPin(firstLimitSwitch_pin);
    }
    else if (secondLimit == LOW) {
      activateLimitPin(secondLimitSwitch_pin);
    }
  }
  else if (waitingForDepressLimit == HIGH && millis() - lastLimitSwitchTime > minDepressionTime) {
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
