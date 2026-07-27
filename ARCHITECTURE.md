# SentinelAI — Architecture Document

> **Version:** 1.0.0
> **Classification:** Internal — Proprietary
> **Last Updated:** 2026-07-27

---

## Table of Contents

1. [Architecture Diagram](#1-architecture-diagram)
2. [Application Data Flow](#2-application-data-flow)
3. [Technology Justification](#3-technology-justification)
4. [Project Structure & Folder Responsibility](#4-project-structure--folder-responsibility)
5. [Coding Conventions](#5-coding-conventions)
6. [Naming Conventions](#6-naming-conventions)
7. [API Conventions](#7-api-conventions)
8. [Development Setup](#8-development-setup)
9. [Environment Variables](#9-environment-variables)
10. [Scalability Considerations](#10-scalability-considerations)
11. [Security Considerations](#11-security-considerations)
12. [Future Expansion](#12-future-expansion)

---

## 1. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CLIENT LAYER                                      │
│                                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐    │
│  │  React SPA   │  │  React Flow   │  │  Recharts     │  │  WebSocket     │    │
│  │  (Vite)      │  │  (Graphs)     │  │  (Analytics)  │  │  (Real-time)   │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └───────┬────────┘    │
│         │                  │                  │                  │             │
│         └──────────────────┴──────────────────┴──────────────────┘             │
│                                │                                              │
│                        Axios HTTP + WebSocket                                 │
└────────────────────────┬───────┴──────────────────────────────────────────────┘
                         │
┌────────────────────────┴──────────────────────────────────────────────────────┐
│                         GATEWAY LAYER                                         │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │                         Nginx Reverse Proxy                          │    │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌──────────────────┐    │    │
│  │  │ SSL/TLS  │  │ Rate     │  │ Request   │  │ Static Files     │    │    │
│  │  │ Term.    │  │ Limiting │  │ Routing   │  │ Cache            │    │    │
│  │  └──────────┘  └──────────┘  └───────────┘  └──────────────────┘    │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
└────────────────────────┬──────────────────────────────────────────────────────┘
                         │
┌────────────────────────┴──────────────────────────────────────────────────────┐
│                        API GATEWAY (FastAPI)                                   │
│                                                                              │
│  ┌─────────┐ ┌──────────┐ ┌───────────┐ ┌───────────┐ ┌────────────────┐    │
│  │ CORS    │ │ Auth     │ │ Rate      │ │ RequestID │ │ Security       │    │
│  │ Middle  │ │ JWT/MFA  │ │ Limiting  │ │ Tracing   │ │ Headers        │    │
│  └─────────┘ └──────────┘ └───────────┘ └───────────┘ └────────────────┘    │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │                        API v1 Routers                                │    │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌─────┐ ┌──────┐ ┌────────┐  │    │
│  │  │Auth  │ │Alert │ │Inc.  │ │Threat│ │Asset│ │AI    │ │Reports │  │    │
│  │  └──────┘ └──────┘ └──────┘ └──────┘ └─────┘ └──────┘ └────────┘  │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
└────────────────────────┬──────────────────────────────────────────────────────┘
                         │
┌────────────────────────┴──────────────────────────────────────────────────────┐
│                       SERVICE LAYER                                           │
│                                                                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐    │
│  │ Auth Service  │ │ Alert        │ │ Incident     │ │ Detection        │    │
│  │ (JWT, MFA,    │ │ Service      │ │ Service      │ │ Engine           │    │
│  │  SSO)         │ │              │ │              │ │ (Sigma, YARA)    │    │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐    │
│  │ AI Service   │ │ Threat Intel │ │ Report       │ │ Integration      │    │
│  │ (Gemini,     │ │ (MITRE,      │ │ Service      │ │ Service          │    │
│  │  ML)         │ │  STIX/TAXII) │ │              │ │ (API, Webhooks)  │    │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘    │
└────────────────────────┬──────────────────────────────────────────────────────┘
                         │
┌────────────────────────┴──────────────────────────────────────────────────────┐
│                      DATA LAYER                                              │
│                                                                              │
│  ┌──────────────────────┐  ┌──────────────────┐  ┌──────────────────────┐   │
│  │  PostgreSQL 17       │  │  Redis 7          │  │  Elasticsearch      │   │
│  │  ┌────────────────┐  │  │  ┌─────────────┐  │  │  (Optional)         │   │
│  │  │ Alerts          │  │  │ │ Cache        │  │  │  ┌───────────────┐  │   │
│  │  │ Incidents       │  │  │ │ Sessions     │  │  │  │ SIEM Events   │  │   │
│  │  │ Assets          │  │  │ │ Rate Limits  │  │  │  │ Threat Intel  │  │   │
│  │  │ Users           │  │  │ │ Task Queue   │  │  │  │ Log Storage   │  │   │
│  │  │ Rules           │  │  │ │ Pub/Sub      │  │  │  │               │  │   │
│  │  │ Audit Logs      │  │  │ └─────────────┘  │  │  └───────────────┘  │   │
│  │  └────────────────┘  │  └──────────────────┘  └──────────────────────┘   │
│  └──────────────────────┘                                                    │
└────────────────────────┬──────────────────────────────────────────────────────┘
                         │
┌────────────────────────┴──────────────────────────────────────────────────────┐
│                   BACKGROUND WORKERS LAYER                                    │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐   │
│  │  Celery Worker    │  │  Celery Beat      │  │  WebSocket Server       │   │
│  │  ┌─────────────┐  │  │  ┌─────────────┐  │  │  ┌──────────────────┐  │   │
│  │  │ Detection   │  │  │ │ Scheduler    │  │  │  │ Real-time Alerts │  │   │
│  │  │ Log Parsing │  │  │ │ Report Gen   │  │  │  │ Live Dashboard  │  │   │
│  │  │ AI Analysis │  │  │ │ Cleanup Jobs │  │  │  │ AI Chat         │  │   │
│  │  │ Report Gen  │  │  │ │ Intel Update │  │  │  │ Event Stream    │  │   │
│  │  └─────────────┘  │  │ └─────────────┘  │  │  └──────────────────┘  │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Application Data Flow

### 2.1 Event Ingestion Flow

```
External Sources (Logs, Network, Cloud, Endpoint)
        │
        ▼
┌─────────────────┐
│  Log Parsers     │  ← Supports: Syslog, JSON, XML, EVTX, PCAP, CSV, custom
│  (FastAPI)       │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Normalization   │  ← ECS/CEF normalization, field mapping, enrichment
│  Engine          │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Detection       │  ← Sigma rules, YARA, custom signatures, ML models
│  Engine          │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ Alert  │ │ Pass   │  ← Low severity / known good
│ Created│ │ Through│
└────┬───┘ └────────┘
     ▼
┌─────────────────┐
│  Enrichment      │  ← Threat intel lookup, geo IP, WHOIS, DNS
│  Pipeline        │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Correlation     │  ← Time-based, sequence-based, statistical
│  Engine          │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Incident        │  ← Alert grouping, deduplication, severity scoring
│  Creation        │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Notification    │  ← Email, Slack, PagerDuty, Webhook
│  & Response      │
└─────────────────┘
```

### 2.2 Authentication Flow

```
User → Login Form → POST /api/v1/auth/login
                        │
                        ▼
              ┌─────────────────┐
              │  Validate        │
              │  Credentials     │
              │  (bcrypt verify) │
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │  Check MFA       │
              │  (if enabled)    │
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │  Issue JWT       │
              │  Access + Refresh│
              │  Token Pair      │
              └────────┬────────┘
                       ▼
              Response: { access_token, refresh_token, expires_in }
                       │
                       ▼
              Client stores tokens →
              Access in memory/localStorage
              Refresh in httpOnly cookie
                       │
                       ▼
              All subsequent requests →
              Authorization: Bearer <access_token>
                       │
                       ▼
              FastAPi middleware →
              Token validation on each request
              Auto-refresh on 401
```

### 2.3 Real-time Event Flow (WebSocket)

```
Client connects → ws://host/ws?token=<jwt>
        │
        ▼
┌─────────────────┐
│  Auth Validate   │
│  (token decode)  │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Subscribe to    │
│  Channels        │
│  - alerts:*      │
│  - incidents:*   │
│  - dashboard:*   │
│  - ai:chat       │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Event-Driven    │  ← Redis Pub/Sub
│  Message Push    │
└────────┬────────┘
         ▼
Client receives real-time updates →
No polling needed
```

---

## 3. Technology Justification

### 3.1 Why React?

| Requirement | React Advantage |
|-------------|----------------|
| **Component reusability** | SOC has many repeated UI patterns (data tables, alert cards, metric tiles). React's component model allows building a library of reusable, composable parts. |
| **Type safety with TypeScript** | Critical for a security platform. TypeScript catches type errors at compile time, preventing runtime failures in production. |
| **React Query** | Excellent for data fetching, caching, and background refetching. Aligns perfectly with SOC's data-heavy dashboards. |
| **Ecosystem** | Shadcn UI, Framer Motion, React Flow, Recharts — all mature libraries that accelerate development. |
| **React 18 concurrent features** | Enables smooth UI even during heavy data processing. `useTransition` and `Suspense` for better perceived performance. |
| **Large talent pool** | Faster hiring and onboarding. |
| **Community & support** | Extensive documentation, Stack Overflow, GitHub issues. |

**Alternatives considered:** Vue 3 (smaller ecosystem for enterprise UI), Svelte (too new for enterprise), Angular (more boilerplate, steeper learning curve).

### 3.2 Why FastAPI?

| Requirement | FastAPI Advantage |
|-------------|-------------------|
| **Async by default** | SOC needs to handle hundreds of concurrent connections for log ingestion, WebSocket, and API requests. Async I/O is essential. |
| **Performance** | FastAPI is on par with Node.js and Go for API performance. |
| **Pydantic integration** | Automatic request/response validation with detailed error messages. Critical for a data-heavy SOC platform. |
| **Auto-generated OpenAPI docs** | Interactive Swagger UI for API testing and client generation. |
| **Python ecosystem** | Python is the language of cybersecurity. Libraries for ML (scikit-learn), threat intel (STIX/TAXII), log parsing, and AI (Gemini). |
| **WebSocket support** | Built-in WebSocket support for real-time SOC features. |
| **Dependency injection** | Clean, testable code with FastAPI's `Depends` system. |

**Alternatives considered:** Django REST (too heavy, sync-only by default), Flask (not async, more boilerplate), Node.js/Express (not Python, loses ML/security libs), Go (less ecosystem for security/ML).

### 3.3 Why PostgreSQL?

| Requirement | PostgreSQL Advantage |
|-------------|---------------------|
| **ACID compliance** | Critical for audit trails, incident records, and alert integrity. No data loss. |
| **JSONB support** | Store semi-structured alert data, enrichment results, and raw logs alongside relational data. |
| **Advanced indexing** | GIN/GiST indexes for full-text search on log data, BRIN indexes for time-series data. |
| **Extensions** | `uuid-ossp`, `pg_trgm` (fuzzy search), `pgcrypto`, `pg_stat_statements`. |
| **Partitioning** | Table partitioning by time for log/alert data. Essential for data retention policies. |
| **Replication** | Streaming replication for HA, logical replication for zero-downtime upgrades. |
| **Maturity** | 30+ years of production use. Battle-tested for enterprise workloads. |

**Alternatives considered:** MySQL (weaker JSON support, fewer extensions), MongoDB (no ACID for critical data, eventual consistency), TimescaleDB (PostgreSQL extension, can add later).

### 3.4 Why React Query?

| Requirement | React Query Advantage |
|-------------|----------------------|
| **Automatic caching** | Dashboard data is fetched once and cached. Subsequent visits are instant. |
| **Background refetching** | SOC dashboards need fresh data. React Query refetches on window focus, interval, or mutation. |
| **Pagination support** | Built-in cursor and offset-based pagination for alert lists. |
| **Optimistic updates** | Update alert status instantly in UI while backend processes the change. |
| **DevTools** | Debug data fetching, cache state, and query invalidation during development. |

### 3.5 Why Framer Motion?

| Requirement | Framer Motion Advantage |
|-------------|------------------------|
| **Security theater** | Animated threat indicators, pulsing severity badges, and smooth transitions create urgency and guide operator attention. |
| **Layout animations** | AnimatePresence handles list transitions when alerts arrive/disappear. |
| **Performance** | Uses native CSS animations where possible, falls back to JS. Hardware accelerated. |
| **Declarative API** | Simple `motion.div` syntax. No complex animation state machines. |

---

## 4. Project Structure & Folder Responsibility

### 4.1 Frontend (`sentinelai-frontend/`)

```
sentinelai-frontend/
├── public/                          # Static assets served directly
│   ├── favicon.svg
│   └── robots.txt
├── src/
│   ├── assets/                      # Static resources
│   │   ├── images/                  # PNG, SVG illustrations, logos
│   │   ├── icons/                   # Custom SVG icons (non-Lucide)
│   │   └── fonts/                   # Self-hosted fonts (fallback)
│   ├── components/                  # Reusable UI components
│   │   ├── ui/                      # Shadcn UI primitives (button, card, dialog, etc.)
│   │   │                           # Auto-generated. Do not edit directly.
│   │   ├── auth/                    # Login form, MFA, password reset
│   │   ├── layout/                  # Sidebar, Topbar, Breadcrumbs
│   │   ├── common/                  # Loading, ErrorBoundary, EmptyState, Pagination
│   │   ├── alerts/                  # AlertCard, AlertTable, AlertTimeline
│   │   ├── incidents/              # IncidentCard, IncidentTimeline, IncidentNotes
│   │   ├── threats/                # ThreatIntelCard, IndicatorList
│   │   ├── assets/                 # AssetCard, AssetTable
│   │   ├── dashboard/             # StatCard, ChartWidget, RecentAlerts
│   │   ├── reports/               # ReportCard, ScheduleForm
│   │   ├── ai/                    # AIChat, AnalysisResult, ThreatSummary
│   │   ├── playbooks/            # PlaybookNode, PlaybookEditor
│   │   ├── forms/                 # Reusable form fields, validators
│   │   ├── charts/                # Wrapper components for Recharts
│   │   ├── tables/                # DataTable, ColumnVisibility
│   │   └── modals/                # ConfirmDialog, AlertDetail, IncidentForm
│   ├── contexts/                   # React Context providers
│   │   ├── AuthContext.tsx         # Authentication state
│   │   ├── ThemeContext.tsx        # Dark/light theme
│   │   ├── WebSocketContext.tsx    # Real-time connection
│   │   └── SidebarContext.tsx      # Sidebar collapse state
│   ├── hooks/                      # Custom React hooks
│   │   ├── useAlerts.ts           # Alert data fetching & mutations
│   │   ├── useIncidents.ts        # Incident data fetching & mutations
│   │   ├── useAuth.ts             # Authentication operations
│   │   ├── useDebounce.ts         # Debounced value
│   │   ├── useLocalStorage.ts     # Persistent state
│   │   └── useWebSocket.ts        # WebSocket connection
│   ├── layouts/                    # Page layout wrappers
│   │   ├── AppLayout.tsx          # Authenticated app shell (sidebar + topbar)
│   │   └── AuthLayout.tsx         # Login/registration layout
│   ├── pages/                      # Route-level page components
│   │   ├── auth/                  # Login, ForgotPassword, ResetPassword
│   │   ├── dashboard/             # Main SOC dashboard
│   │   ├── alerts/                # Alert list, alert detail
│   │   ├── incidents/             # Incident list, incident detail
│   │   ├── threats/               # Threat intelligence, threat detail
│   │   ├── assets/                # Asset inventory, asset detail
│   │   ├── reports/               # Reports list, report builder
│   │   ├── settings/              # User settings, organization settings
│   │   ├── ai/                    # AI Security Center
│   │   ├── playbooks/             # Playbook list, playbook editor
│   │   ├── integrations/          # Third-party integrations
│   │   ├── admin/                 # User management, system config
│   │   └── errors/                # 404, 403, 500 pages
│   ├── services/                   # API client layer
│   │   ├── api.ts                 # Axios instance, interceptors
│   │   ├── authService.ts         # Login, logout, refresh, MFA
│   │   ├── alertService.ts        # CRUD alerts, stats, bulk ops
│   │   ├── incidentService.ts     # CRUD incidents, timeline, notes
│   │   ├── threatService.ts       # Threats, indicators, feeds
│   │   ├── assetService.ts        # Assets, inventory
│   │   ├── aiService.ts          # AI chat, analysis, enrichment
│   │   └── reportService.ts      # Reports, schedules
│   ├── store/                      # Zustand state stores
│   │   ├── alertStore.ts          # Alert list, filter, selection
│   │   ├── incidentStore.ts       # Incident list, filter, selection
│   │   ├── uiStore.ts            # Sidebar, modals, notifications
│   │   └── settingsStore.ts      # User preferences
│   ├── types/                      # TypeScript type definitions
│   │   ├── api.ts                 # API response types
│   │   ├── alert.ts               # Alert, AlertFilter, AlertStats
│   │   ├── incident.ts            # Incident, TimelineEntry
│   │   ├── threat.ts              # Threat, Indicator
│   │   ├── asset.ts               # Asset, AssetFilter
│   │   └── user.ts                # User, AuthTokens, Preferences
│   ├── utils/                      # Utility functions
│   │   ├── cn.ts                  # Tailwind class merger (clsx + twMerge)
│   │   ├── date.ts                # Date formatting helpers
│   │   ├── constants.ts           # Severity colors, status colors, config
│   │   └── validators.ts          # Form validation schemas (Zod)
│   ├── styles/
│   │   └── globals.css             # Tailwind directives, CSS variables
│   ├── App.tsx                     # Root component with routing
│   └── main.tsx                    # Application entry point
├── .env.example                    # Environment variable template
├── .eslintrc.cjs                   # ESLint configuration
├── .prettierrc                     # Prettier configuration
├── index.html                      # HTML entry point
├── postcss.config.js               # PostCSS configuration
├── tailwind.config.js              # TailwindCSS configuration
├── tsconfig.json                   # TypeScript configuration
└── vite.config.ts                  # Vite build configuration
```

### 4.2 Backend (`sentinelai-backend/`)

```
sentinelai-backend/
├── alembic/                         # Database migrations
│   ├── versions/                   # Migration files
│   ├── env.py                      # Alembic environment config
│   └── script.py.mako              # Migration template
├── app/
│   ├── api/                        # API entry points
│   │   └── v1/
│   │       └── router.py           # API v1 router aggregation
│   ├── core/                       # Core application components
│   │   ├── config.py              # Settings (Pydantic BaseSettings)
│   │   ├── dependencies.py        # FastAPI dependency injection
│   │   ├── events.py              # Application lifecycle (startup/shutdown)
│   │   ├── exceptions.py          # Custom exception classes
│   │   ├── logging.py             # Structured logging (structlog)
│   │   └── security.py            # JWT, bcrypt, API key generation
│   ├── database/                   # Database connections
│   │   ├── session.py             # SQLAlchemy async engine & session
│   │   ├── base.py                # Declarative base model
│   │   └── redis.py               # Redis client & cache service
│   ├── models/                     # SQLAlchemy ORM models
│   │   ├── user.py                # User model
│   │   ├── alert.py               # Alert model
│   │   ├── incident.py            # Incident model
│   │   ├── threat.py              # Threat & indicator models
│   │   ├── asset.py               # Asset model
│   │   ├── rule.py                # Detection rule model
│   │   ├── playbook.py            # Playbook model
│   │   ├── report.py              # Report & schedule models
│   │   └── audit.py               # Audit log model
│   ├── schemas/                    # Pydantic schemas (request/response)
│   │   ├── base.py                # Base schema, pagination, API response
│   │   ├── user.py                # User schemas
│   │   ├── alert.py               # Alert schemas
│   │   ├── incident.py            # Incident schemas
│   │   ├── threat.py              # Threat schemas
│   │   ├── asset.py               # Asset schemas
│   │   ├── auth.py                # Auth request/response schemas
│   │   ├── detection.py           # Detection rule schemas
│   │   ├── ai.py                  # AI request/response schemas
│   │   └── report.py              # Report schemas
│   ├── services/                   # Business logic layer
│   │   ├── auth_service.py        # Authentication, authorization
│   │   ├── alert_service.py       # Alert management, enrichment
│   │   ├── incident_service.py    # Incident lifecycle management
│   │   ├── threat_service.py      # Threat intelligence processing
│   │   ├── asset_service.py       # Asset management
│   │   ├── detection_service.py   # Detection engine
│   │   ├── ai_service.py          # Gemini AI integration
│   │   ├── report_service.py      # Report generation
│   │   ├── notification_service.py # Alerts, email, webhook
│   │   └── integration_service.py # Third-party integrations
│   ├── routers/                    # FastAPI route definitions
│   │   ├── auth.py                # Authentication endpoints
│   │   ├── alerts.py              # Alert CRUD endpoints
│   │   ├── incidents.py           # Incident endpoints
│   │   ├── threats.py             # Threat intelligence endpoints
│   │   ├── assets.py              # Asset endpoints
│   │   ├── detection.py           # Detection rule endpoints
│   │   ├── ai.py                  # AI endpoints
│   │   ├── reports.py             # Report endpoints
│   │   ├── playbooks.py           # Playbook endpoints
│   │   ├── integrations.py        # Integration endpoints
│   │   ├── admin.py               # Admin endpoints
│   │   ├── webhooks.py            # Webhook receivers
│   │   └── analytics.py           # Analytics endpoints
│   ├── middleware/                  # ASGI middleware
│   │   ├── audit.py               # Audit logging middleware
│   │   ├── request_id.py          # Request ID tracking
│   │   └── security.py            # Security headers middleware
│   ├── parsers/                    # Log parsing engines
│   │   ├── base.py                # Abstract parser interface
│   │   ├── syslog_parser.py       # RFC 5424/3164 syslog
│   │   ├── json_parser.py         # JSON log parsing
│   │   ├── xml_parser.py          # XML log parsing
│   │   ├── evtx_parser.py         # Windows Event Log (EVTX)
│   │   ├── csv_parser.py          # CSV log parsing
│   │   └── pcap_parser.py         # PCAP/PCAPng parsing
│   ├── detection/                  # Detection engine
│   │   ├── engine.py              # Core detection engine
│   │   ├── sigma_engine.py        # Sigma rule engine
│   │   ├── correlation.py         # Event correlation
│   │   └── rules/                 # Built-in detection rules
│   ├── incident/                   # Incident response
│   │   ├── response.py            # Automated response actions
│   │   ├── playbook_executor.py   # Playbook execution engine
│   │   └── templates/             # Incident response templates
│   ├── ai/                         # AI integration
│   │   ├── gemini_client.py       # Gemini API client
│   │   ├── threat_analyzer.py     # AI threat analysis
│   │   ├── log_analyzer.py        # AI log pattern analysis
│   │   ├── summarizer.py          # Alert/incident summarization
│   │   ├── chatbot.py             # Security assistant chatbot
│   │   └── embeddings.py          # Vector embeddings for semantic search
│   ├── reports/                    # Report engine
│   │   ├── generator.py           # Report generation
│   │   ├── templates/             # Report templates (Jinja2)
│   │   └── exporters/             # PDF, CSV, JSON, HTML, XLSX
│   └── utils/                      # Shared utilities
│       ├── pagination.py          # Pagination helpers
│       ├── serialization.py       # Custom JSON encoders
│       ├── validators.py          # Input validation helpers
│       └── file_utils.py          # File handling utilities
├── tests/                          # Test suite
│   ├── api/                       # API integration tests
│   ├── core/                      # Core component tests
│   ├── services/                  # Service layer tests
│   ├── detection/                 # Detection engine tests
│   ├── ai/                        # AI integration tests
│   └── parsers/                   # Parser tests
├── .env.example                    # Environment variables template
├── alembic.ini                     # Alembic configuration
├── Dockerfile                      # Docker image definition
├── pyproject.toml                  # Python project configuration
└── requirements.txt               # Python dependencies
```

### 4.3 Infrastructure (`infra/`)

```
infra/
├── docker/
│   ├── frontend/
│   │   └── nginx.conf             # Nginx config for SPA
│   ├── backend/
│   │   └── gunicorn.conf.py       # Gunicorn config for production
│   ├── nginx/
│   │   └── nginx.conf             # Main Nginx reverse proxy config
│   └── postgres/
│       └── init.sql               # Database initialization script
├── k8s/                            # Kubernetes manifests (future)
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── configmap.yaml
└── terraform/                      # Infrastructure as Code (future)
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

---

## 5. Coding Conventions

### 5.1 General

- **All code is written in English** (comments, variables, commits).
- **No commented-out code** in production branches.
- **Maximum line length:** 100 characters (Python), 100 characters (TypeScript).
- **Use 2 spaces for indentation** (TypeScript, YAML, JSON).
- **Use 4 spaces for indentation** (Python).
- **Semicolons required** (TypeScript).
- **Trailing commas** where valid (TypeScript/Python).

### 5.2 Python (Backend)

- **Follow PEP 8** with Black formatter (100 char line length).
- **Type hints required** on all functions and methods.
- **Docstrings**: Google style for public APIs, optional for private.
- **Async/await** for all I/O operations. No blocking calls.
- **Use `structlog`** for structured logging. No `print()`.
- **No wildcard imports** (`from module import *`).
- **Relative imports** within the `app` package.
- **Raise custom exceptions** (`SentinelAIException` subclasses) instead of generic `HTTPException`.
- **Schema validation** at service layer, not router layer.
- **Database sessions** injected via FastAPI `Depends`.

### 5.3 TypeScript/React (Frontend)

- **Strict TypeScript** enabled. No `any` without explicit justification.
- **Prefer interfaces over types** for object shapes.
- **React components** as functions, not classes. Use hooks.
- **File naming**: PascalCase for components (`AlertCard.tsx`), camelCase for hooks (`useAlerts.ts`).
- **One component per file**, except for small closely related components.
- **Named exports** for components, utilities, and hooks. No default exports except page components.
- **Import order**: React → third-party → internal → styles.
- **No prop drilling**. Use Context or Zustand for shared state.
- **All data fetching** through React Query. No `useEffect` for API calls.

### 5.4 CSS/Tailwind

- **Use Tailwind utility classes** exclusively. No custom CSS unless absolutely necessary.
- **Custom styles** go in `globals.css` using Tailwind's `@layer` directive.
- **Use `cn()` utility** for conditional class merging.
- **Color scheme** defined in `tailwind.config.js` as CSS variables.
- **Dark mode** is default and required. Light mode is secondary.

---

## 6. Naming Conventions

### 6.1 Backend (Python)

| Category | Convention | Example |
|----------|-----------|---------|
| Files & directories | `snake_case` | `alert_service.py` |
| Classes | `PascalCase` | `AlertService`, `IncidentModel` |
| Functions & methods | `snake_case` | `get_alerts()`, `create_incident()` |
| Variables | `snake_case` | `user_id`, `alert_count` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_LOGIN_ATTEMPTS` |
| Private functions | `_prefix` | `_validate_schema()` |
| Async functions | Include `async def` | `async def process_alert()` |
| SQLAlchemy models | `PascalCase` | `User`, `Alert`, `Incident` |
| Pydantic schemas | `PascalCase` | `AlertCreate`, `UserResponse` |
| API route files | `snake_case` | `auth.py`, `incidents.py` |

### 6.2 Frontend (TypeScript/React)

| Category | Convention | Example |
|----------|-----------|---------|
| Files (components) | `PascalCase.tsx` | `AlertCard.tsx` |
| Files (hooks) | `camelCase.ts` | `useAlerts.ts` |
| Files (utilities) | `camelCase.ts` | `dateUtils.ts` |
| Files (services) | `camelCase.ts` | `alertService.ts` |
| React components | `PascalCase` | `function AlertCard()` |
| Hooks | `camelCase` prefixed with `use` | `function useAlerts()` |
| Functions | `camelCase` | `formatDate()`, `handleSubmit()` |
| Variables | `camelCase` | `userData`, `alertList` |
| Constants | `UPPER_SNAKE_CASE` | `SEVERITY_COLORS` |
| Types/Interfaces | `PascalCase` | `interface AlertProps` |
| Enums | `PascalCase` | `enum SeverityLevel` |
| CSS classes | Tailwind utility classes | `flex`, `items-center` |
| Route paths | `kebab-case` | `/incident-detail` |
| Environment variables | `UPPER_SNAKE_CASE` | `VITE_API_BASE_URL` |

---

## 7. API Conventions

### 7.1 General

| Convention | Standard |
|-----------|----------|
| **Base URL** | `/api/v1` |
| **Protocol** | HTTPS (production), HTTP (development) |
| **Content-Type** | `application/json` |
| **Authentication** | `Authorization: Bearer <jwt>` or `X-API-Key: <key>` |
| **Request ID** | `X-Request-ID` header (auto-generated if missing) |
| **Rate limiting** | `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers |

### 7.2 URL Structure

```
/api/v1/{resource}
/api/v1/{resource}/{id}
/api/v1/{resource}/{id}/{sub-resource}
```

### 7.3 HTTP Methods

| Method | Action | Idempotent | Safe |
|--------|--------|-----------|------|
| `GET` | Retrieve resource(s) | Yes | Yes |
| `POST` | Create resource | No | No |
| `PUT` | Full update | Yes | No |
| `PATCH` | Partial update | No | No |
| `DELETE` | Delete resource | Yes | No |

### 7.4 Response Format

**Success:**
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... },
  "errors": null
}
```

**Paginated:**
```json
{
  "success": true,
  "message": "Alerts retrieved successfully",
  "data": {
    "items": [ ... ],
    "total": 1042,
    "page": 1,
    "pageSize": 25,
    "totalPages": 42,
    "hasNext": true,
    "hasPrev": false
  }
}
```

**Error:**
```json
{
  "success": false,
  "errorCode": "VALIDATION_ERROR",
  "message": "Invalid input data",
  "details": {
    "field": "email",
    "reason": "Invalid email format"
  },
  "requestId": "abc-123-def-456"
}
```

### 7.5 HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| `200` | OK | Successful GET, PUT, PATCH |
| `201` | Created | Successful POST |
| `204` | No Content | Successful DELETE |
| `400` | Bad Request | Validation errors, malformed input |
| `401` | Unauthorized | Missing/invalid authentication |
| `403` | Forbidden | Authenticated but not authorized |
| `404` | Not Found | Resource doesn't exist |
| `409` | Conflict | Duplicate resource |
| `422` | Unprocessable Entity | Schema validation failure |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Unhandled server error |
| `503` | Service Unavailable | Dependency failure (DB, Redis, AI) |

### 7.6 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| **Auth** | | |
| POST | `/auth/login` | User login |
| POST | `/auth/logout` | User logout |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/forgot-password` | Request password reset |
| POST | `/auth/reset-password` | Reset password with token |
| GET | `/auth/profile` | Get current user profile |
| PATCH | `/auth/profile` | Update profile |
| POST | `/auth/mfa/setup` | Setup MFA |
| POST | `/auth/mfa/verify` | Verify MFA code |
| **Alerts** | | |
| GET | `/alerts` | List alerts (paginated, filtered) |
| GET | `/alerts/{id}` | Get alert detail |
| PATCH | `/alerts/{id}/status` | Update alert status |
| POST | `/alerts/{id}/assign` | Assign to incident |
| GET | `/alerts/stats` | Get alert statistics |
| POST | `/alerts/bulk/status` | Bulk status update |
| DELETE | `/alerts/{id}` | Delete alert |
| **Incidents** | | |
| GET | `/incidents` | List incidents |
| POST | `/incidents` | Create incident from alerts |
| GET | `/incidents/{id}` | Get incident detail |
| PATCH | `/incidents/{id}` | Update incident |
| POST | `/incidents/{id}/notes` | Add note |
| POST | `/incidents/{id}/timeline` | Add timeline entry |
| PATCH | `/incidents/{id}/status` | Update status |
| POST | `/incidents/{id}/assign` | Assign analyst |
| **Threats** | | |
| GET | `/threats` | List threats |
| GET | `/threats/{id}` | Get threat detail |
| GET | `/threats/indicators` | List IOCs |
| GET | `/threats/feeds` | List threat intel feeds |
| POST | `/threats/feeds` | Add threat intel feed |
| **AI** | | |
| POST | `/ai/analyze` | Analyze alert/incident |
| POST | `/ai/chat` | Chat with AI assistant |
| POST | `/ai/summarize` | Summarize incident |
| POST | `/ai/enrich` | Enrich indicator |
| POST | `/ai/generate-rules` | Generate detection rules |
| GET | `/ai/models` | List AI models |
| **Reports** | | |
| GET | `/reports` | List reports |
| POST | `/reports/generate` | Generate report |
| GET | `/reports/{id}` | Download report |
| GET | `/reports/schedules` | List report schedules |
| POST | `/reports/schedules` | Create schedule |
| PATCH | `/reports/schedules/{id}` | Update schedule |
| DELETE | `/reports/schedules/{id}` | Delete schedule |
| **Detection** | | |
| GET | `/detection/rules` | List detection rules |
| POST | `/detection/rules` | Create rule |
| PATCH | `/detection/rules/{id}` | Update rule |
| DELETE | `/detection/rules/{id}` | Delete rule |
| POST | `/detection/rules/test` | Test rule against sample |
| GET | `/detection/mitre` | Get MITRE ATT&CK matrix |
| **Assets** | | |
| GET | `/assets` | List assets |
| GET | `/assets/{id}` | Get asset detail |
| PATCH | `/assets/{id}` | Update asset |
| GET | `/assets/stats` | Asset statistics |
| **Playbooks** | | |
| GET | `/playbooks` | List playbooks |
| POST | `/playbooks` | Create playbook |
| GET | `/playbooks/{id}` | Get playbook |
| PATCH | `/playbooks/{id}` | Update playbook |
| DELETE | `/playbooks/{id}` | Delete playbook |
| POST | `/playbooks/{id}/execute` | Execute playbook |
| **Integrations** | | |
| GET | `/integrations` | List integrations |
| POST | `/integrations` | Add integration |
| PATCH | `/integrations/{id}` | Update integration |
| DELETE | `/integrations/{id}` | Remove integration |
| POST | `/integrations/{id}/test` | Test connection |
| **Admin** | | |
| GET | `/admin/users` | List users |
| POST | `/admin/users` | Create user |
| PATCH | `/admin/users/{id}` | Update user |
| DELETE | `/admin/users/{id}` | Delete user |
| GET | `/admin/audit-logs` | View audit logs |
| GET | `/admin/system-health` | System health status |
| **Webhooks** | | |
| POST | `/webhooks/siem` | SIEM event ingestion |
| POST | `/webhooks/cloud` | Cloud provider events |
| POST | `/webhooks/generic` | Generic webhook receiver |
| **Analytics** | | |
| GET | `/analytics/dashboard` | Dashboard metrics |
| GET | `/analytics/timeline` | Event timeline data |
| GET | `/analytics/heatmap` | Alert heatmap data |

---

## 8. Development Setup

### 8.1 Prerequisites

- Node.js 22+
- Python 3.12+
- PostgreSQL 17+
- Redis 7+
- Docker & Docker Compose (optional, for containerized setup)
- Git

### 8.2 Local Development (Without Docker)

**Frontend:**
```bash
cd sentinelai-frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start development server
npm run dev
# Opens at http://localhost:3000
```

**Backend:**
```bash
cd sentinelai-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# API at http://localhost:8000
# Docs at http://localhost:8000/api/v1/docs
```

### 8.3 Docker Development

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f backend frontend

# Rebuild specific service
docker compose build backend
docker compose up -d backend

# Run migrations
docker compose exec backend alembic upgrade head

# Create test data
docker compose exec backend python scripts/seed.py

# Stop all services
docker compose down

# Destroy volumes (reset data)
docker compose down -v
```

### 8.4 Development Scripts

| Script | Purpose |
|--------|---------|
| `npm run dev` | Start Vite dev server |
| `npm run build` | Production build |
| `npm run lint` | Lint all files |
| `npm run format` | Format all files |
| `npm run typecheck` | TypeScript type checking |
| `npm test` | Run frontend tests |
| `uvicorn app.main:app --reload` | Start backend dev server |
| `alembic upgrade head` | Run database migrations |
| `alembic revision --autogenerate -m "desc"` | Create new migration |
| `pytest` | Run backend tests |
| `ruff .` | Lint Python files |
| `black .` | Format Python files |

---

## 9. Environment Variables

### 9.1 Frontend (`sentinelai-frontend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_APP_NAME` | No | `SentinelAI` | Application display name |
| `VITE_APP_ENV` | No | `development` | Environment name |
| `VITE_API_BASE_URL` | Yes | — | Backend API URL |
| `VITE_API_PREFIX` | No | `/api/v1` | API version prefix |
| `VITE_WS_URL` | No | — | WebSocket URL |
| `VITE_API_TIMEOUT` | No | `30000` | Request timeout (ms) |
| `VITE_AUTH_TOKEN_KEY` | No | `sentinelai_auth_token` | localStorage key for token |
| `VITE_AUTH_REFRESH_KEY` | No | `sentinelai_refresh_token` | localStorage key for refresh |
| `VITE_SENTRY_DSN` | No | — | Sentry error tracking DSN |
| `VITE_FEATURE_AI_ASSISTANT` | No | `true` | Enable AI features |
| `VITE_DEFAULT_THEME` | No | `dark` | Default theme |

### 9.2 Backend (`sentinelai-backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | **Yes** | — | JWT signing key (min 32 chars) |
| `POSTGRES_SERVER` | Yes | `localhost` | PostgreSQL host |
| `POSTGRES_PORT` | No | `5432` | PostgreSQL port |
| `POSTGRES_USER` | Yes | `sentinelai` | Database user |
| `POSTGRES_PASSWORD` | **Yes** | — | Database password |
| `POSTGRES_DB` | No | `sentinelai` | Database name |
| `REDIS_HOST` | No | `localhost` | Redis host |
| `REDIS_PORT` | No | `6379` | Redis port |
| `GEMINI_API_KEY` | **Yes** | — | Google Gemini API key |
| `ENVIRONMENT` | No | `development` | Runtime environment |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Allowed CORS origins |
| `SMTP_HOST` | No | — | Email server host |
| `SMTP_USER` | No | — | Email username |
| `SMTP_PASSWORD` | No | — | Email password |
| `SENTRY_DSN` | No | — | Sentry DSN for error tracking |

> **Security:** Never commit `.env` files. Use `.env.example` as a template. Rotate secrets regularly in production.

---

## 10. Scalability Considerations

### 10.1 Horizontal Scaling

| Component | Strategy |
|-----------|----------|
| **FastAPI** | Stateless. Scale behind Nginx/ALB with multiple workers (`gunicorn -w 4`). Each worker handles concurrent requests via async. |
| **Celery Workers** | Multiple worker instances consuming from same Redis queue. Different queues for different priorities (detection, reports, notifications). |
| **PostgreSQL** | Read replicas for dashboard queries. Connection pooling with PgBouncer. Partitioning by time for event/alert tables. |
| **Redis** | Redis Cluster for cache sharding. Sentinel for high availability. |
| **Nginx** | Multiple upstream backend servers. Round-robin or least-connections load balancing. |

### 10.2 Database Optimization

- **Table partitioning** by `created_at` for alerts (monthly), events (daily), audit logs (monthly).
- **Composite indexes** on frequently queried columns: `(severity, status, created_at)`.
- **Partial indexes** for active alerts: `WHERE status IN ('new', 'acknowledged', 'investigating')`.
- **BRIN indexes** for time-series data (10x smaller than B-tree for sequential data).
- **Connection pooling** with `pgbouncer` (transaction mode) for efficient connection reuse.
- **Read replicas** for reporting and analytics queries.
- **Materialized views** for dashboard metrics, refreshed every 30 seconds.

### 10.3 Performance Targets

| Metric | Target |
|--------|--------|
| API response time (p95) | < 200ms |
| Alert ingestion | > 100,000 events/sec |
| Dashboard load time | < 2 seconds |
| Report generation | < 60 seconds |
| AI analysis | < 5 seconds |
| WebSocket latency | < 100ms |
| Concurrent users | 500+ |
| Uptime SLA | 99.9% |

### 10.4 Caching Strategy

| Data | Cache | TTL | Invalidation |
|------|-------|-----|-------------|
| Dashboard stats | Redis | 30s | Time-based |
| Threat intel | Redis | 5min | On feed update |
| User sessions | Redis | Until logout | Session expiry |
| Detection rules | Local memory | 60s | Polling |
| MITRE ATT&CK data | Redis | 1h | On cache miss |
| API rate limits | Redis | Per window | Sliding window |
| AI responses | Redis | 1h | On cache miss |

---

## 11. Security Considerations

### 11.1 Authentication & Authorization

- **JWT** with short-lived access tokens (30 min) and long-lived refresh tokens (7 days).
- **Refresh token rotation** — old refresh token invalidated on use.
- **MFA support** via TOTP (time-based one-time passwords).
- **bcrypt** with 12 rounds for password hashing.
- **Account lockout** after 5 failed attempts (15-minute lockout).
- **API key authentication** for machine-to-machine communication.
- **RBAC** with three roles: Admin, Analyst, Viewer.
- **Audit trail** for all authentication events (login, logout, failed attempts).

### 11.2 Network Security

- **HTTPS only** in production. HSTS header set.
- **Nginx reverse proxy** terminates SSL. Backend runs on internal network.
- **CORS** restricted to specific origins.
- **Trusted Host middleware** prevents host header injection.
- **Rate limiting** at both Nginx (per IP) and FastAPI (per user/token).

### 11.3 Application Security

| Measure | Implementation |
|---------|---------------|
| **SQL Injection** | SQLAlchemy ORM with parameterized queries. No raw SQL. |
| **XSS** | React's JSX auto-escapes output. CSP header restricts script sources. |
| **CSRF** | `X-CSRF-Token` header validation for state-changing requests. SameSite cookies. |
| **SSRF** | URL validation and allowlisting for webhooks and threat intel fetches. |
| **NoSQL Injection** | Strict Pydantic validation on all inputs. |
| **Path Traversal** | File path sanitization for log uploads. `os.path.basename` restriction. |
| **DoS** | Rate limiting, request size limits (100MB upload cap), timeout enforcement. |
| **Insecure Deserialization** | Use Pydantic for deserialization. No `pickle` or `eval()`. |

### 11.4 Data Security

- **Encryption at rest:** PostgreSQL TDE (if available) or application-level encryption for sensitive fields (PII, credentials).
- **Encryption in transit:** TLS 1.3 for all communications.
- **Data masking:** Sensitive fields masked in API responses based on user role.
- **Data retention:** Automated cleanup of logs and alerts after retention period.
- **Audit logging:** All access to sensitive resources logged with user, action, timestamp.

### 11.5 Secrets Management

| Secret | Storage |
|--------|---------|
| Database passwords | Environment variables / Vault |
| JWT signing keys | Environment variables / Vault |
| API keys (Gemini, etc.) | Environment variables / Vault |
| TLS certificates | File system / cert-manager |
| Encryption keys | Hardware Security Module (HSM) / Vault |

---

## 12. Future Expansion

### 12.1 Planned Modules

| Module | Description | Priority |
|--------|-------------|----------|
| **Module 1: Auth & RBAC** | User registration, login, MFA, role management, SSO (OAuth2, SAML) | P0 |
| **Module 2: Alert Management** | Alert ingestion, triage, enrichment, deduplication, correlation | P0 |
| **Module 3: Detection Engine** | Sigma rule engine, custom rules, YARA, ML-based anomaly detection | P0 |
| **Module 4: Incident Response** | Incident lifecycle, playbook automation, containment actions, reporting | P0 |
| **Module 5: Threat Intelligence** | MITRE ATT&CK mapping, STIX/TAXII feeds, IOC management, enrichment | P0 |
| **Module 6: AI Security Center** | Gemini-powered analysis, chat assistant, summarization, rule generation | P0 |
| **Module 7: Reporting & Analytics** | Scheduled reports, custom dashboards, compliance reporting, data export | P1 |
| **Module 8: Integrations** | SIEM connectors, cloud provider integration, webhook system, API marketplace | P1 |
| **Module 9: Compliance & Audit** | SOC 2, ISO 27001, HIPAA, PCI DSS compliance modules, audit trails | P1 |
| **Module 10: Advanced Analytics** | User behavior analytics (UBA), network traffic analysis, SOAR | P2 |

### 12.2 Technical Expansions

| Area | Future Enhancement |
|------|-------------------|
| **Search** | Elasticsearch integration for full-text search on logs and alerts |
| **Streaming** | Kafka for event streaming between services |
| **ML Pipeline** | Dedicated ML training pipeline for anomaly detection models |
| **Graph Database** | Neo4j for entity relationship graphs (threat mapping, asset dependencies) |
| **Service Mesh** | Istio for advanced traffic management, mTLS, observability |
| **Multi-tenancy** | Organization-level isolation for MSSP use case |
| **Chaos Engineering** | LitmusChaos for resilience testing |
| **Canary Deployments** | Argo Rollouts for progressive delivery |
| **eBPF** | Cilium for network security observability |
| **GenAI Agents** | Autonomous AI agents for incident response, threat hunting |
| **Cloud Native** | Full Kubernetes deployment with Helm charts |
| **Observability** | OpenTelemetry for distributed tracing, Grafana dashboards |
| **Mobile App** | React Native app for on-call alerts and quick actions |

### 12.3 Architectural Improvements

```
Current: Monolith (FastAPI) with background workers
                 │
                 ▼
    Phase 1: Modular monolith with clear bounded contexts
                 │
                 ▼
    Phase 2: Domain services (auth, detection, ai, reports) as separate services
                 │
                 ▼
    Phase 3: Event-driven architecture with Kafka
                 │
                 ▼
    Phase 4: Full microservices with service mesh
```

---

*This document is confidential and proprietary. Unauthorized distribution is prohibited.*

**SentinelAI** — *Your AI-Powered SOC Platform*
