#include <Arduino.h>

// Pin assignments
const int PUL_PIN = 18;
const int DIR_PIN = 19;
const int ENA_PIN = 21;  // ENA− connected here, ENA+ tied to +5V

// Motor & microstep specs
const int stepsPerRev = 1600;  // 200 full steps/rev * 8 microsteps/step

// Timing constants (µs)
const unsigned int SETUP_US = 100;     // DIR must settle before PUL rising edge
unsigned int PULSE_LEN_US = 250;   // keep PUL high for ≥ 2.5 µs

// Length of loop.
unsigned int LOOP_LEN = 3000; // Loop iterates every 3000 microseconds

bool isOn = false;
bool isReversed = false;

// Current rotator task.
int fullTaskLength = 0;
int remainingTaskLength = 0;
unsigned int taskTimeUS = 0;

void pulse(int length) {
    length /= 2;
    // Generate pulses to rotate motor
    digitalWrite(PUL_PIN, HIGH);
    delayMicroseconds(length);  // Adjust for speed
    digitalWrite(PUL_PIN, LOW);
    delayMicroseconds(length);
}

// Unneeded for now
/* 
int getSubtaskLength() {
    if ( remainingTaskLength == 0 ) return 0;
    int maxSubtaskLen = ceil(fullTaskLength * LOOP_LEN / taskTimeUS); 
    return (maxSubtaskLen >= remainingTaskLength) ? maxSubtaskLen : remainingTaskLength;
}
*/

void safeWritePin(int pin, int state) {
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
    // Set ENA to disabled (high)
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
                if (PULSE_LEN_US > 25)
                    PULSE_LEN_US /= 2;
                break;
        }
    }

    if (isOn) {
        pulse(PULSE_LEN_US);
    }
}
