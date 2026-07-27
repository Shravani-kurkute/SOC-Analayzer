import { PageHeader } from '@components/common/PageHeader';
import { Card, CardContent } from '@components/ui/card';
import { EmptyState } from '@components/common/EmptyState';
import { PlayCircle } from 'lucide-react';

export default function PlaybooksPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Playbooks" description="Automated incident response playbooks" />
      <Card>
        <CardContent className="p-6">
          <EmptyState
            icon={PlayCircle}
            title="No playbooks defined"
            description="Create automated response workflows for common scenarios."
            action={{ label: 'Create Playbook', onClick: () => {} }}
          />
        </CardContent>
      </Card>
    </div>
  );
}
