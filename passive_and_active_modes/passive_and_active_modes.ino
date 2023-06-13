// Including important libraries
#include <AccelStepper.h>
#include <MedianFilter.h>
#include <HX711_ADC.h>
#include <VL53L0X.h>
#include <Wire.h>

// Defining pins
#define interruptPin1 2  // front limit switch
#define interruptPin2 3  // rear limit switch
#define HX711_dout 4       // mcu > HX711 dout pi
#define HX711_sck 5        // mcu > HX711 sck pin
#define stepperPulse 7
#define stepperDirection 8
#define stepperEnable 9
#define start_EMG 12       // communicate the EMG arduino 2 to start grabbing data
#define start_position 11  // communicate with position sensor arduino 3 grabing data
//analog_in A0
//SDA_pin A4
//SCL_pin A5

/*  Motor speed range for passive mode 100 RPM (666 P/s) - 300 RPM (2000 P/s)
  
    666  P/s = 100 RPM --> test
    800  P/s = 120 RPM --> 10%
    933  P/s = 140 RPM --> 20%
    1066 P/s = 160 RPM --> 30%
    1200 P/s = 180 RPM --> 40%
    1333 P/s = 200 RPM --> 50%
    1466 P/s = 220 RPM --> 60%
    1600 P/s = 240 RPM --> 70%
    1733 P/s = 260 RPM --> 80%
    1866 P/s = 280 RPM --> 90%
    2000 P/s = 300 RPM --> 100%
 */

String stringCommand;
AccelStepper motor_actuator(1, stepperPulse, stepperDirection);
MedianFilter filterObject(28, 360);

// Initiate objects with their constructors
HX711_ADC LoadCell(HX711_dout, HX711_sck);
VL53L0X distance_sensor;

// Global Variables

// PID variable computation
float e2 = 0, e1 = 0, e0 = 0;
float u2 = 0, u1 = 0, u0 = 0;
float a0, a1, a2, b0, b1, b2;
float ku1, ku2, ke0, ke1, ke2;

float r;  // reference command
float y;  // plant output

float Kp = 80;  // proportional
float Ki = 0;   // integral
float Kd = 0;   // derivative

float N = 0;      // filter coeff
float Ts = 0.05;  // 20 Hz sample frequency

// Methods & functions
void init_pid(float Kp, float Ki, float Kd, float N, float Ts);

// Passive training control utilities
int maxSpeed_contCommand = 900;  // during continuous command mode

// Angle sensor utilities
const int angleSensorPin = A0;  // pot at knee mechanism
int sensorValue = 0;
const int offsetAngle = 90;  // systematic offset from absolute potensiometer reading

// PID input and activation parameters
float targetAngle;        // target angle value (for single/continuous command)
float measuredAngle = 0;  // value read from pot
bool pidGo = false;       // Go-NoGo for pid controller
bool led_state = LOW;

// Undersampling utilities
unsigned long startTime_dur;
unsigned long startTime;           // start time
unsigned long currentTime;         // current time
const unsigned long period = 500;  // undersampling data period
unsigned long start_program = millis();
unsigned int offsetCount = 0;      // timer offset counting

// Volatile passive mode parameters:
float max_ref;          // maximum angle limit
float min_ref;          // minimum angle limit
long maxMotorSpeed;     // moving speed of passive exercise
unsigned long endTime;  // duration of passive exercise
volatile long assignedSpeed;

// Haptic rendering terms
float y_n, y_n_1;          // position term
float a_coef_1;            // position coef
float b_coef_0, b_coef_1;  // force coefficient
float f_n, f_n_1;          // force term
long step_target_n;        // position converted to steps

// Proportional control input paramters (for angle tracking)
float max_angle;              // maximum angle limit
float min_angle;              // minimum angle limit

// Activation parameters for ISR
int count_pidGo = 0;    // to down sample the proportional control
bool activeGo = false;  // Go-NoGo for active admittance

// Max speeds for functions in ISR
long max_active_speed = 1500;  // [step/s]
long max_return_speed = 900;   // [step/s]

// HX711 utilities
unsigned long t = 0;
float measuredForce = 0;
boolean newDataReady = false;

// VLX Distance sensor utils
float sliderDistance;  // Origin is at theta = max_angle
float zeroDistance;    // correcting value to sliderDistance
// float sensorReading; // actual mm reading of sensor
// Note: sliderDistance = zeroDistance-sensorReading

