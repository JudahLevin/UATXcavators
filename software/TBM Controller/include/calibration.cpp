#ifndef CALIBRATION_CPP
#define CALIBRATION_CPP

#include "motorControl.cpp"

bool calibrated = false;
void calibrateAll();

void calibrateADC() {
    int sum = 0;
    for (int i = 0; i < NUM_ADC_READINGS; i++) {
        sum += analogRead(CURR_PIN);
        delay(5);
    }
    V_off = (sum / NUM_ADC_READINGS) / ADC_MAX * ADC_SCALE;

    Serial.printf("Motor sensor calibrated\n");
}

inline void calibrateIfNeeded() {
    if (!calibrated) {
        calibrateAll();
        calibrated = true;
    }
}

void calibrateAll() {
    calibrateADC();
    Serial.printf("Ready\n\n");
}

#endif