# 🚀 Quick Start Guide

## Super Fast Setup (2 minutes)

### Step 1: One-Command Setup
```bash
./setup.sh
```
This script will:
- ✅ Check your system requirements
- 📦 Install all dependencies
- 🔑 Help you configure API keys
- 🐳 Optionally start Weaviate database
- 🎯 Let you choose your interface

### Step 2: Get Your OpenAI API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign up/log in and create a new key
3. Copy the key (starts with `sk-`)

### Step 3: Start the Application

```bash
./start-react.sh
```
Then open: http://localhost:3000

## 📱 How to Use

### Upload Your First Recording
1. **Click "Browse files"** or drag & drop your audio/video
2. **Select your file** (MP3, WAV, MP4, AVI, MOV - max 100MB)
3. **Click "Start Processing"** and wait 2-5 minutes
4. **Review results** in the tabs:
   - 📋 **Summary**: Quick overview
   - 📰 **Article**: Detailed writeup  
   - 📜 **Transcript**: Full text with timestamps
   - ❓ **Test**: Study questions with answers

### What You Get
- ✨ **AI Summary** of main points and decisions
- 📄 **Follow-up Article** perfect for sharing with your team
- 📝 **Full Transcript** with timestamps for reference
- 🧠 **Comprehension Test** with multiple choice, true/false, and short answer questions
- 🔍 **Semantic Search** across all your recordings (advanced)

## 🎯 Perfect For

### Students
- **Missed a lecture?** Get a complete summary and study guide
- **Preparing for exams?** Use the auto-generated test questions
- **Group study?** Share the article with classmates

### Business Professionals  
- **Missed a meeting?** Get the executive summary and action items
- **Need to brief stakeholders?** Use the comprehensive article
- **Want accountability?** Review decisions and follow-ups

### Educators
- **Create study materials** automatically from recorded lectures
- **Generate assessment questions** for any topic
- **Provide accessibility support** with full transcripts

## 💡 Pro Tips

### For Best Results
- 🎤 **Use good audio quality** - clear speech, minimal background noise
- ⏱️ **Start with shorter files** (5-10 minutes) to test the system
- 🔊 **Speak clearly** if you're the presenter
- 📱 **Use a good microphone** if recording meetings

### File Recommendations
- **Audio**: MP3 or WAV files work best
- **Video**: MP4 files are fastest to process
- **Size**: Keep under 50MB for faster processing
- **Length**: 30-60 minutes is optimal for quality results

## 🆘 Need Help?

### Quick Fixes
- **"API Error"**: Check your OpenAI API key in the `.env` file
- **"Processing Failed"**: Try a smaller file or check audio quality
- **"Port in Use"**: Stop other applications or restart your computer

### Get Support
- 📖 **Full Documentation**: Read `USER_GUIDE.md`
- 🔗 **API Reference**: http://localhost:8000/docs (when running)
- 🐛 **Report Issues**: Create a GitHub issue

## 🎉 Ready to Go!

Try uploading a short recording (1-2 minutes) to see the magic happen. The AI will transcribe, summarize, and create study materials automatically!

**Your recordings stay private** - everything processes locally on your computer.
