Bearing model: [TIMKEN 23140-EMB-W33](https://cad.timken.com/item/spherical-roller-bearings/spherical-roller-bearings-brass-cage/23140embw33)

Grease model: [Timken Construction and Off-Highway Grease](https://www.timken.com/products/timken-mechanical-power-transmission-products/lubrication-lubrication-systems/construction-and-off-highway-grease/)

Grease properties:
* Heavy Loads
* High Sliding Wear
* Dirty Environments
* Slow Speeds
* Shock Loading
* [1022gm grease qt. for 90% fill / 1261.7cm^3 bearing free volume = 810kg/m^3 grease density](https://engineering.timken.com/engineering-tool/grease-lubrication-tool/)
* [~200cSt at operating temp 60C](https://engineering.timken.com/engineering-tool/grease-lubrication-tool/)
* ~40cSt at worst-case temp 90C

$$\text{Dynamic Viscosity (Pa·s)} = [\text{Kinematic Viscosity (m/s)}] \times [\text{Density (kg/m}^3)]$$
  
$$\mu\(\text{Pa}\cdot\text{s}) = \nu\(\text{cSt}) \times \rho\(\text{kg/m}^3) \times 10^{-6}$$

=> normal case $\mu$ = 0.162Pa·s and worst-case $\mu$ = 0.0324Pa·s

Each relubrication requires 102.8g of grease. At operating temp 60C, relube every 11171hrs and at worst-case 90C, relube every 2793 hours. Given our negligible operating timespan, we do not need to relube again after the initial greasing of 1022g (see above).

A labyrinth seal is our best option to stop dirt ingress because it does not require contact with the shaft and can be more cheaply and easily fabricated in-house. For highly viscous fluids like muck, Poiseuille's Law dominates (as opposed to Bernoulli's principle of inviscid fluids). This means that muck is slowed down by the friction of the narrow axial gap between spinning teeth and the stationary, flat plate.

Then, given the ID/OD of the labyrinth equals the 200mm ID and 340mm OD, the effective radius $r_{\text{eff}}$ = 135mm. Then, $b$, the circumferential width of the flow path, is $2\pi r$ = 848mm. 

Given our bearing model's 2.5-degree misalignment tolerance from the vertical we can determine $g$, the gap height of the labyrinth seal, by computing the axial depression of the T-shaped rotor with radius $r = .07m$ after misalignment:

$$g = r\sin(\theta) = 0.0031m$$.

Our grease pump model: [SK-505 Lubricator](https://www.amazon.com/ZHHWKNBD-Electric-Automatic-Lubricating-SK505BM-1/dp/B0F26YD4YX?utm_source=chatgpt.com&th=1): 

Grease pump properties:
* [13 cc/min @ no load / negligible resistance](https://lubeng.com.au/wp-content/uploads/2019/10/SLP-SK-505-Grease-pump_DS-R4.pdf?utm_source=chatgpt.com
)

* ~6 cc/min @ full-load / maximum rated resistance

$$Q = vbg$$

Where:

- $Q$ = volumetric flow rate of grease (m³/s)
- $v$ = average outward grease velocity (m/s)

So, at maximum rated resistance 1e-7m³/s, $g = 0.0031m$, and b = .848m (see above) we can expect $v = Q/(bg)$ = 0.0000386m/s, or around 3.9mm/s.

Now, we can check our laminar flow assumption:

$$\text{Re} = \frac{\rho vg}{\mu}$$

- $$\text{Re}$$ — Reynolds number  
- $$\rho$$ — fluid density

Given our numbers above, including $\rho$ = 810kg/m^3, $\text{Re}$ =0.0029 << 1. This confirms that the viscous forces in the labyrinth's fluid flow are significantly dominant over the inertial forces.


$$\Delta P = \frac{12\mu vL}{g^2}$$

Where:
- $L$ = effective restriction length (m)

According to our worst-case numbers, $\frac{\Delta P}{L} = 1.6Pa/m$. Since $L$ has an upper bound of $r$ (see above), that gets 0.113Pa max with our current $g$. Here, viscous resistance is negligible and the muck will not slow down. Since $g^2$ is dominant in this equation, it is clear $g$ must be decreased.

Suppose instead of using the same axial gap for all teeth, we use stepped teeth that start at a small axial gap and increase toward 6.9mm max.

At some radius $r$ along the rotor, s.t. $r \in \[0, .07\]$ m, we can compute the $g$ required as:

$$r \sin(2.5 \text{ degrees})$$

Now, we can compute the largest allowable $g$ given $\Delta P$, by computing the radial pressure difference between the muck region and the bearing / labyrinth region:

$$\Delta P \approx \frac{1}{2}\rho \omega^2 (r_o^2 - r_i^2)$$

So, we can get a conservative $g$ by finding the minimum $r_i$, which is the ID/2 of the bearing, and the maximum $r_o$, the ID/2 of the muck reservoir. Then, at 0.524rad/s (5RPM), and 1600kg/m^3 density of muck, we get 94.2Pa. 
We also add hydrostatic pressure, given that the muck reservoir is completely filled and the labyrinth is 135mm from the muck reservoir top, to get $P_\text{hydrostatic} = \rho \g \h$ = 2112Pa. 

Now, we add the total radial and hydrostatic pressure to get 2213Pa. Since we want local grease pressure at the labyrinth gap slightly higher than the local muck pressure, multiply by 2x FOS to get 4.4kPa. Thus, plugging in the values to the $\Delta P$ equation we get 4.51mm.

