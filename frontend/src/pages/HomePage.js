import React, { useState } from 'react';
import { Upload, File, Play, Clock, Brain, BookOpen, X, FileText, HelpCircle } from 'lucide-react';

const HomePage = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [showFullResults, setShowFullResults] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Validate file type
      const allowedTypes = [
        'audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/x-wav',
        'video/mp4', 'video/mpeg', 'video/quicktime', 'video/x-msvideo',
        'video/avi', 'application/octet-stream'
      ];
      
      const allowedExtensions = ['.mp3', '.wav', '.mp4', '.avi', '.mov', '.mpeg', '.mpg'];
      const fileExtension = selectedFile.name.toLowerCase().substring(selectedFile.name.lastIndexOf('.'));
      
      const isValidType = allowedTypes.includes(selectedFile.type) || allowedExtensions.includes(fileExtension);
      
      if (!isValidType) {
        alert('Please select a valid audio or video file (MP3, WAV, MP4, AVI, MOV, MPEG)');
        return;
      }
      
      // Validate file size (100MB)
      if (selectedFile.size > 100 * 1024 * 1024) {
        alert('File size must be less than 100MB');
        return;
      }
      
      setFile(selectedFile);
      setResults(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      console.log('Uploading file:', file.name, 'Type:', file.type, 'Size:', file.size);

      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        console.log('Upload successful:', data);
        setUploading(false);
        setProcessing(true);
        
        // Poll for results
        pollForResults(data.recording_id);
      } else {
        throw new Error(data.detail || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploading(false);
      alert(`Upload failed: ${error.message}. Please try again.`);
    }
  };

  const pollForResults = async (recordingId) => {
    try {
      const response = await fetch(`http://localhost:8000/recordings/${recordingId}`);
      const data = await response.json();
      
      if (data.status === 'completed') {
        setResults(data);
        setProcessing(false);
      } else if (data.status === 'processing') {
        setTimeout(() => pollForResults(recordingId), 3000);
      } else if (data.status === 'failed') {
        setProcessing(false);
        alert('Processing failed. Please try again.');
      }
    } catch (error) {
      console.error('Polling error:', error);
      setProcessing(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Meeting & Lecture Summarizer
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Transform your audio and video recordings into comprehensive summaries, articles, and study materials using AI
          </p>
        </div>

        {/* Features Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="bg-white rounded-lg p-6 shadow-md text-center">
            <Upload className="h-8 w-8 text-blue-500 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Upload Files</h3>
            <p className="text-sm text-gray-600">Support for audio & video formats</p>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-md text-center">
            <Brain className="h-8 w-8 text-green-500 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">AI Analysis</h3>
            <p className="text-sm text-gray-600">Intelligent summarization</p>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-md text-center">
            <BookOpen className="h-8 w-8 text-purple-500 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Study Materials</h3>
            <p className="text-sm text-gray-600">Articles & comprehension tests</p>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-md text-center">
            <Clock className="h-8 w-8 text-orange-500 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Quick Results</h3>
            <p className="text-sm text-gray-600">Process in minutes</p>
          </div>
        </div>

        {/* Upload Section */}
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="text-center mb-6">
              <Upload className="mx-auto h-16 w-16 text-blue-500 mb-4" />
              <h2 className="text-3xl font-semibold text-gray-900 mb-2">
                Upload Your Recording
              </h2>
              <p className="text-gray-600">
                Supports MP3, WAV, MP4, AVI, MOV, MPEG files up to 100MB
              </p>
            </div>
            
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
              <input
                type="file"
                accept="audio/*,video/*,.mp3,.wav,.mp4,.avi,.mov,.mpeg,.mpg"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
                disabled={uploading || processing}
              />
              <label
                htmlFor="file-upload"
                className={`cursor-pointer inline-flex items-center px-8 py-4 rounded-lg font-medium transition-colors ${
                  uploading || processing
                    ? 'bg-gray-400 text-gray-700 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                <File className="mr-3 h-6 w-6" />
                {uploading ? 'Uploading...' : processing ? 'Processing...' : 'Choose File'}
              </label>
              
              {file && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-center space-x-4">
                    <div className="text-left">
                      <p className="font-medium text-gray-900">{file.name}</p>
                      <p className="text-sm text-gray-600">{formatFileSize(file.size)}</p>
                    </div>
                  </div>
                  
                  {!uploading && !processing && (
                    <button
                      onClick={handleUpload}
                      className="mt-4 inline-flex items-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
                    >
                      <Play className="mr-2 h-5 w-5" />
                      Start Processing
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Progress Indicators */}
            {(uploading || processing) && (
              <div className="mt-6">
                <div className="flex items-center justify-center space-x-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="text-gray-700 font-medium">
                    {uploading ? 'Uploading file...' : 'Processing recording...'}
                  </span>
                </div>
                <div className="mt-4 bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '45%' }}></div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Results Section */}
        {results && (
          <div className="max-w-4xl mx-auto mt-12">
            <div className="bg-white rounded-xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Processing Results</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {results.summary && (
                  <div className="bg-blue-50 rounded-lg p-6">
                    <h3 className="font-semibold text-blue-900 mb-3">Summary</h3>
                    <p className="text-blue-800 text-sm leading-relaxed">
                      {results.summary.substring(0, 150)}...
                    </p>
                  </div>
                )}
                
                {results.article && (
                  <div className="bg-green-50 rounded-lg p-6">
                    <h3 className="font-semibold text-green-900 mb-3">Article</h3>
                    <p className="text-green-800 text-sm leading-relaxed">
                      {results.article.substring(0, 150)}...
                    </p>
                  </div>
                )}
                
                {results.test_questions && (
                  <div className="bg-purple-50 rounded-lg p-6">
                    <h3 className="font-semibold text-purple-900 mb-3">Quiz</h3>
                    <p className="text-purple-800 text-sm">
                      {results.test_questions.length} questions generated
                    </p>
                  </div>
                )}
              </div>
              
              <div className="mt-6 text-center">
                <button
                  onClick={() => setShowFullResults(true)}
                  className="inline-flex items-center px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
                >
                  View Full Results
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Full Results Modal */}
        {showFullResults && results && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900">Full Results: {results.filename}</h2>
                <button
                  onClick={() => setShowFullResults(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="h-6 w-6 text-gray-500" />
                </button>
              </div>
              
              <div className="p-6 space-y-8">
                {/* Transcript Section */}
                {results.transcript && (
                  <div className="bg-gray-50 rounded-lg p-6">
                    <div className="flex items-center mb-4">
                      <FileText className="h-6 w-6 text-gray-600 mr-2" />
                      <h3 className="text-xl font-semibold text-gray-900">Transcript</h3>
                    </div>
                    <div className="text-gray-700 leading-relaxed max-h-60 overflow-y-auto">
                      {results.transcript}
                    </div>
                  </div>
                )}

                {/* Summary Section */}
                {results.summary && (
                  <div className="bg-blue-50 rounded-lg p-6">
                    <div className="flex items-center mb-4">
                      <BookOpen className="h-6 w-6 text-blue-600 mr-2" />
                      <h3 className="text-xl font-semibold text-blue-900">Summary</h3>
                    </div>
                    <div className="text-blue-800 leading-relaxed">
                      {results.summary}
                    </div>
                  </div>
                )}

                {/* Article Section */}
                {results.article && (
                  <div className="bg-green-50 rounded-lg p-6">
                    <div className="flex items-center mb-4">
                      <FileText className="h-6 w-6 text-green-600 mr-2" />
                      <h3 className="text-xl font-semibold text-green-900">Article</h3>
                    </div>
                    <div className="text-green-800 leading-relaxed whitespace-pre-line">
                      {results.article}
                    </div>
                  </div>
                )}

                {/* Quiz Section */}
                {results.test_questions && results.test_questions.length > 0 && (
                  <div className="bg-purple-50 rounded-lg p-6">
                    <div className="flex items-center mb-4">
                      <HelpCircle className="h-6 w-6 text-purple-600 mr-2" />
                      <h3 className="text-xl font-semibold text-purple-900">Quiz Questions</h3>
                    </div>
                    <div className="space-y-4">
                      {results.test_questions.map((question, index) => (
                        <div key={index} className="bg-white rounded-lg p-4 border border-purple-200">
                          <p className="font-medium text-purple-900 mb-3">
                            {index + 1}. {question.question}
                          </p>
                          
                          {question.type === 'multiple_choice' && question.options && (
                            <div className="space-y-2">
                              {question.options.map((option, optionIndex) => (
                                <div 
                                  key={optionIndex} 
                                  className={`p-2 rounded border ${
                                    option === question.correct_answer 
                                      ? 'bg-green-100 border-green-300 text-green-800' 
                                      : 'bg-gray-50 border-gray-200 text-gray-700'
                                  }`}
                                >
                                  {String.fromCharCode(65 + optionIndex)}. {option}
                                  {option === question.correct_answer && (
                                    <span className="ml-2 text-green-600 font-medium">✓ Correct</span>
                                  )}
                                </div>
                              ))}
                            </div>
                          )}
                          
                          {question.type === 'true_false' && (
                            <div className="space-y-2">
                              <div className={`p-2 rounded border ${
                                question.correct_answer === 'true' 
                                  ? 'bg-green-100 border-green-300 text-green-800' 
                                  : 'bg-gray-50 border-gray-200 text-gray-700'
                              }`}>
                                True {question.correct_answer === 'true' && <span className="ml-2 text-green-600 font-medium">✓ Correct</span>}
                              </div>
                              <div className={`p-2 rounded border ${
                                question.correct_answer === 'false' 
                                  ? 'bg-green-100 border-green-300 text-green-800' 
                                  : 'bg-gray-50 border-gray-200 text-gray-700'
                              }`}>
                                False {question.correct_answer === 'false' && <span className="ml-2 text-green-600 font-medium">✓ Correct</span>}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Quick Start Guide */}
        <div className="max-w-3xl mx-auto mt-16">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">How It Works</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="bg-blue-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                  <span className="text-2xl font-bold text-blue-600">1</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Upload</h3>
                <p className="text-gray-600 text-sm">Upload your audio or video recording</p>
              </div>
              
              <div className="text-center">
                <div className="bg-green-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                  <span className="text-2xl font-bold text-green-600">2</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Process</h3>
                <p className="text-gray-600 text-sm">AI analyzes and transcribes content</p>
              </div>
              
              <div className="text-center">
                <div className="bg-purple-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                  <span className="text-2xl font-bold text-purple-600">3</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Study</h3>
                <p className="text-gray-600 text-sm">Get summaries, articles, and tests</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