/*
  PASSIVE MODE 
  Description
  *
  *   This script is for testing passive capabilities only.
  *   
  *   COMMAND '0'
  *   First part of this code deals with with continuous motion 
  *   tracking that comes from the serial buffer
  * 
  *   COMMAND '1'0;3
  *   Second part of this code deals with giving single commands
  *   that will first parse the command signals into parameters, and 
  *   then execute training program based on the parameters parsed.

  ACTIVE MODE
  Description
  *   Full-active and assistive control functionality
  *   --------------------------------------------------
  *   for all active exercises, there are two operation running
  *   within internal interrupt:
  *     1. haptic rendering for active mode (activeGo)
  *     2. knee angle proporsional control (pidGo)
  * 
  *   Active exercise split in two ways:
  *     1. assistive exercise
  *     2. full-active exercise (2 subprograms)
  *        - isotonic
  *        - isometric
*/

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  // Serial.setTimeout(0.1);

  Serial.println(measuredAngle);

  pinMode(LED_BUILTIN, OUTPUT);

  // Pin setup
  pinMode(stepperPulse, OUTPUT);
  pinMode(stepperDirection, OUTPUT);
  pinMode(stepperEnable, OUTPUT);

  // Pin init
  digitalWrite(stepperPulse, LOW);
  digitalWrite(stepperDirection, HIGH);
  digitalWrite(stepperEnable, HIGH);

  digitalWrite(LED_BUILTIN, led_state);

  //=== I. Basic system functionality ===
  setup_stepper();

  //=== II. Load cell config ===
  setup_load_cell();

  //=== III. Distance Sensor config ===
  //setup_distance_sensor();

  // Enable PID and internal interrupt
  init_pid(Kp, Ki, Kd, N, Ts);
  TimerInit();
  startTime = millis();
}

void loop() {

  // 1. Null: Loop level, set motor speed to zero
  activeGo = false;
  motor_actuator.setSpeed(0);
  motor_actuator.runSpeed();  // making sure the motor stops when command stops

  // 2. program functionality (mode '0', '1', '2', and '3')
  check_serial();

  // 3. Checking knee angle
  read_angle();
  print_data("void");
  sensorValue = analogRead(angleSensorPin);
  measuredAngle = float(map(sensorValue, 0, 1023, 0, 333) - offsetAngle);  // map it from 0 to 333 degrees

  // currentTime = millis();  // grab time
  // if (currentTime - startTime >= period) {
  //   Serial.print("loop ");
  //   Serial.print(measuredAngle);
  //   Serial.print(" ");
  //   Serial.print(u0);
  //   Serial.print(" ");
  //   //Serial.print(u1); Serial.print(" ");
  //   //Serial.print(u2); Serial.print(" ");
  //   Serial.print(e0);
  //   Serial.println(" ");
  //   //Serial.print(e1); Serial.print(" ");
  //   //Serial.print(e2); Serial.println(" ");
  //   startTime = currentTime;
  // }
}

