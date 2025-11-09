#include <Arduino.h>

// test
// Earl's dvrk twisted beautiful maga test the quick brown fox jumped over all the lazy dogs

/*
    ========================================================================
    TBM CONTROLLER — FULL SIMULATION LOGIC
    --------------------------------------------------------------------
    This ESP32 program encodes all tunnel boring machine (TBM)
    alarm, warning, and interlock behavior directly from your CSV data.

    Features implemented:
    Low / High warning and alarm thresholds
    Trip delays before alarm activation
    Auto-clear when value returns to safe zone
    Interlocks for motor and actuator systems
    Manual reset via Serial Monitor
    Simulated random readings for testing
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

// ========================= CHANNEL INITIALIZATION =========================
//

// New stuff (keep):

enum action 
{
    motorOff,
    actuatorOff
};

enum state
{
    clear,
    warning,
    alarm
};

enum channel 
{
    motorCurrent,
    motorSpeed,
    reactionForce,
    reactionTorque,
    actuatorCurrent,
    thrustForce,
    linearDisplacement,
    linearSpeed,

    numChannels
};

enum field 
{
    lowWarn,
    lowAlarm,
    highWarn,
    highAlarm,
    interlockAction,
    tripDelayMs,
    clearLow,
    clearHigh,

    numFields
};

// Global data
struct Global {
    // Lookup table by channel and field for numeric channel data.
    // {lowWarn, lowAlarm, highWarn, highAlarm, interlockAction, tripDelay(ms), lowClear, highClear}
    const double channelData[numChannels][numFields] = {
        {3.5, 3.0, 5.0, 6.0, motorOff, 200, 4.8, 5.8},
        {25.0, 15.0, 45.0, 50.0, motorOff, 500, 17.0, 48.0},
        {164.04, 131.23, 216.54, 249.34, motorOff, 200, 244.0, 244.0},
        {25.0, 20.0, 33.0, 38.0, motorOff, 200, 37.0, 37.0},
        {2.0, 1.5, 7.0, 8.0, actuatorOff, 200, 6.8, 7.8},
        {155.69, 133.45, 578.27, 600.51, actuatorOff, 200, 578.0, 578.0},
        {0.0, 0.0, 0.45, 0.50, actuatorOff, 0, 0.497, 0.497},
        {3.0, 2.0, 7.0, 8.0, actuatorOff, 500, 2.5, 7.5}
    };

    // Lookup table for channel name by channel.
    const char* names[8] = {"Motor Current", "Motor Speed", 
                            "Reaction Force", "Reaction Torque", 
                            "Actuator Current", "Thrust Force", 
                            "Linear Displacement", "Linear Speed"};

    // Lookup table for units by channel.
    const char* units[8] = {"A", "RPM", "N", "Nm", "A", "N", "m", "mm/s"};

    // True global variables.
    bool alarmLatched[numChannels] = {false};
    uint32_t violationStart[numChannels] = {0};
    float currentValue[numChannels] = {0.0};
};

Global global;

// ========================= CHANNEL UPDATE FUNCTION =========================
//
// This runs once per cycle for each sensor channel.
//
// Steps:
// 1️. Generate simulated random reading (1.0 – 8.0)
// 2️. Check if it violates a threshold
// 3️. Apply trip-delay logic before confirming alarm
// 4️. Latch alarms and disable motor/actuator outputs
// 5️. Auto-clear after 2 s stable in safe range
//
void updateChannel(int ch, uint32_t now) 
{
    // Step 1 — Simulate a random live reading (replace with real sensor later)
    global.currentValue[ch] = random(100, 800) / 100.0;  // 1.00 – 8.00
    state currentState;

    // Step 2 — Evaluate thresholds
    bool alarmCondition = (global.currentValue[ch] <= global.channelData[ch][lowAlarm]
                        || global.currentValue[ch] >= global.channelData[ch][highAlarm]);
    bool warningCondition = (global.currentValue[ch] <= global.channelData[ch][lowWarn]
                        || global.currentValue[ch] >= global.channelData[ch][highWarn]);
    

    // Step 3 — Trip delay logic: alarm triggers only after sustained violation
    if (!alarmCondition) {
        global.violationStart[ch] = 0;  // reset timer if safe again
    } else if (!global.alarmLatched[ch]) {
        if (global.violationStart[ch] == 0) 
        {
            global.violationStart[ch] = now;
        }
        if (now - global.violationStart[ch] >= global.channelData[ch][tripDelayMs]) 
        {
            global.alarmLatched[ch] = true;
            Serial.printf("🚨 ALARM: %s = %.2f %s\n", global.names[ch], global.currentValue[ch], global.units[ch]);
        }
    }

    // Step 4 — Print warnings (non-latching)
    if (warningCondition && !global.alarmLatched[ch]) 
    {
        Serial.printf("⚠️  WARNING: %s = %.2f %s\n", global.names[ch], global.currentValue[ch], global.units[ch]);
    }

    // Step 5 — Auto-clear logic: if value back in safe zone for > 2 s
    if (global.alarmLatched[ch] && global.currentValue[ch] <= global.channelData[ch][clearHigh]
       && global.currentValue[ch] >= global.channelData[ch][clearLow]) 
    {
        static uint32_t safeStart[8] = {0};
        if (safeStart[ch] == 0) 
        {
            safeStart[ch] = now;
        }
        if (now - safeStart[ch] > 2000) // 2 seconds stable
        {  
            global.alarmLatched[ch] = false;
            safeStart[ch] = 0;
            Serial.printf("✅ Cleared: %s returned to safe range (%.2f %s)\n", global.names[ch], global.currentValue[ch], global.units[ch]);
        }
    }
}

// ========================= INTERLOCK HANDLER =========================
//
// If any channel alarm is latched, disable motor or actuator outputs.
//
void handleInterlocks() 
{
    bool motorTrip = false;
    bool actuatorTrip = false;

    // Check each channel for an active alarm
    for (int i = 0; i < numChannels; i++) 
    {

        if (global.alarmLatched[i]) 
        {
            if (global.channelData[i][interlockAction] == motorOff) 
            {
                motorTrip = true;
            }
            else
            {
                actuatorTrip = true;
            }
        }
    }

    // Apply GPIO output changes
    digitalWrite(MOTOR_PIN, motorTrip ? LOW : HIGH);
    digitalWrite(ACTUATOR_PIN, actuatorTrip ? LOW : HIGH);

    // Print once whenever interlock state changes
    if (motorTrip || actuatorTrip) 
    {
        Serial.println("\n⚡ INTERLOCK TRIGGERED ⚡");
        if (motorTrip) 
        {
            Serial.println("🔴 Motor Disabled");
        }
        if (actuatorTrip) 
        { 
            Serial.println("🔴 Actuator Disabled");
        }
        Serial.println();
    }
}

// ========================= MANUAL RESET FUNCTION =========================
//
// Type "reset" in the Serial Monitor to clear all alarms.
//
void manualReset() 
{
    for (int i = 0; i < numChannels; i++) 
    {
        global.alarmLatched[i] = false;
        global.violationStart[i] = 0;
    }
    digitalWrite(MOTOR_PIN, HIGH);
    digitalWrite(ACTUATOR_PIN, HIGH);
    Serial.println("✅ Manual Reset: All interlocks cleared.\n");
}

// ========================= SETUP =========================
//
// Runs once at startup.
//
void setup() 
{
  Serial.begin(115200);
  delay(500);
  Serial.println("=== TBM CONTROLLER - FULL SIMULATION MODE ===");
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
void loop() 
{
    uint32_t now = millis(); // milliseconds since boot

    // Listen for serial commands (manual reset)
    if (Serial.available()) 
    {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        if (cmd.equalsIgnoreCase("reset")) 
        {
            manualReset();
        }
    }

    // Process each channel
    for (int i = 0; i < numChannels; i++) 
    {
        updateChannel(i, now);
    }

    // Apply interlock actions
    handleInterlocks();

    // Print a divider for readability
    Serial.println("------------------------------------------");
    delay(1000);  // one-second update interval
}