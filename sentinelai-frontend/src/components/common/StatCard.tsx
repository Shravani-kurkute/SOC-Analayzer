import { motion } from 'framer-motion';
import { cn } from '@utils/cn';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: React.ElementType;
  trend?: {
    value: number;
    isUp: boolean;
  };
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}

const variantStyles = {
  default: {
    icon: 'text-primary bg-primary/10',
    border: 'border-primary/20',
    glow: 'shadow-primary/5',
  },
  success: {
    icon: 'text-emerald-400 bg-emerald-500/10',
    border: 'border-emerald-500/20',
    glow: 'shadow-emerald-500/5',
  },
  warning: {
    icon: 'text-yellow-400 bg-yellow-500/10',
    border: 'border-yellow-500/20',
    glow: 'shadow-yellow-500/5',
  },
  danger: {
    icon: 'text-red-400 bg-red-500/10',
    border: 'border-red-500/20',
    glow: 'shadow-red-500/5',
  },
  info: {
    icon: 'text-[#00F5FF] bg-[#00F5FF]/10',
    border: 'border-[#00F5FF]/20',
    glow: 'shadow-[#00F5FF]/5',
  },
};

export function StatCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
  variant = 'default',
  className,
}: StatCardProps) {
  const styles = variantStyles[variant];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'group relative overflow-hidden rounded-xl border bg-gradient-to-b from-card to-card/95 p-5 shadow-lg backdrop-blur-sm transition-all duration-300 hover:shadow-xl',
        styles.border,
        styles.glow,
        className,
      )}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-white/[0.02] pointer-events-none" />
      <div className="relative z-10 flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground/70">
            {title}
          </p>
          <p className="text-3xl font-bold tracking-tight text-foreground">{value}</p>
          {description && (
            <p className="text-xs text-muted-foreground">{description}</p>
          )}
        </div>
        {Icon && (
          <div className={cn('rounded-lg p-2.5 transition-all duration-300 group-hover:scale-110', styles.icon)}>
            <Icon className="h-5 w-5" />
          </div>
        )}
      </div>
      {trend && (
        <div className="relative z-10 mt-4 flex items-center gap-1.5">
          {trend.isUp ? (
            <TrendingUp className="h-3.5 w-3.5 text-emerald-400" />
          ) : (
            <TrendingDown className="h-3.5 w-3.5 text-red-400" />
          )}
          <span
            className={cn(
              'text-xs font-medium',
              trend.isUp ? 'text-emerald-400' : 'text-red-400',
            )}
          >
            {trend.value}%
          </span>
          <span className="text-xs text-muted-foreground">vs last hour</span>
        </div>
      )}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-current opacity-10" />
    </motion.div>
  );
}
