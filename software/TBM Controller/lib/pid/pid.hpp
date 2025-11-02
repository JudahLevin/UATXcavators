#include <limits>

class pid {
    public:
        pid();
        pid(double k_p, double k_i, double k_d, double dt = 1.0, 
            double setpoint = 1.0,
            double hi = std::numeric_limits<double>::infinity(), 
            double lo = -std::numeric_limits<double>::infinity(), 
            double initial = 0.0);
        
        void test(double bias = 0.0, double overshoot = 1.0);
        double getPIDscore(double pv);

        double getSetpoint() { return setpoint; }
        void setSetpoint(double d) { setpoint = d; }
        
    private:
        double k_p;
        double k_i;
        double k_d;

        double setpoint;
        double last_error;
        
        double accumulator = 0.0;
        
        const double dt;

        // steady_clock::time_point intervalStart = steady_clock::now();

        const double hi;
        const double lo;
};