# Medical RAG Application

A FastAPI-based application for processing medical notes and extracting structured data using LLM and ICD API integration.

## Prerequisites

- Docker and Docker Compose installed on your system
- Python 3.11 or higher (for local development)
- Access to OpenAI API
- Access to WHO ICD API (Client ID and Secret)

## Environment Setup

1. Create a `.env` file in the project root with the following variables:
```bash
OPENAI_API_KEY=your_openai_api_key
ICD_CLIENT_ID=your_icd_client_id
ICD_CLIENT_SECRET=your_icd_client_secret
APP_ENV=production
LOG_LEVEL=INFO
```

## Docker Setup

### Building and Running with Docker Compose

1. Build the Docker image and start the services:
```bash
docker-compose up --build
```

2. To run in detached mode (background):
```bash
docker-compose up -d
```

3. To stop the services:
```bash
docker-compose down
```

### Manual Docker Build (Alternative)

If you prefer to build and run without Docker Compose:

1. Build the Docker image:
```bash
docker build -t medical-rag-app .
```

2. Run the container:
```bash
docker run -p 8000:8000 --env-file .env medical-rag-app
```

## API Endpoints

Once the service is running, the following endpoints will be available:

### Health and Documentation
- `GET /health`: Health check endpoint that returns `{"status": "ok"}` when the server is running
- `GET /docs`: Swagger UI documentation
- `GET /redoc`: ReDoc documentation
- `GET /`: Redirects to the API documentation

### Document Management
- `POST /documents/`: Create a new document
  - Request Body: `{"title": "string", "content": "string"}`
  - Response: Created document with ID and timestamps

- `GET /documents/`: List all documents with pagination
  - Query Parameters:
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Maximum number of records to return (default: 100)
  - Response: List of documents

- `GET /documents/{document_id}`: Get a specific document by ID
  - Path Parameter: `document_id` (integer)
  - Response: Document details or 404 if not found

### Medical Note Processing
- `POST /summarize_note/`: Summarize a medical note using LLM
  - Request Body: `{"title": "string", "content": "string"}`
  - Response: `{"summary": "string", "error": "string or null"}`

- `POST /extract_structured`: Extract structured data from a medical note
  - Request Body: `{"title": "string", "content": "string"}`
  - Response: Structured data including:
    - Patient information
    - Conditions (with ICD codes)
    - Medications
    - Procedures
    - Allergies
    - Vitals
    - Lab results

### Search and Question Answering
- `POST /search/`: Search for similar documents using semantic search
  - Request Body: `{"query": "string", "k": integer}`
  - Response: List of relevant documents with similarity scores

- `POST /answer_question/`: Answer questions using relevant documents and LLM
  - Request Body: `{"question": "string", "k": integer}`
  - Response: `{
    "answer": "string",
    "relevant_documents": [Document],
    "error": "string or null"
  }`

### Example Requests

#### Summarize a Medical Note
```bash
curl -X POST "http://localhost:8000/summarize_note/" \
     -H "Content-Type: application/json" \
     -d '{
           "title": "Patient Note",
           "content": "Patient presents with severe headache and fever..."
         }'
```

#### Extract Structured Data
```bash
curl -X POST "http://localhost:8000/extract_structured" \
     -H "Content-Type: application/json" \
     -d '{
           "title": "Patient Note",
           "content": "Patient presents with severe headache and fever..."
         }'
```

#### Search Documents
```bash
curl -X POST "http://localhost:8000/search/" \
     -H "Content-Type: application/json" \
     -d '{
           "query": "patient with headache",
           "k": 5
         }'
```

## Development

### Local Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application locally:
```bash
uvicorn app:app --reload
```

This project uses OpenAI's GPT model for medical note summarization. To set up the LLM integration:

1. Create a `.env` file in the project root directory
2. Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
