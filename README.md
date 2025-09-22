NAMASTE to ICD-11 (TM2) Terminology BridgeEnabling Seamless Dual-Coding for India's 2016 EHR Standards.A full-stack prototype developed for the Smart India Hackathon (SIH), designed to solve the critical challenge of integrating traditional Ayush medicine into India's modern digital health ecosystem.1. The ProblemTraditional Indian medicine (Ayurveda, Siddha, Unani) and modern biomedical systems are disconnected. Diagnoses made in Ayush (e.g.,"Vataja Jvara") are not machine-readable or understood by modern Electronic Medical Record (EMR) systems. This creates data silos, breaks the continuity of patient care, and prevents the Ministry of Ayush from gathering real-time, high-quality data for national health analytics.2. Our SolutionWe have built a lightweight, standards-compliant microservice that acts as a universal translator for health data. Our tool, the Terminology Bridge, provides a simple web interface for clinicians to:Search for a diagnosis using familiar Ayush terms.Automatically dual-code the diagnosis with both the official Indian NAMASTE code and the globally recognized WHO ICD-11 (TM2) code.Generate a compliant FHIR R4 Bundle, the national standard for health data exchange.Securely submit this record, creating an auditable transaction.This bridge turns unstructured traditional knowledge into standardized, interoperable data, ready for India's National Digital Health Ecosystem.3. Tech Stack & ArchitectureWe used a modern, efficient, and standards-compliant tech stack:Frontend: Lightweight HTML, CSS, & Vanilla JavaScript for easy integration into any EMR.Backend: A high-performance API built with Python & FastAPI.Database: A Dockerized HAPI FHIR Server for managing terminology according to global healthcare standards.External API: Live, secure integration with the official WHO ICD-11 API for real-time biomedical data.4. How to Run This ProjectFollow these steps to get the full application running on your local machine.PrerequisitesDocker Desktop: Make sure it is installed and running.Python 3.8+: Make sure Python and pip are installed.Git: For cloning the repository.VS Code with the Live Server extension is recommended.Step-by-Step Instructions1. Start the Backend Servers:First, we need to get the database and the API running.# 1.1. Start the Database (in the main project folder)
# This will start a HAPI FHIR server in the background.
docker compose up -d

# 1.2. Wait 30-45 seconds for the database to initialize.

# 1.3. Load the NAMASTE Data (in the backend folder)
cd backend
python ingest.py 
# You must see the two "Success!" messages.

# 1.4. Start the API Server (in the backend folder)
uvicorn main:app --reload
# The server will be running at [http://127.0.0.1:8000](http://127.0.0.1:8000)
2. Launch the Frontend:Now that the backend is running, you can start the user interface.# 2.1. Open the 'frontend' folder in VS Code.

# 2.2. Right-click on the 'index.html' file.

# 2.3. Select "Open with Live Server".