void check_serial() {

  if (Serial.available() > 0) {

    stringCommand = Serial.readStringUntil('\n');

    // if and else if statement to see if string command
    // is either '0', '1', '2', '3', '9', or "-s"

    // OPTION '0'
    if (stringCommand.charAt(0) == '9') {
      bool check_angle = true;
      while (check_angle) {
        if (Serial.available() > 0) {
          stringCommand = Serial.readStringUntil('\n');

          if (stringCommand == "-s") {
            check_angle = false;
            break;
          }
        }
        sensorValue = analogRead(angleSensorPin);
        measuredAngle = float(map(sensorValue, 0, 1023, 0, 333) - offsetAngle);  // map it from 0 to 333 degrees
        Serial.println(measuredAngle);
      }
    }
    if (stringCommand.charAt(0) == '0') {
      pidGo = true;
      startTime = millis();
      // Serial.println("Entering mode 0");
      // delay(1000);

      // a. Update max speed
      maxMotorSpeed = maxSpeed_contCommand;
      motor_actuator.setMaxSpeed(maxMotorSpeed);
      zero_everything();
      while (pidGo) {

        // b. Keep checking for Reference angle
        targetAngle = float(getValue(stringCommand, ';', 1).toInt());

        // c. Measured angle
        sensorValue = analogRead(angleSensorPin);
        measuredAngle = float(map(sensorValue, 0, 1023, 0, 333) - offsetAngle);  // map it from 0 to 333 degrees

        if (Serial.available() > 0) {
          stringCommand = Serial.readStringUntil('\n');

          if (stringCommand == "-s") {
            pidGo = false;
            break;
          }

          else if (stringCommand.charAt(0) == '0') {
            targetAngle = float(getValue(stringCommand, ';', 1).toInt());
          }
        }

        else if (measuredAngle == targetAngle) {
          pidGo = false;
          break;
        }

        //Note: update the reference and measured angle @ t = n for
        // control loop @ t = n.
        // e. run motor
        motor_actuator.setSpeed(assignedSpeed);
        motor_actuator.runSpeed();

        // d. undersampling serial print
        currentTime = millis();
        if (currentTime - startTime >= period) {
          // Serial.print("'0' ");
          Serial.println(measuredAngle);
          // Serial.print(" ");  //print to raspberry pi system
          // Serial.print(u0);
          // Serial.print(" ");
          //Serial.print(u1); Serial.print(" ");
          //Serial.print(u2); Serial.print(" ");
          // Serial.print(e0);
          // Serial.println(" ");
          //Serial.print(e1); Serial.print(" ");
          //Serial.print(e2); Serial.println(" ");
          startTime = currentTime;
        }
      }
    }

    // OPTION '1'
    if (stringCommand.charAt(0) == '1') {

      passive_mode_control(stringCommand);  // parsing single command
      pidGo = true;
      bool from_front = true, from_rear = !from_front;  // initialize direction to max_ref
      // front: near motor (min_ref domain)
      // rear: far from motor (max_ref domain)
      // Serial.println("Entering 1 mode");
      // Serial.print("Max angle: ");
      // Serial.println(max_ref);
      // Serial.print("Min angle: ");
      // Serial.println(min_ref);
      // Serial.print("Max speed: ");
      // Serial.println(maxMotorSpeed);
      // Serial.print("Duration: ");
      // Serial.println(endTime);
      // delay(1000);
      startTime = millis();
      startTime_dur = millis();
      zero_everything();
      start_program = millis();

      while (pidGo) {

        // a. *Update max speed

        //  *already handled in 'passive_mode_control' (utilizing 'speed' variable)

        // b. Reference angle (utlizing 'max angle' and 'min angle' variable)

        // -> assigning target while still on going
        if (from_front == true && from_rear == false) {
          if (measuredAngle == max_ref) {  // -> change direction at the end of the rail
            delay(1000);
            // Serial.print("current and target angle: ");
            Serial.println(measuredAngle);
            // Serial.print(" ");
            // Serial.println(max_ref);
            from_front = !from_front;
            from_rear = !from_rear;
            targetAngle = min_ref;

          } else {
            targetAngle = max_ref;
          }
        }
        if (from_front == false && from_rear == true) {
          if (measuredAngle == min_ref) {
            delay(1000);
            // Serial.print("current and target angle: ");
            Serial.println(measuredAngle);
            // Serial.print(" ");
            // Serial.println(max_ref);
            from_front = !from_front;
            from_rear = !from_rear;
            targetAngle = max_ref;
          } else {
            targetAngle = min_ref;
          }
        }

        // c. Measured angle
        /*sensorValue = analogRead(angleSensorPin);
        measuredAngle = float(map(sensorValue, 0, 1023, 0, 333)-offsetAngle);
        */
        // d. run motor
        motor_actuator.setSpeed(assignedSpeed);
        motor_actuator.runSpeed();

        // e. Stoping criteria (utilizing 'duration' variable and force stop "-s")
        if (Serial.available() > 0) {
          stringCommand = Serial.readStringUntil('\n');

          if (stringCommand == "-s") {
            pidGo = false;
            break;
          }
        }

        // f. undersampling print
        currentTime = millis();
        if (currentTime - startTime >= period) {
          // Serial.print("'1' ");
          Serial.println(measuredAngle);
          // Serial.print(" ");  //print to raspberry pi system
          // Serial.print(u0);
          // Serial.print(" ");
          // Serial.print(e0);
          // Serial.print(" ");
          // Serial.print(targetAngle);
          // Serial.print(" ");
          // Serial.println(currentTime - start_program);
          startTime = currentTime;
        }

        currentTime = millis();
        if (currentTime - startTime_dur >= endTime) {
          pidGo = false;
          break;
        }
      }
    }
  }
  /* OPTION '2'
     * Command usage:
     * "2;ka;an;bn;bn1;max_angle;min_angle\n"
     */
  if (stringCommand.charAt(0) == '2') {
    // semi-assistive code goes here
  }

  /* OPTION '3'
     * Command usage:
     * "3;0;an;bn;bn1;max_angle;min_angle\n"
     * 
     * Test system:
     * [damper spring] = [0.2 0.03] Ns/mm, N/mm, sampling_freq = 20 Hz
     * usage: 3;0;0.99252802;0.124533;0.124533;110;20
     * 
     * manually calculate other usage with 
     * other parameters using this google colab:
     * https://colab.research.google.com/drive/1NBvsuMGZIsFkjUHBi1qZHPs5PDAhqjWN#scrollTo=d69cb7a7
     * 
     */
  if (stringCommand.charAt(0) == '3' && stringCommand.charAt(2) == '0') {
    // Serial.println("Initiating mode '3' Isotonic");
    // Serial.println(" ");
    pidGo = false;
    activeGo = false;

    // Mode '3' initialization
    // a. parse command
    // Serial.println("a. parsing command");
    // Serial.println(" ");
    // delay(500);
    parse_active_isotonic(stringCommand);  // parsing single command

    // b. zero proportional control
    // Serial.println("b. zeroing control param");
    // Serial.println(" ");
    delay(500);
    zero_everything();

    // c. zeroing stepper position (home)
    // Serial.println("c. zeroing motor position");
    // Serial.println(" ");
    delay(500);
    read_angle();
    back_to_flexion();
    motor_actuator.setCurrentPosition(0);  // set home

    // d. zeroing load cell (tare)
    // Serial.println("d. zeroing force sensor");
    // Serial.println(" ");
    LoadCell.tare();  // tare (zero load cell)
    boolean tareStatus = false;
    while (!tareStatus) {

      // Serial.println("taring");
      delay(1000);
      if (LoadCell.getTareStatus() == true) {
        tareStatus = true;
      }
      Serial.println(tareStatus);
    }
    // Serial.println("Tare complete.");
    // Serial.println(" ");
    // delay(500);

    // e. slider position
    /*distance_sensor.setMeasurementTimingBudget(200000); //set measurements for high accuracy
      zeroDistance = distance_sensor.readRangeSingleMillimeters(); //read position once
      sliderDistance = zeroDistance - distance_sensor.readRangeSingleMillimeters(); //current slider position from origin
      distance_sensor.setMeasurementTimingBudget(50000); //set measurements for high speed (takes up to 50 ms on loop)
      //distance_sensor.startContinuous(); //read distance continuously
      */

    // f. enter program
    // Serial.println("Entering mode '3': isotonic");
    // delay(500);
    activeGo = true;

    digitalWrite(start_EMG, HIGH);       // start getting EMG data!
    digitalWrite(start_position, HIGH);  // start getting slider position data!


    //long startTime_local = millis(); // local variable to track loop duration
    start_program = millis();
    currentTime = millis();
    print_data_once("mode30");
    startTime = millis();

    while (activeGo) {  // EXECUTE ACTIVE TRAINING MODE
      //long start_loop = millis(); // local variable to track loop duration
      // a. Read force sensor
      read_force();

      // b. move motor
      move_motor();

      // c. Current measured angle
      read_angle();

      // d. Current measure slider position
      //read_slider_position();

      // e. Stoping criteria (force stop "-s")
      stopping_criteria_hap_ren();

      // e. undersampling print
      print_data("mode30");

      // f. check if measured angle <= min_angle
      back_to_flexion_2();

      // g. tare force sensor when received 't' command
      tare_force_sensor();


      // h. print loop duration time
      /*
        currentTime = millis();
        if (currentTime-startTime_local >= period){
          Serial.println(currentTime-start_loop);
          startTime_local = currentTime;
        }*/
    }
    digitalWrite(start_EMG, LOW);
    digitalWrite(start_position, LOW);
  }
}

