import { useState, useEffect, useCallback, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { recordingAPI, searchAPI, analyticsAPI } from '../utils/api';
import { parseErrorMessage } from '../utils/helpers';
import toast from 'react-hot-toast';

// Custom hook for file upload with progress tracking
export const useFileUpload = () => {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const queryClient = useQueryClient();

  const uploadMutation = useMutation(
    ({ file }) => recordingAPI.upload(file, setUploadProgress),
    {
      onMutate: () => {
        setIsUploading(true);
        setUploadProgress(0);
      },
      onSuccess: (data) => {
        setIsUploading(false);
        setUploadProgress(100);
        queryClient.invalidateQueries('recordings');
        toast.success('File uploaded successfully!');
        return data;
      },
      onError: (error) => {
        setIsUploading(false);
        setUploadProgress(0);
        toast.error(parseErrorMessage(error));
      },
    }
  );

  const uploadFile = useCallback((file) => {
    return uploadMutation.mutateAsync({ file });
  }, [uploadMutation]);

  return {
    uploadFile,
    uploadProgress,
    isUploading,
    error: uploadMutation.error,
    reset: () => {
      setUploadProgress(0);
      setIsUploading(false);
      uploadMutation.reset();
    },
  };
};

// Custom hook for managing recordings
export const useRecordings = (params = {}) => {
  return useQuery(
    ['recordings', params],
    () => recordingAPI.getAll(params),
    {
      keepPreviousData: true,
      staleTime: 5 * 60 * 1000, // 5 minutes
      onError: (error) => {
        toast.error(parseErrorMessage(error));
      },
    }
  );
};

// Custom hook for a single recording
export const useRecording = (id) => {
  return useQuery(
    ['recording', id],
    () => recordingAPI.getById(id),
    {
      enabled: !!id,
      staleTime: 5 * 60 * 1000,
      onError: (error) => {
        toast.error(parseErrorMessage(error));
      },
    }
  );
};

// Custom hook for recording processing status
export const useRecordingStatus = (id, interval = 2000) => {
  const [isPolling, setIsPolling] = useState(false);
  
  const query = useQuery(
    ['recording-status', id],
    () => recordingAPI.getStatus(id),
    {
      enabled: !!id && isPolling,
      refetchInterval: interval,
      refetchIntervalInBackground: true,
      onSuccess: (data) => {
        // Stop polling when processing is complete
        if (data?.status === 'completed' || data?.status === 'failed') {
          setIsPolling(false);
        }
      },
      onError: (error) => {
        setIsPolling(false);
        toast.error(parseErrorMessage(error));
      },
    }
  );

  const startPolling = useCallback(() => {
    setIsPolling(true);
  }, []);

  const stopPolling = useCallback(() => {
    setIsPolling(false);
  }, []);

  return {
    ...query,
    isPolling,
    startPolling,
    stopPolling,
  };
};

// Custom hook for search functionality
export const useSearch = () => {
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchHistory, setSearchHistory] = useState([]);

  const semanticSearchMutation = useMutation(
    ({ query, filters }) => searchAPI.semantic(query, filters),
    {
      onMutate: () => {
        setIsSearching(true);
      },
      onSuccess: (data) => {
        setSearchResults(data.results || []);
        setIsSearching(false);
        // Add to search history
        setSearchHistory(prev => {
          const newHistory = [data.query, ...prev.filter(q => q !== data.query)];
          return newHistory.slice(0, 10); // Keep last 10 searches
        });
      },
      onError: (error) => {
        setIsSearching(false);
        toast.error(parseErrorMessage(error));
      },
    }
  );

  const fulltextSearchMutation = useMutation(
    ({ query, filters }) => searchAPI.fulltext(query, filters),
    {
      onMutate: () => {
        setIsSearching(true);
      },
      onSuccess: (data) => {
        setSearchResults(data.results || []);
        setIsSearching(false);
      },
      onError: (error) => {
        setIsSearching(false);
        toast.error(parseErrorMessage(error));
      },
    }
  );

  const semanticSearch = useCallback((query, filters = {}) => {
    return semanticSearchMutation.mutateAsync({ query, filters });
  }, [semanticSearchMutation]);

  const fulltextSearch = useCallback((query, filters = {}) => {
    return fulltextSearchMutation.mutateAsync({ query, filters });
  }, [fulltextSearchMutation]);

  const clearResults = useCallback(() => {
    setSearchResults([]);
  }, []);

  return {
    searchResults,
    isSearching,
    searchHistory,
    semanticSearch,
    fulltextSearch,
    clearResults,
  };
};

