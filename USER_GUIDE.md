# User Guide: Meeting & Lecture Summarizer

Welcome! This guide will walk you through using the Meeting & Lecture Summarizer to transform your audio and video recordings into comprehensive summaries, articles, and study materials.

## 🚀 Quick Start (5 minutes)

### Step 1: Initial Setup

1. **Get your OpenAI API key** (required):
   - Go to [OpenAI API](https://platform.openai.com/api-keys)
   - Create an account and get your API key
   - You'll need this for AI transcription and content generation

2. **Set up environment**:
   ```bash
   # Copy the environment template
   cp .env.example .env
   
   # Edit the .env file and add your OpenAI API key
   nano .env  # or use any text editor
   ```

3. **Install dependencies**:
   ```bash
   # Install Python packages
   pip3 install -r requirements.txt
   
   # Install FFmpeg for media processing (macOS)
   brew install ffmpeg
   ```

### Step 2: Start the Application

Start the React web application:

```bash
# Start the Meeting Summarizer application
./start-react.sh
```

### Step 3: Access the Application

After running the startup script, open your browser:

- **React Web App**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

---

## 📱 Using the React Web App

### Main Interface Features

1. **File Upload Section**
   - Drag and drop or click to select files
   - Supports: MP3, WAV, MP4, AVI, MOV (max 100MB)
   - Real-time upload progress

2. **Processing Dashboard**
   - Live progress tracking
   - Step-by-step processing updates
   - Estimated completion time

3. **Results Viewer**
   - Tabbed interface for different content types
   - Download options for all generated content
   - Share functionality

### Step-by-Step Usage

#### 1. Upload Your Recording
```
🎯 Click "Browse files" or drag your recording into the upload area
📁 Select your meeting/lecture file (audio or video)
✅ Confirm file details and click "Start Processing"
```

#### 2. Monitor Processing
The system will show progress through these stages:
- 🎵 **Audio Extraction** (for video files)
- 🎤 **Transcription** (speech-to-text)
- 🧠 **AI Analysis** (summarization)
- 📝 **Content Generation** (articles & tests)
- 🔍 **Semantic Indexing** (for search)

#### 3. Review Results
Navigate through the tabs to access:

- **📋 Summary Tab**
  - Executive summary of main points
  - Key takeaways and decisions
  - Action items identified

- **📰 Article Tab**
  - Comprehensive follow-up article
  - Perfect for sharing with team members
  - Includes context and background

- **📜 Transcript Tab**
  - Full timestamped transcript
  - Searchable content
  - Speaker identification (when available)

- **❓ Comprehension Test Tab**
  - Multiple choice questions
  - True/false statements  
  - Short answer questions
  - Answer key included

- **🔍 Advanced Features Tab**
  - **Semantic Search Interface**
    - Natural language search across all recordings
    - Similar content discovery and recommendations
    - Search history and saved queries
    - Advanced filters (date, speaker, topic, relevance)
  
  - **Knowledge Graph Visualization**
    - Interactive network diagrams showing entity relationships
    - Timeline views of project and decision evolution
    - Speaker interaction maps and influence analysis
    - Topic clustering and concept hierarchies
  
  - **Web Research Integration**
    - Real-time fact-checking indicators and source citations
    - Contextual background information panels
    - Related news and industry updates
    - Enhanced content with hyperlinked references
  
  - **Cross-Recording Analytics**
    - Topic trend analysis across time periods
    - Speaker participation and contribution metrics
    - Decision tracking and follow-up identification
    - Content quality and engagement scoring

#### 4. Manage Your Library
- **View Past Recordings**: Browse your recording history
- **Search Content**: Find specific topics across all recordings
- **Export Data**: Download transcripts, summaries, or tests
- **Share Results**: Generate shareable links or PDFs

---

## 🌐 Using the React Web App

### Enhanced Features

The React interface provides additional capabilities:

#### Real-time Collaboration
- Live processing updates
- Multi-user support
- Shared workspaces

#### Advanced Analytics
- Recording statistics dashboard
- Topic trend analysis
- Speaker analysis (when available)
- Content quality metrics

#### Enhanced Search
- **Semantic Search Dashboard**
  - Natural language query interface powered by Weaviate
  - Real-time suggestions as you type
  - Visual similarity scores and relevance indicators
  - Cross-recording content discovery with relationship mapping

- **Knowledge Graph Explorer**
  - Interactive 3D network visualizations of content relationships
  - Entity timeline views showing how topics evolve over time
  - Speaker influence analysis and interaction patterns
  - Clickable nodes to explore connected concepts and recordings

- **Web-Enhanced Results**
  - Live fact-checking badges on search results
  - Contextual information panels with current web research
  - Source citation overlays with credibility scoring
  - Related news and industry updates integrated into search results

- **Advanced Analytics Dashboard**
  - Topic trend analysis with GraphRAG insights
  - Content quality metrics enhanced by web verification
  - Speaker engagement patterns and decision influence
  - Predictive insights about project outcomes and team dynamics

### Navigation Guide

1. **Dashboard Home**
   - Upload new recordings
   - View recent activity
   - Quick access to favorites

2. **Processing Queue**
   - Monitor multiple uploads
   - Batch processing status
   - Priority management

3. **Content Library**
   - Grid or list view of recordings
   - Advanced filtering options
   - Bulk operations

4. **Analytics Center**
   - Visual insights dashboard
   - Export analytics reports
   - Custom report generation

5. **Settings & Preferences**
   - Processing preferences
   - Quality settings
   - Integration configurations

---

## 📋 Common Use Cases

### For Students

#### Lecture Review
1. Upload lecture recording after class
2. Review AI-generated summary for quick overview
3. Use comprehension test for self-assessment
4. Search transcript for specific topics during study

#### Study Group Preparation
1. Process multiple lecture recordings
2. Generate comprehensive study guides
3. Create quiz questions for group sessions
4. Share summaries with classmates

### For Business Professionals

#### Meeting Follow-up
1. Upload meeting recording
2. Generate executive summary for stakeholders
3. Extract action items and decisions
4. Share article with absent team members

#### Training Documentation
1. Process training sessions
2. Create standardized documentation
3. Generate assessment materials
4. Build searchable knowledge base

### For Educators

#### Curriculum Development
1. Record and analyze sample lectures
2. Generate study materials automatically
3. Create assessment questions
4. Track content effectiveness

#### Student Support
1. Provide missed lecture summaries
2. Generate personalized study guides
3. Create accessibility-friendly transcripts
4. Monitor comprehension through tests

---

## 🔧 Troubleshooting

### Common Issues

#### "OpenAI API Error"
```bash
# Check your API key in .env file
cat .env | grep OPENAI_API_KEY

# Verify API key format (should start with sk-)
# Check OpenAI account credits and usage limits
```

#### "File Processing Failed"
```bash
# Check file format and size
ls -lh your_file.mp4

# Ensure FFmpeg is installed
ffmpeg -version

# Try with a smaller file first
```

#### "Weaviate Connection Error"
```bash
# Check if Docker is running
docker ps

# Restart Weaviate container
docker restart weaviate-summarizer

# Or disable Weaviate in .env
ENABLE_WEAVIATE=false

# Check Weaviate health
curl http://localhost:8080/v1/meta
```

#### "GraphRAG Processing Slow"
```bash
# Reduce graph complexity in .env
GRAPHRAG_MAX_ENTITIES=100
GRAPHRAG_MIN_CONFIDENCE=0.8

# Use smaller knowledge graphs for faster processing
ENABLE_REAL_TIME_GRAPHS=false

# Check system memory usage
htop  # Ensure sufficient RAM for graph processing
```

#### "Web Research Not Working"
```bash
# Check API keys in .env file
cat .env | grep NEWS_API_KEY
cat .env | grep WEB_RESEARCH_API_KEY

# Test web connectivity
curl -I https://newsapi.org/v2/everything?q=test

# Disable web research temporarily
ENABLE_WEB_RESEARCH=false

# Check rate limits
# News API: 1000 requests/day for free tier
# Consider upgrading for production use
```

#### "Search Results Not Relevant"
```bash
# Rebuild Weaviate indexes
curl -X DELETE http://localhost:8080/v1/schema/Recording

# Clear embedding cache
rm -rf ./cache/embeddings/*

# Adjust search parameters in settings:
SEARCH_SIMILARITY_THRESHOLD=0.7
SEARCH_MAX_RESULTS=20
ENABLE_HYBRID_SEARCH=true
```

#### "Port Already in Use"
```bash
# Find process using the port
lsof -i :8000  # for FastAPI
lsof -i :3000  # for React

# Kill the process and restart
kill <PID>
```

### Performance Tips

#### For Large Files
- Use compressed audio formats (MP3 vs WAV)
- Split very long recordings into segments
- Use "base" Whisper model for faster processing
- Ensure sufficient disk space (2x file size)

#### For Better Quality
- Use high-quality audio recordings
- Minimize background noise
- Use "large" Whisper model for accuracy
- Enable speaker identification for multi-person meetings

---

## 📊 Understanding Your Results

### Summary Quality Indicators
- **Coverage**: How much of the content is captured
- **Accuracy**: Factual correctness of key points
- **Relevance**: Focus on important topics
- **Clarity**: Readability and organization

### Test Question Types
- **Multiple Choice**: Test factual knowledge
- **True/False**: Verify understanding
- **Short Answer**: Assess comprehension depth
- **Essay Questions**: Evaluate critical thinking

### Transcript Features
- **Timestamps**: Navigate to specific moments
- **Speaker Labels**: Identify who said what
- **Confidence Scores**: Transcription accuracy
- **Topic Segments**: Automatic content organization

---

## 🔐 Privacy & Security

### Data Handling
- All files processed locally by default
- Transcripts stored in local database
- OpenAI API calls use your personal key
- No data sharing with third parties

### File Security
- Temporary files automatically deleted
- Database encryption available
- User access controls supported
- GDPR compliance features

---

## 📈 Advanced Features

Our system leverages three cutting-edge technologies to provide advanced content analysis and discovery capabilities:

### 🔍 Weaviate Vector Database - Semantic Search Engine

**What it does:** Weaviate transforms your recordings into searchable knowledge using vector embeddings, enabling you to find content by meaning rather than just keywords.

#### How Weaviate Works in Our System:
```python
# When you upload a recording, we:
1. Split transcript into meaningful chunks (sentences/paragraphs)
2. Generate vector embeddings for each chunk using sentence transformers
3. Store vectors in Weaviate with metadata (timestamp, speaker, topic)
4. Enable semantic search across all your content
```

#### Real-World Examples:
**Traditional Search vs. Weaviate:**
- **Keyword search:** "budget" → only finds exact word "budget"
- **Weaviate search:** "financial planning" → finds "budget allocation", "cost management", "resource distribution"

**Practical Use Cases:**
```
🔍 "Find discussions about team performance"
   → Returns segments about "productivity", "employee reviews", "goal achievement"

🔍 "What did we decide about the project timeline?"
   → Returns decisions about "deadlines", "milestones", "delivery dates"

🔍 "Show me content similar to this marketing strategy"
   → Finds related discussions across different meetings
```

#### Configuration in Your System:
```bash
# In your .env file:
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your_api_key_here

# Weaviate automatically:
- Indexes new recordings as they're processed
- Updates embeddings when content is modified
- Provides sub-second search responses
```

#### Benefits You'll Experience:
- **Cross-recording discovery:** Find related topics across months of meetings
- **Intelligent suggestions:** System recommends related content automatically
- **Context-aware search:** Understands synonyms, related concepts, and context
- **Multilingual support:** Search in one language, find content in another

---

### 🕸️ GraphRAG - Knowledge Graph Intelligence

**What it does:** GraphRAG (Graph Retrieval-Augmented Generation) builds knowledge graphs from your recordings, revealing hidden connections between people, topics, and decisions.

#### How GraphRAG Enhances Your Content:

**1. Entity Extraction & Relationship Mapping**
```python
# GraphRAG automatically identifies:
- People: "John mentioned the new project"
- Organizations: "Microsoft partnership discussion"
- Concepts: "Machine learning implementation"
- Relationships: "John manages the AI team"
```

**2. Knowledge Graph Construction**
```
    [John Smith] ──manages──→ [AI Team]
         │                      │
    mentioned                 working_on
         │                      │
         ▼                      ▼
    [New Project] ──uses──→ [Machine Learning]
```

**3. Graph-Enhanced Content Generation**
When creating summaries and articles, GraphRAG:
- Adds context about relationships between mentioned entities
- Identifies key decision makers and their roles
- Maps project dependencies and timelines
- Suggests related topics for deeper exploration

#### Real-World Applications:

**Meeting Analysis:**
- **Who's Connected:** "Show me everyone who worked on Project Alpha"
- **Decision Tracking:** "What decisions did Sarah make about the budget?"
- **Project Timelines:** "Map the evolution of our AI strategy"

**Knowledge Discovery:**
```
📊 Visual Knowledge Maps:
   - Topic clusters showing related concepts
   - Speaker interaction networks
   - Project dependency graphs
   - Decision flow diagrams
```

**Enhanced Search Results:**
Instead of just finding mentions, GraphRAG provides:
- **Context:** "John (CTO) mentioned AI budget (Project Alpha) in Q3 planning"
- **Relationships:** "This connects to previous discussions about team expansion"
- **Implications:** "Decision affects Marketing team timeline"

#### Integration Points:
```python
# GraphRAG enhances multiple features:
- Summary generation (adds relationship context)
- Article creation (includes background connections)
- Test questions (tests understanding of relationships)
- Search results (shows connected concepts)
```

---

### 🌐 nlweb - Real-Time Web Research Integration

**What it does:** nlweb enhances your content with real-time web research, fact-checking, and contextual information from current sources.

#### How nlweb Enriches Your Content:

**1. Automatic Fact-Checking**
```python
# When processing your recordings, nlweb:
- Identifies factual claims and statistics
- Searches current web sources for verification
- Flags outdated or contradictory information
- Provides source citations for claims
```

**2. Contextual Enhancement**
```python
# For each key topic mentioned, nlweb adds:
- Current news and developments
- Background information and definitions
- Related articles and resources
- Industry trends and analysis
```

**3. Citation and Source Integration**
```python
# Enhanced content includes:
- Hyperlinked citations to source materials
- Publication dates and credibility scores
- Related reading suggestions
- Real-time updates when information changes
```

#### Practical Examples:

**Before nlweb:**
> "We discussed the new AI regulations affecting our product."

**After nlweb enhancement:**
> "We discussed the new AI regulations affecting our product. **[Background: The EU AI Act, passed in 2024, establishes risk-based requirements for AI systems. Current status: Phase 2 implementation began September 2025.]** Related developments include similar legislation in [California](source-link) and [Singapore](source-link). **[Impact Analysis: Companies report 15% increase in compliance costs according to recent TechCrunch survey.]**"

**Enhanced Search with Web Context:**
```
🔍 Search: "AI compliance costs"
📊 Results include:
   - Your internal discussions about compliance
   - Current market data on implementation costs
   - Recent regulatory updates and changes
   - Industry best practices and case studies
```

#### Web Research Features:

**1. News Integration**
- Latest news articles related to your meeting topics
- Industry developments affecting discussed projects
- Competitive intelligence and market updates

**2. Background Context**
- Definitions and explanations of technical terms
- Historical context for mentioned events
- Related concepts and technologies

**3. Fact Verification**
- Cross-reference claims against multiple sources
- Identify potential misinformation or outdated data
- Provide confidence scores for factual assertions

**4. Trend Analysis**
- Market trends related to your business discussions
- Technology adoption patterns
- Industry benchmarks and comparisons

#### Configuration Options:
```bash
# In your .env file:
NEWS_API_KEY=your_news_api_key
ENABLE_WEB_RESEARCH=true
FACT_CHECK_THRESHOLD=0.7  # Confidence level for fact-checking
WEB_RESEARCH_SOURCES=news,academic,industry  # Source types
```

#### Privacy and Control:
- **Selective Enhancement:** Choose which recordings get web research
- **Source Filtering:** Control which types of sources are used
- **Local Processing:** Web data is processed locally, not stored externally
- **Citation Transparency:** All enhanced content shows sources clearly

---

### 🔗 How These Technologies Work Together

**Integrated Intelligence Pipeline:**
```
1. Recording Upload
   ↓
2. Whisper Transcription
   ↓
3. Weaviate Vector Indexing (semantic search capability)
   ↓
4. GraphRAG Entity & Relationship Extraction
   ↓
5. nlweb Contextual Enhancement & Fact-Checking
   ↓
6. GPT Content Generation (enhanced with all context)
   ↓
7. Comprehensive Results with Multi-layer Intelligence
```

**Synergistic Benefits:**
- **Weaviate + GraphRAG:** Semantic search enhanced with relationship understanding
- **GraphRAG + nlweb:** Knowledge graphs enriched with current web context
- **nlweb + Weaviate:** Web research results become searchable across recordings
- **All Three + GPT:** AI content generation informed by semantic understanding, relationship mapping, and real-time context

#### Example of Full Integration:
**Input:** Meeting about "expanding our AI team"

**Weaviate finds:** Related discussions about "machine learning hiring," "technical recruitment," "team growth"

**GraphRAG maps:** 
- John (CTO) → manages → AI Team
- AI Team → needs → Senior Engineers
- Expansion → affects → Budget Planning

**nlweb enhances with:**
- Current AI talent market statistics
- Salary benchmarks for AI engineers
- Recent news about AI hiring trends
- Competitor hiring announcements

**Final Result:** Comprehensive summary with semantic context, relationship understanding, and current market intelligence - far beyond what any single technology could provide.

---

## 🆘 Getting Help

### Documentation
- API Documentation: http://localhost:8000/docs
- GitHub Repository: [Link to your repo]
- User Manual: This guide

### Support Channels
- GitHub Issues for bug reports
- Discussions for feature requests
- Email support for technical help

### Community Resources
- Example recordings and use cases
- Best practices guide
- Integration tutorials
- User community forum

---

Ready to transform your recordings into comprehensive study and reference materials? Start by running `./start-react.sh` and upload your first file!
