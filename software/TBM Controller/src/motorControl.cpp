#ifndef MOTORCONTROL_CPP
#define MOTORCONTROL_CPP

#include "Arduino.h"
#include <cmath>
#include "pins.cpp"

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

const float ALPHA = 0.1;
int V_off = -1;
const int NUM_ADC_READINGS = 100;
double filtCurrent = 0;

const double ADC_MAX = 4095.0;
const double ADC_SCALE = 3.3;
const double SENSITIVITY = 0.04;
const double TORQUE_CONST = 0.714;


void calibrateADC() {
    int sum = 0;
    for (int i = 0; i < NUM_ADC_READINGS; i++) {
        sum += analogRead(CURR_PIN);
        delay(5);
    }
    V_off = (sum / NUM_ADC_READINGS) / ADC_MAX * ADC_SCALE;
}

inline double readMotorVolts() {
    return analogRead(CURR_PIN) / ADC_MAX * ADC_SCALE;
}

inline double readMotorRawAmps() {
    return (readMotorVolts() - V_off) / SENSITIVITY;
}

inline double readMotorFiltAmps() {
    return filtCurrent = (1 - ALPHA) * filtCurrent + ALPHA * readMotorRawAmps();
}

inline double readMotorTorque() {
    return readMotorFiltAmps() * TORQUE_CONST;
}

#endif