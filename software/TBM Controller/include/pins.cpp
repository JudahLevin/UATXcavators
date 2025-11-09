#ifndef PINS_CPP
#define PINS_CPP

const unsigned int SETUP_US = 100;     // DIR must settle before PUL rising edge

// Pin assignments
const int PUL_PIN = 18;
const int DIR_PIN = 19;
const int ENA_PIN = 21;  // ENA− connected here, ENA+ tied to +5V
const int CURR_PIN = 34;

inline void safeWritePin(int pin, int state) {
    digitalWrite(pin, state);
    delayMicroseconds(SETUP_US);
}

#endif