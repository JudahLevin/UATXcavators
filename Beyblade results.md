# 1. Finding the force specs for our rubber band

| Unstretched (cm) | Stretched (cm) |
| :------------ | :------------ |
| 18 | 87 |
| 15 | 65 |
| 12 | 52 |
| 9 | 45 |
| 6 | 28 |
| 3 | 15 |

In this experiment, we lifted a fixed weight of 5.2 N (a 500 mL plastic bottle), pinching a rubber band at the unstretched length, and then recording the stretched length at which the rubber band could lift the fixed weight (when the bottle overcame gravity).

$$
\begin{aligned}
F = EA \frac{\Delta L}{L_0}
\end{aligned}
$$

Here, $EA$ is a constant, and so force is proportional to the ratio between the change in length and the unstretched state. When there is less original length, there is more force since there is less slack and the band resists more. 

Strain $\sigma$ is another way to think of $\frac{\Delta L}{L_0}$, which is just a way to measure and an equalized version of the deformation (since it adjusts for original length). 

Stress is different--it is the force applied per area of material. A way to see a material's durability, for instance, is to measure its stress vs. strain. $E$ is how stiff the material is in N/m^2, which is the relationship between stress and strain, calculated as:

$$
\begin{aligned}
E = \frac{\text{stress}}{\text{strain}} = \text{stress} \times \frac{L_0}{\Delta L} \implies stress = E \times \frac{\Delta L}{L_0}
\end{aligned}
$$

To get back to force $F$, the stress times the area, since stress is a kind of pressure metric:

$$
\begin{aligned}
F = \text{stress} \times A = EA \frac{\Delta L}{L_0}
\end{aligned}
$$

From our experiment, $EA$ = 1.42 N, SD ≈ 0.12 N

# 2. Determining the relationship between rubber band force and cutter head turn count

We measured wetted dirt at .558lb/cup, which is 10.5kPa. Then, we measured out an unstretched (nearly taut) rubber band from the cutter head center to the edge on both sides, then wrapped the rubber band around a central spindle on the cutter head, and released as the cutter head span due to the rubber band contraction. Finally, we recorded the number of revolutions of the cutter head.

We did this for 1 - 4 wraps, with a band distance of 15cm and then 32cm on each side.

We can define wrap count in terms of $\Delta L$ of the rubber band by using the circumference of the spindle, about 4cm. 

Not including the zeros, here are the statistical averages and force computations (given $EA$ = 1.42N) for $L_0$ = 15cm, where $R$ is revolutions (for computational simplicity, we assume only a one-rubber-band-spin for now, but later we will double forces since the setup uses two, symmetric rubber bands that pull in the same rotational sense):

| $\Delta L$  (cm)   | $R$     | Force (N)   |
| :------------ | :------------ | :------------ |
| 4 | didn't turn | 0.38 |
| 8 | $\mu = .775$, SD = .035 | 0.76 |
| 12 | $\mu = 1.25$, SD = .12 | 1.14 |
| 16 | $\mu = 2.22$, SD = .2 | 1.52 |

For $L_0$ = 32cm:

| $\Delta L$ (cm) | $R$ | Force (N) |
| :-------------- | :----------- | :--------- |
| 4  | didn't turn | 0.18 |
| 6  | $\mu = .625$, SD = 0 | 0.27 |
| 8  | 1 | 0.36 |
| 10 | $\mu = 1$, SD = .35 | 0.44 |
| 12 | 1.65 | 0.53 |
| 14 | 2 | 0.62 |
| 16 | 2.75 | 0.71 |

It's reassuring to see that we get around half the force values when our band length doubles.

To determine the relationship between force and revolutions, we must therefore adjust for $L_0$ (cm). Suppose $F^* = FL_0$. Then, our empirical pattern is:

| $F^*$ (N·cm) | $R$ | $k_i$ (rev/N·cm) |
| :-----------: | :----------: | :---------------: |
| 8.6  | 0.625 | 0.073 |
| 11.4 | 0.775 | 0.068 |
| 11.5 | 1.000 | 0.087 |
| 14.1 | 1.000 | 0.071 |
| 17.0 | 1.650 | 0.097 |
| 17.1 | 1.250 | 0.073 |
| 19.8 | 2.000 | 0.101 |
| 22.7 | 2.750 | 0.121 |
| 22.8 | 2.220 | 0.097 |

Taking the statistics of $k$, we get $\mu = 0.0876$, SD = .017. That describes the linear assumption: $kF^* = R$.

Using Google Sheets to find the line of best fit, we obtain the equation: 0.671 + -0.0522x + 5.82E-03x^2. This has an RMSE of .18 (better than our linear version). The small coefficient on the squared term suggests it's probably linear. What may be non-linear, and something that has been cleaned from the data thus far, is the number of revolutions when accounting for zero turns. This happens when we let go of the rubber bands, and the cutter head doesn't move.

Here is a table counting the percentage of "zeroes" that happened (for $L_0$ = 15cm, 5 trials each):

| Wrap count | Zeroes % |
| :------------ | :------------ |
| 1 | 100 |
| 2 | 80 |
| 3 | 20 |
| 4 | 0 |

# 3. Computing breakaway torque

From this data, we learn there is a threshold of force that is required to "kickstart" the cutter head--this is likely why teams who get stuck switch the direction of their cutter head. The impulse creates some inertia that makes the newly moving cutter head easier to continue moving, rather than starting at rest. This impulse may also be part of what overcomes the shearing component of the ground.

We also haven't mentioned that the rubber band force will decrease over time as the cutter head turns and adds slack to it. But we can still use the instantaneous force $F$, which happens at the moment of release, to inform our understanding of overcoming ground pressure components.

Returning to this *threshold force*, we can estimate it as the midpoint between the force at zero turns and the force at the first nonzero turn. That can get us a best guess at the *breakaway torque* $\tau$ at radius = 2cm. So we have:

| $L_0$ (cm) | “didn’t turn” $F$ (N) | First turn $F$ (N) | Estimated $F_{\text{turn}}$ (N) | Breakaway Torque $\tau = rF_{\text{turn}}$ (N·m) |
| :---------- | :-------------------- | :------------------ | :------------------------------ | :---------------------------------------------- |
| 15 | 0.38 | 0.76 | ≈ 0.55 | **0.011** |
| 32 | 0.18 | 0.27 | ≈ 0.23 | **0.0046** |

So, $\tau = .008 \pm .003\text{Nm}$

Now, we can do the same experiment for another cutter head type and compare the breakaway torque to determine cutter head efficiency.
