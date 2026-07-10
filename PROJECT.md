# EngiBuddy Completed Phase Prompts

## Phase 0: Empathize

```text
I am in Phase 0 Empathize. My project is a Smart Classroom Comfort Monitor.

I completed stakeholder analysis. The main stakeholders are students, teachers, and school facilities staff. Students are affected because classroom comfort can change their focus and energy. Teachers are affected because discomfort can reduce attention and participation. Facilities staff are affected because they may need evidence before adjusting ventilation, heating, or lighting.

I completed user research. I interviewed two students and one teacher. Student 1 said the room often feels stuffy during long lessons and that it becomes harder to concentrate after about 30 minutes. Student 2 said lighting is sometimes too low during afternoon classes and makes reading harder. The teacher said students often complain that the room is hot or stuffy, but there is no simple data to show what is wrong.

I also observed one lesson. During the lesson, several students opened windows and complained about the air feeling heavy. No one knew whether the issue was temperature, humidity, air quality, or just perception.

The main user pain points are:
- students lose focus when classroom conditions are uncomfortable
- teachers only receive subjective complaints
- there is no quick shared signal showing the room condition
- any alert must be quiet and not interrupt the lesson

My research summary is that classroom comfort can affect attention, and simple environmental readings such as temperature, humidity, light level, and air quality can help identify possible causes of discomfort.

My problem scope is limited to detecting and communicating classroom comfort conditions. I am not trying to control HVAC, create a medical-grade sensor, or permanently install a system.

My How-Might-We question is: How might we help students and teachers quickly recognize classroom comfort problems without interrupting the lesson?

This is my completed Phase 0 evidence. Please check if this is enough to pass Phase 0 and move to Phase 1.
```

## Phase 1: Conceive

```text
I am in Phase 1 Conceive. My project is a Smart Classroom Comfort Monitor.

My problem statement is: Students and teachers need a simple way to notice uncomfortable classroom conditions because stuffy air, poor lighting, or temperature discomfort can reduce focus, but the current process relies only on subjective complaints.

My project scope is to create a prototype that measures or simulates temperature, humidity, light level, and air quality, then displays a simple comfort status and recommendation.

In scope:
- reading or simulating classroom environmental data
- showing temperature, humidity, light level, and air quality
- classifying the room as comfortable, warning, or uncomfortable
- giving simple recommendations such as ventilate, improve lighting, or room is comfortable
- testing the prototype with sample data and user feedback

Out of scope:
- automatic HVAC control
- permanent school installation
- medical-grade air quality measurement
- complex user accounts
- mobile app deployment

My success criteria are:
1. The prototype shows temperature, humidity, light level, and air quality.
2. The dashboard can be understood by a user in less than 10 seconds.
3. The system can log or process at least 30 minutes of readings.
4. The system gives at least three clear recommendations.
5. At least three users can correctly explain the dashboard status during testing.

I considered three solution options:
- Arduino display: low cost and good for hardware demonstration, but harder to show history and graphs.
- Python dashboard: easy to build and test with CSV data, good for charts and logging.
- Web dashboard: clear for presentation and easy for users to view, but may take more frontend work.

My chosen approach is a Python or web dashboard using CSV or sensor data. I chose this because it is feasible, easy to test, clear for presentation, and allows me to show reading history and recommendations.

My technology decisions are:
- use CSV data first so the prototype works even without hardware
- use simple comfort rules for classification
- use a dashboard to display values, status, and recommendation
- optionally connect real sensors later if time allows

My risk assessment is:
- Hardware may not be available, so I will support CSV data.
- Sensor readings may be inaccurate, so I will label the prototype as educational and not medical-grade.
- Users may not understand technical values, so I will use simple labels and recommendations.
- The project could become too large, so I will avoid HVAC control and mobile app features.

This is my completed Phase 1 evidence. Please check if this is enough to pass Phase 1 and move to Phase 2.
```

## Phase 2: Design

