import json
import random
import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ------------------------------------------------------------
# Page setup
# ------------------------------------------------------------
st.set_page_config(
    page_title="TBM Control & Safety Dashboard",
    layout="wide",
)

# Auto-refresh every 1 second (1000 ms)
st_autorefresh(interval=1000, key="tbm_refresh")

# ------------------------------------------------------------
# Load TBM system data
# ------------------------------------------------------------
DATA_PATH = Path(__file__).parent / "tbm_systems_power.json"
with open(DATA_PATH, "r") as f:
    tbm_data = json.load(f)

# ------------------------------------------------------------
# Define safety interlocks (from safety architecture)
# ------------------------------------------------------------
INTERLOCK_DEFS = [
    # Safety PLC layer (A)
    {
        "id": "A1",
        "category": "Safety PLC",
        "name": "E-Stop / Dual-channel",
        "source": "XALK178W3B140G → Safety PLC SI1/SI2",
        "condition": "Any E-stop channel open or wiring fault",
        "effect": "Assert STO, drop K_JACK & K_PWR, stop all motion",
        "severity": "Critical",
    },
    {
        "id": "A2",
        "category": "Safety PLC",
        "name": "Contactor feedback mismatch",
        "source": "AF09 & K_PWR aux contacts",
        "condition": "Commanded OFF but feedback still ON (or vice versa)",
        "effect": "Safety PLC refuses reset, STO remains active",
        "severity": "Critical",
    },
    {
        "id": "A3",
        "category": "Safety PLC",
        "name": "VFD STO loop integrity",
        "source": "VFD STO1/STO2",
        "condition": "STO wiring fault or mismatch",
        "effect": "VFD torque removed, safety trip latched",
        "severity": "Critical",
    },
    {
        "id": "A4",
        "category": "Safety PLC",
        "name": "Internal safety PLC fault",
        "source": "Safety PLC self-diagnostics",
        "condition": "Watchdog, CRC, output stage or supply fault",
        "effect": "All safety outputs drop immediately",
        "severity": "Critical",
    },
    # Main PLC logical interlocks (B)
    {
        "id": "B1",
        "category": "Main PLC",
        "name": "Safety OK required",
        "source": "Safety PLC → Main PLC DI",
        "condition": "SAFETY_OK = FALSE",
        "effect": "All motion commands blocked, state = FAULT",
        "severity": "High",
    },
    {
        "id": "B2",
        "category": "Main PLC",
        "name": "Screw jack travel limits",
        "source": "Jack home/extended limit switches",
        "condition": "Command would drive beyond limit, or both limits active",
        "effect": "Block jack movement in unsafe direction",
        "severity": "High",
    },
    {
        "id": "B3",
        "category": "Main PLC",
        "name": "Cutterhead VFD fault / overcurrent",
        "source": "VFD fault relay, current feedback",
        "condition": "Drive fault, overcurrent, or overtemp",
        "effect": "Block cutterhead RUN, raise alarm",
        "severity": "High",
    },
    {
        "id": "B4",
        "category": "Main PLC",
        "name": "Process pressure limits",
        "source": "PT-101 (IO-Link pressure)",
        "condition": "Low pressure (dry) or high pressure",
        "effect": "Auto pump control, inhibit cutterhead start",
        "severity": "Medium",
    },
    {
        "id": "B5",
        "category": "Main PLC",
        "name": "Enclosure temperature",
        "source": "CTH-101 (IO-Link T/RH)",
        "condition": "Enclosure temperature above threshold",
        "effect": "Force fans ON; inhibit cutterhead if critical",
        "severity": "Medium",
    },
    {
        "id": "B6",
        "category": "Main PLC",
        "name": "Pump / flow confirmation",
        "source": "Pump relay + pressure response",
        "condition": "Pump ON but no pressure change",
        "effect": "Stop pump, block cutterhead, raise alarm",
        "severity": "Medium",
    },
    {
        "id": "B7",
        "category": "Main PLC",
        "name": "IO-Link master comm loss",
        "source": "DXMR110 connection",
        "condition": "No communication with IO-Link master",
        "effect": "Stop pumps, block cutterhead",
        "severity": "High",
    },
    {
        "id": "B8",
        "category": "Main PLC",
        "name": "Contactor feedback (non-safety)",
        "source": "AF09/K_PWR aux → Main PLC",
        "condition": "Mismatch between command and feedback",
        "effect": "Set FAULT state, inhibit motion",
        "severity": "Medium",
    },
    {
        "id": "B9",
        "category": "Main PLC",
        "name": "Jack motor overload",
        "source": "Leeson thermal & KBMG fault",
        "condition": "Overtemp or drive fault",
        "effect": "Block jack movement",
        "severity": "Medium",
    },
    {
        "id": "B10",
        "category": "Main PLC",
        "name": "Cutterhead direction validity",
        "source": "VFD DI FWD/REV",
        "condition": "Both FWD & REV active",
        "effect": "Inhibit cutterhead RUN",
        "severity": "Low",
    },
    # Electrical / device (C)
    {
        "id": "C1",
        "category": "Electrical",
        "name": "480 V breaker A",
        "source": "C60X3C10",
        "condition": "Breaker open / no 480 V",
        "effect": "VFD powerless → no cutterhead motion",
        "severity": "Medium",
    },
    {
        "id": "C2",
        "category": "Electrical",
        "name": "240/120 V breaker B",
        "source": "CH2100",
        "condition": "Breaker open / no 240/120 V",
        "effect": "No PSUs, KBMG, pumps, fans",
        "severity": "Medium",
    },
    {
        "id": "C3",
        "category": "Electrical",
        "name": "Supply quality",
        "source": "Generator voltage",
        "condition": "Brownout or wrong voltage",
        "effect": "Blocks drive operation",
        "severity": "Medium",
    },
    {
        "id": "C4",
        "category": "Electrical",
        "name": "24 V sensor power",
        "source": "24 V PSUs",
        "condition": "Sensor supply undervoltage",
        "effect": "Sensor failure → PLC interlocks",
        "severity": "Medium",
    },
    {
        "id": "C5",
        "category": "Electrical",
        "name": "VFD internal protection",
        "source": "VFD hardware",
        "condition": "Heatsink temp, phase loss, internal fault",
        "effect": "Drive shuts down, PLC sees fault",
        "severity": "High",
    },
]

