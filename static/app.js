// Main application JavaScript for Meeting & Lecture Summarizer

class SummarizerApp {
    constructor() {
        this.currentRecordingId = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Form submission
        document.getElementById('uploadForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFileUpload();
        });

        // File input change
        document.getElementById('fileInput').addEventListener('change', (e) => {
            this.validateFileSize(e.target.files[0]);
        });
    }

    validateFileSize(file) {
        const maxSize = 100 * 1024 * 1024; // 100MB
        if (file && file.size > maxSize) {
            alert('File size must be less than 100MB');
            document.getElementById('fileInput').value = '';
            return false;
        }
        return true;
    }

    async handleFileUpload() {
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];
        
        if (!file) {
            alert('Please select a file');
            return;
        }

        if (!this.validateFileSize(file)) {
            return;
        }

        // Show progress section
        this.showProgress();
        
        try {
            const formData = new FormData();
            formData.append('file', file);

            // Update progress
            this.updateProgress(20, 'Uploading file...');

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            this.updateProgress(60, 'Transcribing audio...');

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }

            this.updateProgress(80, 'Generating content...');

            const result = await response.json();
            
            this.updateProgress(100, 'Complete!');
            
            // Display results
            setTimeout(() => {
                this.displayResults(result);
                this.hideProgress();
            }, 1000);

        } catch (error) {
            console.error('Upload error:', error);
            alert('Failed to process file: ' + error.message);
            this.hideProgress();
        }
    }

    showProgress() {
        document.getElementById('progressSection').style.display = 'block';
        document.getElementById('progressSection').classList.add('fade-in');
        document.getElementById('submitBtn').disabled = true;
        document.getElementById('submitBtn').innerHTML = '<div class="spinner"></div>Processing...';
    }

    hideProgress() {
        document.getElementById('progressSection').style.display = 'none';
        document.getElementById('submitBtn').disabled = false;
        document.getElementById('submitBtn').innerHTML = '<i class="fas fa-magic me-2"></i>Process Recording';
    }

    updateProgress(percentage, text) {
        document.getElementById('progressBar').style.width = percentage + '%';
        document.getElementById('progressText').textContent = text;
    }

    displayResults(result) {
        this.currentRecordingId = result.id;
        
        // Show results section
        document.getElementById('resultsSection').style.display = 'block';
        document.getElementById('resultsSection').classList.add('slide-up');

        // Populate content
        this.displaySummary(result);
        this.displayArticle(result);
        this.displayTranscript(result);
        this.displayTest(result);

        // Scroll to results
        document.getElementById('resultsSection').scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }

    displaySummary(result) {
        const keyPoints = JSON.parse(result.key_points);
        const summaryHtml = `
            <div class="content-section">
                <h4><i class="fas fa-lightbulb me-2"></i>Executive Summary</h4>
                <p>${result.summary}</p>
                
                <div class="key-points">
                    <h5><i class="fas fa-star me-2"></i>Key Points</h5>
                    <ul>
                        ${keyPoints.map(point => `<li>${point}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
        document.getElementById('summaryContent').innerHTML = summaryHtml;
    }

    displayArticle(result) {
        const articleHtml = `
            <div class="content-section">
                <h4><i class="fas fa-newspaper me-2"></i>Comprehensive Review</h4>
                <div style="white-space: pre-line;">${result.article}</div>
            </div>
        `;
        document.getElementById('articleContent').innerHTML = articleHtml;
    }

    displayTranscript(result) {
        // Format transcript with timestamps
        const transcriptLines = result.transcript.split('\n');
        const formattedTranscript = transcriptLines.map(line => {
            if (line.includes('[') && line.includes(']')) {
                const timestampMatch = line.match(/\[(.*?)\]/);
                if (timestampMatch) {
                    const timestamp = timestampMatch[1];
                    const text = line.replace(/\[.*?\]\s*/, '');
                    return `<div><span class="timestamp">[${timestamp}]</span>${text}</div>`;
                }
            }
            return line ? `<div>${line}</div>` : '';
        }).join('');

        const transcriptHtml = `
            <div class="transcript-content">
                ${formattedTranscript}
            </div>
        `;
        document.getElementById('transcriptContent').innerHTML = transcriptHtml;
    }

    displayTest(result) {
        const testData = JSON.parse(result.test_questions);
        let testHtml = `
            <div class="content-section">
                <h4><i class="fas fa-question-circle me-2"></i>Comprehension Test</h4>
                <p class="text-muted">${testData.instructions}</p>
        `;

        // Multiple Choice Questions
        if (testData.multiple_choice && testData.multiple_choice.length > 0) {
            testHtml += '<h5 class="mt-4">Multiple Choice Questions</h5>';
            testData.multiple_choice.forEach((q, index) => {
                testHtml += `
                    <div class="test-question">
                        <div class="d-flex align-items-start">
                            <span class="question-number">${index + 1}</span>
                            <div class="flex-grow-1">
                                <p><strong>${q.question}</strong></p>
                                ${q.options.map(option => `<div class="mb-2">${option}</div>`).join('')}
                                <div class="correct-answer">
                                    <strong>Answer:</strong> ${q.correct_answer} - ${q.explanation}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
        }

        // True/False Questions
        if (testData.true_false && testData.true_false.length > 0) {
            testHtml += '<h5 class="mt-4">True/False Questions</h5>';
            testData.true_false.forEach((q, index) => {
                testHtml += `
                    <div class="test-question">
                        <div class="d-flex align-items-start">
                            <span class="question-number">${index + 1}</span>
                            <div class="flex-grow-1">
                                <p><strong>${q.statement}</strong></p>
                                <div class="correct-answer">
                                    <strong>Answer:</strong> ${q.correct_answer ? 'True' : 'False'} - ${q.explanation}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
        }

        // Short Answer Questions
        if (testData.short_answer && testData.short_answer.length > 0) {
            testHtml += '<h5 class="mt-4">Short Answer Questions</h5>';
            testData.short_answer.forEach((q, index) => {
                testHtml += `
                    <div class="test-question">
                        <div class="d-flex align-items-start">
                            <span class="question-number">${index + 1}</span>
                            <div class="flex-grow-1">
                                <p><strong>${q.question}</strong> (${q.points} points)</p>
                                <div class="correct-answer">
                                    <strong>Sample Answer:</strong> ${q.sample_answer}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
        }

        testHtml += '</div>';
        document.getElementById('testContent').innerHTML = testHtml;
    }

    async loadRecordings() {
        try {
            const response = await fetch('/recordings');
            const recordings = await response.json();
            
            this.displayRecordingsList(recordings);
            
            // Show recordings section
            document.getElementById('recordingsSection').style.display = 'block';
            document.getElementById('recordingsSection').scrollIntoView({ 
                behavior: 'smooth' 
            });
            
        } catch (error) {
            console.error('Failed to load recordings:', error);
            alert('Failed to load past recordings');
        }
    }

    displayRecordingsList(recordings) {
        if (recordings.length === 0) {
            document.getElementById('recordingsList').innerHTML = 
                '<p class="text-muted">No recordings found.</p>';
            return;
        }

        const listHtml = recordings.map(recording => `
            <div class="recording-item" onclick="app.loadRecording(${recording.id})">
                <div class="recording-title">${recording.filename}</div>
                <div class="recording-date">
                    ${new Date(recording.created_at).toLocaleDateString()} at 
                    ${new Date(recording.created_at).toLocaleTimeString()}
                </div>
                <div class="recording-preview">${recording.summary}</div>
            </div>
        `).join('');

        document.getElementById('recordingsList').innerHTML = listHtml;
    }

    async loadRecording(recordingId) {
        try {
            const response = await fetch(`/recording/${recordingId}`);
            const recording = await response.json();
            
            this.displayResults(recording);
            
        } catch (error) {
            console.error('Failed to load recording:', error);
            alert('Failed to load recording');
        }
    }
}

// Global functions
function loadRecordings() {
    app.loadRecordings();
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SummarizerApp();
});
