import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ShieldOff, Home, ArrowLeft } from 'lucide-react';
import { Button } from '@components/ui/button';

export default function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-8">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-red-500/5 via-transparent to-transparent" />
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 flex flex-col items-center text-center"
      >
        <motion.div
          animate={{ rotate: [0, -5, 5, -5, 0] }}
          transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
          className="mb-6 flex h-24 w-24 items-center justify-center rounded-3xl bg-red-500/10"
        >
          <ShieldOff className="h-12 w-12 text-red-400" />
        </motion.div>
        <h1 className="mb-2 text-7xl font-bold tracking-tighter text-foreground">404</h1>
        <div className="mb-6 h-px w-32 bg-gradient-to-r from-transparent via-red-500/50 to-transparent" />
        <h2 className="mb-2 text-xl font-semibold text-foreground">Page Not Found</h2>
        <p className="mb-8 max-w-md text-sm text-muted-foreground">
          The page you are looking for doesn't exist or has been moved. The SOC analysts have been notified.
        </p>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={() => navigate(-1)}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Go Back
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
