#include "Arduino.h"

// Pin assignments
const int PUL_PIN = 18;
const int DIR_PIN = 19;
const int ENA_PIN = 21;  // ENA− connected here, ENA+ tied to +5V
const int CURR_PIN = 34;

// Timing constants (µs)
const unsigned int SETUP_US = 100;     // DIR must settle before PUL rising edge
unsigned int PULSE_LEN_US = 250;   // keep PUL high for ≥ 2.5 µs

inline void pulse(int length) {
    int highLen = length / 2;
    // Generate pulses to rotate motor
    digitalWrite(PUL_PIN, HIGH);
    delayMicroseconds(highLen);  // Adjust for speed
    digitalWrite(PUL_PIN, LOW);
    delayMicroseconds(highLen - length);
}