CRITICAL_IDS = {"A1", "A2", "A3", "A4"}

# ------------------------------------------------------------
# Session state initialisation
# ------------------------------------------------------------
if "device_states" not in st.session_state:
    # Expand json into a richer runtime structure
    st.session_state.device_states = {}
    for category, devices in tbm_data.items():
        st.session_state.device_states[category] = {}
        for dev in devices:
            st.session_state.device_states[category][dev["Label"]] = {
                "on": dev.get("State", "OFF") == "ON",
                "current": 0.0,
                "speed": 0.0,
                "torque": 0.0,
            }

if "interlock_states" not in st.session_state:
    # Track active/latching states and last trip times
    st.session_state.interlock_states = {
        d["id"]: {
            "active": False,
            "latched": False,
            "last_trip": None,
        }
        for d in INTERLOCK_DEFS
    }

if "system_state" not in st.session_state:
    st.session_state.system_state = "IDLE"  # IDLE / READY / RUNNING / FAULT

if "system_mode" not in st.session_state:
    st.session_state.system_mode = "AUTO"  # AUTO / MANUAL

if "log_series" not in st.session_state:
    st.session_state.log_series = {
        "time": [],
        "cutterhead_current": [],
        "jack_current": [],
        "pressure": [],
        "enclosure_temp": [],
    }

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------
def any_critical_interlock_active() -> bool:
    for iid in CRITICAL_IDS:
        if st.session_state.interlock_states[iid]["active"]:
            return True
    return False


def compute_safety_ok() -> bool:
    # In real system this is from the safety PLC.
    return not any_critical_interlock_active()


