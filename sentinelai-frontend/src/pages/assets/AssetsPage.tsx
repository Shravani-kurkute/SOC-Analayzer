import { PageHeader } from '@components/common/PageHeader';
import { Card, CardContent } from '@components/ui/card';
import { EmptyState } from '@components/common/EmptyState';
import { Server } from 'lucide-react';

export default function AssetsPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Asset Inventory" description="Monitor all managed assets" />
      <Card>
        <CardContent className="p-6">
          <EmptyState
            icon={Server}
            title="No assets discovered"
            description="Assets will appear once agents are deployed and reporting."
            action={{ label: 'Deploy Agent', onClick: () => {} }}
          />
        </CardContent>
      </Card>
    </div>
  );
}
