import React from 'react';
import { motion } from 'framer-motion';

// Animated icons and graphics components

export const WaveAnimation = ({ className = "" }) => (
  <div className={`relative ${className}`}>
    <svg
      viewBox="0 0 400 100"
      className="w-full h-full"
      preserveAspectRatio="none"
    >
      <defs>
        <linearGradient id="waveGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.8" />
          <stop offset="50%" stopColor="#8B5CF6" stopOpacity="0.6" />
          <stop offset="100%" stopColor="#06B6D4" stopOpacity="0.4" />
        </linearGradient>
      </defs>
      <motion.path
        d="M0,50 Q100,20 200,50 T400,50 V100 H0 Z"
        fill="url(#waveGradient)"
        initial={{ d: "M0,50 Q100,20 200,50 T400,50 V100 H0 Z" }}
        animate={{
          d: [
            "M0,50 Q100,20 200,50 T400,50 V100 H0 Z",
            "M0,50 Q100,80 200,50 T400,50 V100 H0 Z",
            "M0,50 Q100,20 200,50 T400,50 V100 H0 Z"
          ]
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
    </svg>
  </div>
);

export const AudioWaveform = ({ className = "", isPlaying = false }) => (
  <div className={`flex items-center space-x-1 ${className}`}>
    {[...Array(20)].map((_, i) => (
      <motion.div
        key={i}
        className="bg-gradient-to-t from-blue-500 to-purple-600 rounded-full"
        style={{
          width: '3px',
          height: isPlaying ? '20px' : '8px'
        }}
        animate={isPlaying ? {
          height: [8, Math.random() * 30 + 10, 8],
          opacity: [0.6, 1, 0.6]
        } : {}}
        transition={{
          duration: 0.5 + Math.random() * 0.5,
          repeat: Infinity,
          ease: "easeInOut",
          delay: i * 0.1
        }}
      />
    ))}
  </div>
);

export const ProcessingSpinner = ({ className = "" }) => (
  <div className={`relative ${className}`}>
    <motion.div
      className="w-12 h-12 border-4 border-gray-200 border-t-blue-600 rounded-full"
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
    />
    <motion.div
      className="absolute inset-2 w-8 h-8 border-2 border-gray-100 border-b-purple-500 rounded-full"
      animate={{ rotate: -360 }}
      transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
    />
  </div>
);

export const FloatingElements = ({ children, className = "" }) => (
  <motion.div
    className={className}
    animate={{
      y: [-10, 10, -10],
      rotate: [-1, 1, -1]
    }}
    transition={{
      duration: 6,
      repeat: Infinity,
      ease: "easeInOut"
    }}
  >
    {children}
  </motion.div>
);

export const GradientOrb = ({ size = "w-64 h-64", className = "" }) => (
  <div className={`${size} ${className} relative`}>
    <motion.div
      className="absolute inset-0 bg-gradient-to-br from-blue-400 via-purple-500 to-pink-500 rounded-full opacity-70 blur-xl"
      animate={{
        scale: [1, 1.2, 1],
        opacity: [0.7, 0.9, 0.7]
      }}
      transition={{
        duration: 4,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    />
    <motion.div
      className="absolute inset-4 bg-gradient-to-tr from-cyan-400 via-blue-500 to-purple-600 rounded-full opacity-80"
      animate={{
        scale: [1.1, 0.9, 1.1],
        rotate: [0, 180, 360]
      }}
      transition={{
        duration: 8,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    />
  </div>
);

export const ProgressRing = ({ progress = 0, size = 120, strokeWidth = 8, className = "" }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDasharray = `${circumference} ${circumference}`;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <div className={`relative ${className}`}>
      <svg
        className="transform -rotate-90"
        width={size}
        height={size}
      >
        <defs>
          <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#3B82F6" />
            <stop offset="100%" stopColor="#8B5CF6" />
          </linearGradient>
        </defs>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#E5E7EB"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="url(#progressGradient)"
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={strokeDasharray}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1, ease: "easeInOut" }}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-2xl font-bold text-gray-700">{Math.round(progress)}%</span>
      </div>
    </div>
  );
};

export const ParticleField = ({ className = "" }) => (
  <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
    {[...Array(15)].map((_, i) => (
      <motion.div
        key={i}
        className="absolute w-2 h-2 bg-blue-400 rounded-full opacity-30"
        style={{
          left: `${Math.random() * 100}%`,
          top: `${Math.random() * 100}%`,
        }}
        animate={{
          y: [-20, -100],
          opacity: [0, 0.6, 0],
          scale: [0, 1, 0]
        }}
        transition={{
          duration: 3 + Math.random() * 2,
          repeat: Infinity,
          delay: Math.random() * 2,
          ease: "easeOut"
        }}
      />
    ))}
  </div>
);

export const IconContainer = ({ children, className = "", variant = "primary" }) => {
  const variants = {
    primary: "bg-gradient-to-br from-blue-500 to-purple-600",
    secondary: "bg-gradient-to-br from-green-500 to-teal-600",
    accent: "bg-gradient-to-br from-orange-500 to-pink-600",
    neutral: "bg-gradient-to-br from-gray-500 to-gray-700"
  };

  return (
    <motion.div
      className={`${variants[variant]} rounded-2xl p-4 shadow-lg ${className}`}
      whileHover={{ scale: 1.05, rotate: 2 }}
      whileTap={{ scale: 0.95 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      <motion.div
        className="text-white"
        whileHover={{ scale: 1.1 }}
        transition={{ type: "spring", stiffness: 400, damping: 10 }}
      >
        {children}
      </motion.div>
    </motion.div>
  );
};

export const DataVisualization = ({ data = [], className = "" }) => (
  <div className={`space-y-2 ${className}`}>
    {data.map((item, index) => (
      <div key={index} className="flex items-center space-x-3">
        <span className="text-sm font-medium text-gray-600 w-20">{item.label}</span>
        <div className="flex-1 bg-gray-200 rounded-full h-3 overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${item.value}%` }}
            transition={{ duration: 1, delay: index * 0.1, ease: "easeOut" }}
          />
        </div>
        <span className="text-sm font-bold text-gray-800 w-10">{item.value}%</span>
      </div>
    ))}
  </div>
);

export const AnimatedCounter = ({ end = 0, duration = 2, className = "" }) => {
  const [count, setCount] = React.useState(0);

  React.useEffect(() => {
    let startTime;
    const animate = (currentTime) => {
      if (!startTime) startTime = currentTime;
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / (duration * 1000), 1);
      
      setCount(Math.floor(end * progress));
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }, [end, duration]);

  return <span className={className}>{count}</span>;
};
