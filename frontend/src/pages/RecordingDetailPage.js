import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Clock, 
  User, 
  FileText, 
  MessageSquare, 
  Download, 
  Share2,
  BookOpen,
  CheckCircle,
  Search as SearchIcon
} from 'lucide-react';
import { apiHelpers as api } from '../utils/api';

const RecordingDetailPage = () => {
  const { id } = useParams();

  const { data: recording, isLoading, error } = useQuery(
    ['recording', id],
    () => api.getRecording(id),
    {
      enabled: !!id,
      refetchOnWindowFocus: false,
    }
  );

  const formatDuration = (duration) => {
    if (!duration) return 'Unknown';
    const minutes = Math.floor(duration / 60);
    const seconds = duration % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const downloadContent = (content, filename) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !recording) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">
          <FileText className="h-12 w-12 mx-auto mb-2" />
          <p>Recording not found or failed to load</p>
        </div>
        <Link
          to="/recordings"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Recordings
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Link
          to="/recordings"
          className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Recordings
        </Link>
        
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {recording.title || `Recording ${recording.id}`}
            </h1>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <div className="flex items-center">
                <Clock className="h-4 w-4 mr-1" />
                <span>{formatDuration(recording.duration)}</span>
              </div>
              <div className="flex items-center">
                <User className="h-4 w-4 mr-1" />
                <span>{formatDate(recording.created_at)}</span>
              </div>
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                recording.status === 'completed' 
                  ? 'bg-green-100 text-green-800'
                  : recording.status === 'processing'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {recording.status}
              </span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2 mt-4 md:mt-0">
            <button
              onClick={() => downloadContent(
                recording.transcript || '', 
                `${recording.title || 'recording'}-transcript.txt`
              )}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Download className="h-4 w-4 mr-2" />
              Download
            </button>
            <button className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </button>
          </div>
        </div>
      </div>

      {/* Content Tabs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Transcript */}
          {recording.transcript && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-lg shadow-sm border border-gray-200"
            >
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                    <MessageSquare className="h-5 w-5 mr-2" />
                    Transcript
                  </h2>
                  <button
                    onClick={() => downloadContent(recording.transcript, `${recording.title || 'recording'}-transcript.txt`)}
                    className="text-sm text-blue-600 hover:text-blue-700"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <div className="p-6">
                <div className="prose max-w-none">
                  <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed">
                    {recording.transcript}
                  </pre>
                </div>
              </div>
            </motion.div>
          )}

          {/* Summary */}
          {recording.summary && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-lg shadow-sm border border-gray-200"
            >
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                    <FileText className="h-5 w-5 mr-2" />
                    Summary
                  </h2>
                  <button
                    onClick={() => downloadContent(recording.summary, `${recording.title || 'recording'}-summary.txt`)}
                    className="text-sm text-blue-600 hover:text-blue-700"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <div className="p-6">
                <div className="prose max-w-none">
                  <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {recording.summary}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Article */}
          {recording.article && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-lg shadow-sm border border-gray-200"
            >
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                    <BookOpen className="h-5 w-5 mr-2" />
                    Article
                  </h2>
                  <button
                    onClick={() => downloadContent(recording.article, `${recording.title || 'recording'}-article.txt`)}
                    className="text-sm text-blue-600 hover:text-blue-700"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <div className="p-6">
                <div className="prose max-w-none">
                  <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {recording.article}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <Link
                to={`/search?query=${encodeURIComponent(recording.title || '')}`}
                className="w-full flex items-center px-4 py-2 text-sm bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <SearchIcon className="h-4 w-4 mr-2" />
                Search Similar Content
              </Link>
              <button className="w-full flex items-center px-4 py-2 text-sm bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors">
                <CheckCircle className="h-4 w-4 mr-2" />
                Generate Test
              </button>
            </div>
          </div>

          {/* Recording Info */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recording Details</h3>
            <div className="space-y-3 text-sm">
              <div>
                <span className="font-medium text-gray-700">File Type:</span>
                <span className="ml-2 text-gray-600">{recording.file_type || 'Unknown'}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Duration:</span>
                <span className="ml-2 text-gray-600">{formatDuration(recording.duration)}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Created:</span>
                <span className="ml-2 text-gray-600">{formatDate(recording.created_at)}</span>
              </div>
              {recording.updated_at && (
                <div>
                  <span className="font-medium text-gray-700">Last Updated:</span>
                  <span className="ml-2 text-gray-600">{formatDate(recording.updated_at)}</span>
                </div>
              )}
            </div>
          </div>

          {/* Test Results */}
          {recording.test_questions && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Comprehension Test</h3>
              <p className="text-sm text-gray-600 mb-4">
                {JSON.parse(recording.test_questions).length} questions generated
              </p>
              <button className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                Take Test
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RecordingDetailPage;
