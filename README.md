# 🚚 TransitIQ – AI Fleet Intelligence & Smart Vehicle Tracking Platform

TransitIQ is a modern AI-powered fleet management platform designed to provide real-time vehicle tracking, intelligent analytics, driver monitoring, and live operational insights. The platform combines interactive dashboards, live GPS visualization, WebSocket-based communication, and AI-driven fleet intelligence to help organizations efficiently monitor and manage their transportation systems.

✨ Features
📊 Interactive Analytics Dashboard
🚗 Real-time Fleet Tracking
🗺️ Live GPS Map Visualization
👨‍✈️ Driver Tracking & Monitoring
📈 Fleet Performance Analytics
⚡ Live Updates using WebSockets
🤖 AI-powered Fleet Intelligence
🚨 Safety Alerts & Notifications
🔍 Vehicle Search & Filtering
📱 Responsive Modern UI
🔐 Secure Authentication System
🌐 Production-ready Deployment

## Technologies

- **Spring Boot** — application framework
- **Netty Socket.IO** — real-time client communication
- **JUnit / Mockito** — tests
- **MongoDB** — persistence for vehicles and tracking data
- **Spring AOP** — cross-cutting concerns such as validation around service calls

## Prerequisites

- Java 17+
- Maven (or use the included `mvnw` wrapper)
- A MongoDB instance (local or hosted)

## Getting started

1. **Clone this repository** (after you create it on GitHub under your account):

   ```bash
   git clone https://github.com/theparamvrsingh/fleet-analytics-tracking-backend.git
   cd fleet-analytics-tracking-backend
   ```

2. **Configure MongoDB** — set `MONGODB_URI` in your environment, for example:

   ```bash
   export MONGODB_URI=mongodb://localhost:27017
   ```

   You can also define `MONGODB_URI` in `src/main/resources/application.properties` for local development (avoid committing secrets).

3. **Build**:

   ```bash
   ./mvnw clean install
   ```

4. **Run**:

   ```bash
   ./mvnw spring-boot:run
   ```

5. **Open** [http://localhost:8080](http://localhost:8080) in a browser (and ensure Socket.IO is configured for port `8082` if you use that client).

## Publishing to GitHub


1. On GitHub, create a new empty repository (for example `fleet-analytics-tracking-backend`).
2. From this project directory:

   ```bash
   git init
   git add .
   git commit -m "Initial commit: Fleet Analytics & Tracking Backend"
   git branch -M main
   git remote add origin https://github.com/theparamvrsingh/fleet-analytics-tracking-backend.git
   git push -u origin main
   ```

## License

This project is licensed under the [MIT License](LICENSE).
