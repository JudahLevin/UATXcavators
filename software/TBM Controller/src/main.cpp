#include <Arduino.h>
#include "motorControl.cpp"

// Motor & microstep specs
const int stepsPerRev = 1600;  // 200 full steps/rev * 8 microsteps/step

bool isOn = false;
bool isReversed = false;

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

inline void safeWritePin(int pin, int state) {
    digitalWrite(pin, state);
    delayMicroseconds(SETUP_US);
}

void setup() {
    Serial.begin(115200);
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
    // Whenever a character is typed, runs loop body
    if (Serial.available()) {
        String keyword = Serial.readString();
        switch (tolower(keyword.charAt(0))) {
            case 's':
                isOn = !isOn;
                safeWritePin(ENA_PIN, isOn);
                break;
            case 'r':
                isReversed = !isReversed;
                safeWritePin(DIR_PIN, isReversed);
                break;
            case '-':
            case '_':
                if (PULSE_LEN_US < 1000000)
                    PULSE_LEN_US *= 2;
                break;
            case '+':
            case '=':
                if (PULSE_LEN_US > 62)
                    PULSE_LEN_US /= 2;
                break;
            case 'p':
                Serial.printf("on: %d\n reversed: %d\n pulse length: %d us\n\n", isOn, isReversed, PULSE_LEN_US);
                break;
            case 't':
                analogRead(CURR_PIN);
        }
    }

    if (isOn) {
        pulse(PULSE_LEN_US);
    }
}
