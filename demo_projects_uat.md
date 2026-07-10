# EngiBuddy UAT: 3 Student Demo Projects

This document contains 3 distinct engineering project scenarios designed for students to test the EngiBuddy platform. Each scenario contains a project description, target users, copy-pasteable chat messages, and mock validation files to test the **Push-Back mechanism** and **Review Mode**.

---

## Project 1: Smart Plant Watering System
**Focus:** IoT, Smart Home, Sensor Calibration

### 1. Project Overview
*   **Goal:** Build a device that automatically monitors soil moisture and waters household plants using a mini water pump to prevent drying or root rot.
*   **Target Users:** Houseplant owners who travel frequently or forget to water their plants.
*   **Key Components:** Arduino Uno, capacitive soil moisture sensor, 5V mini water pump, relay module.

### 2. Testing Steps for Students

#### **Step 1: Introduction (Guidance Mode)**
*   Start a new chat session at `http://localhost:3000/guidance` (Phase 0: Empathize).
*   **Message to write:** 
    > *"Hi! I want to build a smart plant watering system that automatically waters my house plants when the soil gets dry."*
*   **Expected Behavior:** The AI should not give you code or wiring diagrams. It should ask you who the plant owners are, or ask you about a time they forgot to water their plants.

#### **Step 2: Try to Skip Ahead (Test Push-Back)**
*   **Message to write:** 
    > *"I already wrote the Arduino C++ code for the soil moisture sensor and the water pump, let's deploy it now!"*
*   **Expected Behavior:** The AI must refuse to move on to code/implementation. It should remind you that you are in the Empathize phase and ask you to clarify user needs. The stepper at the top must remain locked on **Phase 0**.

#### **Step 3: Upload Evidence (Review Mode)**
*   Create a text file on your computer named `plant_research.txt` containing the following text:
    ```text
    Project: Smart Plant Watering System
    Target Users: Urban apartment dwellers who own houseplants and travel for work.
    Problem: Plants dry out or get overwatered (leading to root rot) due to irregular manual watering routines.
    Scope & Constraints: Budget under $25, battery-powered (must last 1 month), water reservoir capacity of 1 Liter.
    ```
*   Switch to **Review Mode** in EngiBuddy, upload `plant_research.txt`, and click **Re-run Review Validation**.
*   **Expected Behavior:** All Phase 0 checklist points should turn **Green (Complete)** with evidence snippets.

#### **Step 4: Advance Phase**
*   Switch back to **Guidance Mode** and write:
    > *"Now that we completed our stakeholder research and defined the constraints, let's brainstorm mounting configurations for the pump."*
*   **Expected Behavior:** The stepper at the top should successfully advance to **Phase 1: Conceive**.

---

## Project 2: Dual-Axis Solar Tracker
**Focus:** Green Energy, Automation, Mechanical Gears

### 1. Project Overview
*   **Goal:** Design a dual-axis solar tracker that automatically tilts a solar panel toward the brightest source of light to maximize solar energy generation.
*   **Target Users:** Off-grid cabin owners and remote research stations requiring stable green power.
*   **Key Components:** ESP32, 4 LDR light sensors, 2 servo motors (pitch and yaw), 3D-printed gears.

### 2. Testing Steps for Students

#### **Step 1: Introduction (Guidance Mode)**
*   Start a new chat session at `http://localhost:3000/guidance` (Phase 0: Empathize).
*   **Message to write:** 
    > *"I want to design a dual-axis solar tracker that follows the sun to maximize solar panel efficiency for off-grid cabins."*
*   **Expected Behavior:** The AI should ask Socratic questions regarding the off-grid cabin owners, their energy storage limits, or how they currently handle power generation.

#### **Step 2: Try to Skip Ahead (Test Push-Back)**
*   **Message to write:** 
    > *"I already bought the servos and LDRs. Let's write the code to calculate the difference between the left and right sensors."*
*   **Expected Behavior:** The AI should push back, pointing out that you are still in Phase 0 and need to establish stakeholder expectations first. The stepper must remain locked on **Phase 0**.

#### **Step 3: Upload Evidence (Review Mode)**
*   Create a text file named `solar_research.txt` containing the following text:
    ```text
    Project: Dual-Axis Solar Tracker
    Target Users: Remote cabin owners who rely on solar power for refrigeration and basic lighting.
    Problem: Fixed solar panels lose up to 40% efficiency during mornings and evenings when the sun's angle is low, causing power shortages.
    Constraints: Frame must support up to 5kg panels, operate in rain (IP64 enclosure), and budget under $80.
    ```
*   Switch to **Review Mode**, upload `solar_research.txt`, and click **Re-run Review Validation**.
*   **Expected Behavior:** Phase 0 checklist points will turn **Green (Complete)**.

#### **Step 4: Advance Phase**
*   Switch back to **Guidance Mode** and write:
    > *"We have completed the stakeholder research and defined the constraints for the cabin. Now, let's explore different options for the gear mechanism."*
*   **Expected Behavior:** The stepper should advance to **Phase 1: Conceive**.

---

## Project 3: Smart Pill Dispenser
**Focus:** Healthcare, Accessibility, Real-Time Clock (RTC)

### 1. Project Overview
*   **Goal:** Build a physical container with multiple pill compartments that alerts elderly patients to take their medication at scheduled times and dispenses them automatically.
*   **Target Users:** Elderly patients taking multiple daily medications or people with memory impairment.
*   **Key Components:** Arduino Uno, RTC (Real-Time Clock) module, servo motors (for compartment doors), buzzer, LED indicators.

### 2. Testing Steps for Students

#### **Step 1: Introduction (Guidance Mode)**
*   Start a new chat session at `http://localhost:3000/guidance` (Phase 0: Empathize).
*   **Message to write:** 
    > *"I want to build a smart pill dispenser that opens compartments and rings a buzzer to remind my grandfather to take his pills on time."*
*   **Expected Behavior:** The AI should ask who the user is (the grandfather or a caregiver), what difficulties they have handling pills, or how they currently remember their dosage.

#### **Step 2: Try to Skip Ahead (Test Push-Back)**
*   **Message to write:** 
    > *"Let's connect the DS3231 RTC module and code the servo triggers for 8:00 AM and 8:00 PM."*
*   **Expected Behavior:** The AI should guide you back to Phase 0, reminding you to focus on the elderly user's cognitive and physical constraints before writing code. The stepper must remain locked on **Phase 0**.

#### **Step 3: Upload Evidence (Review Mode)**
*   Create a text file named `dispenser_research.txt` containing the following text:
    ```text
    Project: Smart Pill Dispenser
    Target Users: Elderly patients (ages 70+) taking daily prescription medications.
    Problem: Patients miss doses or double-dose due to memory lapses, leading to health risks. Caregivers struggle to monitor adherence.
    Scope & Constraints: At least 3 separate pill slots, simple physical design for arthritic hands, audible buzzer + flashing LED indicators.
    ```
*   Switch to **Review Mode**, upload `dispenser_research.txt`, and click **Re-run Review Validation**.
*   **Expected Behavior:** Phase 0 checklist points will turn **Green (Complete)**.

#### **Step 4: Advance Phase**
*   Switch back to **Guidance Mode** and write:
    > *"Now that we completed our research on elderly users and defined dispenser constraints, let's write a problem statement and scope."*
*   **Expected Behavior:** The stepper should successfully advance to **Phase 1: Conceive**.
