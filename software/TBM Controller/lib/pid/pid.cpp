// License:
// Thou shalt not steal. (Exodus 20:15)

#ifndef PID_CPP
#define PID_CPP

#include "pid.hpp"
#include "Arduino.h"

pid::pid() : 
    dt(1.0),
    setpoint(1.0),
    last_error(0.0),
    hi(std::numeric_limits<double>::infinity()),
    lo(-std::numeric_limits<double>::infinity()) {
    k_p = k_i = k_d = 1.0;
}

pid::pid(double k_p, double k_i, double k_d, double dt, double setpoint, double hi, double lo, double initial) : 
    dt(dt),
    setpoint(setpoint),
    last_error(initial),
    hi(std::numeric_limits<double>::infinity()), 
    lo(-std::numeric_limits<double>::infinity()) {
    this->k_p = k_p;
    this->k_i = k_i;
    this->k_d = k_d;
    last_error = initial;
}

double pid::getPIDscore(double pv) {
    double score;
    double error = setpoint - pv;

    // P
    score += (k_p * error);

    // I
    accumulator += (last_error + error) / 2 * dt;
    score += (k_i * accumulator);

    // D
    score += (k_d * (last_error - error) / dt);

    return score;
}

void pid::test(double bias, double overshoot) {
    double dx;

    double pv = 0;
    for (int i = 0; i < 100; i++) {
        dx = this->getPIDscore(pv);
        Serial.printf("val: %.2f, inc: %.2f \n", pv, dx);
        pv += (dx * overshoot + bias);
    }
}

#endif