```text
I am in Phase 2 Design. My project is a Smart Classroom Comfort Monitor.

My system architecture is:
- Inputs: temperature in degrees Celsius, humidity percentage, light level, and air quality level.
- Processing: the system reads the data, applies comfort rules, classifies the room status, and chooses a recommendation.
- Outputs: the dashboard shows current readings, comfort status, recommendation, and reading history.
- Storage: readings are stored or loaded using a CSV file with timestamps.

My data format is:
timestamp, temperature_c, humidity_percent, light_level, air_quality

Example rows:
2026-06-26 09:00, 21, 45, medium, good
2026-06-26 09:05, 24, 52, medium, moderate
2026-06-26 09:10, 27, 68, low, poor

My comfort rules are:
- temperature below 18 C means too cold
- temperature from 18 C to 25 C means comfortable
- temperature above 25 C means too warm
- humidity below 30 percent or above 65 percent means uncomfortable
- low light means the room may need more light
- poor air quality means the room should be ventilated
- if all values are acceptable, the recommendation is that the room is comfortable

My Work Breakdown Structure is:
1. Research simple classroom comfort thresholds.
2. Create the CSV data format.
3. Build or prepare sample classroom readings.
4. Write comfort classification rules.
5. Build the dashboard or display.
6. Add recommendation text.
7. Add reading history.
8. Test the prototype against success criteria.
9. Collect user feedback.
10. Prepare report, presentation, handover, and reflection.

My timeline is:
- Day 1: complete user research and problem framing
- Day 2: choose solution and success criteria
- Day 3: finish architecture, rules, WBS, and test plan
- Day 4-5: build working prototype
- Day 6: test, collect feedback, and revise
- Day 7: prepare final delivery and presentation

My test plan outline is:
- Test that all four environmental values are displayed.
- Test normal, hot, cold, low-light, high-humidity, and poor-air-quality cases.
- Test that the system gives the correct recommendation for each case.
- Test that at least 30 minutes of readings can be logged or processed.
- Ask three users to interpret the dashboard and record whether they understand it in less than 10 seconds.
- Record bugs, revise the prototype, and retest.

This is my completed Phase 2 evidence. Please check if this is enough to pass Phase 2 and move to Phase 3.
```

## Phase 3: Implement

```text
I am in Phase 3 Implement. My project is a Smart Classroom Comfort Monitor.

I built the first working prototype. The prototype loads classroom comfort readings from a CSV file. Each row includes timestamp, temperature, humidity, light level, and air quality.

I implemented the comfort classification logic. The system checks whether temperature, humidity, light, and air quality are within acceptable ranges. It classifies the room as comfortable, warning, or uncomfortable.

I implemented recommendations:
- If air quality is poor, the system recommends ventilating the room.
- If temperature is above 25 C, the system recommends cooling or ventilating the room.
- If temperature is below 18 C, the system recommends warming the room.
- If humidity is outside the 30-65 percent range, the system warns that humidity may be uncomfortable.
- If light is low, the system recommends improving lighting.
- If all values are acceptable, the system says the room is comfortable.

I implemented a dashboard or display that shows:
- current temperature
- current humidity
- current light level
- current air quality
- overall comfort status
- recommendation
- recent reading history

I completed integration between the data file, classification logic, and dashboard output. The prototype can process sample readings and update the displayed status and recommendation.

I kept version notes. My implementation steps were:
1. Created sample CSV data.
2. Built the reading/import function.
3. Added comfort rules.
4. Added recommendation logic.
5. Built the dashboard output.
6. Tested different sample rows manually.
7. Fixed issues with missing values and unclear recommendation text.

I wrote technical documentation explaining:
- what the prototype does
- what input data format it expects
- how to run it
- how to read the output
- known limitations

Known limitations:
- The current version uses CSV data unless sensors are connected later.
- The comfort thresholds are simplified for a school prototype.
- The system suggests actions but does not control the classroom environment.

This is my completed Phase 3 evidence. Please check if this is enough to pass Phase 3 and move to Phase 4.
```

## Phase 4: Test/Revise

```text
I am in Phase 4 Test/Revise. My project is a Smart Classroom Comfort Monitor.

I tested the finished prototype against my success criteria.

Success criterion 1: The prototype shows temperature, humidity, light level, and air quality.
Result: Pass. The dashboard displays all four values from the CSV readings.
Evidence: Screenshot of dashboard with all values visible.

Success criterion 2: The dashboard can be understood in less than 10 seconds.
Result: Partial pass at first, then pass after revision. Three users tested the dashboard. Two understood it immediately, but one was confused by the phrase "moderate air quality." I changed the label to "ventilate soon" to make it clearer.
Evidence: User feedback notes and revised screenshot.

Success criterion 3: The system can log or process at least 30 minutes of readings.
Result: Pass. The prototype processed seven timestamped readings covering more than 30 minutes.
Evidence: CSV file and reading history output.

Success criterion 4: The system gives at least three clear recommendations.
Result: Pass. The prototype gives recommendations for ventilating, improving lighting, warming the room, cooling the room, and room comfortable.
Evidence: Screenshots of multiple test cases.

Success criterion 5: At least three users can correctly explain the dashboard status during testing.
Result: Pass after revision. After simplifying the labels, all three users correctly explained the room status and recommendation.
Evidence: User test notes.

Bugs found and fixed:
- Some recommendation text was too technical, so I simplified it.
- Low light and poor air quality warnings competed with each other, so I prioritized poor air quality first.
- One CSV row with a missing light value caused unclear output, so I added a fallback message.

Edge cases checked:
- hot room
- cold room
- low light
- poor air quality
- high humidity
- missing value in the CSV
- comfortable room

Revision summary:
I revised the dashboard labels, simplified recommendation text, added a fallback for missing values, and prioritized the most important warning when multiple problems appear.

This is my completed Phase 4 evidence. Please check if this is enough to pass Phase 4 and move to Phase 5.
```

