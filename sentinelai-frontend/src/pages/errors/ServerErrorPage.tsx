import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AlertTriangle, Home, RefreshCw } from 'lucide-react';
import { Button } from '@components/ui/button';

export default function ServerErrorPage() {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-8">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-red-500/10 via-transparent to-transparent" />
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 flex flex-col items-center text-center"
      >
        <motion.div
          animate={{ rotate: [0, -10, 10, -10, 0] }}
          transition={{ duration: 1.5, repeat: Infinity, repeatDelay: 4 }}
          className="mb-6 flex h-24 w-24 items-center justify-center rounded-3xl bg-red-500/10"
        >
          <AlertTriangle className="h-12 w-12 text-red-400" />
        </motion.div>
        <h1 className="mb-2 text-7xl font-bold tracking-tighter text-foreground">500</h1>
        <div className="mb-6 h-px w-32 bg-gradient-to-r from-transparent via-red-500/50 to-transparent" />
        <h2 className="mb-2 text-xl font-semibold text-foreground">Server Error</h2>
        <p className="mb-8 max-w-md text-sm text-muted-foreground">
          An unexpected error occurred on our servers. Our team has been automatically notified and is working on a fix.
        </p>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={() => window.location.reload()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Try Again
          </Button>
          <Button variant="accent" onClick={() => navigate('/dashboard')}>
            <Home className="mr-2 h-4 w-4" />
            Dashboard
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