// Custom hook for analytics data
export const useAnalytics = () => {
  const dashboardQuery = useQuery(
    'analytics-dashboard',
    analyticsAPI.getDashboard,
    {
      staleTime: 10 * 60 * 1000, // 10 minutes
      onError: (error) => {
        toast.error(parseErrorMessage(error));
      },
    }
  );

  const getUsage = useCallback((period = '30d') => {
    return analyticsAPI.getUsage(period);
  }, []);

  const getTrends = useCallback((metric, period = '30d') => {
    return analyticsAPI.getTrends(metric, period);
  }, []);

  return {
    dashboard: dashboardQuery.data,
    isDashboardLoading: dashboardQuery.isLoading,
    getUsage,
    getTrends,
    refetchDashboard: dashboardQuery.refetch,
  };
};

// Custom hook for local storage
export const useLocalStorage = (key, initialValue) => {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = useCallback((value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  const removeValue = useCallback(() => {
    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (error) {
      console.error(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  return [storedValue, setValue, removeValue];
};

// Custom hook for debounced value
export const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Custom hook for previous value
export const usePrevious = (value) => {
  const ref = useRef();
  
  useEffect(() => {
    ref.current = value;
  });
  
  return ref.current;
};

// Custom hook for intersection observer
export const useIntersectionObserver = (options = {}) => {
  const [entry, setEntry] = useState(null);
  const [node, setNode] = useState(null);

  const observer = useRef(null);

  useEffect(() => {
    if (observer.current) observer.current.disconnect();

    observer.current = new IntersectionObserver(([entry]) => {
      setEntry(entry);
    }, options);

    const currentObserver = observer.current;

    if (node) currentObserver.observe(node);

    return () => currentObserver.disconnect();
  }, [node, options]);

  return [setNode, entry];
};

// Custom hook for window size
export const useWindowSize = () => {
  const [windowSize, setWindowSize] = useState({
    width: undefined,
    height: undefined,
  });

  useEffect(() => {
    function handleResize() {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    }

    window.addEventListener('resize', handleResize);
    handleResize();

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowSize;
};

// Custom hook for media query
export const useMediaQuery = (query) => {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    if (media.matches !== matches) {
      setMatches(media.matches);
    }

    const listener = () => setMatches(media.matches);
    media.addListener(listener);

    return () => media.removeListener(listener);
  }, [matches, query]);

  return matches;
};

// Custom hook for keyboard shortcuts
export const useKeyboard = (keyMap) => {
  useEffect(() => {
    const handleKeyPress = (event) => {
      const key = event.key.toLowerCase();
      const ctrl = event.ctrlKey || event.metaKey;
      const shift = event.shiftKey;
      const alt = event.altKey;

      const keyString = [
        ctrl && 'ctrl',
        shift && 'shift',
        alt && 'alt',
        key
      ].filter(Boolean).join('+');

      if (keyMap[keyString]) {
        event.preventDefault();
        keyMap[keyString]();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [keyMap]);
};

// Custom hook for clipboard
export const useClipboard = () => {
  const [copiedText, setCopiedText] = useState('');

  const copy = useCallback(async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedText(text);
      toast.success('Copied to clipboard!');
      return true;
    } catch (err) {
      toast.error('Failed to copy to clipboard');
      return false;
    }
  }, []);

  return { copy, copiedText };
};
