# Cantilever-Strip and Stiffened-Strip Model for Ring Plate Under Column Loads

## 1. Setup and Problem Description

We have a **flat annular plate (ring)**:

* Inner diameter (ID) is **fixed** (built-in support).
* Outer diameter (OD) is **free**, except at **four square columns** welded/bolted along the outer edge.
* Each column is loaded in **downward axial force** (in side view), so the plate is loaded in **out-of-plane bending**.
* The ID reacts these loads by providing a fixed (clamped) support around the inner circumference.

Rather than analyzing the entire ring at once, we look at **one representative strip** of plate **under a column**, and model how that strip bends out of plane between:

* The **ID clamp** (fixed end), and
* The **column footprint at the OD** (loaded end).

The goal is:

1. Show that a **bare plate** is overstressed under the column load.
2. Develop a **composite plate + stiffener model** to reduce bending stress to acceptable levels.

---

## 2. Justification for the Cantilever-Strip Model

Because:

* The column load is localized under each column footprint, and
* The ID is effectively a continuous fixed support,

it is reasonable to idealize:

* A **radial strip** of the plate, of effective width $$b$$, under a given column.
* That strip behaves approximately like a **cantilever beam**:

  * Fixed at the ID (built-in),
  * Span length $$L$$ (radial distance from ID to column),
  * Tip load $$F$$ (column load per strip).

This ignores 2D plate effects and circumferential load spreading, but it is **conservative** for checking local bending under a column because:

* Bending is highest near the fixed end.
* The strip model directly captures the dominant bending mechanism: **radial plate bending between OD and ID**.

So we treat the plate strip as a **rectangular-section cantilever beam** with:

* Beam depth (bending direction): plate thickness $$t$$
* Beam width (into page): effective width $$b$$

---

## 3. Un-Stiffened Plate: Bending Stress Check

For a **bare plate strip** (no rib):

* Cantilever span:
  $$L = 0.17911976\ \text{m}$$
* Plate thickness:
  $$t = 0.0127\ \text{m}$$
* Effective strip width:
  $$b = 0.05\ \text{m}$$
* Tip load (per strip):
  $$F = 8896.4\ \text{N}$$

### 3.1. Bending moment at the fixed end

For a tip-loaded cantilever:

$$
M_{\max} = F L
= 8896.4 \cdot 0.17911976
\approx 1593.5\ \text{N·m}
$$

### 3.2. Section properties of the plate strip

Rectangular cross-section (width $$b$$, thickness $$t$$):

* Second moment of area:

$$
I = \frac{b t^3}{12}
\approx 8.53 \times 10^{-9}\ \text{m}^4
$$

* Distance to extreme fiber (top/bottom):

$$
c = \frac{t}{2} = 0.00635\ \text{m}
$$

### 3.3. Maximum bending stress

$$
\sigma_{\max}
= \frac{M_{\max} c}{I}
= \frac{1593.5 \cdot 0.00635}{8.53 \times 10^{-9}}
\approx 1.19 \times 10^{9}\ \text{Pa}
= 1186\ \text{MPa}
$$

This is **far above** the yield strength of typical structural steels (e.g. 250–500 MPa).
Conclusion: **a 12.7 mm plate alone is nowhere near sufficient** for this load and span, and requires stiffening.

---

## 4. Composite Plate + Stiffener Model (New Coordinate System)

To reduce bending stress, we weld a **longitudinal stiffening rib** under the plate strip, along the entire span. The plate + stiffener form a **T-shaped composite section**.

We use the following **right-hand 3D coordinate system**:

* **Y**: vertical **height** direction (bending direction)
* **Z**: along the **cantilever length** (span), from fixed end to loaded end
* **X**: through-plate **thickness** direction

We analyze the T-section in the **Y–Z plane**, with bending about the **X-axis**.

### 4.1. Geometry and variables

* Plate (flange):

  * Thickness in X:
    $$t\ (\text{m})$$
  * Effective strip width (circumferential):
    $$b\ (\text{m})$$

