#include <Arduino.h>
#include "motorControl.cpp"
#include "pins.cpp"
#include "calibration.cpp"

bool isOn = false;
bool isReversed = false;
double torque = 0.0;

// Unneeded for now
/*
// Current rotator task.
int fullTaskLength = 0;
int remainingTaskLength = 0;
unsigned int taskTimeUS = 0;


int getSubtaskLength() {
    if ( remainingTaskLength == 0 ) return 0;
    int maxSubtaskLen = ceil(fullTaskLength * LOOP_LEN / taskTimeUS); 
    return (maxSubtaskLen >= remainingTaskLength) ? maxSubtaskLen : remainingTaskLength;
}
*/

void setup() {
    Serial.begin(115200);
    analogReadResolution(12);
    delay(1000);
    Serial.println("Motor test with ENA control");

    pinMode(PUL_PIN, OUTPUT);
    pinMode(DIR_PIN, OUTPUT);
    pinMode(ENA_PIN, OUTPUT);

    // Idle states
    digitalWrite(PUL_PIN, LOW);
    digitalWrite(DIR_PIN, LOW);
    digitalWrite(ENA_PIN, HIGH);
}

void loop() {
    torque = readMotorTorque();

    // Whenever a character is typed, runs loop body
    if (Serial.available()) {
        String keyword = Serial.readString();
        switch (tolower(keyword.charAt(0))) {
            case 'c':
                calibrateAll();
                break;
            case 's':
                calibrateIfNeeded();
                isOn = !isOn;
                safeWritePin(ENA_PIN, isOn);
                break;
            case 'r':
                calibrateIfNeeded();
                isReversed = !isReversed;
                safeWritePin(DIR_PIN, isReversed);
                break;
            case '-':
            case '_':
                calibrateIfNeeded();
                if (PULSE_LEN_US < 1000000)
                    PULSE_LEN_US *= 2;
                break;
            case '+':
            case '=':
                calibrateIfNeeded();
                if (PULSE_LEN_US > 62)
                    PULSE_LEN_US /= 2;
                break;
            case 'p':
                calibrateIfNeeded();
                Serial.printf("on: %d\n reversed: %d\n pulse length: %d us\n\n", isOn, isReversed, PULSE_LEN_US);
                break;
            case 't':
                calibrateIfNeeded();
                Serial.printf("torque: %.2f N*m\n\n", torque);
                break;
        }
    }

    if (isOn) {
        pulse(PULSE_LEN_US);
    }
}