def update_system_state():
    safety_ok = compute_safety_ok()
    old_state = st.session_state.system_state

    if not safety_ok:
        st.session_state.system_state = "FAULT"
    else:
        # Simple heuristic: RUNNING if cutterhead ON, else READY if safe
        cutter_on = st.session_state.device_states["Cutter Head & Drive"]["Cutter Head Motor"]["on"]
        if cutter_on:
            st.session_state.system_state = "RUNNING"
        else:
            st.session_state.system_state = "READY"

    if old_state != st.session_state.system_state:
        st.session_state["state_changed_at"] = datetime.datetime.now()


def simulate_signals():
    """
    Simple simulation: if a device is ON, give it a random-ish current.
    Also simulate one process pressure and enclosure temp.
    """
    now = datetime.datetime.now()

    # Cutterhead and jack currents
    ch_state = st.session_state.device_states["Cutter Head & Drive"]["Cutter Head Motor"]
    jack_state = st.session_state.device_states["Cutter Head & Drive"]["Screw Jack"]

    if ch_state["on"]:
        ch_state["current"] = round(random.uniform(8.0, 15.0), 2)
        ch_state["speed"] = round(random.uniform(300.0, 600.0), 1)
        ch_state["torque"] = round(random.uniform(150.0, 400.0), 1)
    else:
        ch_state["current"] = 0.0
        ch_state["speed"] = 0.0
        ch_state["torque"] = 0.0

    if jack_state["on"]:
        jack_state["current"] = round(random.uniform(3.0, 6.0), 2)
        jack_state["speed"] = round(random.uniform(5.0, 15.0), 1)
        jack_state["torque"] = round(random.uniform(50.0, 200.0), 1)
    else:
        jack_state["current"] = 0.0
        jack_state["speed"] = 0.0
        jack_state["torque"] = 0.0

    # Process pressure & temp (pretend IO-Link PT/CTH)
    pressure = round(random.uniform(1.0, 5.0), 2)  # bar
    enclosure_temp = round(random.uniform(25.0, 45.0), 1)  # °C

    st.session_state.log_series["time"].append(now)
    st.session_state.log_series["cutterhead_current"].append(ch_state["current"])
    st.session_state.log_series["jack_current"].append(jack_state["current"])
    st.session_state.log_series["pressure"].append(pressure)
    st.session_state.log_series["enclosure_temp"].append(enclosure_temp)

    # Trim log to last N points
    max_points = 300
    for key in st.session_state.log_series:
        st.session_state.log_series[key] = st.session_state.log_series[key][-max_points:]


def status_badge(text: str, level: str):
    color = {
        "ok": "💚",
        "warn": "🟡",
        "bad": "🔴",
    }.get(level, "⚪️")
    st.markdown(f"{color} **{text}**")


# ------------------------------------------------------------
# Top-level layout: header + main tabs
# ------------------------------------------------------------
st.title("TBM Control, Power & Safety Dashboard")

# Simulate signals for this refresh tick
simulate_signals()
update_system_state()

safety_ok = compute_safety_ok()
cutter_on = st.session_state.device_states["Cutter Head & Drive"]["Cutter Head Motor"]["on"]
jack_on = st.session_state.device_states["Cutter Head & Drive"]["Screw Jack"]["on"]

# ------- Top status bar ------------------------------------------------------
top_col1, top_col2, top_col3, top_col4 = st.columns(4)

with top_col1:
    st.metric("System State", st.session_state.system_state)
    st.caption("IDLE / READY / RUNNING / FAULT")

with top_col2:
    if safety_ok:
        status_badge("Safety OK", "ok")
    else:
        status_badge("SAFETY NOT OK", "bad")
    st.caption("Derived from Safety PLC interlocks")

with top_col3:
    status_badge(f"Mode: {st.session_state.system_mode}", "ok")
    st.caption("AUTO selects interlocks and sequences automatically")

with top_col4:
    ch_curr = st.session_state.log_series["cutterhead_current"][-1] if st.session_state.log_series["cutterhead_current"] else 0
    st.metric("Cutterhead Current (A)", ch_curr)
    st.caption("Simulated from SEW RF127R77 motor")

