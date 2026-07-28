import { useState } from 'react';
import { motion } from 'framer-motion';
import { Beaker, X, CheckCircle2, AlertCircle, Loader2, FileText } from 'lucide-react';
import { Button } from '@components/ui/button';
import { Card } from '@components/ui/card';
import { demoService } from '@services/demoService';

interface SeedResult {
  uploaded: number;
  parsed: number;
}

export function DemoModeBanner() {
  const [isSeeding, setIsSeeding] = useState(false);
  const [result, setResult] = useState<SeedResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  const handleSeedData = async () => {
    setIsSeeding(true);
    setError(null);
    setResult(null);
    try {
      const res = await demoService.seedDemoData();
      setResult(res);
    } catch {
      setError('Failed to seed demo data. Make sure the backend is running.');
    } finally {
      setIsSeeding(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-6"
    >
      <Card className="border-[#00F5FF]/30 bg-gradient-to-r from-[#00F5FF]/5 to-transparent p-4">
        <div className="flex items-start gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#00F5FF]/10">
            <Beaker className="h-4 w-4 text-[#00F5FF]" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-medium text-foreground">Demo Mode</h3>
              <span className="rounded bg-[#00F5FF]/10 px-1.5 py-0.5 text-[10px] font-medium text-[#00F5FF]">ACTIVE</span>
            </div>
            <p className="mt-0.5 text-xs text-muted-foreground">
              Seed the system with sample logs to demonstrate parsing and dashboard capabilities.
              Normal operation should use real log sources.
            </p>

            {error && (
              <div className="mt-2 flex items-center gap-2 text-xs text-red-400">
                <AlertCircle className="h-3 w-3" />
                {error}
              </div>
            )}

            {result && (
              <div className="mt-2 flex items-center gap-2 text-xs text-emerald-400">
                <CheckCircle2 className="h-3 w-3" />
                Seeded {result.uploaded} log files ({result.parsed} events parsed)
              </div>
            )}

            <div className="mt-3 flex items-center gap-2">
              <Button
                variant="accent"
                size="sm"
                onClick={handleSeedData}
                disabled={isSeeding}
              >
                {isSeeding ? (
                  <><Loader2 className="mr-1.5 h-3 w-3 animate-spin" />Seeding...</>
                ) : (
                  <><FileText className="mr-1.5 h-3 w-3" />Seed Sample Data</>
                )}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsVisible(false)}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>

            <div className="mt-2 space-y-0.5">
              <p className="text-[10px] text-muted-foreground">Sample data includes:</p>
              {demoService.getSampleDescriptions().map((s) => (
                <p key={s.filename} className="text-[10px] text-muted-foreground">
                  &bull; {s.filename} &mdash; {s.description}
                </p>
              ))}
            </div>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
