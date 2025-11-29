## Stress from Torque on Segment / Push Plate / L-Bracket Bolts

**Given:**

- $$n = 4$$  
- Worst-case torque per rib: $$T = 1000\ \text{Nm}$$  
- Minimum bolt radius: $$r = 0.225\ \text{m}$$  
- Net bolt force:  
  $$F_{\text{bolt}} = \frac{T}{r} = 4444.4\ \text{N}$$

**Bolt Shear Check**

- Allowable shear for metric Grade 8:  
  $$\tau_{\text{allow}} = 0.3\,\sigma_y = 249\ \text{MPa}$$
- Required bolt shear area:  
  $$A_{\text{req}} = \frac{F_{\text{bolt}}}{\tau_{\text{allow}}} = 0.00001716\ \text{m}^2$$
- Actual tensile stress area (1/2"-28 Grade 8 hex bolt):  
  $$A = 0.0001096772\ \text{m}^2 \gg A_{\text{req}}$$

---

## Bearing on the 3/8" Plate Around the Bolt Hole

- Allowable bearing stress (SF = 4):  
  $$p_{\text{allow}} = \frac{\sigma_y}{4} = 62.5\ \text{MPa}$$
- Bolt diameter: $$d = 0.0127\ \text{m}$$  
- Plate thickness: $$t = 0.009525\ \text{m}$$  
- Bearing stress:  
  $$p = \frac{F_{\text{bolt}}}{d\,t} = 36.7\ \text{MPa} < p_{\text{allow}}$$

We do not worry about bracket rotation because four L-brackets are equally spaced around the segment and balanced for torque.

---

## Segment / Push Plate Rib L-Bracket — Axial Check

- $$n = 4$$  
- Hole diameter: $$d = 0.0127\ \text{m}$$  
- Width: $$b = 0.0381\ \text{m}$$  
- L-bracket thickness: $$t_l = 0.01905\ \text{m}$$  
- Plate thickness: $$t_p = 0.0095\ \text{m}$$  
- Applied force on upright leg: $$F = 8896\ \text{N}$$

### Section Properties

- Second moment of area:  
  $$I = \frac{b\,t_l^3}{12} = 2.2\times 10^{-8}\ \text{m}^4$$
- Neutral-axis extreme fiber:  
  $$c = \frac{b}{2} = 0.01905\ \text{m}$$
- Load height:  
  $$h_v = 0.01905\ \text{m}$$

### Allowable Deflection

- $$\delta_{\text{allow}} = \frac{h_v}{300} = 0.0000635\ \text{m}$$

### Bending Stress at the Heel

- $$\sigma_b = \frac{6Fh_v}{b\,t_l^2} = 73.5\ \text{MPa}$$  
  (within allowable, ~4× FOS)

### Shear Stress at the Heel

- $$\tau = \frac{F}{b\,t_l} = 12.3\ \text{MPa}$$  
  (well within allowable)

### Bearing Stress on Plate at Bolt Hole

- $$\sigma_{\text{bearing}} = \frac{F_{\text{bolt}}}{t_p\,d} = 73.7\ \text{MPa}$$  
  (within allowable)

### Bracket Deflection

- $$\delta = \frac{F\,h_v^3}{3EI} = 0.00000466\ \text{m}$$  
  (far below $$\delta_{\text{allow}}$$)

---

# TBM Wall Axial Stress

**Given:**

- Axial compression: $$N = 35585\ \text{N}$$
- Wall/rib length: $$L = 0.508\ \text{m}$$
- Bending moment (worst case): $$M = 18077\ \text{Nm}$$
- Allowable combined stress (4× FOS):  
  $$\sigma_{\text{allow}} = \frac{\sigma_y}{4} = 60\ \text{MPa}$$
- Rib radius: $$R = 0.27\ \text{m}$$
- Number of ribs: $$n = 4$$
- Rib area: $$A = \text{unknown (solve for required)}$$  
- Skin: 12-gauge sheet (≈2.7 mm) forming thin cylinder

### Axial Stress

Treat ribs as $$n$$ point-areas around radius $$R$$:

- Axial stress:  
  $$\sigma_N = \frac{N}{nA}$$

### Bending Stress from Wall Moment

Section inertia (ribs dominate):

- $$I = n A R^2$$

Bending stress:

- $$\sigma_b = \frac{M R}{I} = \frac{M}{n A R}$$

### Combined Stress

- $$\sigma_c = \sigma_N + \sigma_b$$
- $$\sigma_c = \frac{N}{nA} + \frac{M}{nAR} = \frac{N + \frac{M}{R}}{nA}$$

Set equal to allowable:

- $$A \ge \frac{N + M/R}{n\,\sigma_{\text{allow}}}$$

Numerically:

- $$A \ge \frac{35585 + 18077/0.27}{4 \cdot 60\times 10^6} = 0.000427\ \text{m}^2$$

This corresponds to a rib cross-section of:

- $$21\ \text{mm} \times 21\ \text{mm}$$  
meeting minimum stress requirements.

---

# TBM Wall Rib Buckling Check

- Rib load (per rib): $$P_{\text{rib}} = 8896\ \text{N}$$
- Young’s modulus: $$E = 200\ \text{GPa}$$
- Effective length factor (pinned–pinned): $$K = 1$$
- Rib height/length: $$L = 0.508\ \text{m}$$
- Rib width = $$b$$, thickness = $$t$$

### Euler Buckling Load

For a rectangular rib:

- $$P_{\text{cr}} = \frac{\pi^2 E\, t\, b^3}{12 (K L)^2}$$

With 4× FOS:

- $$P_{\text{cr}} = 35585\ \text{N}$$

Solve for minimum stiffness product:

- $$t b^3 \ge \frac{P_{\text{cr}} \cdot 12 (K L)^2}{\pi^2 E} = 5.6\times 10^{-8}$$

### Example Rib Size (Radially Oriented for Strong Axis)

Let:

- $$b = 38.1\ \text{mm} = 0.0381\ \text{m} \ \text{(1.5 in)}$$  
- $$t = 38.1\ \text{mm} = 0.0381\ \text{m} \ \text{(1.5 in)}$$

Then:

- $$t b^3 = 0.0381^4 = 2.11\times 10^{-6} \gg 5.6\times 10^{-8}$$
- Cross-section area:  
  $$b t = .00145\ \text{m}^2 \gg 0.000427\ \text{m}^2$$

**Conclusion:**  
A 38.1 mm × 38.1 mm (1.5 in × 1.5 in) rib vastly exceeds both bending-compression and Euler-buckling requirements, even under 4× safety factor.

