#!/bin/bash

# Demo Recording Creator Script
# This script helps you create sample recordings for demonstrating the system

echo "🎬 Meeting & Lecture Summarizer - Demo Recording Creator"
echo "======================================================="

# Create demo directory
mkdir -p demo_recordings
cd demo_recordings

echo ""
echo "📝 This script will help you create sample recordings for your demo."
echo "   You can either record live audio or use text-to-speech."
echo ""

# Function to create text-to-speech audio (macOS)
create_tts_recording() {
    local filename="$1"
    local text="$2"
    local voice="${3:-Alex}"
    
    echo "🔊 Creating TTS recording: $filename"
    
    # Use macOS say command to create audio file
    if command -v say >/dev/null 2>&1; then
        echo "$text" | say -v "$voice" -o "$filename.aiff"
        
        # Convert to MP3 if ffmpeg is available
        if command -v ffmpeg >/dev/null 2>&1; then
            ffmpeg -i "$filename.aiff" -y "$filename.mp3" 2>/dev/null
            rm "$filename.aiff"
            echo "✅ Created: $filename.mp3"
        else
            echo "✅ Created: $filename.aiff (install ffmpeg to convert to MP3)"
        fi
    else
        echo "❌ Text-to-speech not available. Please record manually or use another system."
        return 1
    fi
}

# Demo content scripts
BUSINESS_MEETING="Good morning everyone. Let's start today's quarterly planning meeting. Sarah, can you walk us through the marketing budget for Q4? We have three key initiatives to discuss: the digital advertising campaign, the trade show participation, and the new product launch event. Based on last quarter's performance, we saw a 25% increase in lead generation from our digital efforts. However, the trade shows provided higher quality leads with a 40% conversion rate. For the new product launch, we're looking at two options: a virtual event targeting 500 attendees, or a hybrid approach with both in-person and online components. The budget implications are significant. Digital campaign would cost 50,000 dollars, trade shows approximately 75,000, and the hybrid launch event around 100,000. We need to make a decision today so the marketing team can begin implementation next week. John, what are your thoughts on the technical requirements for the hybrid event?"

LECTURE_CONTENT="Welcome to today's lecture on machine learning fundamentals. We'll be covering three key concepts: neural networks, supervised learning, and deep learning applications. First, let's define machine learning. It's a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. Neural networks are computational models inspired by biological neural networks in the human brain. They consist of interconnected nodes called neurons, organized in layers. The input layer receives data, hidden layers process information, and the output layer produces results. Supervised learning is a type of machine learning where the algorithm learns from labeled training data. Examples include email spam detection, image classification, and medical diagnosis systems. The algorithm analyzes training examples and creates a function that maps inputs to desired outputs. Deep learning is a subset of machine learning that uses neural networks with multiple hidden layers. It has revolutionized fields like computer vision, natural language processing, and speech recognition. Applications include autonomous vehicles, language translation, and medical imaging analysis. Next week, we'll dive deeper into specific algorithms and practical implementations."

INTERVIEW_CONTENT="Thank you for joining us today for this software engineering position. Let's start with your background. Can you tell me about your experience with Python and machine learning? I've been working with Python for about five years, primarily in data science and web development. I've built several machine learning models using scikit-learn and TensorFlow, including recommendation systems and image classification projects. That's impressive. What's your approach to debugging complex systems? I usually start by reproducing the issue consistently, then use logging and debugging tools to trace the problem. I also believe in writing comprehensive tests to prevent similar issues in the future. Good methodology. How do you handle technical debt in legacy codebases? I prioritize based on impact and risk. I document technical debt items, advocate for dedicated refactoring time, and try to improve code quality incrementally during regular feature development. Excellent. Do you have any questions about our team or the role? Yes, I'm curious about the team's approach to code reviews and knowledge sharing. We have a collaborative culture with pair programming sessions and regular tech talks. Team members rotate as mentors for new projects, ensuring knowledge distribution across the team."

# Create sample recordings
echo "🎯 Choose what type of demo recordings to create:"
echo "1. Business meeting sample (3 minutes)"
echo "2. Educational lecture sample (3 minutes)" 
echo "3. Interview/discussion sample (2 minutes)"
echo "4. All three samples"
echo "5. Record your own audio"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo "Creating business meeting sample..."
        create_tts_recording "business_meeting_demo" "$BUSINESS_MEETING"
        ;;
    2)
        echo "Creating educational lecture sample..."
        create_tts_recording "lecture_demo" "$LECTURE_CONTENT"
        ;;
    3)
        echo "Creating interview sample..."
        create_tts_recording "interview_demo" "$INTERVIEW_CONTENT"
        ;;
    4)
        echo "Creating all three samples..."
        create_tts_recording "business_meeting_demo" "$BUSINESS_MEETING"
        create_tts_recording "lecture_demo" "$LECTURE_CONTENT"
        create_tts_recording "interview_demo" "$INTERVIEW_CONTENT"
        ;;
    5)
        echo "📱 To record your own audio:"
        echo "1. Open Voice Memos (iOS/macOS) or Voice Recorder (Windows/Android)"
        echo "2. Record 2-3 minutes of clear speech about any topic"
        echo "3. Save as MP3 or WAV format"
        echo "4. Copy to this directory: $(pwd)"
        echo ""
        echo "💡 Recording tips:"
        echo "- Speak clearly and at moderate pace"
        echo "- Include specific names, numbers, and decisions"
        echo "- Minimize background noise"
        echo "- Keep recordings under 5 minutes for demos"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "📁 Demo recordings location: $(pwd)"
ls -la *.mp3 *.wav *.aiff 2>/dev/null || echo "No audio files found."

echo ""
echo "🚀 Next steps for your demo:"
echo "1. Start the application: ./start-react.sh"
echo "2. Open http://localhost:3000"
echo "3. Upload one of your demo recordings"
echo "4. Show the real-time processing"
echo "5. Present the comprehensive results"

echo ""
echo "🎬 Demo tips:"
echo "- Use the shortest file for live demos (2-3 minutes)"
echo "- Have backup files in case of technical issues"
echo "- Practice your presentation timing"
echo "- Highlight the most impressive features for your audience"

echo ""
echo "✨ Ready to demonstrate the future of content analysis!"
