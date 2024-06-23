# B4MAD Racing Website Project

This project is a Django-based web application for managing and analyzing racing telemetry data. It provides features for drivers, coaches, and racing enthusiasts to improve their performance and understand race data.

## Key Features:
- Telemetry data collection and analysis
- Real-time coaching and feedback during races
- Driver profiles and performance tracking
- Track guides and lap analysis
- Integration with various racing games and simulators

## Technology Stack:
- Backend: Django (Python)
- Frontend: HTML, CSS, JavaScript
- Database: PostgreSQL
- Real-time Communication: MQTT
- Data Storage and Querying: InfluxDB
- Containerization: Docker
- Deployment: Kubernetes

The application uses a microservices architecture with components for telemetry processing, coaching, and data visualization. It integrates with external racing simulators and provides a comprehensive platform for racing analysis and improvement.

## Copilot Feature

The copilot feature is a core component of the B4MAD Racing Website Project, providing real-time coaching and feedback to drivers during races. It's implemented through a series of interconnected classes that work together to process telemetry data, analyze driver performance, and deliver timely advice.

### Key Components and Their Interactions:

1. CoachCopilots: This is the main class that orchestrates the copilot feature. It initializes and manages multiple copilot applications for each driver.

2. Application: The base class for all copilot applications. It provides common functionality for processing telemetry data and generating responses.

3. Specific Applications:
   - BrakeApplication: Focuses on providing advice related to braking points and techniques.
   - TrackGuideApplication: Offers guidance based on pre-defined track notes and landmarks.
   - DebugApplication: Used for testing and debugging purposes.

4. History: Maintains a record of the driver's performance and telemetry data, which is used by the applications to provide context-aware advice.

5. Coach: Represents an individual coach instance for a driver. It manages the communication between the MQTT system and the copilot applications.

6. ActiveDrivers: Keeps track of all active driving sessions across the system.

7. Crew: The top-level class that initializes the entire copilot system, including MQTT connections and coach watchers.

8. CoachWatcher: Monitors for new driving sessions and initializes coach instances as needed.

9. Message: Represents individual coaching messages, with various subclasses for specific types of advice (e.g., MessageBrakePoint, MessageThrottle).

10. Segment: Represents a section of the track, containing relevant telemetry data and features used for analysis.

### Data Flow:

1. Telemetry data is received via MQTT and processed by the Crew class.
2. The ActiveDrivers class identifies the relevant driver and session.
3. The CoachWatcher initializes or updates the appropriate Coach instance.
4. The Coach passes the telemetry data to its CoachCopilots instance.
5. CoachCopilots distributes the data to various Application instances (e.g., BrakeApplication, TrackGuideApplication).
6. Each Application analyzes the data using the History and Segment information.
7. Applications generate Message instances with appropriate advice.
8. CoachCopilots collects and prioritizes these messages.
9. The Coach sends the prioritized messages back through MQTT to the driver's interface.

This system allows for modular expansion of coaching capabilities and ensures that drivers receive relevant, timely advice based on their current performance and track position.
