/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_NAME: string;
  readonly VITE_APP_VERSION: string;
  readonly VITE_APP_ENV: string;
  readonly VITE_API_BASE_URL: string;
  readonly VITE_API_PREFIX: string;
  readonly VITE_WS_URL: string;
  readonly VITE_API_TIMEOUT: string;
  readonly VITE_AUTH_TOKEN_KEY: string;
  readonly VITE_AUTH_REFRESH_KEY: string;
  readonly VITE_SESSION_TIMEOUT_MINUTES: string;
  readonly VITE_SENTRY_DSN: string;
  readonly VITE_SENTRY_ENVIRONMENT: string;
  readonly VITE_FEATURE_AI_ASSISTANT: string;
  readonly VITE_FEATURE_PLAYBOOKS: string;
  readonly VITE_FEATURE_ADVANCED_ANALYTICS: string;
  readonly VITE_DEFAULT_THEME: string;
  readonly VITE_REFRESH_INTERVAL: string;
  readonly VITE_DEFAULT_PAGE_SIZE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
