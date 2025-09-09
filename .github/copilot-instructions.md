<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Meeting & Lecture Summarizer - Copilot Instructions

This is a Python-based web application that processes audio and video recordings to generate comprehensive summaries, articles, and comprehension tests for educational and business use.

## Project Overview

The system takes video/audio recordings (lectures, meetings) and creates:
- AI-powered transcriptions using OpenAI Whisper
- Intelligent summaries of main points
- Comprehensive follow-up articles
- Automatically generated comprehension tests (multiple choice, true/false, short answer)
- Semantic search across recordings using Weaviate vector database
- Knowledge graphs with GraphRAG for relationship discovery
- Web research integration with nlweb for enhanced content

## Technology Stack

- **Backend**: FastAPI with Python 3.8+
- **AI/ML**: OpenAI Whisper for transcription, OpenAI GPT for content generation
- **Vector Database**: Weaviate for semantic search and embeddings
- **Knowledge Graphs**: GraphRAG with NetworkX for relationship modeling
- **Web Research**: nlweb for real-time content enhancement
- **Database**: SQLAlchemy with SQLite (configurable)
- **Media Processing**: MoviePy, PyDub, FFmpeg
- **Frontend**: React SPA with Tailwind CSS, React Query, Framer Motion
- **Deployment**: Uvicorn ASGI server

## Key Components

1. **Services** (`app/services/`):
   - `transcription.py`: Handles audio/video processing and speech-to-text
   - `summarization.py`: Generates summaries and articles using OpenAI GPT
   - `test_generation.py`: Creates comprehension tests with multiple question types
   - `weaviate_service.py`: Vector database operations for semantic search
   - `graphrag_service.py`: Knowledge graph generation and querying
   - `nlweb_service.py`: Web research and content enhancement

2. **Models** (`app/models/`):
   - `models.py`: SQLAlchemy database models for storing recordings and results
   - `database.py`: Database configuration and session management

3. **Frontend Options**:
   - **React App** (`frontend/`): Modern React SPA with component-based architecture

# Meeting & Lecture Summarizer - Copilot Instructions

This is a Python-based web application that processes audio and video recordings to generate comprehensive summaries, articles, and comprehension tests for educational and business use.

## Project Overview

The system takes video/audio recordings (lectures, meetings) and creates:
- AI-powered transcriptions using OpenAI Whisper
- Intelligent summaries of main points
- Comprehensive follow-up articles
- Automatically generated comprehension tests (multiple choice, true/false, short answer)

## Technology Stack

- **Backend**: FastAPI with Python 3.8+
- **AI/ML**: OpenAI Whisper for transcription, OpenAI GPT for content generation
- **Database**: SQLAlchemy with SQLite (configurable)
- **Media Processing**: MoviePy, PyDub, FFmpeg
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Deployment**: Uvicorn ASGI server

## Key Components

1. **Services** (`app/services/`):
   - `transcription.py`: Handles audio/video processing and speech-to-text
   - `summarization.py`: Generates summaries and articles using OpenAI GPT
   - `test_generation.py`: Creates comprehension tests with multiple question types

2. **Models** (`app/models/`):
   - `models.py`: SQLAlchemy database models for storing recordings and results
   - `database.py`: Database configuration and session management

3. **Web Interface**:
   - `templates/index.html`: Single-page application with file upload and results display
   - `static/`: CSS and JavaScript for modern, responsive UI

## Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use async/await for I/O operations
- Implement proper error handling and logging
- Add type hints for function parameters and return values

### API Design
- RESTful endpoints with clear naming
- Proper HTTP status codes
- Consistent JSON response format
- File upload validation and size limits

### AI Integration
- Use environment variables for API keys
- Implement retry logic for API calls
- Handle rate limiting and quota management
- Provide fallback options for AI service failures

### Security Considerations
- Validate file types and sizes
- Sanitize user inputs
- Use secure file handling for uploads
- Implement proper session management

### Performance Optimization
- Stream large file uploads
- Use background tasks for long-running processes
- Implement caching for frequently accessed data
- Optimize database queries

## Target Users

- **Students**: Access lecture summaries and study materials
- **Business Professionals**: Review meeting content and action items
- **Educators**: Create assessment materials from recorded content
- **Organizations**: Archive and search meeting/training content

## When generating code:

1. **Prioritize user experience**: Focus on clear, actionable outputs
2. **Handle edge cases**: Large files, poor audio quality, API failures
3. **Maintain consistency**: Follow established patterns in the codebase
4. **Consider scalability**: Design for multiple concurrent users
5. **Implement proper logging**: Help with debugging and monitoring

## Environment Setup

Ensure these environment variables are configured:
- `OPENAI_API_KEY`: Required for AI content generation
- `DATABASE_URL`: Database connection string
- `WHISPER_MODEL_SIZE`: Model size for transcription (tiny/base/small/medium/large)

## Testing Strategy

- Unit tests for individual services
- Integration tests for API endpoints
- End-to-end tests for complete workflows
- Performance tests for large file processing