## Phase 5: Operate

```text
I am in Phase 5 Operate. My project is a Smart Classroom Comfort Monitor.

I prepared the final delivery for the project.

My final demo plan is:
1. Explain the user problem: students and teachers need a quick way to notice uncomfortable classroom conditions.
2. Show the prototype dashboard.
3. Run a comfortable room example.
4. Run a poor air quality example and show the ventilation recommendation.
5. Run a low light example and show the lighting recommendation.
6. Show the reading history.
7. Explain the test results and user feedback.
8. Explain one revision: changing unclear labels into simpler recommendation text.
9. Explain future improvements.

My final report structure is:
1. Introduction and problem statement
2. User research and stakeholder analysis
3. Scope and success criteria
4. Solution options and chosen approach
5. System design and architecture
6. Implementation summary
7. Testing and results
8. Revisions based on feedback
9. Limitations
10. Future improvements
11. Conclusion

My presentation structure is:
- Slide 1: Project title and problem
- Slide 2: User evidence
- Slide 3: Success criteria
- Slide 4: Design and architecture
- Slide 5: Prototype demo
- Slide 6: Test results
- Slide 7: Revisions and lessons learned
- Slide 8: Future improvements

My handover document includes:
- project purpose
- required files
- CSV input format
- setup instructions
- run instructions
- explanation of comfort rules
- how to read dashboard output
- known limitations
- future improvement ideas

My retrospective is:
- What worked well: using CSV data made the prototype reliable and easy to test.
- What did not work well: some labels were too technical for users at first.
- What I changed: I simplified dashboard language and prioritized the most important warning.
- What I learned: user feedback is important because a technically correct dashboard can still be unclear.
- What I would do next: connect real sensors and collect longer-term classroom data.

My future improvement roadmap is:
- connect a real CO2 or air quality sensor
- add long-term trend charts
- store readings in a database
- improve visual design for classroom display
- compare comfort readings with student focus feedback

This is my completed Phase 5 evidence. Please check if this is enough for final submission.
```

## Final Review Prompt

```text
I want to review my full project evidence phase by phase. Please check what is complete, what is weak, and what I should fix before final submission.

Phase 0 Empathize:
I identified students, teachers, and facilities staff as stakeholders. I interviewed two students and one teacher. I observed one lesson. The main pain points are loss of focus, subjective complaints, no shared comfort signal, and the need for quiet non-disruptive alerts. My How-Might-We question is: How might we help students and teachers quickly recognize classroom comfort problems without interrupting the lesson?

Phase 1 Conceive:
My problem statement is that students and teachers need a simple way to notice uncomfortable classroom conditions because stuffy air, poor lighting, or temperature discomfort can reduce focus, but the current process relies only on subjective complaints. I defined scope, out-of-scope items, success criteria, solution options, chosen approach, technology decisions, and risks.

Phase 2 Design:
I created a system architecture with environmental inputs, comfort-rule processing, dashboard outputs, and CSV storage. I defined comfort rules, data format, WBS, timeline, dependencies, and test plan outline.

Phase 3 Implement:
I built a prototype that loads CSV readings, classifies classroom comfort, displays current values and recommendation, and shows reading history. I integrated the data file, classification rules, and dashboard output. I wrote technical documentation and version notes.

Phase 4 Test/Revise:
I tested the prototype against all success criteria. I confirmed the dashboard shows all values, processes more than 30 minutes of readings, gives multiple recommendations, and can be understood by three users after revision. I fixed unclear labels, recommendation priority, and missing-value handling.

Phase 5 Operate:
I prepared the final demo plan, report structure, presentation structure, handover document, retrospective, lessons learned, and future improvement roadmap.
```
