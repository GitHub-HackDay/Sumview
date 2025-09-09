# Sumview - Meeting & Lecture Summarizer

A comprehensive system for processing video and audio recordings to generate follow-up posts, articles, summaries, and comprehension tests. Perfect for university lectures and business meetings.

## Features

- **Audio/Video Processing**: Supports multiple formats (MP3, WAV, MP4, AVI, MOV)
- **AI Transcription**: Uses OpenAI Whisper for accurate speech-to-text conversion
- **Smart Summarization**: Generates concise summaries and comprehensive articles
- **Comprehension Tests**: Automatically creates multiple-choice, true/false, and short-answer questions
- **Vector Search**: Semantic search across recordings using Weaviate
- **Knowledge Graphs**: Build and query knowledge graphs with GraphRAG
- **Web Research Integration**: Enhance content with real-time web research using nlweb
- **Related Content Discovery**: Find connections between different recordings
- **Advanced Analytics**: Insights across your entire recording collection
- **Web Interface**: Beautiful, modern web interface for easy file uploads and result viewing
- **Database Storage**: Saves all processed recordings for future reference

## Target Use Cases

- **University Lectures**: Help students who missed class catch up and study effectively
- **Business Meetings**: Provide comprehensive reviews for stakeholders who couldn't attend
- **Training Sessions**: Create study materials and assessments for ongoing education
- **Conference Presentations**: Generate shareable summaries and key takeaways

## Technology Stack

- **Backend**: FastAPI (Python)
- **AI/ML**: OpenAI Whisper, OpenAI GPT, Transformers
- **Vector Database**: Weaviate for semantic search and embeddings
- **Knowledge Graphs**: GraphRAG with NetworkX for relationship modeling
- **Web Research**: nlweb for real-time content enhancement
- **Database**: SQLAlchemy (SQLite by default)
- **Frontend**: React with Tailwind CSS
- **Media Processing**: MoviePy, PyDub, FFmpeg
- **NLP**: spaCy for advanced natural language processing

## Installation

1. **Clone and navigate to the project**:
   ```bash
   git clone https://github.com/GitHub-HackDay/Sumview.git
   cd Sumview
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Install FFmpeg** (required for audio/video processing):
   ```bash
   # macOS with Homebrew
   brew install ffmpeg
   
   # Or download from https://ffmpeg.org/
   ```

5. **Set up Weaviate (optional but recommended)**:
   ```bash
   # Using Docker
   docker run -d \
     --name weaviate \
     -p 8080:8080 \
     -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
     -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
     semitechnologies/weaviate:latest
   
   # Or use Weaviate Cloud Service (WCS) and update .env file
   ```

6. **Install spaCy model for NLP**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Configuration

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./summarizer.db
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your_weaviate_api_key_here
NEWS_API_KEY=your_news_api_key_here
WHISPER_MODEL_SIZE=base
ENABLE_WEAVIATE=true
ENABLE_GRAPHRAG=true
ENABLE_WEB_RESEARCH=true
```

## Usage

1. **Start the application**:
   ```bash
   python main.py
   ```

2. **Open your browser** and navigate to `http://localhost:8000`

3. **Upload a recording**:
   - Select an audio or video file (max 100MB)
   - Click "Process Recording"
   - Wait for the AI to transcribe and analyze the content

4. **Review the results**:
   - **Summary**: Quick overview of main points
   - **Article**: Comprehensive follow-up article
   - **Transcript**: Full timestamped transcript
   - **Test**: Comprehension questions for study/assessment

5. **Explore enhanced features**:
   - **Semantic Search**: Find content across all recordings
   - **Knowledge Graph**: Explore relationships between concepts
   - **Web Research**: Access enhanced content with real-time research
   - **Related Content**: Discover connections between recordings
   - **Analytics**: View insights across your recording collection

## API Endpoints

### Core Endpoints
- `GET /` - Main web interface
- `POST /upload` - Upload and process audio/video files
- `GET /recording/{id}` - Retrieve a specific recording
- `GET /recordings` - List all processed recordings

### Enhanced Search & Discovery
- `GET /search?q={query}&recording_id={id}&limit={n}` - Semantic search across recordings
- `GET /related/{recording_id}` - Find content related to a specific recording
- `GET /analytics` - Get insights and analytics across all recordings

### Knowledge Graph & Research
- `GET /knowledge-graph/{recording_id}` - Get knowledge graph for a recording
- `POST /query-graph` - Query knowledge graph with natural language
- `GET /enhance/{recording_id}` - Enhance recording with web research

## Development

To run in development mode with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## File Structure

```
Summarizer/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── app/
│   ├── models/            # Database models
│   │   ├── models.py      # SQLAlchemy models
│   │   └── database.py    # Database configuration
│   └── services/          # Business logic services
│       ├── transcription.py    # Audio/video transcription
│       ├── summarization.py    # AI content generation
│       └── test_generation.py  # Comprehension test creation
├── templates/
│   └── index.html         # Main web interface
└── static/
    ├── style.css          # Custom styles
    └── app.js             # Frontend JavaScript
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Requirements

- Python 3.8+
- OpenAI API key
- FFmpeg for media processing
- At least 2GB RAM for Whisper model processing

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure all requirements are installed with `pip install -r requirements.txt`
2. **FFmpeg not found**: Install FFmpeg and ensure it's in your system PATH
3. **OpenAI API errors**: Check that your API key is valid and has sufficient credits
4. **Large file processing**: For files over 25MB, processing may take several minutes

### Performance Tips

- Use smaller Whisper models (`tiny` or `base`) for faster processing
- Compress large video files before uploading
- Ensure sufficient disk space for temporary file processing
