import { PageHeader } from '@components/common/PageHeader';
import { Card, CardContent } from '@components/ui/card';
import { EmptyState } from '@components/common/EmptyState';
import { Shield } from 'lucide-react';

export default function ThreatsPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Threat Intelligence" description="IOC feeds and threat analysis" />
      <Card>
        <CardContent className="p-6">
          <EmptyState
            icon={Shield}
            title="No threats detected"
            description="Threat intelligence feeds will be displayed here."
          />
        </CardContent>
      </Card>
    </div>
  );
}
