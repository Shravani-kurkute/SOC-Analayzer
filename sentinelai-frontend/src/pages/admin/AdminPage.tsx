import { PageHeader } from '@components/common/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@components/ui/card';

export default function AdminPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Administration" description="Manage users and system settings" />
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {['User Management', 'Audit Logs', 'System Health', 'Detection Rules', 'Integrations', 'Data Retention'].map((item) => (
          <Card key={item} className="cursor-pointer transition-all hover:border-primary/50">
            <CardHeader>
              <CardTitle className="text-sm">{item}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">Manage {item.toLowerCase()}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
