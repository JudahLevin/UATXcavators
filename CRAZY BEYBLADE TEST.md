# This is crazy

In the Cutter Head test, henceforth known as "CRAZY BEYBLADE TEST" on  10/11/25, we are going to measure a proxy for *p*, i.e., how many revolutions it takes to plane/clear a surface under (near) zero thrust. That will tell us something about the cutting geometry, which would be obscured by the advance rate of our actuator/jacks in future tests. In other words, we are doing *p* for broke people. 

Ingredients:

1. A container that has a diameter of greater than 4".
2. A luggage scale with at least .2 pounds precision.
3. Four, 3D-printed cutter heads: at least the current one, sharp cut, bigger center scraper, and taller scrapers
4. 4 "spools" epoxied on each cutter head
5. A bunch of rubber bands, two epoxied on each spool on opposing sides
6. A gallon of water
7. Measuring cups
8. Ruler
9. The maximum wrap count *w* of a rubber around the spool.
10. A fixed weight.

Steps:
1. Print the 4 cutter heads and epoxy a spool onto each one.
2. Cut two rubber bands and epoxy an end of each 180 degrees apart on the spool. Do this for all spools/cutter heads => Beyblades. Record 
3. Go to our Brackenridge lot with the equipment and collect a controlled volume of dirt (~1-2 cups).
5. Place the dirt in the container and add a controlled amount of water (e.g., 2 tablespoons).
6. Weigh the dirt and record the density. The volume, weight, and density must be held constant for all tests (so add and subtract as necessary).
7. Take a Beyblade, clean off the dirt, and center it on the container's patted dirt.
8. Mark a fixed distance away from the Beyblade to fix each rubber band end, and test a spot that slows down the velocity (allowing for more precise measurements and recordings). If you have time, try a new distance to test the cutter head types at a different angular velocity.
9. Set up a slo-mo camera in view of the cutters hitting the ground.
10. While holding the rubber bands, crank the Beyblade an incremental number of revolutions, starting at 1.
11. Place the fixed weight on the Beyblade for a fixed (TBD) number of seconds so that it presses into the dirt. Make sure there is no weight during the test.
12. Then, hit record on the slo-mo and LET IT RIP.
13. Let the Beyblade slow to a stop, then pick it up and snag a picture of the hole it made in the dirt.
14. Take a measurement using the ruler of the deepest and shallowest crevice. Estimate the average crevice depth with a margin of error?
15. Do this 5 times for each revolution number, ending *w*.
16. Then, increase the revolution amount, and loop this over again.
17. Finally, loop this for each cutter head type.

Your data should be an array of shape(5, 4, *w*). 5 repeats for each of the 4 cutter heads' *w* trials.

Post processing:
* Determine how much was excavated by comparing photos.
* Compare the crevices' depths and averages across the cutter heads.
      
