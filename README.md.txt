NAMASTE to ICD-11 (TM2) Terminology Bridge
Enabling Seamless Dual-Coding for India's 2016 EHR Standards.

1. The Problem Statement

In India's healthcare landscape, the systems for traditional medicine (Ayush) and modern biomedical medicine operate in disconnected silos. Clinical data from Ayush practitioners is often recorded in non-standard text formats, making it impossible for modern EMR (Electronic Medical Record) systems to understand. This lack of interoperability breaks the continuity of patient care, creates inefficiencies for doctors, and prevents the Ministry of Ayush from gathering the real-time, high-quality data needed for national health management and research.

2. Our Solution

Our Terminology Bridge is a lightweight, FHIR R4-compliant microservice that acts as a universal translator between these two worlds. Our tool empowers clinicians to record a traditional Ayush diagnosis using the official NAMASTE terminology, and it instantly and automatically dual-codes the entry with the globally recognized WHO ICD-11 (TM2) standard.
We transform unstructured traditional diagnoses into standardized, auditable, and globally understood digital health records, ready for integration into India's National Digital Health Ecosystem.

3. Core Features

Smart Search: A simple search interface that provides auto-complete results from both the NAMASTE terminology and the live WHO ICD-11 API.
Automated Dual-Coding: Instantly translates a selected NAMASTE code to its corresponding ICD-11 TM2 code.
FHIR R4 Compliance: Generates a complete, compliant FHIR R4 Bundle containing a Patient and Condition resource (ProblemList Entry) with the dual-coded diagnosis.
Secure & Auditable: Features a secure submission endpoint that simulates ABHA token verification and creates a detailed audit log for each transaction, complying with India's 2016 EHR Standards.
Lightweight & Integrable: Built as a microservice, our tool is designed to be easily "plugged into" any existing hospital EMR or HIMS.

4. Tech Stack

Frontend: A clean, professional user interface built with standard HTML, CSS, and vanilla JavaScript.
Backend API: A high-performance REST API built with Python and the FastAPI framework.
Database: A HAPI FHIR Server running in a Docker container to store and manage terminology resources.
Standards: Our entire project is built on FHIR R4, NAMASTE, and ICD-11, the official standards mandated by the problem statement.

5. How to Run the Project

To run this project, you will need Docker Desktop and Python installed on your machine.

A. Startup Procedure

Please run these commands in the correct order.

1. Start the Database Server (Docker)

Open a terminal in the project's main root folder.
Run the command:
docker compose up -d


Wait about 45 seconds for the server to initialize.

2. Load the Terminology Data

Open a new terminal.
Navigate into the backend folder: cd backend
Run the data ingestion script:
python ingest.py


You must see two Success! messages.

3. Start the Backend API Server

In the same backend terminal, run:
uvicorn main:app --reload


The API will now be running at http://127.0.0.1:8000.

4. Launch the Frontend Website

In VS Code, right-click on the frontend/index.html file.
Select "Open with Live Server".
Your browser will open with the fully functional application.

B. Shutdown Procedure
1. Stop the API Server:
Go to the uvicorn terminal and press Ctrl + C.

2. Stop the Database Server:
Go to the main project folder terminal and run:
docker compose down


6. Future Roadmap

This prototype is a robust proof-of-concept. To move to a production-ready system, our next steps would be:
Implement Real ABHA Authentication: Replace the mock security token with a live integration with the ABDM Sandbox to validate real ABHA-linked OAuth 2.0 tokens.
Persistent Audit Logging: Store the audit logs in a dedicated, secure database instead of printing to the console.
EMR Integration: Package the application as a containerized microservice and develop a clear API for seamless integration into existing hospital EMR systems.
