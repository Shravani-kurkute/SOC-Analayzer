import { PageHeader } from '@components/common/PageHeader';
import { Card, CardContent } from '@components/ui/card';
import { EmptyState } from '@components/common/EmptyState';
import { AlertTriangle } from 'lucide-react';
import { Button } from '@components/ui/button';
import { Filter, Download, RefreshCw } from 'lucide-react';

export default function AlertsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Alerts"
        description="Monitor and manage security alerts"
        actions={
          <>
            <Button variant="outline" size="sm"><Filter className="mr-2 h-4 w-4" />Filter</Button>
            <Button variant="outline" size="sm"><Download className="mr-2 h-4 w-4" />Export</Button>
            <Button variant="accent" size="sm"><RefreshCw className="mr-2 h-4 w-4" />Refresh</Button>
          </>
        }
      />
      <Card>
        <CardContent className="p-6">
          <EmptyState
            icon={AlertTriangle}
            title="No alerts to display"
            description="Alert data will appear here once detection rules are triggered."
            action={{ label: 'View Detection Rules', onClick: () => {} }}
          />
        </CardContent>
      </Card>
    </div>
  );
}
