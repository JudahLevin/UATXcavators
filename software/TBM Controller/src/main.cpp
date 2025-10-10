#include <Arduino.h>

// test
//Earl's dvrk twisted beautiful maga test the quick brown fox jumped over all the lazy dogs

/*
    ========================================================================
    TBM CONTROLLER — FULL SIMULATION LOGIC
    --------------------------------------------------------------------
    This ESP32 program encodes all tunnel boring machine (TBM)
    alarm, warning, and interlock behavior directly from your CSV data.

    Features implemented:
    ✅ Low / High warning and alarm thresholds
    ✅ Trip delays before alarm activation
    ✅ Auto-clear when value returns to safe zone
    ✅ Interlocks for motor and actuator systems
    ✅ Manual reset via Serial Monitor
    ✅ Simulated random readings for testing
    ========================================================================
*/

// ========================= PIN CONFIGURATION =========================
//
// You can attach LEDs to these pins to visualize interlocks:
// GPIO 5 = Motor output
// GPIO 19 = Actuator output
//
#define MOTOR_PIN       5
#define ACTUATOR_PIN    19

// ========================= STRUCT DEFINITION =========================
//
// Each Channel stores threshold and timing info for one sensor.
// Runtime values (alarm states, timers, etc.) are tracked separately.
//
struct Channel {
    const char* name;            // Sensor name
    const char* units;           // Units (A, N, RPM, etc.)
    float lowWarn;               // Low warning threshold
    float lowAlarm;              // Low alarm threshold
    float highWarn;              // High warning threshold
    float highAlarm;             // High alarm threshold
    const char* interlockAction; // "Motor off" or "Actuator off"
    uint32_t tripDelayMs;        // Required time out-of-range before alarm triggers
    float clearLow;              // Safe lower bound to clear alarm
    float clearHigh;             // Safe upper bound to clear alarm
};

// ========================= CHANNEL INITIALIZATION =========================
//
// NEEDS TO BE PHASED OUT
//

// Old stuff (delete):

Channel channels[] = {
    {"Motor Current", "A", 3.5, 3.0, 5.0, 6.0, "Motor off", 200, 4.8, 5.8},
    {"Motor Speed", "RPM", 25.0, 15.0, 45.0, 50.0, "Motor off", 500, 17.0, 48.0},
    {"Reaction Force", "N", 164.04, 131.23, 216.54, 249.34, "Motor off", 200, 244.0, 244.0},
    {"Reaction Torque", "Nm", 25.0, 20.0, 33.0, 38.0, "Motor off", 200, 37.0, 37.0},
    {"Actuator Current", "A", 2.0, 1.5, 7.0, 8.0, "Actuator off", 200, 6.8, 7.8},
    {"Thrust Force", "N", 155.69, 133.45, 578.27, 600.51, "Actuator off", 200, 578.0, 578.0},
    {"Linear Displacement", "m", 0.0, 0.0, 0.45, 0.50, "Actuator off", 0, 0.497, 0.497},
    {"Linear Speed", "mm/s", 3.0, 2.0, 7.0, 8.0, "Actuator off", 500, 2.5, 7.5}
};

// New stuff (keep):

const int NUM_CHANNELS = 8;

enum class interlockAction {
    motorOff,
    actuatorOff
};

enum class channel {
    motorCurrent,
    motorSpeed,
    reactionForce,
    reactionTorque,
    actuatorCurrent,
    thrustForce,
    linearDisplacement,
    linearSpeed
};

// ========================= RUNTIME ARRAYS =========================
//
// These track the *current* state of each channel.
//
bool alarmLatched[8] = {false};
uint32_t violationStart[8] = {0};
float currentValue[8] = {0.0};

// ========================= UTILITY FUNCTION =========================

// Helper to check if a float value is valid
bool inRange(float v) {
    return !isnan(v) && isfinite(v);
}

