# Setup

### Linear actuator
* Red jumper goes to ENA and +24VDC
* Black and red wires go to GND and +24VDC
* Use a 240VAC receptacle for voltage stability
* Place the controller close to the launch structure so the wires of the controller and driver can reach the PSU

### Motor & Driver
* B- -> Blue
* B+ -> Red
* A- -> Green
* A+ -> Black
* PUL- -> IO18
* DIR- -> IO19
* ENA- -> IO21
* GND -> - rail
* Vin -> +rail
* PUL+ -> +rail
* DIR+ -> +rail
* ENA+ -> +rail
* Use green USB->micro from the ESP32 to operator
* Situate the operator close to the launch structure

For adding current/torque sensors:
* OUT1 or OUT2 -> IO34
* Vin/GND power
* Outputs in-line with one of the driver-to-motor wires

PSU:
* Black from controller and driver on -
* Red from controller and driver on +

Vac:
* Pointy side of tube goes into the bucket's button side

Generator:
* Gentle surges after some oepration time is okay
* Turn on before plugging stuff in (reset circuit breakers as needed)

# Operation Checklist

* Use a continuous stroke rate on the linear actuator
* Pulse the vacuum to clear silty muck, then turn off the vacuum and spray conditioner. This makes it more watery.
* During stalls, jog the linear actuator up OR reverse direction on the motor. If jogging up, pause and let the cutter head turn for a few seconds before resuming continuous extension.
