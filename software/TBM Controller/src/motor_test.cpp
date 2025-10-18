#include <Arduino.h>

// ========================= STEPPER MOTOR TEST =========================
// Wiring (matches your current setup):
// COMMON GND SETUP (all “–” pins share same ground line)
//
// WHITE:  GND (3)  -> ENA−
// RED:    IO5 (27) -> ENA+
//
// YELLOW: GND (3)  -> DIR−
// ORANGE: IO4 (26) -> DIR+
//
// BLACK:  GND (3)  -> PUL−
// PURPLE: IO2 (25) -> PUL+
// ======================================================================

// Pin assignments
const int PUL_PIN = 18;
const int DIR_PIN = 19;
const int ENA_PIN = 21;  // ENA− connected here, ENA+ tied to +5V

// Motor & microstep specs
const int stepsPerRev = 1600;  // 1.8° × 1/8 microstep

// Timing constants (µs)
const unsigned int ENA_SETUP_US = 5;     // ENA must settle before DIR in single-pulse mode
const unsigned int DIR_SETUP_US = 5;     // DIR must settle before PUL rising edge
const unsigned int PULSE_HIGH_US = 500;   // keep PUL high for ≥ 2.5 µs
const unsigned int PULSE_LOW_US = 500;    // low time between pulses

// Current rotator task.
int taskLength = 0;
unsigned int taskTime = 0;

// Length of loop.
unsigned int LOOP_LEN = 3000; // Loop iterates every 3000 microseconds

void pulse(int highDur, int lowDur) {
    // 🌀 Generate pulses to rotate motor
    digitalWrite(PUL_PIN, HIGH);
    delayMicroseconds(highDur);  // Adjust for speed
    digitalWrite(PUL_PIN, LOW);
    delayMicroseconds(lowDur);
}

int subtaskLength() {

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
