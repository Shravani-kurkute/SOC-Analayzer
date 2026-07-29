import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { PageHeader } from '@components/common/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@components/ui/tabs';
import { Input } from '@components/ui/input';
import { Label } from '@components/ui/label';
import { Button } from '@components/ui/button';
import { Skeleton } from '@components/ui/skeleton';
import { notificationService } from '@services/notificationService';
import type { NotificationPreferences } from '@typings/notification';

export default function SettingsPage() {
  const [searchParams] = useSearchParams();
  const defaultTab = searchParams.get('tab') || 'profile';
  const [prefs, setPrefs] = useState<NotificationPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    notificationService.getPreferences().then(setPrefs).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const updatePref = (key: keyof NotificationPreferences, value: boolean) => {
    setPrefs(prev => prev ? { ...prev, [key]: value } : prev);
  };

  const savePreferences = async () => {
    if (!prefs) return;
    setSaving(true);
    try {
      await notificationService.updatePreferences(prefs);
    } catch {}
    setSaving(false);
  };

  return (
    <div className="space-y-6">
      <PageHeader title="Settings" description="Manage your preferences" />
      <Tabs defaultValue={defaultTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="api">API Keys</TabsTrigger>
        </TabsList>
        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle>Profile Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="full-name">Full Name</Label>
                  <Input id="full-name" placeholder="John Doe" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" placeholder="john@sentinelai.dev" />
                </div>
              </div>
              <Button variant="accent">Save Changes</Button>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="security">
          <Card>
            <CardHeader>
              <CardTitle>Security Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="current-password">Current Password</Label>
                <Input id="current-password" type="password" />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="new-password">New Password</Label>
                  <Input id="new-password" type="password" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirm-password">Confirm Password</Label>
                  <Input id="confirm-password" type="password" />
                </div>
              </div>
              <Button variant="accent">Update Password</Button>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle>Notification Preferences</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {loading ? (
                <div className="space-y-4">
                  {[1,2,3,4,5,6].map(i => <Skeleton key={i} className="h-10 w-full" />)}
                </div>
              ) : prefs ? (
                <>
                  <div>
                    <p className="text-sm font-medium mb-3">Channels</p>
                    <div className="space-y-3">
                      {[
                        { key: 'email_enabled' as const, label: 'Email', desc: 'Receive notifications via email' },
                        { key: 'desktop_enabled' as const, label: 'Desktop', desc: 'Show desktop push notifications' },
                        { key: 'slack_enabled' as const, label: 'Slack', desc: 'Send notifications to Slack' },
                        { key: 'discord_enabled' as const, label: 'Discord', desc: 'Send notifications to Discord' },
                        { key: 'teams_enabled' as const, label: 'Microsoft Teams', desc: 'Send notifications to Teams' },
                        { key: 'telegram_enabled' as const, label: 'Telegram', desc: 'Send notifications to Telegram' },
                      ].map(ch => (
                        <label key={ch.key} className="flex items-center justify-between p-3 rounded-lg bg-secondary/20 border border-border/50 cursor-pointer hover:bg-secondary/30 transition-colors">
                          <div>
                            <p className="text-sm font-medium">{ch.label}</p>
                            <p className="text-xs text-muted-foreground">{ch.desc}</p>
                          </div>
                          <input
                            type="checkbox"
                            checked={prefs[ch.key]}
                            onChange={(e) => updatePref(ch.key, e.target.checked)}
                            className="h-4 w-4 rounded border-border accent-[#00F5FF]"
                          />
                        </label>
                      ))}
                    </div>
                  </div>

                  <div>
                    <p className="text-sm font-medium mb-3">Filters</p>
                    <div className="space-y-3">
                      <label className="flex items-center justify-between p-3 rounded-lg bg-secondary/20 border border-border/50 cursor-pointer hover:bg-secondary/30 transition-colors">
                        <div>
                          <p className="text-sm font-medium">Critical Only</p>
                          <p className="text-xs text-muted-foreground">Only receive critical severity notifications</p>
                        </div>
                        <input
                          type="checkbox"
                          checked={prefs.critical_only}
                          onChange={(e) => updatePref('critical_only', e.target.checked)}
                          className="h-4 w-4 rounded border-border accent-[#00F5FF]"
                        />
                      </label>
                    </div>
                  </div>

                  <div className="flex justify-end gap-2 pt-2">
                    <Button variant="accent" onClick={savePreferences} disabled={saving}>
                      {saving ? 'Saving...' : 'Save Preferences'}
                    </Button>
                  </div>
                </>
              ) : (
                <p className="text-sm text-muted-foreground">Could not load preferences</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