void TimerInit() {
  /* Initialize timer1 
   * Sampling Frequency = 100 Hz 
   * Timer for PID loop in passive training (angle control)  
   * 
   * Study reference:
   * https://www.robotshop.com/community/forum/t/arduino-101-timers-and-interrupts/13072
   * 
   */
  noInterrupts();  //disable all interrupts
  TCCR1A = 0;      // Timer or Counter Control Register
  TCCR1B = 0;      // The prescaler can be configure in TCCRx
  TCNT1 = 0;       // Timer or Counter Register. The actual timer value is stored here.

  OCR1A = 15624;  // Output Compare Match Register (16Mhz/256/<sampling_freq>Hz)
  //62499 (1 Hz);//31249 (2Hz); //15625 (4Hz) //6249 (10Hz);
  //624 (100Hz);

  TCCR1B |= (1 << WGM12);   // CTC (Clear Time on Compare Match)
  TCCR1B |= (1 << CS12);    // 256 prescaler
  TIMSK1 |= (1 << OCIE1A);  // Interrupt Mask Register (Enable Output Compare Interrupt)
  interrupts();             // Enable all interrupts
}

void passive_mode_control(String activationCode) {
  /* Actuation for passive training commands in
   *  single commands. This is essentially an activation command parser
   *
   * Command content:
   *  '1;XXX;YYY;ZZZ;AAA\n'==>single command code;max angle;min angle;speed;duration
   *  Args:
   *    activationCode [str]: contains parameter to do single command executions
   */

  String cmd_maxAngle = getValue(activationCode, ';', 1);
  String cmd_minAngle = getValue(activationCode, ';', 2);
  String cmd_speed = getValue(activationCode, ';', 3);
  float cmd_duration = getValue(activationCode, ';', 4).toFloat();

  // 1. max angle target
  max_ref = float(cmd_maxAngle.toInt());

  // 2. min angle target
  min_ref = float(cmd_minAngle.toInt());

  // 3. Max speed settings
  maxMotorSpeed = speed_selector(cmd_speed);
  motor_actuator.setMaxSpeed(maxMotorSpeed);
  motor_actuator.setSpeed(0);
  motor_actuator.runSpeed();
  motor_actuator.setAcceleration(800);

  // 4. Training Duration
  float minutes_sys = cmd_duration;                                 // [minutes with decimals]
  endTime = minutes_sys * (unsigned long)60 * (unsigned long)1000;  // [milliseconds]
}

