import { motion } from 'framer-motion';
import { Activity } from 'lucide-react';

interface LoadingScreenProps {
  fullScreen?: boolean;
  message?: string;
}

export default function LoadingScreen({ fullScreen = true, message = 'Loading...' }: LoadingScreenProps) {
  return (
    <div
      className={`flex items-center justify-center bg-background ${
        fullScreen ? 'h-screen' : 'h-full min-h-[400px]'
      }`}
    >
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          <div className="h-12 w-12 animate-spin rounded-full border-2 border-primary/30 border-t-primary" />
          <motion.div
            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="absolute inset-0 flex items-center justify-center"
          >
            <Activity className="h-5 w-5 text-primary" />
          </motion.div>
        </div>
        <p className="text-sm text-muted-foreground animate-pulse">{message}</p>
      </div>
    </div>
  );
}
