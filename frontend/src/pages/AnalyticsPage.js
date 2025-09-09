import React from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  Clock, 
  FileText, 
  Users, 
  Calendar,
  Activity,
  PieChart
} from 'lucide-react';
import { apiHelpers as api } from '../utils/api';

const AnalyticsPage = () => {
  const { data: recordings, isLoading } = useQuery(
    'recordings',
    api.getRecordings,
    {
      refetchOnWindowFocus: false,
    }
  );

  // Calculate basic stats from recordings
  const stats = React.useMemo(() => {
    if (!recordings) return null;

    const totalRecordings = recordings.length;
    const completedRecordings = recordings.filter(r => r.status === 'completed').length;
    const totalDuration = recordings.reduce((acc, r) => acc + (r.duration || 0), 0);
    const avgDuration = totalRecordings > 0 ? totalDuration / totalRecordings : 0;

    // Group by month
    const monthlyData = recordings.reduce((acc, recording) => {
      const month = new Date(recording.created_at).toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short' 
      });
      acc[month] = (acc[month] || 0) + 1;
      return acc;
    }, {});

    // Recent activity (last 30 days)
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    const recentRecordings = recordings.filter(r => 
      new Date(r.created_at) >= thirtyDaysAgo
    ).length;

    return {
      totalRecordings,
      completedRecordings,
      totalDuration,
      avgDuration,
      monthlyData,
      recentRecordings,
      completionRate: totalRecordings > 0 ? (completedRecordings / totalRecordings) * 100 : 0
    };
  }, [recordings]);

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
        <p className="text-gray-600">Insights and statistics about your recordings</p>
      </div>

      {/* Key Metrics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Recordings</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalRecordings}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <Clock className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Duration</p>
                <p className="text-2xl font-bold text-gray-900">{formatDuration(stats.totalDuration)}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Completion Rate</p>
                <p className="text-2xl font-bold text-gray-900">{Math.round(stats.completionRate)}%</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Activity className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Recent Activity</p>
                <p className="text-2xl font-bold text-gray-900">{stats.recentRecordings}</p>
                <p className="text-xs text-gray-500">Last 30 days</p>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Activity Chart */}
        {stats?.monthlyData && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <BarChart3 className="h-5 w-5 mr-2" />
                Monthly Activity
              </h3>
            </div>
            
            <div className="space-y-4">
              {Object.entries(stats.monthlyData).map(([month, count]) => (
                <div key={month} className="flex items-center">
                  <div className="w-16 text-sm text-gray-600">{month}</div>
                  <div className="flex-1 mx-4">
                    <div className="bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                        style={{
                          width: `${(count / Math.max(...Object.values(stats.monthlyData))) * 100}%`
                        }}
                      ></div>
                    </div>
                  </div>
                  <div className="w-8 text-sm font-medium text-gray-900">{count}</div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Status Distribution */}
        {recordings && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <PieChart className="h-5 w-5 mr-2" />
                Status Distribution
              </h3>
            </div>
            
            <div className="space-y-4">
              {['completed', 'processing', 'failed'].map(status => {
                const count = recordings.filter(r => r.status === status).length;
                const percentage = recordings.length > 0 ? (count / recordings.length) * 100 : 0;
                
                return (
                  <div key={status} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className={`w-3 h-3 rounded-full mr-3 ${
                        status === 'completed' ? 'bg-green-500' :
                        status === 'processing' ? 'bg-yellow-500' : 'bg-red-500'
                      }`}></div>
                      <span className="text-sm text-gray-700 capitalize">{status}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-900">{count}</span>
                      <span className="text-sm text-gray-500">({Math.round(percentage)}%)</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}

        {/* Usage Insights */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Users className="h-5 w-5 mr-2" />
              Usage Insights
            </h3>
          </div>
          
          <div className="space-y-4">
            {stats && (
              <>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Average Recording Length</span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatDuration(stats.avgDuration)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Longest Recording</span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatDuration(Math.max(...recordings.map(r => r.duration || 0)))}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Most Active Day</span>
                  <span className="text-sm font-medium text-gray-900">
                    {recordings.length > 0 ? 
                      new Date(recordings[0].created_at).toLocaleDateString('en-US', { weekday: 'long' }) 
                      : 'N/A'
                    }
                  </span>
                </div>
              </>
            )}
          </div>
        </motion.div>

        {/* Recent Activity Timeline */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Calendar className="h-5 w-5 mr-2" />
              Recent Activity
            </h3>
          </div>
          
          <div className="space-y-4">
            {recordings?.slice(0, 5).map((recording, index) => (
              <div key={recording.id} className="flex items-center space-x-3">
                <div className={`w-2 h-2 rounded-full ${
                  recording.status === 'completed' ? 'bg-green-500' :
                  recording.status === 'processing' ? 'bg-yellow-500' : 'bg-red-500'
                }`}></div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {recording.title || `Recording ${recording.id}`}
                  </p>
                  <p className="text-sm text-gray-500">
                    {new Date(recording.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  recording.status === 'completed' ? 'bg-green-100 text-green-800' :
                  recording.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {recording.status}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
