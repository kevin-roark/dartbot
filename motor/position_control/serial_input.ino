
char stepperDir = '0';
char stepperType = '0';

/// SerialEvent called whenever key is pressed, essentially. Runs between loop() calls
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char) Serial.read();
    Serial.println(inChar);
    switch (inChar) {

      // proximal enable control
      case '1':
      case '2':
        setEnabled(1, inChar == '2');
        break;

      // distal enable control
      case '3':
      case '4':
        setEnabled(2, inChar == '4');
        break;

      // position control
      case '5':
        goToA();
        break;
      case '6':
        goToB();
        break;

      // electromagnet control
      case '7':
      case '8':
        writeElectroMagnet(inChar == '8');
        break;

      /// stepper control
      case 'l':
      case 'r':
        stepperDir = inChar;
        break;
      case 's':
      case 'b':
        if (stepperDir == '0') {
          return;
        }
        stepperType = inChar;
        moveStepper(stepperDir, stepperType);
        stepperDir = '0';
        break;
    }
  }
}
