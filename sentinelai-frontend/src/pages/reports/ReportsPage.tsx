import { useNavigate } from 'react-router-dom';
import { PageHeader } from '@components/common/PageHeader';
import { Card, CardContent } from '@components/ui/card';
import { EmptyState } from '@components/common/EmptyState';
import { FileText } from 'lucide-react';

export default function ReportsPage() {
  const navigate = useNavigate();
  return (
    <div className="space-y-6">
      <PageHeader title="Reports" description="Generate and manage reports" />
      <Card>
        <CardContent className="p-6">
          <EmptyState
            icon={FileText}
            title="No reports yet"
            description="Create your first report to get started."
            action={{ label: 'Create Report', onClick: () => navigate('/reports/builder') }}
          />
        </CardContent>
      </Card>
    </div>
  );
}