// FUNCTIONS X: Setup functions
//------------------------------
// setup stepper motor pins and other pins
void setup_stepper() {
  pinMode(stepperPulse, OUTPUT);
  pinMode(stepperDirection, OUTPUT);
  pinMode(stepperEnable, OUTPUT);

  digitalWrite(stepperPulse, LOW);
  digitalWrite(stepperDirection, LOW);
  digitalWrite(stepperEnable, HIGH);
  motor_actuator.setAcceleration(1500);

  // Data acquisition
  pinMode(start_EMG, OUTPUT);
  digitalWrite(start_EMG, LOW);
  pinMode(start_position, OUTPUT);
  digitalWrite(start_position, LOW);
  //=== Limit switch Interrupt ===
  /*pinMode(interruptPin1, INPUT_PULLUP);
  pinMode(interruptPin2, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(interruptPin1), limit_switch, RISING);
  attachInterrupt(digitalPinToInterrupt(interruptPin2), limit_switch, RISING);*/
  //=================================

  // Serial.println("INIT_1: Stepper motor setup complete");
  // Serial.println(" ");
}

// setup HX711 for load cell/force reading
void setup_load_cell() {
  LoadCell.begin();
  float calibrationValue;    // calibration value (see example file "Calibration.ino")
  calibrationValue = 98.35;  //94.83;//104.46;// for beam load cell (219.0 is the value for the s-type load cell at hand)
  unsigned long stabilizingtime = 2000;
  boolean _tare = true;
  LoadCell.start(stabilizingtime, _tare);

  while (LoadCell.getTareTimeoutFlag()) {
    // Serial.println("Timeout, check MCU>HX711 wiring and pin designations");
    // Serial.println("Retrying...");
    delay(200);
  }
  LoadCell.setCalFactor(calibrationValue);
  // Serial.println("INIT_2: Load cell setup complete");
  // Serial.println(" ");
}

// setup VL53L0X distance sensor
void setup_distance_sensor() {
  /*Wire.begin();
  distance_sensor.setTimeout(50);
  
  while (!distance_sensor.init()) {
    Serial.println("Failed to detect and initialize sensor!");
    Serial.println("Retrying...");
    delay(500);
  }
  Serial.println("distance sensor detected"); Serial.println(" ");
  delay(500);*/

  //Note: to get distance, use:
  // distance_sensor.readRangeSingleMillimeters();
  // distance_sensor.startContinuous();
  // distance_sensor.stopContinuous();
  // distance_sensor.readRangeContinuousMillimeters(); -->
  //sensor.setMeasurementTimingBudget(100000); --> change accuracy
  //Serial.println("INIT_3: distance sensor setup complete"); Serial.println(" ");
}