* Stiffener (web):

  * Height in Y (from plate underside down):
    $$h\ (\text{m})$$
  * Thickness in X:
    $$t_s\ (\text{m})$$

* Cantilever span in Z:
  $$L\ (\text{m})$$

* Tip load at $$Z = L$$:
  $$F\ (\text{N})$$

### 4.2. Coordinate convention in Y

Let:

* $$Y = 0$$: **bottom of the stiffener**
* $$Y = h$$: **plate–stiffener interface**
* $$Y = h + t$$: **top of the plate**

### 4.3. Component areas

$$
A_p = b t
$$

$$
A_s = h t_s
$$

$$
A = A_p + A_s
$$

### 4.4. Component centroids (in Y)

$$
Y_p = h + \frac{t}{2}
$$

$$
Y_s = \frac{h}{2}
$$

### 4.5. Neutral axis location $$\bar{Y}$$ (from bottom of stiffener)

$$
\bar{Y}
= \frac{A_p Y_p + A_s Y_s}{A_p + A_s}
= \frac{b t \left(h + \frac{t}{2}\right) + h t_s \left(\frac{h}{2}\right)}
{b t + h t_s}
$$

### 4.6. Second moment of area about the neutral axis

Plate local inertia:

$$
I_{p0} = \frac{b t^3}{12}
$$

Shifted:

$$
I_p = I_{p0} + A_p (Y_p - \bar{Y})^2
$$

Stiffener local inertia:

$$
I_{s0} = \frac{t_s h^3}{12}
$$

Shifted:

$$
I_s = I_{s0} + A_s (\bar{Y} - Y_s)^2
$$

Total:

$$
I = I_p + I_s
$$

### 4.7. Extreme fiber distances

Top:

$$
Y_{\text{top}} = h + t
$$

$$
c_{\text{top}} = (h + t) - \bar{Y}
$$

Bottom:

$$
c_{\text{bot}} = \bar{Y}
$$

Largest:

$$
c_{\max} = \max(c_{\text{top}},\ c_{\text{bot}})
$$

### 4.8. Bending moment and maximum stress

$$
M_{\max} = F L
$$

Stress at distance $$c$$:

$$
\sigma = \frac{M_{\max} c}{I}
$$

Maximum:

$$
\sigma_{\max}
= \frac{F L , c_{\max}}{I}
= \frac{F L , \max\left((h + t) - \bar{Y},\ \bar{Y}\right)}
{I_p + I_s}
$$

with:

$$
I_p = \frac{b t^3}{12} + b t (Y_p - \bar{Y})^2
$$

$$
I_s = \frac{t_s h^3}{12} + h t_s (\bar{Y} - Y_s)^2
$$

and:

$$
Y_p = h + \frac{t}{2}, \quad
Y_s = \frac{h}{2}, \quad
\bar{Y}
= \frac{b t \left(h + \frac{t}{2}\right) + h t_s \left(\frac{h}{2}\right)}
{b t + h t_s}
$$

This model gives us a **closed-form way to size the stiffener** ($$h, t_s$$) and effective strip width $$b$$ for a given load $$F$$, span $$L$$, and plate thickness $$t$$ to ensure:

$$
\sigma_{\max} \leq \sigma_{\text{allowable}}
$$

for the chosen material and safety factor.

---

## 5. Numerical Example: Stiffened-Strip Bending Stress Calculation

This section applies the composite stiffened-strip model to a representative geometry. A plate strip of width $$b$$ is reinforced by a vertical stiffener of height $$h$$ and thickness $$t_s$$, forming a T-shaped composite section. The strip behaves as a cantilever of span $$L$$ carrying a tip load $$F$$.

### 5.1. Input Geometry and Loading

* Plate thickness:
  $$t = 0.009525\ \text{m}$$
* Plate strip width:
  $$b = 0.05\ \text{m}$$
* Stiffener height:
  $$h = 0.075\ \text{m}$$
* Stiffener thickness:
  $$t_s = 0.025\ \text{m}$$
* Tip load:
  $$F = 8896.4\ \text{N}$$
