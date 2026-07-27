import { PageHeader } from '@components/common/PageHeader';
import { Card, CardContent } from '@components/ui/card';
import { EmptyState } from '@components/common/EmptyState';
import { Puzzle } from 'lucide-react';

export default function IntegrationsPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Integrations" description="Connect third-party tools and services" />
      <Card>
        <CardContent className="p-6">
          <EmptyState
            icon={Puzzle}
            title="No integrations configured"
            description="Connect your SIEM, EDR, threat intel feeds, and more."
            action={{ label: 'Add Integration', onClick: () => {} }}
          />
        </CardContent>
      </Card>
    </div>
  );
}