// FUNCTIONS I: Parsing commands
//------------------------------------------
// I.a. Active mode '2': Assistive control
void assistive_control(String command_data) {
  String acoef1 = getValue(command_data, ';', 2);
  String bcoef0 = getValue(command_data, ';', 3);
  String bcoef1 = getValue(command_data, ';', 4);
  String maxAng = getValue(command_data, ';', 5);
  String minAng = getValue(command_data, ';', 6);

  a_coef_1 = acoef1.toFloat();
  b_coef_0 = bcoef0.toFloat();
  b_coef_1 = bcoef1.toFloat();
  max_angle = maxAng.toFloat();
  min_angle = minAng.toFloat();
}

// I.b. Active mode '3' & '0': Isotonic training
void parse_active_isotonic(String command_data) {
  //3;0;0.99252802;0.124533;0.124533;110;20
  String acoef1 = getValue(command_data, ';', 2);
  String bcoef0 = getValue(command_data, ';', 3);
  String bcoef1 = getValue(command_data, ';', 4);
  String maxAng = getValue(command_data, ';', 5);
  String minAng = getValue(command_data, ';', 6);

  a_coef_1 = acoef1.toFloat();
  b_coef_0 = bcoef0.toFloat();
  b_coef_1 = bcoef1.toFloat();
  max_angle = maxAng.toFloat();
  min_angle = minAng.toFloat();
}

// I.c. Active mode '3' & '1': Isometric training
void parse_active_isometric(String command_data) {
  String acoef1 = getValue(command_data, ';', 2);
  String bcoef0 = getValue(command_data, ';', 3);
  String bcoef1 = getValue(command_data, ';', 4);
  String maxAng = getValue(command_data, ';', 5);
  String minAng = getValue(command_data, ';', 6);

  a_coef_1 = acoef1.toFloat();
  b_coef_0 = bcoef0.toFloat();
  b_coef_1 = bcoef1.toFloat();
  max_angle = maxAng.toFloat();
  min_angle = minAng.toFloat();
}

// FUNCTIONS II: Return to flexion position
//------------------------------------------
// II.a. at init, return knee angle to flexion (max_angle) position
// using proportional control.
void back_to_flexion() {
  if (measuredAngle != max_angle) {
    maxMotorSpeed = max_return_speed;
    motor_actuator.setMaxSpeed(maxMotorSpeed);
    pidGo = true;
    activeGo = false;
    while (pidGo) {
      // i. measure angle
      read_angle();

      // ii. set target angle
      targetAngle = max_angle;

      // iii. run motor
      motor_actuator.setSpeed(assignedSpeed);
      motor_actuator.runSpeed();

      // iv. print data
      print_data("back to flexion");
      stopping_criteria_angleCont();
    }
  }
}

// II.b. during training and at min_angle,
//       return knee angle to stepper home position (use homing)
void back_to_flexion_2() {
  if (measuredAngle <= min_angle) {
    maxMotorSpeed = max_return_speed;
    boolean home_pos = false;
    activeGo = false;
    zero_everything();
    while (!home_pos) {
      // i run motor
      motor_actuator.setMaxSpeed(maxMotorSpeed);
      motor_actuator.moveTo(0);
      motor_actuator.run();

      if (motor_actuator.currentPosition() == 0) {
        home_pos = true;
        activeGo = true;
      }
      // iii. print data
      print_data("back to flexion 2");
    }
  }
}

// FUNCTIONS III: Read sensors, store, and run motor
//------------------------------------------
// III.a move the motor to target position
void move_motor() {
  motor_actuator.setMaxSpeed(max_active_speed);
  motor_actuator.moveTo(-step_target_n);  // It's minus because our positive
  motor_actuator.run();                   // and the machine's positive is different.
}  // This is not some sort of a quick fix, it's just logic.

// III.b read force data
void read_force() {

  if (LoadCell.update()) newDataReady = true;

  // get smoothed value from the dataset:
  if (newDataReady) {
    if (millis() > t) {
      measuredForce = LoadCell.getData() / 1000 * 9.81;
      if (measuredForce < 0 || measuredForce < 0.2) {
        measuredForce = 0.00;
      }
      newDataReady = 0;
      t = millis();
    }
  }
}