# ------- Main content tabs ---------------------------------------------------
tab_overview, tab_interlocks, tab_systems, tab_trends = st.tabs(
    ["Overview", "Interlocks & Safety", "Systems & Power", "Trends & Telemetry"]
)

# ------------------------------------------------------------
# Tab 1: Overview (high-level control & status)
# ------------------------------------------------------------
with tab_overview:
    c1, c2 = st.columns([2, 3])

    with c1:
        st.subheader("High-level Controls (Simulated)")
        st.write("These would normally be bound to PLC tags rather than local state.")

        # System mode
        st.radio(
            "Control Mode",
            ["AUTO", "MANUAL"],
            key="system_mode",
            horizontal=True,
        )

        # Cutterhead control
        st.markdown("### Cutterhead")
        ch_toggle = st.toggle("Cutterhead RUN command", value=cutter_on, key="cmd_cutterhead_run")
        st.session_state.device_states["Cutter Head & Drive"]["Cutter Head Motor"]["on"] = ch_toggle

        # Screw jack control
        st.markdown("### Screw Jack")
        jack_toggle = st.toggle("Jack ENABLE command", value=jack_on, key="cmd_jack_run")
        st.session_state.device_states["Cutter Head & Drive"]["Screw Jack"]["on"] = jack_toggle

        st.divider()
        st.markdown("### Process Pumps & Cooling (Simulated)")
        if st.button("Start Process Pumps", use_container_width=True):
            # In a real system, this would set PLC DO's
            st.info("Process pump command issued (simulated).")
        if st.button("Stop All Pumps", use_container_width=True):
            st.info("Process pump stop command issued (simulated).")

        if st.button("Force Cooling Fans ON", use_container_width=True):
            st.info("Cooling fan ON command issued (simulated).")

    with c2:
        st.subheader("System Snapshot")

        ch = st.session_state.device_states["Cutter Head & Drive"]["Cutter Head Motor"]
        jk = st.session_state.device_states["Cutter Head & Drive"]["Screw Jack"]

        st.markdown("#### Cutterhead & Jack")
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            status_badge(
                f"Cutterhead: {'ON' if ch['on'] else 'OFF'}",
                "ok" if ch["on"] else "bad",
            )
            st.write(f"Current: {ch['current']} A")
        with cc2:
            st.write(f"Speed: {ch['speed']} RPM")
            st.write(f"Torque: {ch['torque']} Nm")
        with cc3:
            status_badge(
                f"Screw Jack: {'ON' if jk['on'] else 'OFF'}",
                "ok" if jk["on"] else "bad",
            )
            st.write(f"Current: {jk['current']} A")

        st.markdown("#### Process Pressures & Enclosure Climate (Simulated)")
        df_proc = pd.DataFrame(
            {
                "time": st.session_state.log_series["time"][-60:],
                "Pressure (bar)": st.session_state.log_series["pressure"][-60:],
                "Enclosure Temp (°C)": st.session_state.log_series["enclosure_temp"][-60:],
            }
        ).set_index("time")
        st.line_chart(df_proc)


