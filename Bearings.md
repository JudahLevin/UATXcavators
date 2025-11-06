# Bearings

[Timken Thrust Bearing Catalog](https://catalog.timken.com/Thrust-Bearing-Catalog/18/)

* *Cageless* allows for more load capacity at lower speed since the densely packed rollers increase friction
* *Tapered bearings* are best suited to withstand the shocks or vibrations that will cause radial misalignment. We expect some radial load due to cutting imbalances and moments, as well as ground resistance.
* *Double-acting bearings* handle bidirectional loads for extending the linear actuator and retracting it while carrying the TBM weight.
* Type TTD bearings are double-acting thrust tapered roller bearings
* Angular contact bearings are better suited to radial loads than thrust spherical roller bearings (e.g., tapered, barrel ones) because they don't slide off the raceway but are held in place by angled, flat faces. To calculate the Dynamic Equivalent Thrust Load ($P_a$), the multiplier for radial load ($F_r$) is 1.2 for dynamic spherical (2.7 for static) and .76 for angular contact (p. 20), indicating that the spherical type is more sensitive to radial, dynamically and statically. Also, the axial load ($F_a$) is equally sensitive in both cases. 
* $P_a$ determines the life of the bearing
* Clay is soft and ductile, which can cause lubrication and sealing problems, though fewer mechanical issues.
* Rock is hard and brittle, which is more damaging than clay, particularly mechanically, as it can be both ductile and brittle.
* Significantly more misalignment tolerance in thrust ball bearings than any other type
* DTVL is bidirectional angular contact (mounting on p. 36)
* Worst case speed: 30 RPM or 3.14 rad/s. The heat generation and energy loss due to the bearing are a result of the operation speed, thrust load, lubrication viscosity, and bearing geometry/torque factors.
* *Grease* can act as a sealant, not oil, which is necessary for blocking muck, and better for low-speed applications. Aluminum and Calcium sulfonate greases have the most excellent resistance to water ingress. We want to choose a grease that will resist abrasive particles and water to reduce wear. Timken Construction and Off-Highway Grease, for instance, is meant for dirty environments (p. 60).
* Only for low-speed applications can the entire housing be filled with grease to protect against moisture and contaminants.
* The smallest angular contact TVL has 11.6 in OD, thrust cylindrical roller 6 in, tapered roller has 4 in ID, but the DTBL (double-acting) is too wide.


# Couplers

* Our motor is a 3.625" diameter bore with a 7/8" key
* Increasing the diameter and decreasing the length of the support decreases the bending normal and torsional shear of a shaft at a cubic rate.
* Longer, thicker, taller keys decrease bearing stress.
* Unbalance, vibration forces from the cutter head increase at the square of the RPM. This vibration can dominate if the RPM is too high. But at 5 RPM, there is very little vibrational imbalance, and heat in the elastomer is minimal.
* More OD in rubber increases torque capacity. Increasing axial height absorbs greater forces due to the higher material volume, as well as increases misalignment capacity because angular deflections are stretched out over a longer length. Hardness is measured by a durometer, allowing for increased torque capacity but less shock absorption (more brittle). The durometer grades in increasing hardness are 64A, 80A, 92A, and 98A.
* A flexible coupler acts as a spring or damper to protect the gearbox output against shock loads and misalignment.
* The coupler must handle peak torque, e.g., when hitting a rock, at 3x nominal torque => 12,000 Nm.
* The softer the material, the less torque transmitted since some force is absorbed as it compresses. But it allows for better shock absorption and misalignment protection.
* We will buy a few hardness levels of spider elastomers and fabricate the hub.
* H-type is capacious enough. [ROTEX sizes 110 and up have sufficient torque, in particular](https://www.ktr.com/fileadmin/ktr/media/Tools_Downloads/kataloge/01_flexible_jaw_bin_bush_ROTEX.pdf) That size corresponds with about 200mm diameter, 300mm length.
* We are optimizing to minimize backlash and OD for compactness and more open space on the cutter head.
* [Here is the CAD library](https://www.ktr.com/us/en/services-and-tools/cad-library/3d-cad-library/): ROTEX -> 001 (standard) -> 125/110
