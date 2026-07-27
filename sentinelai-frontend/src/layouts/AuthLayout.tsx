import { Outlet } from 'react-router-dom';

export default function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/20 via-background to-background" />
      <div className="relative z-10 w-full max-w-md px-4">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            SentinelAI
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Security Operations Center
          </p>
        </div>
        <Outlet />
      </div>
    </div>
  );
}
