import { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@contexts/ThemeContext';
import { WebSocketProvider } from '@contexts/WebSocketContext';
import { SidebarProvider } from '@contexts/SidebarContext';
import AppLayout from '@layouts/AppLayout';
import AuthLayout from '@layouts/AuthLayout';
import LoadingScreen from '@components/common/LoadingScreen';
import ProtectedRoute from '@components/auth/ProtectedRoute';
import PublicRoute from '@components/auth/PublicRoute';

const Dashboard = lazy(() => import('@pages/dashboard/DashboardPage'));
const Alerts = lazy(() => import('@pages/alerts/AlertsPage'));
const AlertDetail = lazy(() => import('@pages/alerts/AlertDetailPage'));
const Incidents = lazy(() => import('@pages/incidents/IncidentsPage'));
const IncidentDetail = lazy(() => import('@pages/incidents/IncidentDetailPage'));
const Threats = lazy(() => import('@pages/threats/ThreatsPage'));
const ThreatDetail = lazy(() => import('@pages/threats/ThreatDetailPage'));
const Assets = lazy(() => import('@pages/assets/AssetsPage'));
const AssetDetail = lazy(() => import('@pages/assets/AssetDetailPage'));
const Reports = lazy(() => import('@pages/reports/ReportsPage'));
const ReportBuilder = lazy(() => import('@pages/reports/ReportBuilderPage'));
const Settings = lazy(() => import('@pages/settings/SettingsPage'));
const AICenter = lazy(() => import('@pages/ai/AICenterPage'));
const LogCollection = lazy(() => import('@pages/logs/LogCollectionPage'));
const Correlation = lazy(() => import('@pages/correlation/CorrelationPage'));
const IocExplorer = lazy(() => import('@pages/ioc/IocPage'));
const MitreExplorer = lazy(() => import('@pages/mitre/MitrePage'));
const Playbooks = lazy(() => import('@pages/playbooks/PlaybooksPage'));
const PlaybookDetail = lazy(() => import('@pages/playbooks/PlaybookDetailPage'));
const Integrations = lazy(() => import('@pages/integrations/IntegrationsPage'));
const Admin = lazy(() => import('@pages/admin/AdminPage'));
const Login = lazy(() => import('@pages/auth/LoginPage'));
const ForgotPassword = lazy(() => import('@pages/auth/ForgotPasswordPage'));
const ResetPassword = lazy(() => import('@pages/auth/ResetPasswordPage'));
const NotFound = lazy(() => import('@pages/errors/NotFoundPage'));
const Forbidden = lazy(() => import('@pages/errors/ForbiddenPage'));
const ServerError = lazy(() => import('@pages/errors/ServerErrorPage'));

const PageLoader = () => (
  <div className="flex h-[calc(100vh-4rem)] items-center justify-center">
    <LoadingScreen />
  </div>
);

export default function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="sentinelai-theme">
      <SidebarProvider>
        <WebSocketProvider>
          <Suspense fallback={<LoadingScreen />}>
            <Routes>
              <Route element={<PublicRoute />}>
                <Route element={<AuthLayout />}>
                  <Route path="/login" element={<Login />} />
                  <Route path="/forgot-password" element={<ForgotPassword />} />
                  <Route path="/reset-password" element={<ResetPassword />} />
                </Route>
              </Route>

              <Route element={<ProtectedRoute />}>
                <Route element={<AppLayout />}>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route
                      path="/dashboard"
                      element={
                        <Suspense fallback={<PageLoader />}>
                          <Dashboard />
                        </Suspense>
                      }
                    />
                    <Route
                        path="/logs"
                        element={
                          <Suspense fallback={<PageLoader />}>
                            <LogCollection />
                          </Suspense>
                        }
                      />
                  <Route
                      path="/correlation"
                      element={
                        <Suspense fallback={<PageLoader />}>
                          <Correlation />
                        </Suspense>
                      }
                    />
                  <Route
                      path="/ioc"
                      element={
                        <Suspense fallback={<PageLoader />}>
                          <IocExplorer />
                        </Suspense>
                      }
                    />
                  <Route
                      path="/mitre"
                      element={
                        <Suspense fallback={<PageLoader />}>
                          <MitreExplorer />
                        </Suspense>
                      }
                    />
                  <Route
                      path="/alerts"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <Alerts />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/alerts/:id"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <AlertDetail />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/incidents"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <Incidents />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/incidents/:id"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <IncidentDetail />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/threats"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <Threats />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/threats/:id"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <ThreatDetail />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/assets"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <Assets />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/assets/:id"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <AssetDetail />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/reports"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <Reports />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/reports/builder"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <ReportBuilder />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/ai"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <AICenter />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/playbooks"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <Playbooks />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/playbooks/:id"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <PlaybookDetail />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/integrations"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <Integrations />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/settings/*"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <Settings />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/admin/*"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <Admin />
                      </Suspense>
                    }
                  />
                </Route>
              </Route>

              <Route path="/403" element={<Forbidden />} />
              <Route path="/500" element={<ServerError />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </WebSocketProvider>
      </SidebarProvider>
    </ThemeProvider>
  );
}
