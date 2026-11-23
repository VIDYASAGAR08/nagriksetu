# NagrikSetu — Teacher Viva & Evaluation Quick Defense Guide
## Step-by-Step Live Demonstration Script for SAD Evaluation Committee

Use this guide during your live evaluation with your professor. Each step maps directly to the **Evaluation Criteria SAD.pdf** rubric items.

---

### Quick Launch Command
To ensure all 8 services and databases are running before your teacher walks in:
```bash
docker compose up -d
```
Verify all 8 containers are healthy:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

---

### Viva Defense Script & Rubric Mapping

#### Rubric Items 1 to 6: Problem, Requirements, Cost & ATAM
* **What to tell your teacher:**
  > *"NagrikSetu solves the problem of fragmented government services where education, civic registration, and skill missions exist in separate siloes. Instead of an expensive proprietary monolith costing \$360K+/year in Oracle/SAP licensing, we engineered a federated polyglot microservice architecture using open-source tools (FastAPI, PostgreSQL, MySQL 8.4, SQLite, Docker, RabbitMQ), achieving a 94.9% TCO reduction."*
* **Architecture Tradeoff (ATAM):**
  > *"Under the CAP theorem, we chose Availability and Partition Tolerance (AP) by isolating each microservice's database. Temporary data synchronizations are handled asynchronously using RabbitMQ event queues and transactional Outbox patterns."*

---

#### Rubric Item 7: Front End & Multi-Modal Inputs (Camera, Sensor, Voice)
* **What to show in Browser:**
  1. Open **`http://localhost:5173/register`** (Central Citizen Portal).
  2. **Camera Input (Face ID):** Show Step 2 of registration where the webcam takes a live facial snapshot, encodes it into a 128-dimensional biometric embedding, and stores it for 1-click passwordless login.
  3. **Sensor Input (Touch ID / WebAuthn):** Show the hardware fingerprint / device passkey toggle.
  4. **Voice / WhatsApp Bot:** Open **`http://localhost:5173/whatsapp`** to show the interactive mobile WhatsApp Phone simulator that allows citizens to register and check family status without browsing the site.

---

#### Rubric Item 8: Database for Each Service & Logic Numbers
* **What to show in Terminal / TablePlus:**
  Open the 3 independent SQL dump files from the `database_dumps/` folder or run these commands:
  1. **Central Database (PostgreSQL 16 on Port 5432):**
     ```bash
     docker exec -it nagriksetu_postgres psql -U postgres -d civicadmin_db -c "SELECT id, user_code, email FROM users;"
     ```
     *Explain the Logic ID formula:* `2026101010` = Year 2026 + Service 10 (Central) + Entity 1 (User) + Serial 010.
  2. **Skill Development Database (MySQL 8.4 on Port 3308):**
     ```bash
     docker exec -it nagriksetu_skill_db mysql -u nagriksetu_skill -pskill-app-pass-2026 -e "USE skill_db; SELECT id, code, title FROM training_programs LIMIT 3;"
     ```
     *Show Logic IDs:* `2026302001`, `2026302002` (Service 30 = Skills).
  3. **School Database (SQLite in `School service/backend/data/nagriksetu.db`):**
     ```bash
     sqlite3 "School service/backend/data/nagriksetu.db" "SELECT student_id, student_name, school_id FROM students LIMIT 3;"
     ```
     *Show Domain Codes:* `SCH01125` (Asha Sharma), `SCH001`.

---

#### Rubric Item 9: Application Conditions, DB Updates & UML Diagrams
* **What to show:**
  - Show the 5 UML diagrams in [SAD_EVALUATION_CRITERIA_COMPREHENSIVE_REPORT.md](file:///Users/macbookpro/Documents/sad%201/SAD_EVALUATION_CRITERIA_COMPREHENSIVE_REPORT.md#L280-L460):
    1. System Architecture & DFD Diagram
    2. Use Case Diagram
    3. Sequence Diagram (SSO Verification Flow)
    4. Class / Domain Model Diagram
    5. State Machine Diagram (Application & Enrollment Lifecycle)
  - Explain that whenever a citizen or parent updates records, strict guard clauses enforce authentication, role checks, and two-step OTP verification before updating the database.

---

#### Rubric Item 10: AI Integration
* **What to show:**
  - **1:N Face Recognition Engine:** Go to `http://localhost:5173/login`. Show the *"1-Click Face ID Sign In"*. When looking into the camera, the system computes Euclidean vector distance ($d < 0.35$ threshold, $\ge 70\%$ match score) against all enrolled citizens in the database.
  - **Conversational AI Governance Assistant:** Click the chat bubble in the bottom right of the Central Portal to show AI-powered citizen inquiry answering.

---

#### Rubric Item 11: CI - Testing & GitHub Actions
* **What to show in Browser:**
  - Open: `https://github.com/VIDYASAGAR08/nagriksetu/actions`
  - Show the single, clean, 100% green **`NagrikSetu CI - Continuous Integration Pipeline`**.
  - Show all parallel jobs passing:
    1. `Frontend CI (Central Portal)` — Vite build & TypeScript check.
    2. `Frontend CI (School Service)` — Vite build & TypeScript check.
    3. `Frontend CI (Skill Development Service)` — Vite build & TypeScript check.
    4. `Central Backend CI (FastAPI & Pytest)` — 49 tests passing.
    5. `Skill Development Backend CI (MySQL 8.4)` — 10 tests passing with live MySQL container.
    6. `Docker Compose & Image Builds` — All 6 container images verified.
    7. `CI Pipeline Status Gate` — Required protection gate passed.

---

#### Rubric Item 12: Key API Microservices & Inter-Service Integration
* **What to show in Browser:**
  1. Open OpenAPI / Swagger Interactive Documentation:
     - Central API Docs: **`http://localhost:8000/docs`**
     - School API Docs: **`http://localhost:8001/docs`**
     - Skill API Docs: **`http://localhost:8003/docs`**
  2. Show Cross-Service Data Federation:
     - Visit `http://localhost:8000/api/v1/education/students/SCH01125` &rarr; Central Backend proxies the request to School Backend (Port 8001) in real-time.
  3. Show Event Broker:
     - Open RabbitMQ Web Console: **`http://localhost:15672`** (User: `nagriksetu`, Pass: `nagriksetu-mq-pass-2026`). Show the topic exchange `nagriksetu.events`.

---

#### Rubric Item 13: Containerization & Deployment
* **What to show:**
  - Show [docker-compose.yml](file:///Users/macbookpro/Documents/sad%201/docker-compose.yml): 8 microservices and databases communicating over the isolated bridge network `nagriksetu_network`.
  - Show Nginx Reverse Proxy routing in each frontend container, providing client buffering up to 25MB for biometric payloads.
