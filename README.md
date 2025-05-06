# Medical Workflow Automation

A FastAPI-based application for medical workflow automation.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## LLM Integration Setup

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

## Running the Application

Start the server using:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Database

The application uses SQLite as its database, which is automatically created in the project directory as `medical_workflow.db` when the application first starts.

### Endpoints

#### Health Check
- `GET /health`: Health check endpoint that returns `{"status": "ok"}` when the server is running

#### Documents
- `POST /documents/`: Create a new document
- `GET /documents/`: List all documents (with pagination)
- `GET /documents/{document_id}`: Get a specific document by ID

#### Documentation
- `GET /docs`: Swagger UI documentation
- `GET /redoc`: ReDoc documentation

### Using the Summarization Endpoint

To summarize a medical note, send a POST request to `/summarize_note/` with the following JSON body:

```json
{
    "title": "Patient Note",
    "content": "Your medical note text here..."
}
```

The response will be in the following format:

```json
{
    "summary": "Generated summary of the medical note...",
    "error": null
}
```

If there's an error during summarization, the response will include an error message:

```json
{
    "summary": "",
    "error": "Error message here..."
}
```