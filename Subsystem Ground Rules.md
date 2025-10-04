
# Subsystem Ground Rules

---

## 1. White-Box Your Part

To test or fix a part you bought off-the-shelf, you need to understand how it works — it cannot be a black box.  
For each piece of hardware (e.g., a pump), understand the following:

### 1. Basic Identification
- **Type:** Centrifugal, diaphragm, peristaltic, screw, gear, etc. (each has different response curves and failure modes).  
- **Intended service:** Water, slurry, foam solution, polymer, air–liquid mix, etc.  
- **Datasheet/manual:** Gather official specs, wiring diagrams, I/O, service instructions.  

### 2. Performance Characteristics
- Flow vs. pressure curve (pump curve): how flowrate changes with discharge pressure.  
- Operating range: min/max flow, min/max pressure.  
- Efficiency curve: optimal point of operation.  
- NPSH (Net Positive Suction Head): suction requirements to avoid cavitation.  
- Priming requirements: self-priming or external priming needed.  

### 3. Mechanical & Electrical Limits
- Max RPM / duty cycle (continuous vs intermittent).  
- Power input: voltage, phase, current draw.  
- Start-up current (inrush).  
- Temperature limits: fluid and ambient.  
- Seal/shaft design: dry-run tolerance, lubrication requirements.  
- Noise/vibration levels.  

### 4. Control & Interfaces
- How it starts/stops: relay, contactor, VFD, or onboard driver.  
- Speed control: fixed-speed or variable-speed input (analog 4–20 mA, PWM, Modbus, etc.).  
- Built-in protections: thermal cutoff, overload protection.  
- Feedback signals: flow sensor, tachometer, current feedback, or none.  
- Fail-safe state: what happens if power is lost (coast, lock, vent).  

### 5. Safety & Failure Modes
- Failure points: cavitation, dry running, overheating, overpressure, seal leakage.  
- What happens if blocked: stalls, trips, or bypasses.  
- Overpressure protection: relief valve built in or external required.  
- Safe shutdown procedure: gradual vs immediate stop.  
- Hazards: shock hazard, fluid leakage, stored pressure.  

### 6. Integration Considerations
- Startup sequencing: does it need priming before flow?  
- Shutdown sequencing: does it need flush/clean cycle?  
- Maintenance cycle: lubrication, seal replacement, cleaning frequency.  
- Environmental considerations: can it run outdoors, underground, submerged?  
- Compatibility: chemical resistance of wetted parts.  

### 7. Testing Preparation
Before your test, you should know:  
- Expected flow/pressure at test conditions (compare against the curve).  
- Power draw under load (to size sensors and PSU).  
- Safe limits to enforce in the Finite State Machine (FSM).  
- Baseline sensor readings at known settings for calibration.  

### 8. Documentation to Have in Hand
- Manufacturer’s datasheet (performance curves).  
- Wiring diagram (for safe connection).  
- Operation & maintenance manual (O&M).  
- Spare parts list (seals, impellers, bearings).  
- Certifications (CE, ATEX, NSF, etc. if required).  

---

## 2. Subsystem State Diagrams

From the NABC rules, here’s a step-by-step process to build a pump state diagram inside a conditioning subsystem:

1. **Set scope & interfaces**  
   Decide what’s “the pump” vs. “the conditioning system,” and list external signals it depends on (e.g., `Safety_OK`, `Flush_Cmd`).

2. **List pump states**  
   Choose modes like `OFF`, `INIT`, `PRIMING`, `RUNNING`, `FLUSH`, `HOLD`, `FAULT`, `E_STOP`.

3. **Define entry / during / exit for each state**  
   - **Entry action:** one-time when entering (e.g., open prime valve).  
   - **During action:** continuous while in state (e.g., regulate flow).  
   - **Exit action:** one-time before leaving (e.g., close valve).  

4. **Identify transitions**  
   Write rules that change states (start/stop command, sensor condition, timer expiry).  

5. **Add permissives and interlocks**  
   Example: Permit_Pump = Safety_OK ∧ Tank_Level_OK ∧ No_Fault