* Cantilever span:
  $$L = 0.17911976\ \text{m}$$

The coordinate system uses:

* $$Y$$: vertical direction (plate + stiffener height)
* $$Z$$: cantilever length
* $$X$$: plate/stiffener thickness direction

---

### 5.2. Cross-Sectional Properties

Plate area:

$$
A_p = b t = 4.7625\times 10^{-4}\ \text{m}^2
$$

Stiffener area:

$$
A_s = t_s h = 1.875\times 10^{-3}\ \text{m}^2
$$

Plate centroid:

$$
Y_p = h + \frac{t}{2} = 0.0797625\ \text{m}
$$

Stiffener centroid:

$$
Y_s = \frac{h}{2} = 0.0375\ \text{m}
$$

Composite neutral axis (from bottom of stiffener):

$$
\bar{Y}
= \frac{A_p Y_p + A_s Y_s}{A_p + A_s}
\approx 0.0461\ \text{m}
$$

---

### 5.3. Second Moment of Area

Plate about its own centroid:

$$
I_{p0} = \frac{b t^3}{12} \approx 3.60\times 10^{-9}\ \text{m}^4
$$

Shifted to global NA:

$$
I_p = I_{p0} + A_p (Y_p - \bar{Y})^2
\approx 5.45\times 10^{-7}\ \text{m}^4
$$

Stiffener about its own centroid:

$$
I_{s0} = \frac{t_s h^3}{12} \approx 8.79\times 10^{-7}\ \text{m}^4
$$

Shifted to global NA:

$$
I_s = I_{s0} + A_s (\bar{Y} - Y_s)^2
\approx 1.02\times 10^{-6}\ \text{m}^4
$$

Total composite inertia:

$$
I = I_p + I_s \approx 1.56\times 10^{-6}\ \text{m}^4
$$

---

### 5.4. Extreme-Fiber Distances

Top of plate at $$Y = h + t = 0.084525\ \text{m}$$:

$$
c_{\text{top}} = (h+t) - \bar{Y} \approx 0.0385\ \text{m}
$$

Bottom of stiffener at $$Y = 0$$:

$$
c_{\text{bot}} = \bar{Y} \approx 0.0461\ \text{m}
$$

Maximum distance:

$$
c_{\max} = c_{\text{bot}}
$$

---

### 5.5. Bending Moment and Stress

Maximum bending moment at the fixed end:

$$
M_{\max} = F L
= 8896.4 \cdot 0.17911976
\approx 1593.5\ \text{N·m}
$$

Top fiber stress:

$$
\sigma_{\text{top}} = \frac{M_{\max} c_{\text{top}}}{I}
\approx 3.93 \times 10^{7}\ \text{Pa}
= 39.3\ \text{MPa}
$$

Bottom fiber stress:

$$
\sigma_{\text{bot}} = \frac{M_{\max} c_{\text{bot}}}{I}
\approx 4.70 \times 10^{7}\ \text{Pa}
= 47.0\ \text{MPa}
$$

Maximum bending stress:

$$
\boxed{\sigma_{\max} \approx 47\ \text{MPa}}
$$

---

### 5.6. Interpretation

Even with a relatively thin plate ($$t=9.5\ \text{mm}$$), the stiffener of height $$h=75\ \text{mm}$$ and thickness $$t_s=25\ \text{mm}$$ dramatically increases the bending rigidity. Under the applied load of $$F=8896.4\ \text{N}$$ at a span of $$L=0.17911976\ \text{m}$$, the resulting bending stress is:

* $$\sigma_{\max} \approx 47\ \text{MPa}$$, giving
* $$\text{SF} \approx \dfrac{250}{47} \approx 5.3$$ against $$250\ \text{MPa}$$ steel, or
* $$\text{SF} \approx \dfrac{350}{47} \approx 7.5$$ against $$350\ \text{MPa}$$ steel.

This confirms the stiffened-strip approach provides a structurally sound load path for the ring plate under column loads for the updated shorter cantilever span.
