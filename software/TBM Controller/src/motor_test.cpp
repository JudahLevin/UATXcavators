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

#define PUL_PIN 2   // Purple wire → PUL+
#define DIR_PIN 4   // Orange wire → DIR+
#define ENA_PIN 5   // Red wire → ENA+

void print_rad_to_deg(float radians) {
    Serial.printf("%.2f deg", radians * RAD_TO_DEG);
}

void motorPulse(int wavelengthMicroseconds) {
    // 🌀 Generate pulses to rotate motor
    digitalWrite(PUL_PIN, HIGH);
    delayMicroseconds(wavelengthMicroseconds / 2);  // Adjust for speed
    digitalWrite(PUL_PIN, LOW);
    delayMicroseconds(wavelengthMicroseconds / 2);
}

void setup() {
    Serial.begin(115200);
    pinMode(PUL_PIN, OUTPUT);
    pinMode(DIR_PIN, OUTPUT);
    pinMode(ENA_PIN, OUTPUT);

    // 🟢 Enable the driver (LOW = ON for most DM556T units)
    digitalWrite(ENA_PIN, LOW);

    // 🟢 Set initial direction
    digitalWrite(DIR_PIN, HIGH);

    Serial.println("Stepper test starting...");

    print_rad_to_deg(PI);
}

void loop() {
    uint64_t ticksTurned;
    


}