// III.c re-tare force sensor
void tare_force_sensor() {
  if (Serial.available() > 0) {
    char inByte = Serial.read();
    if (inByte == 't') LoadCell.tare();
  }

  // check if last tare operation is complete:
  if (LoadCell.getTareStatus() == true) {
    // Serial.println("Tare complete");
  }
}

// III.d read current knee angle
void read_angle() {
  sensorValue = analogRead(angleSensorPin);
  measuredAngle = float(map(sensorValue, 0, 1023, 0, 333) - offsetAngle);
}

// III.e read current slider position
void read_slider_position() {
  //sliderDistance = zeroDistance - distance_sensor.readRangeContinuousMillimeters();
  sliderDistance = zeroDistance - distance_sensor.readRangeSingleMillimeters();
}

// III.f print current data to screen/send to high-level controller
// WARNING, printing at higher frequencies can degrade control performance
void print_data(String mode) {
  currentTime = millis();  // grab time
  if (currentTime - startTime >= period) {
    // Serial.print(mode);
    // Serial.print(" ");
    Serial.println(measuredAngle);
    // Serial.print(" ");
    //Serial.print(sliderDistance); Serial.print(" ");
    // Serial.print((float)step_target_n / 50);
    // Serial.print(" ");
    // Serial.print(measuredForce);
    // Serial.print(" ");
    // Serial.print(currentTime - start_program);
    // Serial.println(" ");
    startTime = currentTime;
  }
}

void print_data_once(String mode) {
  // Serial.print(mode);
  // Serial.print(" ");
  Serial.println(measuredAngle);
  // Serial.print(" ");
  // Serial.print(sliderDistance); Serial.print(" ");
  // Serial.print((float)step_target_n / 50);
  // Serial.print(" ");
  // Serial.print(measuredForce);
  // Serial.println(" ");
}

/*==== PID execution routine ====
 *===============================*/
ISR(TIMER1_COMPA_vect) {
  /* Interrupt service routine for
   *  PID execution
   */
  if (pidGo == true) {
    sensorValue = analogRead(angleSensorPin);
    measuredAngle = float(map(sensorValue, 0, 1023, 0, 333) - offsetAngle);
    assignedSpeed = int(pid_execute(targetAngle, measuredAngle, maxMotorSpeed));
    // count_pidGo++;
    //   if(count_pidGo>19){
    //     assignedSpeed = int(pid_execute(targetAngle, measuredAngle, maxMotorSpeed));
    //     count_pidGo = 0;
    //   }
  } else if (pidGo == false) {
    assignedSpeed = 0;
    u0 = 0;
    u1 = 0;
    u2 = 0;
    e0 = 0;
    e1 = 0;
    e2 = 0;
  }
  digitalWrite(LED_BUILTIN, led_state);
  led_state = !led_state;  // to check if the timer works

    if (activeGo == true && pidGo == false){
    step_target_n = haptic_rendering(measuredForce);
    digitalWrite(LED_BUILTIN, HIGH);
  }
  //==================================
}

void zero_everything() {
  e2 = 0, e1 = 0, e0 = 0;
  u2 = 0, u1 = 0, u0 = 0;
  assignedSpeed = 0;
  f_n = 0, f_n_1 = 0;
  y_n = 0, y_n_1 = 0;
  measuredForce = 0.0;
  step_target_n = 0;
}

// IV.c Resistance Algorithm (admittance rendering) 
float haptic_rendering(float measured_force){
  f_n = measured_force;
  y_n = a_coef_1*y_n_1 + b_coef_0*f_n + b_coef_1*f_n_1;
  long position_target = (long) y_n*50.0; // (1/8 rev/mm) * (400 steps/rev) 
  f_n_1 = f_n;
  y_n_1 = y_n;
  return position_target;
}

void init_pid(float Kp, float Ki, float Kd, float N, float Ts) {
  /* Initializing PID equation based on user defined parameters
   * 
   *  Args:
   *    Kp [float]: proportional gain  
   *    Ki [float]: integral gain
   *    Kd [float]: derivative gain
   *    N [float]: filter coefficient
   *    Ts [float]: sample time in seconds
   */

  a0 = (1 + N * Ts);
  a1 = -(2 + N * Ts);
  a2 = 1;

  b0 = Kp * (1 + N * Ts) + Ki * Ts * (1 + N * Ts) + Kd * N;
  b1 = -(Kp * (2 + N * Ts) + Ki * Ts + 2 * Kd * N);
  b2 = Kp + Kd * N;

  ku1 = a1 / a0;
  ku2 = a2 / a0;

  ke0 = b0 / a0;
  ke1 = b1 / a0;
  ke2 = b2 / a0;
}

