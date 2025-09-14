import streamlit as st
import json
import random
import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# -------------------------------
# Auto-refresh every 1 second
# -------------------------------
st_autorefresh(interval=1000, key="power_refresh")

# -------------------------------
# Load TBM system data
# -------------------------------
with open("tbm_systems_power.json") as f:
    tbm_data = json.load(f)

# -------------------------------
# Helpers for thresholds & health
# -------------------------------
SEVERITY_ORDER = {"OK": 0, "LOW": 1, "HIGH": 2, "TRIP": 3}
SEVERITY_EMOJI = {"OK": "🟢", "LOW": "🟡", "HIGH": "🟠", "TRIP": "🔴"}

def op_eval(op: str, value: float, thr: float) -> bool:
    if op == "≥": return value >= thr
    if op == "≤": return value <= thr
    if op == ">": return value > thr
    if op == "<": return value < thr
    return False

def max_sev(a: str, b: str) -> str:
    return a if SEVERITY_ORDER[a] >= SEVERITY_ORDER[b] else b

# -------------------------------
# Devices with RPM / Torque
# -------------------------------
HAS_SPEED_TORQUE = {
    "Cutter Head Motor", 
    "Screw Jack Motor", 
    "Primary Intake Fan", 
    "Secondary Intake Fan", 
    "Conveyor Motor", 
    "Conditioner Pump"
}

# -------------------------------
# Session state
# -------------------------------
if "device_states" not in st.session_state:
    st.session_state.device_states = {}
if "current_log" not in st.session_state:
    st.session_state.current_log = {category: {} for category in tbm_data.keys()}
if "total_log" not in st.session_state:
    st.session_state.total_log = {"time": [], "current": [], "speed": [], "torque": []}
if "interlock_demo" not in st.session_state:
    st.session_state.interlock_demo = None

# -------------------------------
# Fake Safety Interlocks (10 demo rows)
# -------------------------------
demo_interlocks = [
    {"Measurement": "CMVT on cutter motor", "Trip Condition": "≥155 °F", "ID": "G1", "Reset": "L+MR", "Interlock": "Guard door unsafe", "Action": "Stop cutter, close solenoids", "Notes": "Overtemp condition"},
    {"Measurement": "CMTH @ panel", "Trip Condition": "≥122 °F", "ID": "T2", "Reset": "L", "Interlock": "Panel overheated", "Action": "Stop conveyor/pump", "Notes": "Excess panel temp"},
    {"Measurement": "PT16A @ nozzle", "Trip Condition": ">60 psi", "ID": "P1", "Reset": "L+MR", "Interlock": "Pump overpressure", "Action": "Stop pump, clog-clear", "Notes": "Pressure spike"},
    {"Measurement": "PT16A @ pump", "Trip Condition": ">60 psi", "ID": "P2", "Reset": "L+MR", "Interlock": "Pump overpressure", "Action": "Stop pump, close solenoids", "Notes": "Pump overload"},
    {"Measurement": "BCF5", "Trip Condition": "≥5 level", "ID": "B1", "Reset": "L+MR", "Interlock": "Cutter overload", "Action": "Stop cutter", "Notes": "Blockage detected"},
    {"Measurement": "VFD motor-I", "Trip Condition": "≥7.5 A", "ID": "M1", "Reset": "L+MR", "Interlock": "Motor overload", "Action": "Stop cutter motor", "Notes": "Excess current"},
    {"Measurement": "VFD shunt", "Trip Condition": "≥6.0 A", "ID": "M2", "Reset": "L+MR", "Interlock": "Conveyor overload", "Action": "Stop conveyor", "Notes": "Overload condition"},
    {"Measurement": "Coolant Flow", "Trip Condition": "≤5 l/min", "ID": "C1", "Reset": "MR", "Interlock": "Low coolant", "Action": "Stop motor", "Notes": "Flow interruption"},
    {"Measurement": "Hydraulic Pressure", "Trip Condition": "≥220 bar", "ID": "H1", "Reset": "L+MR", "Interlock": "Hydraulic overpressure", "Action": "Dump valves", "Notes": "Excessive pressure"},
    {"Measurement": "Fan Overcurrent", "Trip Condition": "≥12 A", "ID": "F1", "Reset": "L", "Interlock": "Fan overload", "Action": "Stop fan", "Notes": "Electrical overload"}
]

# -------------------------------
# Page/UI
# -------------------------------
st.set_page_config(page_title="TBM Operator GUI", layout="wide")
st.title("⚡ TBM Operator GUI")
st.caption("Monitor, control, and tune powered subsystems")

tabs = st.tabs(["Main Dashboard"] + list(tbm_data.keys()))

