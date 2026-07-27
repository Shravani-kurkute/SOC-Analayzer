import { PageHeader } from '@components/common/PageHeader';
import { Card, CardContent } from '@components/ui/card';
import { EmptyState } from '@components/common/EmptyState';
import { Brain } from 'lucide-react';

export default function AICenterPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="AI Security Center" description="AI-powered threat analysis and investigations" />
      <Card>
        <CardContent className="p-6">
          <EmptyState
            icon={Brain}
            title="AI Center ready"
            description="Connect your AI provider to enable intelligent threat analysis."
          />
        </CardContent>
      </Card>
    </div>
  );
}
