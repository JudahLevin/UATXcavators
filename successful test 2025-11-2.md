# Test Setup

* Anti-torque control with a chopstick arm (2x4) where two protruding steel plates hugged the outer diameter of the PVC mucking tube and stopped it from twisting (with some tolerance)
* A linear actuator running on 240VAC to power the servo, + 24VDC from our RSP PSU to power the controller. Presses the jog button at 0.125 in/sec to press the TBM into the ground.
* First operator on HP laptop controlling the linear actuator in the wizard, manually jogging a 1-2 seconds at a time in either direction, then letting the cutterhead spin in the ground for ~10-30 seconds after each downward jog.
* Gantry lifted two cinder blocks high for clearance between the TBM and the ground. ~100lb sandbag counterweights on the corners.
* Motor inside the TBM running at different speed modes in both directions. Wiring for the motor was ferruled and extended, while the motor driver was taped to a gantry leg. Motor powered by the same PSU as the actuator controller (wires stacked on DC outputs).
* Driver, ESP32, and breadboard taped onto cardboard. The second operator is sitting a foot away from the ESP32 with a micro USB connection.
* Conditioning system including a peristaltic pump to dose dish soap and a diaphragm pump to send water supply down a single line. Then, a manifold splits the streams and rests on the surface. Diaphragm pump and peristaltic, both 12V, powered by a car battery.
* The third operator touches both pumps' negative terminals (black wires) to the negative terminal of the battery to complete the circuit (red + already connected) to spray soapy water from the manifold.
* Generator ran on propane.
* A wet/dry vacuum connected to the external PVC tube on the TBM, sucking up muck above the cutter head and dumping it into a Home Depot bucket.

# Observations
* Initial DC voltage link low errors on the linear actuator wizard. Simultaneous circuit-breaking on the 120VAC generator ports when two slots were used for the actuator's main power + controls. This was even after a new receptacle on the problematic one. This was solved by using 240VAC to power the actuator, which was in a different receptacle with more current. We suspect the current rating on the 120VAC outlet was insufficient to handle both actuator loads.
* Backflow?? TBD
* When jogging the linear actuator, in case of a motor stall, if reversing direction worked, it only worked the first time (i.e., when the motor operator hit 'R' on the keyboard once). But if >1 reversal happened and the motor was still stalled, reversing repeatedly afterwards did nothing. In that case, jogging the linear actuator to retract slightly allowed the cutter head to start spinning again. Then, we jogged back down to continue digging.
* Motor stalls occurred temporarily (1-2 seconds) if a rock was in the way or the cutter head caught on something. Stalls that necessitated motor reversals/jogs to break free happened when the cutter head wasn't allowed to cut the same spot for long enough ("idle time"). Stalling happened <10 seconds of cutter head idle time. Using the jog speed above, this implies that the TBM could sustain a max speed of .0125in/sec (a 1-second jog every 10 seconds) or 19mm/min.
* The vacuum successfully picked up the muck, even at a distance of about 1” from the muck level. The largest particle it picked up was .68in (from inside the disposal bucket). It clogged 2-3 times, and during clogs, flushing the tube with water and ensuring the intake was not immersed in water was sufficient to continue suction. Inside the disposal bucket, there was an 8-inch high material, three layers of material formed (@ 10in diameter, that is about 2.75gal). ~½ of the height was warm form, then the bottom part was noticeably cooler silt, with the density increasing as we went down. We confirmed this separation was due to settling. The inner diameter of the PVC tube is .75in, which means it fits a .68in particle. Because there was no curve in this smaller tube, by the time there was a curve, it was already in the larger 1.25-inch-diameter vacuum tube and had space to move.
* We dug a 5-inch deep, 9-inch diameter hole.
* The metal on the end of the chopstick arms began to bend since there was only one set of screws and it was on the opposite end, creating a torque arm/bending moment. Also, as the TBM lowered into the ground, the reaction arm on the top end of the PVC tube created a torque arm at the bottom, causing shakiness in the cutter head. This requires another reaction arm at the bottom. A good idea is to create a cutout of the machine with a wooden plate and then situate the cinders on top of it to stop it from twisting. The cutout part hugs the external PVC pipe.
* The soapy water successfully created a slurry and loosened the ground. 


# For the future
* Add sensors for current, RPM, and vibration, to automate and get feedback from the motor to respond with movements with the actuator when it stalls.
* Add methods to control the pump flow/current.
* Alligator clips to safely connect wires to the battery.
* Switches to turn on and off the two pumps rather than repeatedly touching the wire.
* Automate the linear actuator control instead of manually jogging. Get data on current, stroke length, and advance speed that we can control for and experiment with.
* Create a better anti-torque control method by stabilizing the bottom of the TBM—and allowing for deeper digging. Make the metal pieces on the 2x4 more sturdy–scale them back and use the second set of screws, or buy longer, thicker, narrower pieces (~$4 at Ace).
* Test with professional conditioner and record data vs dry or soapy conditions.
* Test and compare different cutter head designs (e.g., with smaller bolts and/or gaps) and record max tunneling speeds.
* Use an emergency stop in the motor code so that it doesn’t loop through and delay when we need to immediately shut down, but instead bypasses control logic.
* Do a better spray paint job on the TBM. 
* Go DEEPER (up to the max stroke length)!

