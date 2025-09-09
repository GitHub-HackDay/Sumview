import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import { Search, Filter, FileText, Clock, User, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { apiHelpers as api } from '../utils/api';

const SearchPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('semantic');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState(null);

  const { data: recordings } = useQuery(
    'recordings',
    api.getRecordings,
    {
      refetchOnWindowFocus: false,
    }
  );

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      let results;
      if (searchType === 'semantic') {
        results = await api.semanticSearch(searchQuery);
      } else {
        // Basic text search through recordings
        results = recordings?.filter(recording => 
          recording.transcript?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          recording.summary?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          recording.title?.toLowerCase().includes(searchQuery.toLowerCase())
        ) || [];
      }
      setSearchResults(results);
    } catch (error) {
      console.error('Search failed:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatDuration = (duration) => {
    if (!duration) return 'Unknown';
    const minutes = Math.floor(duration / 60);
    const seconds = duration % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const highlightText = (text, query) => {
    if (!text || !query) return text;
    
    const regex = new RegExp(`(${query})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} className="bg-yellow-200 px-1 rounded">
          {part}
        </mark>
      ) : part
    );
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Search Recordings</h1>
        <p className="text-gray-600">Find content across all your recordings using semantic search</p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <input
                type="text"
                placeholder="Search for topics, concepts, or specific content..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              />
            </div>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <select
                value={searchType}
                onChange={(e) => setSearchType(e.target.value)}
                className="pl-10 pr-8 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
              >
                <option value="semantic">Semantic Search</option>
                <option value="text">Text Search</option>
              </select>
            </div>
            <button
              type="submit"
              disabled={isSearching || !searchQuery.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {isSearching ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Searching...
                </div>
              ) : (
                'Search'
              )}
            </button>
          </div>
          
          {searchType === 'semantic' && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start">
                <Sparkles className="h-5 w-5 text-blue-600 mr-2 mt-0.5" />
                <div>
                  <p className="text-sm text-blue-800 font-medium mb-1">Semantic Search Enabled</p>
                  <p className="text-sm text-blue-700">
                    Search by meaning and context, not just keywords. Find related concepts even if they use different words.
                  </p>
                </div>
              </div>
            </div>
          )}
        </form>
      </div>

      {/* Search Results */}
      {searchResults !== null && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              Search Results
              {searchResults.length > 0 && (
                <span className="text-gray-500 font-normal ml-2">
                  ({searchResults.length} {searchResults.length === 1 ? 'result' : 'results'})
                </span>
              )}
            </h2>
          </div>

          {searchResults.length === 0 ? (
            <div className="text-center py-12">
              <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
              <p className="text-gray-600">
                Try different keywords or search terms
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {searchResults.map((result, index) => (
                <motion.div
                  key={result.id || index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <Link
                        to={`/recording/${result.id}`}
                        className="text-lg font-semibold text-blue-600 hover:text-blue-700 transition-colors"
                      >
                        {result.title || `Recording ${result.id}`}
                      </Link>
                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                        <div className="flex items-center">
                          <Clock className="h-4 w-4 mr-1" />
                          <span>{formatDuration(result.duration)}</span>
                        </div>
                        <div className="flex items-center">
                          <User className="h-4 w-4 mr-1" />
                          <span>{formatDate(result.created_at)}</span>
                        </div>
                        {result.score && (
                          <div className="flex items-center">
                            <Sparkles className="h-4 w-4 mr-1" />
                            <span>Relevance: {Math.round(result.score * 100)}%</span>
                          </div>
                        )}
                      </div>
                    </div>
                    <FileText className="h-6 w-6 text-gray-400" />
                  </div>

                  {/* Search snippet */}
                  {(result.snippet || result.summary) && (
                    <div className="bg-gray-50 rounded-lg p-4 mb-4">
                      <p className="text-sm text-gray-700 leading-relaxed">
                        {searchType === 'text' 
                          ? highlightText(result.snippet || result.summary?.substring(0, 300) + '...', searchQuery)
                          : result.snippet || result.summary?.substring(0, 300) + '...'
                        }
                      </p>
                    </div>
                  )}

                  {/* Matched content preview */}
                  {result.matched_content && (
                    <div className="border-l-4 border-blue-200 pl-4 mb-4">
                      <p className="text-sm text-gray-600 font-medium mb-1">Matched Content:</p>
                      <p className="text-sm text-gray-700">
                        {searchType === 'text' 
                          ? highlightText(result.matched_content, searchQuery)
                          : result.matched_content
                        }
                      </p>
                    </div>
                  )}

                  <div className="flex items-center justify-between">
                    <div className="flex space-x-2">
                      {result.has_transcript && (
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                          Transcript
                        </span>
                      )}
                      {result.has_summary && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                          Summary
                        </span>
                      )}
                      {result.has_article && (
                        <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-medium rounded-full">
                          Article
                        </span>
                      )}
                    </div>
                    <Link
                      to={`/recording/${result.id}`}
                      className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                    >
                      View Details →
                    </Link>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Search Tips */}
      {searchResults === null && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Search Tips</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Semantic Search</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Search by concepts and meaning</li>
                <li>• Find related topics automatically</li>
                <li>• Works across different word choices</li>
                <li>• Example: "team collaboration" finds "working together"</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Text Search</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Search for exact words and phrases</li>
                <li>• Case-insensitive matching</li>
                <li>• Highlights matching text</li>
                <li>• Example: "budget" finds exactly "budget"</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchPage;