float pid_execute(float target_angle, float plant_output, long speed_sat) {
  /* Executing PID control algorithm
   * 
   *  Args:
   *    target_angle [float]: reference angle [deg]
   *    plant_output [float]: measured angle [deg]
   *    speed_sat [float]: max/min speed of motor [pulse/s] (aka speed saturation)
   */

  //e2 = e1;
  e1 = e0;
  //u2 = u1;
  u1 = u0;

  r = target_angle;
  y = plant_output;

  float speed_sat_fl = float(speed_sat);
  e0 = (r - y);   // compute error
  u0 = ke0 * e0;  // + ke1*e1 + ke2*e2 - ku1*u1; - ku2*u2; //Kp*e0;//-ku1*u1 - ku2*u2 + ke0*e0 + ke1*e1 + ke2*e2;
  //u0 = (Kp+Ki*Ts)*e0 - Kp*e1 + u1;

  if (u0 >= speed_sat_fl) {
    u0 = speed_sat;
  }

  else if (u0 <= -speed_sat_fl) {
    u0 = -speed_sat;
  }
  return u0;
}
/*===============================
 *===============================*/

// FUNCTIONS V: loop stopping criteria
//------------------------------------------
// V.a stopping criteria for angle tracking (proportional control)
void stopping_criteria_angleCont(){
  if (Serial.available() > 0){
    stringCommand = Serial.readStringUntil('\n');
    if (stringCommand == "-s"){
      pidGo = false;
      activeGo = true;
    }
  }
  
  if (measuredAngle >= max_angle){ // when exceeding max_angle, disable proportional control
    pidGo = false;
    activeGo = true;
  }
}

// V.b stopping criteria for haptic rendering
void stopping_criteria_hap_ren(){
  if (Serial.available() > 0){
    stringCommand = Serial.readStringUntil('\n');
    if (stringCommand == "-s"){
      pidGo = false;
      activeGo = false;
    }
  }
  
  if (measuredAngle >= max_angle){ // when exceeding max_angle, disable proportional control 
    pidGo = false;
    activeGo = true;
  }
}

// External interrupt - limit switch
void limit_switch(){
  //Hardware safety @software level: forcefully stop the driver when 
  //the slider happens to reach the absolute endz of the rail
  digitalWrite(stepperEnable, LOW);

}

//======USEFULL CODES======//

String getValue(String command_data, char separator, int index) {
  /* This code is thanks to the people of stackOverflow <3!!
  * convinient for extracting command usage.
  */
  int found = 0;
  int strIndex[] = { 0, -1 };
  int maxIndex = command_data.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++) {
    if (command_data.charAt(i) == separator || i == maxIndex) {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }

  return found > index ? command_data.substring(strIndex[0], strIndex[1]) : "";
}

long speed_selector(String speed_percent) {
  /*
  * 800 P/s  = 120 RPM --> 10%
  * 933 P/s  = 140 RPM --> 20%
  * 1066 P/s = 160 RPM --> 30%
  * 1200 P/s = 180 RPM --> 40%
  * 1333 P/s = 200 RPM --> 50%
  * 1466 P/s = 220 RPM --> 60%
  * 1600 P/s = 240 RPM --> 70%
  * 1733 P/s = 260 RPM --> 80%
  * 1866 P/s = 280 RPM --> 90%
  * 2000 P/s = 300 RPM --> 100%
  *
  */
  long MaxSpeed;
  switch (speed_percent.toInt()) {

    case 10:
      MaxSpeed = 800;
      break;

    case 20:
      MaxSpeed = 933;
      break;

    case 30:
      MaxSpeed = 1066;
      break;

    case 40:
      MaxSpeed = 1200;
      break;

    case 50:
      MaxSpeed = 1333;
      break;

    case 60:
      MaxSpeed = 1466;
      break;

    case 70:
      MaxSpeed = 1600;
      break;

    case 80:
      MaxSpeed = 1733;
      break;

    case 90:
      MaxSpeed = 1866;
      break;

    case 100:
      MaxSpeed = 2000;
      break;

    default:
      MaxSpeed = 666;
      break;
  }  // end switch case

  return MaxSpeed;
}

/*int analogRead(int pin)
{
int total=0;
for(int n=0;n<32;n++)
  total= total + analogRead(pin);
return total/32;
}*/