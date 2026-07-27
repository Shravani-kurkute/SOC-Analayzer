import { format, formatDistanceToNow, parseISO } from 'date-fns';

export function formatDate(date: string | Date, pattern = 'MMM dd, yyyy HH:mm:ss'): string {
  return format(typeof date === 'string' ? parseISO(date) : date, pattern);
}

export function timeAgo(date: string | Date): string {
  return formatDistanceToNow(typeof date === 'string' ? parseISO(date) : date, { addSuffix: true });
}

export function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  const parts: string[] = [];
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  if (secs > 0 || parts.length === 0) parts.push(`${secs}s`);

  return parts.join(' ');
}

export function toISO(date: Date): string {
  return date.toISOString();
}

export function formatSeverity(severity: string): string {
  return severity.charAt(0).toUpperCase() + severity.slice(1);
}
