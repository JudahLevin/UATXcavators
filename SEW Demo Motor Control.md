# SEW Demo Motor Control

## 🟢 Startup Procedure

1. Plug in transformer  
2. Switch transformer **ON**  
3. Turn **motor key switch to “O”**  
4. Rotate **black lever vertically**  
5. On the HMI screen, press **Start → OK**  
6. Plug in **mini USB**

---

## ⚙️ Communication Setup

1. Navigate to: **Settings → Communication → Scan + Apply**  
2. Press **Scan** (top right)  

---

## ▶️ To Turn On

1. Open **MOVIKIT Diagnostics → Activate**
2. Set the following values:

| Parameter | Value |
|------------|-------|
| Enable / Emergency Stop | 1 |
| Enable / Application Stop | 1 |
| Activate Output Stage Inhibit | 0 |
| Start / Stop with Fields Ramp | 1 |
| Setpoint Speed | `[desired speed]` |

---

## ⏹ To Turn Off

Do everything **in reverse order** of the startup sequence.

---

## 📈 Viewing Scope Data (e.g., Torque)

1. Hit **Back**  
2. Select **Yes** to deactivate  
3. Open **Right Project → Tools → Scope**  
4. Click the **red “SCOPE”** button → *Recording Channel*  
5. Double-click **Lag Error**  
6. Enter value **8364.95** and press **Apply**  
   - You may toggle off any functions you don’t want to display  
7. Click **red SCOPE → Trigger → 9: Status Bits**  
8. Turn **Bit 1: Output Stage Enabled → 1s** and **Apply**  
9. Go to **Controls → Apply**

---

## 🧪 Creating a New Measurement

1. In the **Live Data** window, right-click the **Measurements** folder on the left.  
2. Select **Create New Measurement**.  
3. Verify the measurement pop-up shows the same scope values, then click **Apply**.

---

## 🧩 Recording Data

1. Go to the **Home Page** (with the two bubbles icon).  
2. Right-click on the **red control box**.  
3. Select **Activate Manual Mode**.  
4. In the **Live Data** window:
   - Press the **Play ▶️** button (top right).  
   - Set a **velocity** in the manual controls area.  
   - Turn **ON** the motor.  
5. The central graph should now populate with **live input data** from the motor.

---

✅ **Tip:** Save your scope or measurement configuration files after successful tests so you can reload them instantly for future demos.
