# October Tests
The purpose of this doc is to explain what October's tests will look like.

## Test Schedule

October's test objectives are to determine:
1. The best cutter head design
2. How to operate the conditioning subsystem
3. Expected forces for structural, propulsion, and cutter head systems

This fits into our broader goals of:
* Submitting the November Design Briefing (NDB) by November 4th (in 1 month)
* Preparing for our sequentially built and tested, full-sized TBM

### Future Tests
| Deadline | Test |
|---|---|
| Monday, October 13 | Cutter Head Test |
| Monday, October 20 | Forces Test|
| Monday, October 27 | Conditioning Test |

> 🚨 As we source parts, always weigh the tradeoffs of sourcing in-house or off-the-shelf. 

### Cutter Head Test

Let *p* be how much ground in mm the TBM eats per revolution of the cutter head, and *RPM* be the number of cutter head revolutions every minute. Then, 

$$
\begin{aligned}
\text{TBM speed (mm/min)} = p \ \text{(mm/rev)} \times \textbf{RPM}
\end{aligned}
$$

We want to increase speed. So, **Cutter Head Test**'s goal is to find the cutter head design that maximizes *p*. 
Subgoals:
* Find a low-cost way to measure *p* accurately: how do we measure how much stuff is torn up by the cutter head?
* CAD cutter head designs and 3D-print them
* Set up controlled variables, including thrust, RPM, and ground conditions

**Cutter Head Test**'s item dependencies:
* 3D-printed cutter head
* TBD materials for the experiment


### Forces Test

We need to know how to push the machine into the ground to 1) overcome friction and 2) control reaction torque.
Because of that pesky opposite reaction law, we also need a launch structure to handle the force coming off the ground.

**Forces Test** will entail a small TBM prototype:
* Torque mechanism (Jema motor delivery 10/16)
* Thrust mechanism (Valin linear actuator in dorm or gravity)
* Structure (3D-printed guide ring, launch structure, TBM body, and cutter head)
* ESP32/FPGA/stock controls, current & voltage & load cell sensors

This small-scale test is for gauging our force expectations for the real version and submitting them with the NDB, as well as finding designs that minimize specific energy (*SE*).
Objectives include:
* Measure the ground pressure for various ground conditions--very useful in physics calculations
* Measure loads on all structures
* Measure reaction torque at different ramp-ups, push speeds, and mediums
* Measure *SE* across various experimental scenarios 
* Iterate all structural designs (guide ring, et.al.)
* Do a friction analysis both axially and with torque (NDB)

### Conditioning Test

All future subsystem tests will feature the conditioning subsystem to create real cutting conditions. So, we need to determine the following:
* Injection ratio (how much conditioner vs. dirt)
* How to transport conditioner from the mixer tank (start) ➡️ tunnel face (finish)
* How to mix the conditioner and water
* How to operate the pump (including software, mechanical, and electrical)
* Whether we need a pump with different specs
* Whether ultrasound emitters are a good idea
* Which spray nozzle design to use

***Every test needs an optimization goal.*** For **Cutter Head Test**, that was maximizing *p*. For **Conditioning Test**, we are reducing $\tau$ (tau) and maximizing *p* simultaneously. 
Doesn't optimizing two things at once cause mediocre returns for both?
In this case, they behave hand-in-hand:
* $\tau$ is the torque needed to dig, which decreases when we condition (or loosen) sticky or hard ground. 
* Removing blockages on the cutter head's scrapers with conditioner makes them cut more effectively. That increases *p*.

**Conditioning Test**'s item dependencies:
* Pump: Pentair Shurflo #5059-1310-D011 (in our dorm)
* 1/2" tubing (dependent on 10/15-10/18 est. delivery from MSC)
* Solenoid valves (Amazon B09W9W5LF8)
* Pump current sensor (INA260)
* TBD controls/electronics
* TBD pump pressure sensor
* TBD other sensors (e.g. vibration/temp) and valves (e.g. clean)
* TBD any other parts for NABC compliance
