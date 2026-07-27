import { PageHeader } from '@components/common/PageHeader';
import { Card, CardContent } from '@components/ui/card';
import { EmptyState } from '@components/common/EmptyState';
import { Siren } from 'lucide-react';

export default function IncidentsPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Incidents" description="Track and manage security incidents" />
      <Card>
        <CardContent className="p-6">
          <EmptyState
            icon={Siren}
            title="No incidents"
            description="All clear. Incidents will be created from correlated alerts."
          />
        </CardContent>
      </Card>
    </div>
  );
}