# -------------------------------
# MAIN DASHBOARD
# -------------------------------
with tabs[0]:
    st.header("📊 Main Dashboard")

    st.markdown("### Status Key")
    st.write("🟢 **OK** — Normal")
    st.write("🟡 **LOW** — Low warning threshold crossed")
    st.write("🟠 **HIGH** — High warning threshold crossed")
    st.write("🔴 **TRIP** — Emergency shutdown condition")

    device_status = []
    for category in tbm_data.keys():
        for item in tbm_data[category]:
            label = item["Label"].replace("Screw Jack", "Screw Jack Motor")
            if label not in st.session_state.device_states:
                st.session_state.device_states[label] = {"on": False, "current": 0.0, "speed": 0, "torque": 0}

            state = st.session_state.device_states[label]
            current = state["current"] if state["on"] else 0.0
            speed = state["speed"] if state["on"] else 0
            torque = state["torque"] if state["on"] else 0

            device_status.append({
                "Device": label,
                "Current (A)": round(current, 2),
                "Torque (Nm)": round(torque, 1) if label in HAS_SPEED_TORQUE else "N/A",
                "Speed (RPM)": round(speed, 1) if label in HAS_SPEED_TORQUE else "N/A",
                "Status": f"🟢 OK",
                "Notes": ""
            })

    st.subheader("📋 System Status Panel")
    st.dataframe(pd.DataFrame(device_status), use_container_width=True)

    st.subheader("📈 TBM Running Summary")
    now = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.total_log["time"].append(now)
    total_current = sum([s["current"] for s in st.session_state.device_states.values()])
    st.session_state.total_log["current"].append(total_current)

    df_summary = pd.DataFrame({
        "Time": st.session_state.total_log["time"][-60:],
        "Current (A)": st.session_state.total_log["current"][-60:],
    })
    st.line_chart(df_summary.set_index("Time"))

    st.subheader("🛑 Demo Interlock Trigger")
    if st.button("Trigger Demo Interlock"):
        st.session_state.interlock_demo = random.choice(demo_interlocks)

    if st.session_state.interlock_demo:
        demo = st.session_state.interlock_demo
        st.warning(f"🔔 **Demo Interlock Triggered**\n\n"
                   f"**Measurement:** {demo['Measurement']}\n\n"
                   f"**Trip Condition:** {demo['Trip Condition']}\n\n"
                   f"**ID:** {demo['ID']}\n\n"
                   f"**Reset:** {demo['Reset']}\n\n"
                   f"**Interlock:** {demo['Interlock']}\n\n"
                   f"**Action on Trip:** {demo['Action']}\n\n"
                   f"**Notes:** {demo['Notes']}")

# -------------------------------
# SUBSYSTEM TABS
# -------------------------------
for i, category in enumerate(tbm_data.keys()):
    with tabs[i + 1]:
        st.header(category)

        for item in tbm_data[category]:
            label = item["Label"].replace("Screw Jack", "Screw Jack Motor")
            explanation = item["Explanation"]
            model = item["Model"]
            qty = item["Quantity"]

            if label not in st.session_state.device_states:
                st.session_state.device_states[label] = {"on": False, "current": 0.0, "speed": 0, "torque": 0}

            state = st.session_state.device_states[label]

            st.subheader(label)
            st.write(explanation)
            st.write(f"Model: `{model}` | Qty: {qty}")

            col1, col2 = st.columns(2)
            if col1.button(f"ON {label}", key=f"on_{label}"):
                state["on"] = True
            if col2.button(f"OFF {label}", key=f"off_{label}"):
                state["on"] = False

            if state["on"]:
                new_current = st.slider(f"Set Current (A) - {label}", 0.0, 10.0, state["current"], 0.1, key=f"slider_{label}")
                state["current"] = new_current

                if label in HAS_SPEED_TORQUE:
                    state["torque"] = round(new_current * 800, 1)
                    state["speed"] = round(new_current * 600, 1)
                else:
                    state["torque"] = 0
                    state["speed"] = 0

                now = datetime.datetime.now().strftime("%H:%M:%S")
                if label not in st.session_state.current_log[category]:
                    st.session_state.current_log[category][label] = {"time": [], "values": []}
                st.session_state.current_log[category][label]["time"].append(now)
                st.session_state.current_log[category][label]["values"].append(new_current)

                df = pd.DataFrame({
                    "Time": st.session_state.current_log[category][label]["time"][-60:],
                    "Current (A)": st.session_state.current_log[category][label]["values"][-60:]
                })
                st.line_chart(df.set_index("Time"))

                if label in HAS_SPEED_TORQUE:
                    st.write(f"**Current:** {state['current']} A | **Torque:** {state['torque']} Nm | **Speed:** {state['speed']} RPM")
                else:
                    st.write(f"**Current:** {state['current']} A")
            else:
                st.write("🔴 OFF")