// ========================= CHANNEL UPDATE FUNCTION =========================
//
// This runs once per cycle for each sensor channel.
//
// Steps:
// 1️⃣ Generate simulated random reading (1.0 – 8.0)
// 2️⃣ Check if it violates a threshold
// 3️⃣ Apply trip-delay logic before confirming alarm
// 4️⃣ Latch alarms and disable motor/actuator outputs
// 5️⃣ Auto-clear after 2 s stable in safe range
//
void updateChannel(int i, uint32_t now) {
    Channel &ch = channels[i];

    // Step 1 — Simulate a random live reading (replace with real sensor later)
    currentValue[i] = random(100, 800) / 100.0;  // 1.00 – 8.00

    bool alarmCondition = false;
    bool warningCondition = false;

    // Step 2 — Evaluate thresholds
    if (inRange(ch.lowAlarm) && currentValue[i] <= ch.lowAlarm) alarmCondition = true;
    else if (inRange(ch.highAlarm) && currentValue[i] >= ch.highAlarm) alarmCondition = true;
    else if (inRange(ch.lowWarn) && currentValue[i] <= ch.lowWarn) warningCondition = true;
    else if (inRange(ch.highWarn) && currentValue[i] >= ch.highWarn) warningCondition = true;

    // Step 3 — Trip delay logic: alarm triggers only after sustained violation
    if (alarmCondition && !alarmLatched[i]) {
        if (violationStart[i] == 0) {
            violationStart[i] = now;
        }
        if (now - violationStart[i] >= ch.tripDelayMs) {
            alarmLatched[i] = true;
            Serial.printf("🚨 ALARM: %s = %.2f %s\n", ch.name, currentValue[i], ch.units);
        }
    } else if (!alarmCondition) {
        violationStart[i] = 0;  // reset timer if safe again
    }

    // Step 4 — Print warnings (non-latching)
    if (warningCondition && !alarmLatched[i]) {
        Serial.printf("⚠️  WARNING: %s = %.2f %s\n", ch.name, currentValue[i], ch.units);
    }

    // Step 5 — Auto-clear logic: if value back in safe zone for > 2 s
    if (alarmLatched[i] && inRange(ch.clearLow) && currentValue[i] <= ch.clearHigh && currentValue[i] >= ch.clearLow) {
        static uint32_t safeStart[8] = {0};
        if (safeStart[i] == 0) {
            safeStart[i] = now;
        }
        if (now - safeStart[i] > 2000) {  // 2 seconds stable
            alarmLatched[i] = false;
            safeStart[i] = 0;
            Serial.printf("✅ Cleared: %s returned to safe range (%.2f %s)\n", ch.name, currentValue[i], ch.units);
        }
    }
}

// ========================= INTERLOCK HANDLER =========================
//
// If any channel alarm is latched, disable motor or actuator outputs.
//
void handleInterlocks() {
    bool motorTrip = false;
    bool actuatorTrip = false;

    // Check each channel for an active alarm
    for (int i = 0; i < NUM_CHANNELS; i++) {
        Channel &ch = channels[i];
        if (alarmLatched[i]) {
            if (String(ch.interlockAction).indexOf("Motor") >= 0) {
                motorTrip = true;
            }
            if (String(ch.interlockAction).indexOf("Actuator") >= 0) {
                actuatorTrip = true;
            }
        }
    }

    // Apply GPIO output changes
    digitalWrite(MOTOR_PIN, motorTrip ? LOW : HIGH);
    digitalWrite(ACTUATOR_PIN, actuatorTrip ? LOW : HIGH);

    // Print once whenever interlock state changes
    if (motorTrip || actuatorTrip) {
        Serial.println("\n⚡ INTERLOCK TRIGGERED ⚡");
        if (motorTrip) {
            Serial.println("🔴 Motor Disabled");
        }
        if (actuatorTrip) { 
            Serial.println("🔴 Actuator Disabled");
        }
        Serial.println();
    }
}

// ========================= MANUAL RESET FUNCTION =========================
//
// Type "reset" in the Serial Monitor to clear all alarms.
//
void manualReset() {
    for (int i = 0; i < NUM_CHANNELS; i++) {
        alarmLatched[i] = false;
        violationStart[i] = 0;
    }
    digitalWrite(MOTOR_PIN, HIGH);
    digitalWrite(ACTUATOR_PIN, HIGH);
    Serial.println("✅ Manual Reset: All interlocks cleared.\n");
}

// ========================= SETUP =========================
//
// Runs once at startup.
//
void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("=== TBM CONTROLLER – FULL SIMULATION MODE ===");
  Serial.println("Type 'reset' in Serial Monitor to clear interlocks.\n");

  // Initialize GPIOs
  pinMode(MOTOR_PIN, OUTPUT);
  pinMode(ACTUATOR_PIN, OUTPUT);
  digitalWrite(MOTOR_PIN, HIGH);
  digitalWrite(ACTUATOR_PIN, HIGH);
}

// ========================= MAIN LOOP =========================
//
// Runs continuously.  Each cycle checks all channels, applies logic,
// and updates outputs.
//
void loop() {
    uint32_t now = millis(); // milliseconds since boot

    // Listen for serial commands (manual reset)
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        if (cmd.equalsIgnoreCase("reset")) {
            manualReset();
        }
    }

    // Process each channel
    for (int i = 0; i < NUM_CHANNELS; i++) {
        updateChannel(i, now);
    }

    // Apply interlock actions
    handleInterlocks();

    // Print a divider for readability
    Serial.println("------------------------------------------");
    delay(1000);  // one-second update interval
}