# ------------------------------------------------------------
# Tab 2: Interlocks & Safety
# ------------------------------------------------------------
with tab_interlocks:
    st.subheader("Safety Interlocks & Trip Simulation")
    st.write(
        "This table reflects the Safety PLC, Main PLC, and Electrical interlocks that gate motion. "
        "Use the buttons to simulate trips and resets; in the real system, these would be driven by "
        "field signals and safety logic rather than GUI buttons."
    )

    # Filter by category
    interlock_category_filter = st.multiselect(
        "Filter by category",
        options=sorted(set(d["category"] for d in INTERLOCK_DEFS)),
        default=sorted(set(d["category"] for d in INTERLOCK_DEFS)),
    )

    # Render table row-by-row with controls
    for interlock in INTERLOCK_DEFS:
        if interlock["category"] not in interlock_category_filter:
            continue

        iid = interlock["id"]
        state = st.session_state.interlock_states[iid]

        with st.container(border=True):
            top_row = st.columns([1, 2, 2, 2, 2])
            with top_row[0]:
                st.markdown(f"**{interlock['id']}**")
                st.caption(interlock["category"])

                level = "ok"
                if state["active"]:
                    level = "bad"
                elif state["latched"]:
                    level = "warn"
                status_badge("ACTIVE" if state["active"] else ("LATCHED" if state["latched"] else "OK"), level)

            with top_row[1]:
                st.markdown(f"**{interlock['name']}**")
                st.caption(f"Severity: {interlock['severity']}")

            with top_row[2]:
                st.markdown("**Source**")
                st.write(interlock["source"])

            with top_row[3]:
                st.markdown("**Trip condition**")
                st.write(interlock["condition"])

            with top_row[4]:
                st.markdown("**Effect**")
                st.write(interlock["effect"])

            bcol1, bcol2, bcol3 = st.columns([1, 1, 2])
            with bcol1:
                if st.button(f"Trip {iid}", key=f"trip_{iid}"):
                    state["active"] = True
                    state["latched"] = True
                    state["last_trip"] = datetime.datetime.now()

            with bcol2:
                if st.button(f"Reset {iid}", key=f"reset_{iid}"):
                    # In real safety, reset usually only allowed if condition cleared
                    state["active"] = False
                    state["latched"] = False

            with bcol3:
                if state["last_trip"] is not None:
                    st.caption(f"Last trip: {state['last_trip'].strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    st.caption("Last trip: —")

    st.divider()
    st.markdown("### Derived Safety Bits (Simulated)")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        status_badge(f"SAFETY_OK = {compute_safety_ok()}", "ok" if compute_safety_ok() else "bad")
    with col_s2:
        estop_latched = st.session_state.interlock_states["A1"]["latched"]
        status_badge(f"ESTOP_LATCHED = {estop_latched}", "bad" if estop_latched else "ok")
    with col_s3:
        st.write("These bits would normally be read from the Safety PLC and exposed to the main PLC & HMI.")


# ------------------------------------------------------------
# Tab 3: Systems & Power (device cards from JSON)
# ------------------------------------------------------------
with tab_systems:
    st.subheader("Systems, Power, and Devices")
    st.write("Pulled directly from `tbm_systems_power.json` and combined with simulated runtime state.")

    for category, devices in tbm_data.items():
        st.markdown(f"### {category}")
        cols = st.columns(3)
        idx = 0
        for dev in devices:
            col = cols[idx % 3]
            idx += 1

            label = dev["Label"]
            runtime = st.session_state.device_states.get(category, {}).get(label, None)

            with col:
                with st.container(border=True):
                    st.markdown(f"**{label}**")
                    st.caption(dev["Explanation"])
                    st.write(f"Model: `{dev['Model']}`")
                    st.write(f"Quantity: {dev['Quantity']}")

                    if runtime is not None:
                        on = runtime["on"]
                        status_badge("ON" if on else "OFF", "ok" if on else "bad")
                        st.write(f"Current: {runtime['current']} A")
                    else:
                        status_badge("MONITORED ONLY", "warn")


# ------------------------------------------------------------
# Tab 4: Trends & Telemetry
# ------------------------------------------------------------
with tab_trends:
    st.subheader("Live Telemetry & Trends (Simulated)")

    if len(st.session_state.log_series["time"]) > 1:
        df_trend = pd.DataFrame(
            {
                "time": st.session_state.log_series["time"],
                "Cutterhead Current (A)": st.session_state.log_series["cutterhead_current"],
                "Jack Current (A)": st.session_state.log_series["jack_current"],
                "Pressure (bar)": st.session_state.log_series["pressure"],
                "Enclosure Temp (°C)": st.session_state.log_series["enclosure_temp"],
            }
        ).set_index("time")

        st.line_chart(df_trend)
    else:
        st.info("Waiting for telemetry samples…")

    st.caption(
        "In a real deployment, these series would be driven by PLC tags and IO-Link data "
        "instead of random simulation."
    )