6. **Tie transitions to real I/O tags**  
Example: `PT_Header` (pressure), `FM_Water` (flow), `LS_Tank_LL` (level switch).  

7. **Add timers & debounce**  
Define minimum on/off times, priming timeout, ramp-up/ramp-down.  

8. **Define setpoints & regulation in RUNNING**  
Choose flow/pressure targets and control method (fixed speed, PID, etc.).  

9. **Enumerate faults and safe reactions**  
Examples: Overpressure, no-flow/dry-run, overcurrent, bad sensor.  
Define detection, shutdown, and reset rules (latched or auto-reset).  

10. **Define fail-safe states**  
 Decide outputs if control is lost (e.g., pump OFF, valves CLOSED).  

11. **Wire pump ↔ subsystem interactions**  
 Example: subsystem `DOSE_STEADY` → pump must be `RUNNING`; subsystem `FLUSH` → pump must be `FLUSH`.  

12. **Draw the diagram (FSM)**  
 - **Boxes = states**  
 - **Arrows = transitions labeled with conditions**  

13. **Create companion tables**  
 - **State table:** State | Entry | During | Exit | Exit conditions  
 - **Permissive matrix**  
 - **Fault matrix**  

14. **Validate with test paths**  
 Walk the “happy path” (`OFF → INIT → PRIMING → RUNNING → FLUSH → OFF`) and fault paths (`RUNNING → FAULT`).  
 First simulate I/O, then run on hardware.  

---

## Example State Diagram

```mermaid
stateDiagram-v2
%% =========================
%% Top-Level: Conditioning
%% =========================
[*] --> C_OFF

C_OFF --> C_INIT: Power_On & Safety_OK
C_INIT --> C_READY: Sensors_OK & Levels_OK & Mixer_OK
C_READY --> C_DOSE: Start_Dosing & Permits_OK
C_DOSE --> C_FLUSH: Flush_Cmd | Bin_High | Stop_Dosing
C_READY --> C_FLUSH: Flush_Cmd
C_FLUSH --> C_READY: Lines_Clear & Timer_Done
C_ANY: C_OFF
C_ANY --> C_FAULT: OverP | DryRun | Sensor_Bad | Level_CritLow
C_ANY --> C_ESTOP: EStop

C_FAULT --> C_READY: Fault_Reset & Health_OK & Permits_OK
C_ESTOP --> C_OFF: Safety_Reset

state "Conditioning: DOSE_STEADY" as C_DOSE {
 [*] --> RUN_LOGIC
 RUN_LOGIC: Set flows to recipe (FIR)\nRegulate header pressure\nMonitor quality & limits
 RUN_LOGIC --> [*]: Stop_Dosing | Flush_Cmd
}

%% Notes showing interlocks between layers
note right of C_DOSE
 Requires Pump.RUNNING
 Permit_Dose = Safety_OK ∧ Tank_Level_OK ∧ No_Leak
end note

%% =========================
%% Nested: Pump FSM
%% =========================
state "Pump Subsystem" as PUMP {
 [*] --> P_OFF
 P_OFF --> P_INIT: Power_On & Safety_OK
 P_INIT --> P_PRIME: Start_Cmd & Suction_OK
 P_PRIME --> P_RUN: Flow_Detected within T_prime
 P_PRIME --> P_FAULT: Prime_Timeout | DryRun
 P_RUN --> P_FLUSH: Flush_Cmd | Stop_Cmd
 P_RUN --> P_FAULT: OverP | NoFlow | OverCurrent | Sensor_Bad
 P_FLUSH --> P_OFF: Flush_Done & Lines_Clear
 P_FAULT --> P_INIT: Fault_Reset & Health_OK
 P_ANY: P_OFF
 P_ANY --> P_ESTOP: EStop
 P_ESTOP --> P_OFF: Safety_Reset
}

%% Coupling rules (top-level → pump)
C_DOSE --> P_RUN: (Ensure) Pump.RUNNING
C_FLUSH --> P_FLUSH: Flush_Cmd
C_READY --> P_OFF: Idle

%% Global ANY aliases for readability
state C_ANY <<choice>>
state P_ANY <<choice>>
