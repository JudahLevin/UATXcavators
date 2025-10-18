#include <Arduino.h>

// Pin assignments
const int PUL_PIN = 18;
const int DIR_PIN = 19;
const int ENA_PIN = 21;  // ENA− connected here, ENA+ tied to +5V

// Motor & microstep specs
const int stepsPerRev = 1600;  // 200 full steps/rev * 8 microsteps/step

// Timing constants (µs)
const unsigned int ENA_SETUP_US = 5;     // ENA must settle before DIR in single-pulse mode
const unsigned int DIR_SETUP_US = 5;     // DIR must settle before PUL rising edge
const unsigned int PULSE_HIGH_US = 500;   // keep PUL high for >= 2.5 us
const unsigned int PULSE_LOW_US = 500;    // low time between pulses

// Current rotator task.
int fullTaskLength = 0;
int remainingTaskLength = 0;
unsigned int taskTimeUS = 0;

// Length of loop.
unsigned int LOOP_LEN = 3000; // Loop iterates every 3000 microseconds

void pulse(int highDur, int lowDur) {
    // Generate pulses to rotate motor
    digitalWrite(PUL_PIN, HIGH);
    delayMicroseconds(highDur);  // Adjust for speed
    digitalWrite(PUL_PIN, LOW);
    delayMicroseconds(lowDur);
}

int getSubtaskLength() {
    if ( remainingTaskLength == 0 ) return 0;
    int maxSubtaskLen = ceil(fullTaskLength * LOOP_LEN / taskTimeUS); 
    return (maxSubtaskLen >= remainingTaskLength) ? maxSubtaskLen : remainingTaskLength;
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
    // Set ENA to enabled (low)
    digitalWrite(ENA_PIN, LOW);
}

void loop() {
    // Whenever a character is typed, runs loop body
    while (!Serial.available())
        delay(100);
    Serial.read();
    // String keyword = Serial.readStringUntil('\n');



    // Ensure driver is enabled
    digitalWrite(ENA_PIN, LOW);
    delayMicroseconds(ENA_SETUP_US);

    // Spin one revolution forward
    Serial.println("Forward");
    digitalWrite(DIR_PIN, HIGH);
    delayMicroseconds(DIR_SETUP_US);

    for (int i = 0; i < stepsPerRev; i++) {
        pulse(PULSE_HIGH_US, PULSE_LOW_US);
    }
    delay(2000);

    // Spin one revolution backward
    Serial.println("Reverse");
    // ENA is already low (enabled)
    digitalWrite(DIR_PIN, LOW);
    delayMicroseconds(DIR_SETUP_US);

    for (int i = 0; i < stepsPerRev; i++) {
        pulse(PULSE_HIGH_US, PULSE_LOW_US);
    }
    delay(1000);
}
