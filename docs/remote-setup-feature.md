# Feature: Custom Test Orchestration System mit Remote Workers

**Status:** Konzept / Planung
**Priorität:** Hoch
**Aufwand:** ~42 Stunden (Initial Development) + 2-4h/Monat Wartung
**Kosten:** €0/Monat (nutzt vorhandenes HostEurope Hosting)

---

## Executive Summary

Ein custom-entwickeltes, zentrales Test-Orchestrierungs-System, das es ermöglicht:
- Beliebig viele Test-Rechner (Laptops, Desktops, VMs) als Worker zu registrieren
- Tests automatisch und intelligent auf verfügbare Worker zu verteilen
- Via Web-Dashboard Tests zu starten, zu überwachen und Ergebnisse zu analysieren
- **100+ parallele Tests** gleichzeitig auszuführen (abhängig von verfügbaren Workern)

Das System nutzt das bereits vorhandene HostEurope Webhosting (PHP + MySQL) als Coordinator und Worker-Agents (Node.js) auf allen Test-Rechnern.

---

## Skalierbarkeits-Berechnung

### Beispiel-Szenarien

| Szenario | Anzahl Worker | Tests/Worker parallel | **Gesamt parallele Tests** | Hardware |
|----------|---------------|----------------------|---------------------------|----------|
| **Klein** | 3 Worker | 4 parallel | **12 gleichzeitig** | 3× Laptops |
| **Mittel** | 10 Worker | 8 parallel | **80 gleichzeitig** | 5× Laptops + 5× Desktops |
| **Groß** | 20 Worker | 10 parallel | **200 gleichzeitig** | 10× Desktops + 10× VMs |
| **Enterprise** | 50 Worker | 20 parallel | **1.000 gleichzeitig** | 50× Cloud VMs (spot instances) |

### Konkrete Rechnung für Globetrotter Setup

Angenommen:
- **5 Team-Laptops** (während Arbeit verfügbar)
- **3 Team-Desktops** (24/7 verfügbar)
- **2 alte Rechner** (dedicated Test-Maschinen)
- **5 AWS EC2 Spot Instances** (bei Bedarf, ~$0.02/h)

```
Tagsüber (Mo-Fr 9-17 Uhr):
= 5 Laptops × 6 parallel + 3 Desktops × 10 parallel + 2 dedicated × 15 parallel
= 30 + 30 + 30
= 90 parallele Tests gleichzeitig

Nachts (automatisiert):
= 3 Desktops × 10 parallel + 2 dedicated × 15 parallel + 5 EC2 × 20 parallel
= 30 + 30 + 100
= 160 parallele Tests gleichzeitig

Bei Bedarf (Peak-Load-Tests):
= Alle oben + 20 zusätzliche EC2 Spot Instances × 20 parallel
= 160 + 400
= 560 parallele Tests gleichzeitig
```

**Kosten für Peak-Szenario:**
- 25× AWS EC2 t3.xlarge Spot Instances für 2 Stunden = ~25 × $0.02 × 2h = **$1 pro Peak-Test-Run**

---

## Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────────────────┐
│                    HOSTEUROPE WEBHOSTING                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     WEB FRONTEND                              │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │   │
│  │  │ Dashboard  │  │ Test-Runs  │  │ Analytics  │             │   │
│  │  │ index.php  │  │ runs.php   │  │ stats.php  │             │   │
│  │  └────────────┘  └────────────┘  └────────────┘             │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │   │
│  │  │ Workers    │  │ Logs       │  │ Settings   │             │   │
│  │  │ workers.php│  │ logs.php   │  │ config.php │             │   │
│  │  └────────────┘  └────────────┘  └────────────┘             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                      REST API LAYER                           │   │
│  │  ┌─────────────────────────────────────────────────────────┐ │   │
│  │  │  Worker Management API                                   │ │   │
│  │  │  POST   /api/v1/workers/register                        │ │   │
│  │  │  GET    /api/v1/workers/{id}                            │ │   │
│  │  │  PUT    /api/v1/workers/{id}/heartbeat                  │ │   │
│  │  │  DELETE /api/v1/workers/{id}                            │ │   │
│  │  │  GET    /api/v1/workers (list all)                      │ │   │
│  │  └─────────────────────────────────────────────────────────┘ │   │
│  │  ┌─────────────────────────────────────────────────────────┐ │   │
│  │  │  Task Management API                                     │ │   │
│  │  │  GET    /api/v1/tasks/next (worker polls for task)      │ │   │
│  │  │  POST   /api/v1/tasks/{id}/claim                        │ │   │
│  │  │  POST   /api/v1/tasks/{id}/start                        │ │   │
│  │  │  POST   /api/v1/tasks/{id}/complete                     │ │   │
│  │  │  POST   /api/v1/tasks/{id}/fail                         │ │   │
│  │  │  POST   /api/v1/tasks/{id}/heartbeat                    │ │   │
│  │  └─────────────────────────────────────────────────────────┘ │   │
│  │  ┌─────────────────────────────────────────────────────────┐ │   │
│  │  │  Test Run Management API                                 │ │   │
│  │  │  POST   /api/v1/test-runs/create                        │ │   │
│  │  │  GET    /api/v1/test-runs/{id}                          │ │   │
│  │  │  GET    /api/v1/test-runs/{id}/progress                 │ │   │
│  │  │  POST   /api/v1/test-runs/{id}/cancel                   │ │   │
│  │  │  GET    /api/v1/test-runs (list + filter)               │ │   │
│  │  └─────────────────────────────────────────────────────────┘ │   │
│  │  ┌─────────────────────────────────────────────────────────┐ │   │
│  │  │  Results & Reporting API                                 │ │   │
│  │  │  POST   /api/v1/results/submit                          │ │   │
│  │  │  GET    /api/v1/results/{test_run_id}                   │ │   │
│  │  │  GET    /api/v1/results/{test_run_id}/download          │ │   │
│  │  │  GET    /api/v1/metrics/performance                     │ │   │
│  │  │  GET    /api/v1/metrics/trends                          │ │   │
│  │  └─────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    BUSINESS LOGIC LAYER                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │   │
│  │  │  Scheduler   │  │ LoadBalancer │  │ HealthCheck  │       │   │
│  │  │  (Cron)      │  │ (Task→Worker)│  │ (Workers)    │       │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │   │
│  │  │ Aggregator   │  │ Notifier     │  │ Cleaner      │       │   │
│  │  │ (Merge Rslts)│  │ (Alerts)     │  │ (Old Data)   │       │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘       │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                      DATABASE LAYER                           │   │
│  │  MySQL 8.0+ (InnoDB)                                          │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │   │
│  │  │ workers  │ │test_runs │ │  tasks   │ │ results  │        │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │   │
│  │  │  logs    │ │  metrics │ │  alerts  │ │  config  │        │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    FILE STORAGE LAYER                         │   │
│  │  - HTML Reports: /reports/{test_run_id}/{task_id}/           │   │
│  │  - Screenshots:  /screenshots/{test_run_id}/{task_id}/       │   │
│  │  - Videos:       /videos/{test_run_id}/{task_id}/            │   │
│  │  - Traces:       /traces/{test_run_id}/{task_id}/            │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              ▲ HTTPS REST API
                              │ (Polling every 10-60s)
                              │
      ┌───────────────────────┼───────────────────────────────┐
      │                       │                               │
┌─────▼───────┐      ┌────────▼────────┐           ┌────────▼────────┐
│  Worker 1   │      │   Worker 2      │    ...    │   Worker N      │
│  (Laptop)   │      │   (Desktop)     │           │   (EC2 Spot)    │
├─────────────┤      ├─────────────────┤           ├─────────────────┤
│ Node.js     │      │ Node.js Agent   │           │ Node.js Agent   │
│ Agent       │      │                 │           │                 │
│             │      │                 │           │                 │
│ Capabilities│      │ Capabilities:   │           │ Capabilities:   │
│ - 4 parallel│      │ - 10 parallel   │           │ - 20 parallel   │
│ - Chromium  │      │ - All browsers  │           │ - All browsers  │
│ - 8GB RAM   │      │ - 32GB RAM      │           │ - 64GB RAM      │
│             │      │                 │           │                 │
│ Status:     │      │ Status:         │           │ Status:         │
│ BUSY (3/4)  │      │ IDLE (0/10)     │           │ BUSY (18/20)    │
│             │      │                 │           │                 │
│ Current:    │      │ Waiting for     │           │ Running:        │
│ ├─ Task 42  │      │ next task...    │           │ ├─ Task 78-95   │
│ ├─ Task 43  │      │                 │           │ └─ 18 tasks     │
│ └─ Task 44  │      │                 │           │                 │
└─────────────┘      └─────────────────┘           └─────────────────┘
```

---

## Komponenten-Übersicht

### 1. HostEurope Coordinator (PHP + MySQL)

**Verantwortlichkeiten:**
- Worker-Registration & Health-Monitoring
- Task-Scheduling & Load-Balancing
- Test-Run Management
- Ergebnis-Aggregation
- Web-Dashboard für Benutzer
- REST API für Workers

**Technologie-Stack:**
- PHP 8.0+ (Backend)
- MySQL 8.0+ (Datenbank)
- Bootstrap 5 / Tailwind CSS (Frontend)
- Chart.js (Visualisierungen)
- Apache/Nginx (Webserver)

### 2. Worker Agent (Node.js)

**Verantwortlichkeiten:**
- Registrierung beim Coordinator
- Polling für neue Tasks (alle 10-60 Sekunden)
- Playwright-Tests ausführen
- Ergebnisse zurückmelden
- System-Metriken sammeln (CPU, RAM)
- Heartbeat senden

**Technologie-Stack:**
- Node.js 20+
- Axios (HTTP Client)
- Playwright (Test-Execution)
- OS-Modul (System-Metriken)

### 3. Datenbank-Schema

Siehe ausführliches Schema in `schema-detailed.sql` (unten)

**Haupttabellen:**
- `workers` - Registrierte Test-Rechner
- `test_runs` - Test-Sessions
- `tasks` - Einzelne Test-Shards
- `test_results` - Detaillierte Ergebnisse
- `worker_logs` - Heartbeat & Event-Log
- `performance_metrics` - Trend-Daten
- `alerts` - Alert-Definitionen
- `config` - System-Konfiguration

---

## Umsetzungsschritte (Detailliert)

| Phase | Schritt | Beschreibung | Technologie | Aufwand | Dateien |
|-------|---------|--------------|-------------|---------|---------|
| **Phase 1: Foundation** | 1.1 Datenbank-Schema | MySQL-Tabellen, Views, Stored Procedures, Triggers | MySQL | 2h | `schema-detailed.sql` |
| | 1.2 API Config | Datenbank-Verbindung, Auth-Helper | PHP | 1h | `api/config.php` |
| | 1.3 Load Balancer | Task-Verteilungs-Logik | PHP | 4h | `api/lib/LoadBalancer.php` |
| **Phase 2: API** | 2.1 Worker Management | Register, Heartbeat, Status | PHP | 4h | `api/v1/workers/*.php` |
| | 2.2 Task Management | Next Task, Claim, Complete, Fail | PHP | 4h | `api/v1/tasks/*.php` |
| | 2.3 Test Run Management | Create, List, Progress, Cancel | PHP | 3h | `api/v1/test-runs/*.php` |
| | 2.4 Results API | Submit, Download, Metrics | PHP | 3h | `api/v1/results/*.php` |
| **Phase 3: Worker Agent** | 3.1 Agent Core | Registration, Polling, Heartbeat | Node.js | 4h | `agent/worker.js` |
| | 3.2 Task Execution | Playwright-Integration | Node.js | 3h | `agent/executor.js` |
| | 3.3 Results Upload | Ergebnisse & Artifacts hochladen | Node.js | 2h | `agent/uploader.js` |
| **Phase 4: Web UI** | 4.1 Dashboard | Übersicht Worker & Test-Runs | PHP/HTML | 4h | `index.php` |
| | 4.2 Worker View | Worker-Details, Logs | PHP/HTML | 2h | `workers.php` |
| | 4.3 Test Run Details | Fortschritt, Ergebnisse | PHP/HTML | 3h | `runs.php` |
| | 4.4 Analytics | Performance-Trends, Charts | PHP/Chart.js | 3h | `stats.php` |
| **Phase 5: Automation** | 5.1 Scheduler | Cron-Jobs für wiederkehrende Tests | PHP/Cron | 2h | `scheduler.php` |
| | 5.2 Alerting | Slack/Email-Benachrichtigungen | PHP | 2h | `notifier.php` |
| | 5.3 Cleanup | Alte Daten löschen | PHP/MySQL Events | 1h | In Schema |
| **Phase 6: Deployment** | 6.1 HostEurope Upload | FTP/Git Deploy | - | 1h | - |
| | 6.2 Worker Installation | Agent auf allen Rechnern | - | 2h | `install.sh` / `.bat` |
| | 6.3 Testing & Bugfixes | End-to-End Tests | - | 4h | - |
| **Gesamt** | | | | **~48h** | |

---

## Datenbank-Schema (Komplett)

```sql
-- schema-detailed.sql
CREATE DATABASE IF NOT EXISTS playwright_orchestrator
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE playwright_orchestrator;

-- ============================================================================
-- TABLE: workers
-- Speichert alle registrierten Test-Worker (Rechner)
-- ============================================================================
CREATE TABLE workers (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    -- Identifikation
    hostname VARCHAR(255) NOT NULL UNIQUE COMMENT 'Eindeutiger Hostname/Name des Workers',
    ip_address VARCHAR(45) NULL COMMENT 'IPv4 oder IPv6 Adresse',
    api_key CHAR(64) NOT NULL UNIQUE COMMENT 'SHA256 API-Key für Authentifizierung',

    -- Status
    status ENUM('idle', 'busy', 'offline', 'maintenance') DEFAULT 'offline'
        COMMENT 'idle=bereit, busy=arbeitet, offline=nicht erreichbar, maintenance=deaktiviert',

    -- Capabilities (JSON)
    capabilities JSON NULL COMMENT 'Worker-Fähigkeiten: browsers, max_parallel, platform, etc.',

    -- Limits & Configuration
    max_parallel_tasks INT UNSIGNED DEFAULT 4
        COMMENT 'Maximale Anzahl paralleler Tasks',
    current_tasks_count INT UNSIGNED DEFAULT 0
        COMMENT 'Aktuelle Anzahl laufender Tasks (Cache)',

    -- Priority & Load Balancing
    priority INT DEFAULT 100 COMMENT 'Worker-Priorität (höher = bevorzugt)',
    weight DECIMAL(3,2) DEFAULT 1.0 COMMENT 'Gewichtung für Task-Verteilung (0.0 - 1.0)',

    -- Monitoring
    total_tasks_completed INT UNSIGNED DEFAULT 0,
    total_tasks_failed INT UNSIGNED DEFAULT 0,
    avg_task_duration_ms INT UNSIGNED NULL,

    -- Health Check
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    health_check_failures INT UNSIGNED DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Metadata
    tags JSON NULL,
    notes TEXT NULL,

    -- Indexes
    INDEX idx_status (status),
    INDEX idx_last_seen (last_seen),
    INDEX idx_priority (priority DESC)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: test_runs
-- Ein Test-Run repräsentiert eine komplette Test-Session
-- ============================================================================
CREATE TABLE test_runs (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    -- Identifikation
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,

    -- Konfiguration
    config JSON NOT NULL COMMENT 'Test-Konfiguration (Browser, URL, Timeouts, etc.)',

    -- Sharding
    total_shards INT UNSIGNED NOT NULL DEFAULT 1,
    total_tests INT UNSIGNED DEFAULT 0,

    -- Status & Progress
    status ENUM('pending', 'scheduling', 'running', 'completed', 'failed', 'cancelled')
        DEFAULT 'pending',
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,

    -- Scheduling
    scheduled_for TIMESTAMP NULL,
    schedule_cron VARCHAR(100) NULL,

    -- Execution tracking
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    duration_ms BIGINT UNSIGNED NULL,

    -- Results aggregation
    total_passed INT UNSIGNED DEFAULT 0,
    total_failed INT UNSIGNED DEFAULT 0,
    total_skipped INT UNSIGNED DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.00,

    -- User tracking
    created_by VARCHAR(100) NULL,

    -- Metadata
    tags JSON NULL,
    metadata JSON NULL,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_status (status),
    INDEX idx_created_at (created_at DESC),
    INDEX idx_scheduled_for (scheduled_for)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: tasks
-- Ein Task ist ein einzelner Test-Shard der auf einem Worker ausgeführt wird
-- ============================================================================
CREATE TABLE tasks (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    -- Relations
    test_run_id INT UNSIGNED NOT NULL,
    worker_id INT UNSIGNED NULL,

    -- Shard Information
    shard_index INT UNSIGNED NOT NULL,
    shard_total INT UNSIGNED NOT NULL,

    -- Status
    status ENUM('pending', 'assigned', 'running', 'completed', 'failed', 'timeout', 'cancelled')
        DEFAULT 'pending',

    -- Retry logic
    retry_count INT UNSIGNED DEFAULT 0,
    max_retries INT UNSIGNED DEFAULT 2,

    -- Timing
    assigned_at TIMESTAMP NULL,
    started_at TIMESTAMP NULL,
    last_heartbeat_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    duration_ms BIGINT UNSIGNED NULL,

    -- Timeout handling
    timeout_seconds INT UNSIGNED DEFAULT 3600,

    -- Priority
    priority INT DEFAULT 100,

    -- Error tracking
    error_message TEXT NULL,
    error_stack TEXT NULL,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Foreign Keys
    FOREIGN KEY (test_run_id) REFERENCES test_runs(id) ON DELETE CASCADE,
    FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE SET NULL,

    -- Indexes
    INDEX idx_test_run (test_run_id),
    INDEX idx_worker (worker_id),
    INDEX idx_status (status),
    INDEX idx_priority (priority DESC)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: test_results
-- Detaillierte Ergebnisse eines Tasks
-- ============================================================================
CREATE TABLE test_results (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    -- Relation
    task_id INT UNSIGNED NOT NULL UNIQUE,

    -- Test counts
    total_tests INT UNSIGNED DEFAULT 0,
    passed INT UNSIGNED DEFAULT 0,
    failed INT UNSIGNED DEFAULT 0,
    skipped INT UNSIGNED DEFAULT 0,
    flaky INT UNSIGNED DEFAULT 0,

    -- Performance metrics
    duration_ms BIGINT UNSIGNED DEFAULT 0,
    avg_test_duration_ms INT UNSIGNED NULL,
    p50_duration_ms INT UNSIGNED NULL,
    p95_duration_ms INT UNSIGNED NULL,
    p99_duration_ms INT UNSIGNED NULL,

    -- Resource usage
    peak_memory_mb INT UNSIGNED NULL,
    avg_cpu_percent DECIMAL(5,2) NULL,

    -- Files & Artifacts
    report_html_url VARCHAR(512) NULL,
    report_json_url VARCHAR(512) NULL,
    trace_url VARCHAR(512) NULL,
    video_urls JSON NULL,
    screenshot_urls JSON NULL,

    -- Logs
    stdout_log MEDIUMTEXT NULL,
    stderr_log MEDIUMTEXT NULL,

    -- Custom metrics
    custom_metrics JSON NULL,

    -- Failed tests detail
    failed_tests JSON NULL,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,

    -- Indexes
    INDEX idx_task (task_id),
    INDEX idx_created_at (created_at DESC)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: worker_logs
-- Heartbeat & Event-Log für Worker
-- ============================================================================
CREATE TABLE worker_logs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    -- Relation
    worker_id INT UNSIGNED NOT NULL,

    -- Event
    event_type ENUM(
        'register',
        'heartbeat',
        'task_claimed',
        'task_started',
        'task_heartbeat',
        'task_completed',
        'task_failed',
        'error',
        'shutdown'
    ) NOT NULL,

    -- Context
    task_id INT UNSIGNED NULL,

    -- Message & Data
    message TEXT NULL,
    data JSON NULL,

    -- System metrics
    cpu_percent DECIMAL(5,2) NULL,
    memory_used_mb INT UNSIGNED NULL,
    memory_total_mb INT UNSIGNED NULL,
    disk_free_gb INT UNSIGNED NULL,

    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL,

    -- Indexes
    INDEX idx_worker (worker_id),
    INDEX idx_created_at (created_at DESC),
    INDEX idx_event_type (event_type)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: config
-- System-Konfiguration (Key-Value Store)
-- ============================================================================
CREATE TABLE config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value TEXT NOT NULL,
    value_type ENUM('string', 'int', 'float', 'boolean', 'json') DEFAULT 'string',
    description TEXT NULL,
    is_secret BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100) NULL
) ENGINE=InnoDB;

-- Default config values
INSERT INTO config (config_key, config_value, value_type, description) VALUES
('worker_heartbeat_timeout_seconds', '120', 'int', 'Worker als offline markieren nach X Sekunden'),
('task_timeout_default_seconds', '3600', 'int', 'Standard-Timeout für Tasks (1 Stunde)'),
('task_max_retries', '2', 'int', 'Maximale Anzahl automatischer Task-Wiederholungen'),
('scheduler_enabled', 'true', 'boolean', 'Automatisches Scheduling aktiviert'),
('load_balancer_strategy', 'least_loaded', 'string', 'Strategie: least_loaded, round_robin, priority, weighted'),
('report_retention_days', '90', 'int', 'Aufbewahrungsdauer für Reports in Tagen'),
('log_retention_days', '30', 'int', 'Aufbewahrungsdauer für Logs'),
('max_parallel_test_runs', '10', 'int', 'Maximale Anzahl gleichzeitiger Test-Runs'),
('slack_webhook_url', '', 'string', 'Slack Webhook für Notifications'),
('smtp_server', '', 'string', 'SMTP Server für Email-Alerts');

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Worker mit aktuellen Stats
CREATE VIEW v_workers_current AS
SELECT
    w.*,
    TIMESTAMPDIFF(SECOND, w.last_seen, NOW()) as seconds_since_seen,
    CASE
        WHEN TIMESTAMPDIFF(SECOND, w.last_seen, NOW()) > 120 THEN 'offline'
        ELSE w.status
    END as effective_status,
    (SELECT COUNT(*) FROM tasks t WHERE t.worker_id = w.id AND t.status IN ('assigned', 'running')) as current_tasks,
    w.max_parallel_tasks - (SELECT COUNT(*) FROM tasks t WHERE t.worker_id = w.id AND t.status IN ('assigned', 'running')) as available_slots
FROM workers w;

-- View: Test-Run Progress
CREATE VIEW v_test_runs_progress AS
SELECT
    tr.*,
    COUNT(t.id) as total_tasks,
    SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
    SUM(CASE WHEN t.status = 'failed' THEN 1 ELSE 0 END) as failed_tasks,
    SUM(CASE WHEN t.status = 'running' THEN 1 ELSE 0 END) as running_tasks,
    ROUND((SUM(CASE WHEN t.status IN ('completed', 'failed') THEN 1 ELSE 0 END) / COUNT(t.id)) * 100, 2) as progress_pct
FROM test_runs tr
LEFT JOIN tasks t ON tr.id = t.test_run_id
GROUP BY tr.id;

-- ============================================================================
-- STORED PROCEDURES
-- ============================================================================

DELIMITER //

CREATE PROCEDURE sp_claim_next_task(
    IN p_worker_id INT UNSIGNED,
    OUT p_task_id INT UNSIGNED
)
BEGIN
    DECLARE v_max_parallel INT;
    DECLARE v_current_tasks INT;

    SELECT max_parallel_tasks INTO v_max_parallel
    FROM workers WHERE id = p_worker_id;

    SELECT COUNT(*) INTO v_current_tasks
    FROM tasks
    WHERE worker_id = p_worker_id AND status IN ('assigned', 'running');

    IF v_current_tasks >= v_max_parallel THEN
        SET p_task_id = NULL;
    ELSE
        SELECT t.id INTO p_task_id
        FROM tasks t
        JOIN test_runs tr ON t.test_run_id = tr.id
        WHERE t.status = 'pending'
          AND tr.status = 'running'
        ORDER BY t.priority DESC, t.id ASC
        LIMIT 1
        FOR UPDATE;

        IF p_task_id IS NOT NULL THEN
            UPDATE tasks
            SET status = 'assigned',
                worker_id = p_worker_id,
                assigned_at = NOW()
            WHERE id = p_task_id;

            UPDATE workers
            SET current_tasks_count = current_tasks_count + 1,
                status = 'busy'
            WHERE id = p_worker_id;
        END IF;
    END IF;
END//

CREATE PROCEDURE sp_check_worker_health()
BEGIN
    DECLARE v_timeout INT;

    SELECT config_value INTO v_timeout
    FROM config WHERE config_key = 'worker_heartbeat_timeout_seconds';

    UPDATE workers
    SET status = 'offline',
        health_check_failures = health_check_failures + 1
    WHERE TIMESTAMPDIFF(SECOND, last_seen, NOW()) > v_timeout
      AND status != 'offline'
      AND status != 'maintenance';
END//

DELIMITER ;

-- ============================================================================
-- MYSQL EVENTS (Cron-Jobs)
-- ============================================================================

SET GLOBAL event_scheduler = ON;

CREATE EVENT evt_worker_health_check
ON SCHEDULE EVERY 2 MINUTE
DO CALL sp_check_worker_health();

CREATE EVENT evt_cleanup_old_logs
ON SCHEDULE EVERY 1 DAY
STARTS (TIMESTAMP(CURRENT_DATE) + INTERVAL 3 HOUR)
DO
DELETE FROM worker_logs
WHERE created_at < DATE_SUB(NOW(), INTERVAL (SELECT config_value FROM config WHERE config_key = 'log_retention_days') DAY);
```

---

## Load Balancing Strategien

Das System unterstützt verschiedene Strategien zur Task-Verteilung:

### 1. Least Loaded (Standard)
Wählt den Worker mit den meisten freien Slots:
```
Worker A: 2/10 Tasks → 8 freie Slots
Worker B: 7/10 Tasks → 3 freie Slots
Worker C: 0/4 Tasks  → 4 freie Slots
→ Wählt Worker A (8 freie Slots)
```

### 2. Round Robin
Verteilt gleichmäßig über alle verfügbaren Worker im Kreis:
```
Task 1 → Worker A
Task 2 → Worker B
Task 3 → Worker C
Task 4 → Worker A (wrap around)
```

### 3. Priority-Based
Bevorzugt Worker mit höherer Priorität:
```
Worker A: Priority 150, 2/10 Tasks
Worker B: Priority 100, 0/10 Tasks
Worker C: Priority 50,  1/4 Tasks
→ Wählt Worker A (höchste Priorität mit freien Slots)
```

### 4. Weighted
Berücksichtigt Performance-History:
```
Score = (Weight × 100) + (Freie Slots × 10) + (Success Ratio × 50) - (Avg Duration / 1000)

Worker A: Weight 1.0, 8 slots frei, 95% success, 5s avg → Score: 245
Worker B: Weight 0.8, 3 slots frei, 98% success, 3s avg → Score: 210
→ Wählt Worker A
```

**Konfiguration:**
```sql
UPDATE config SET config_value = 'least_loaded' WHERE config_key = 'load_balancer_strategy';
-- Optionen: least_loaded, round_robin, priority, weighted
```

---

## Worker Agent (Node.js)

### Installation auf Windows

```powershell
# Voraussetzungen
node --version  # Node.js 20+ erforderlich
npm --version

# Installation
cd C:\Projekte\GE-ECommerce-Testing
mkdir agent
cd agent

# Dependencies
npm init -y
npm install axios

# Konfiguration
$env:COORDINATOR_URL = "https://playwright.your-domain.de"
$env:WORKER_NAME = "laptop-max"
$env:PLAYWRIGHT_PROJECT_PATH = "C:\Projekte\GE-ECommerce-Testing"
$env:POLL_INTERVAL = "60"  # Sekunden

# Agent starten
node worker.js

# Als Service (optional mit PM2)
npm install -g pm2
pm2 start worker.js --name playwright-worker
pm2 save
pm2 startup
```

### Installation auf Linux/Mac

```bash
# Installation
cd ~/projects/GE-ECommerce-Testing
mkdir agent
cd agent

npm init -y
npm install axios

# Konfiguration
export COORDINATOR_URL="https://playwright.your-domain.de"
export WORKER_NAME="desktop-ci"
export PLAYWRIGHT_PROJECT_PATH="/home/user/GE-ECommerce-Testing"
export POLL_INTERVAL="60"

# Agent starten
node worker.js

# Als Service (systemd)
sudo nano /etc/systemd/system/playwright-worker.service
# [Inhalt siehe unten]
sudo systemctl enable playwright-worker
sudo systemctl start playwright-worker
```

### Worker Agent Code (Grundgerüst)

```javascript
// agent/worker.js
const os = require('os');
const axios = require('axios');
const { exec } = require('child_process');
const util = require('util');
const fs = require('fs').promises;

const execPromise = util.promisify(exec);

// Configuration
const COORDINATOR_URL = process.env.COORDINATOR_URL || 'https://playwright.example.com';
const POLL_INTERVAL = parseInt(process.env.POLL_INTERVAL || '60') * 1000;
const WORKER_NAME = process.env.WORKER_NAME || os.hostname();
const PLAYWRIGHT_PROJECT_PATH = process.env.PLAYWRIGHT_PROJECT_PATH || process.cwd();

let apiKey = null;
let workerId = null;
let isProcessingTask = false;

// Worker capabilities
const capabilities = {
    browsers: ['chromium', 'firefox', 'webkit'],
    max_parallel: 4,
    platform: os.platform(),
    arch: os.arch(),
    cpu_count: os.cpus().length,
    total_memory_gb: Math.round(os.totalmem() / 1024 / 1024 / 1024),
};

async function registerWorker() {
    console.log(`🔌 Registering worker: ${WORKER_NAME}`);

    const response = await axios.post(`${COORDINATOR_URL}/api/v1/workers/register`, {
        hostname: WORKER_NAME,
        capabilities: capabilities,
    });

    apiKey = response.data.api_key;
    workerId = response.data.worker_id;

    await fs.writeFile('.worker-api-key', apiKey);
    console.log(`✅ Registered (ID: ${workerId})`);
}

async function pollForTask() {
    if (isProcessingTask) return;

    const response = await axios.get(`${COORDINATOR_URL}/api/v1/tasks/next`, {
        headers: { 'X-API-Key': apiKey },
    });

    if (response.data.task) {
        await executeTask(response.data);
    }
}

async function executeTask(task) {
    isProcessingTask = true;
    console.log(`🚀 Starting task ${task.task_id}`);

    const config = task.config || {};
    const command = `npx playwright test --shard=${task.shard_index}/${task.shard_total}`;

    try {
        await execPromise(command, { cwd: PLAYWRIGHT_PROJECT_PATH });
        await submitResults(task.task_id, { passed: 10, failed: 0, duration_ms: 5000 });
        console.log(`✅ Task ${task.task_id} completed`);
    } catch (error) {
        await submitResults(task.task_id, { passed: 0, failed: 1, error_log: error.message });
        console.error(`❌ Task ${task.task_id} failed`);
    } finally {
        isProcessingTask = false;
    }
}

async function submitResults(taskId, results) {
    await axios.post(
        `${COORDINATOR_URL}/api/v1/tasks/submit-result`,
        { task_id: taskId, ...results },
        { headers: { 'X-API-Key': apiKey } }
    );
}

async function main() {
    console.log('🎭 Playwright Worker Agent');

    try {
        apiKey = await fs.readFile('.worker-api-key', 'utf8');
    } catch (e) {
        // No existing key
    }

    await registerWorker();

    setInterval(pollForTask, POLL_INTERVAL);
    await pollForTask();
}

main().catch(console.error);
```

---

## Web-Dashboard

### Features

**Dashboard (index.php):**
- Worker-Übersicht (Status: Idle/Busy/Offline)
- Aktuelle Test-Runs mit Fortschritt
- System-Stats (Gesamt-Tests, Success-Rate)
- Quick-Actions (Test-Run starten, Worker verwalten)

**Worker-Ansicht (workers.php):**
- Detaillierte Worker-Liste mit Capabilities
- Aktuelle Tasks pro Worker
- Performance-Metriken (Avg Duration, Success-Rate)
- Logs & Heartbeat-History

**Test-Runs (runs.php):**
- Liste aller Test-Runs (filtierbar)
- Detailansicht: Task-Status, Progress-Bar
- Ergebnis-Download (HTML-Report, JSON)
- Fehler-Analyse bei Failed Tests

**Analytics (stats.php):**
- Performance-Trends (Chart.js)
- Test-Dauer über Zeit
- Success-Rate Verlauf
- Top 10 langsamste Tests
- Worker-Auslastung

---

## Monitoring & Alerting

### Health Checks

**Worker Health:**
- Heartbeat alle 60 Sekunden
- Offline nach 120 Sekunden ohne Heartbeat
- Automatisches Reassignment von Tasks wenn Worker offline

**Task Monitoring:**
- Task-Timeout nach 1 Stunde (konfigurierbar)
- Automatischer Retry (max 2×)
- Heartbeat während Task-Ausführung

### Alert-Typen

| Alert | Bedingung | Schwere | Benachrichtigung |
|-------|-----------|---------|------------------|
| Test Failure Rate | > 5% in letzten 60 Min | Critical | Slack + Email |
| Worker Offline | Worker seit 5 Min offline | Warning | Slack |
| Slow Tests | P95 > 60s | Warning | Slack |
| Task Timeout | Task läuft > 2h | Critical | Email |
| Disk Space Low | < 10% frei | Warning | Slack |

### Benachrichtigungs-Kanäle

**Slack:**
```sql
UPDATE config
SET config_value = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
WHERE config_key = 'slack_webhook_url';
```

**Email (SMTP):**
```sql
UPDATE config SET config_value = 'smtp.office365.com' WHERE config_key = 'smtp_server';
UPDATE config SET config_value = '587' WHERE config_key = 'smtp_port';
UPDATE config SET config_value = 'playwright@globetrotter.de' WHERE config_key = 'smtp_from';
```

---

## API-Dokumentation

### Worker Management

```http
POST /api/v1/workers/register
Content-Type: application/json

{
  "hostname": "laptop-max",
  "capabilities": {
    "browsers": ["chromium", "firefox"],
    "max_parallel": 4,
    "platform": "win32"
  }
}

Response 201:
{
  "worker_id": 42,
  "api_key": "abc123...",
  "message": "Worker registered successfully"
}
```

```http
GET /api/v1/tasks/next
X-API-Key: abc123...

Response 200:
{
  "task_id": 123,
  "test_run_id": 45,
  "shard_index": 2,
  "shard_total": 10,
  "config": {
    "browser": "chromium",
    "base_url": "https://www.globetrotter.de"
  }
}
```

```http
POST /api/v1/results/submit
X-API-Key: abc123...
Content-Type: application/json

{
  "task_id": 123,
  "passed": 42,
  "failed": 2,
  "skipped": 1,
  "duration_ms": 125000,
  "report_url": "https://..."
}

Response 200:
{
  "message": "Result submitted successfully",
  "status": "completed"
}
```

### Test Run Management

```http
POST /api/v1/test-runs/create
Content-Type: application/json
Authorization: Bearer admin-token

{
  "name": "Nightly E2E Tests",
  "total_shards": 10,
  "config": {
    "browser": "chromium",
    "base_url": "https://www.globetrotter.de",
    "timeout": 30000
  }
}

Response 201:
{
  "test_run_id": 45,
  "message": "Test run created with 10 shards"
}
```

---

## Vergleich mit Cloud-Lösungen

| Kriterium | Custom System | GitHub Actions | k6 + Grafana | Kubernetes |
|-----------|---------------|----------------|--------------|------------|
| **Monatliche Kosten** | €0 | $30-50 | $60-150 | $450-1.000 |
| **Setup-Zeit** | 48h | 9h | 19h | 48h+ |
| **Max Parallelität** | Unbegrenzt (abhängig von Workern) | 20 Jobs | 500 VUs | 1.000+ Pods |
| **Hardware** | Eigene Rechner + optional Cloud | GitHub Runner | Eigene/Cloud | Cloud |
| **Web-UI** | ✅ Custom | ❌ Nur GitHub | ✅ Grafana | ✅ k8s Dashboard |
| **Lokale Rechner** | ✅ Ja | ❌ Nein | ⚠️ Möglich | ⚠️ Möglich |
| **Monitoring** | ⭐⭐⭐ Gut | ⭐⭐ Basis | ⭐⭐⭐⭐ Sehr gut | ⭐⭐⭐⭐⭐ Exzellent |
| **Wartung** | Mittel | Niedrig | Mittel | Hoch |
| **Flexibilität** | ✅ Sehr hoch | ❌ Limitiert | ⭐⭐⭐ Hoch | ✅ Sehr hoch |
| **Vendor Lock-in** | ❌ Keiner | GitHub | Gering | Cloud-Anbieter |

---

## Vor- und Nachteile

### Vorteile ✅

1. **Keine Cloud-Kosten:** Nutzt vorhandenes HostEurope-Hosting (€0 extra/Monat)
2. **Unbegrenzte Skalierung:** Beliebig viele Worker hinzufügen (Laptops, Desktops, VMs)
3. **Lokale Rechner:** Team-Laptops können während Arbeit als Worker dienen
4. **Volle Kontrolle:** Kompletter Zugriff auf Code, Daten, Infrastruktur
5. **Flexible Worker:** Unterschiedliche Hardware-Konfigurationen möglich
6. **Web-Dashboard:** Benutzerfreundliche Oberfläche für Team
7. **Bekannte Technologien:** PHP, MySQL, Node.js - keine neue Lernkurve
8. **Hybrid-Setup:** Mix aus lokalen und Cloud-Workern möglich
9. **Kein Vendor Lock-in:** Vollständig selbst-gehostet
10. **Custom Extensions:** Einfach erweiterbar mit neuen Features

### Nachteile ❌

1. **Initial Development:** ~48 Stunden Entwicklungszeit
2. **Wartungsaufwand:** 2-4h/Monat für Updates, Bugfixes
3. **Kein Enterprise-Support:** Keine professionelle Support-Hotline
4. **HostEurope Performance:** Shared Hosting hat Limitierungen
5. **Skalierung:** Bei >50 Workern könnte MySQL zur Bottleneck werden
6. **Monitoring:** Kein Prometheus/Grafana-Level Observability
7. **Security:** API-Key-Verwaltung muss sicher implementiert werden
8. **Backup:** Manuelles Backup-System erforderlich
9. **High Availability:** Kein automatisches Failover bei HostEurope-Ausfall
10. **Worker-Verwaltung:** Manuelle Installation auf allen Rechnern

---

## Sicherheits-Überlegungen

### API-Sicherheit

**API-Key-Generation:**
```php
$api_key = bin2hex(random_bytes(32)); // 64 Zeichen SHA256
```

**Best Practices:**
- API-Keys in `.env` Dateien speichern (nie in Git)
- HTTPS obligatorisch (Let's Encrypt SSL)
- Rate-Limiting auf API-Endpunkten
- Input-Validation & SQL-Injection Prevention (Prepared Statements)
- CORS-Header richtig konfigurieren

### Worker-Sicherheit

**Isolation:**
- Worker läuft mit eigenen Berechtigungen
- Playwright-Tests in Sandbox ausführen
- Keine Secrets im Test-Code (über ENV-Vars)

**Network:**
- Worker → Coordinator: HTTPS
- Firewall: Nur ausgehende Verbindungen erlauben

---

## Deployment-Checkliste

### HostEurope Setup

- [ ] MySQL-Datenbank erstellen (phpMyAdmin)
- [ ] `schema-detailed.sql` importieren
- [ ] PHP-Dateien via FTP hochladen
- [ ] `.htaccess` für Clean URLs konfigurieren
- [ ] SSL-Zertifikat aktivieren (Let's Encrypt)
- [ ] Cron-Job für Scheduler einrichten
- [ ] Backup-Strategie definieren

### Worker Installation

- [ ] Node.js 20+ installieren auf allen Rechnern
- [ ] `agent/` Ordner kopieren
- [ ] `npm install` ausführen
- [ ] ENV-Variablen setzen (Coordinator-URL, etc.)
- [ ] Worker-Agent starten
- [ ] Als Service konfigurieren (pm2/systemd)
- [ ] Im Dashboard verifizieren (Worker sollte als "idle" erscheinen)

### Testing

- [ ] Test-Run manuell über Dashboard starten
- [ ] Verifizieren dass Tasks verteilt werden
- [ ] Ergebnisse prüfen
- [ ] Logs kontrollieren
- [ ] Alert-System testen (Slack/Email)
- [ ] Load-Test mit vielen parallelen Tasks

---

## Erweiterungsmöglichkeiten

### Phase 2 Features (später)

1. **Docker-Support:** Worker als Docker-Container
2. **Grafana-Integration:** Performance-Dashboards
3. **GitHub Integration:** Auto-Trigger bei Push
4. **Flaky Test Detection:** Automatische Erkennung instabiler Tests
5. **Test-Priorisierung:** Häufig fehlende Tests zuerst ausführen
6. **Visual Regression:** Screenshot-Vergleich
7. **Mobile Testing:** Geräte-Farm Integration
8. **API-Testing:** REST/GraphQL Tests
9. **Performance Budgets:** Automatische Warnungen bei Slow-Down
10. **Multi-Tenancy:** Mehrere Teams/Projekte

---

## Kostenvergleich (12 Monate)

| Lösung | Setup | Monatlich | Jahr 1 | Jahr 2 |
|--------|-------|-----------|--------|--------|
| **Custom System** | 48h × €80 = €3.840 | €0 | €3.840 | €0 |
| **GitHub Actions** | 9h × €80 = €720 | $50 | €1.320 | €600 |
| **k6 + Grafana** | 19h × €80 = €1.520 | $100 | €2.720 | €1.200 |
| **Kubernetes** | 48h × €80 = €3.840 | $500 | €9.840 | €6.000 |

**Break-Even:**
- vs GitHub Actions: Nach 3 Jahren
- vs k6: Nach 2 Jahren
- vs Kubernetes: Nach 1 Jahr

**Bei hoher Nutzung (täglich 10 Test-Runs):**
- GitHub Actions: $200/Monat → Break-Even nach 1,6 Jahren
- Custom System amortisiert sich schneller bei intensiver Nutzung

---

## Empfehlung & Nächste Schritte

### Empfehlung: JA, umsetzen! ✅

Das Custom Test Orchestration System ist für euren Use-Case **optimal**, weil:

1. ✅ Vorhandenes HostEurope-Hosting nutzen (keine extra Kosten)
2. ✅ Team-Rechner als Worker nutzen (keine neue Hardware)
3. ✅ Skalierbar auf 100+ parallele Tests
4. ✅ Volle Kontrolle & Flexibilität
5. ✅ Bekannte Technologien (PHP, Node.js)
6. ✅ Keine laufenden Cloud-Kosten

### Implementierungs-Plan

**Sprint 1 (Woche 1-2): Foundation**
- Datenbank-Schema implementieren
- API-Grundgerüst aufsetzen
- Load-Balancer implementieren

**Sprint 2 (Woche 3-4): Worker Agent**
- Node.js Agent entwickeln
- Playwright-Integration
- Testing auf 2-3 Rechnern

**Sprint 3 (Woche 5-6): Web-Dashboard**
- Dashboard-UI entwickeln
- Worker-Verwaltung
- Test-Run-Ansicht

**Sprint 4 (Woche 7): Polish & Deploy**
- Bugfixes
- Deployment auf HostEurope
- Team-Schulung
- Dokumentation

### Sofort starten mit

1. **Proof of Concept (8h):**
   - Minimales Schema (workers, tasks, test_runs)
   - Einfacher Worker-Agent
   - Basic API (register, get-task, submit-result)
   - → Zeigt Machbarkeit

2. **Dann entscheiden:** PoC erfolgreich? → Full Implementation

---

## Fragen & Antworten

**Q: Kann ich auch Cloud-Worker verwenden?**
A: Ja! AWS EC2 Spot Instances, Azure VMs, etc. können als Worker dienen. Agent einfach dort installieren.

**Q: Was passiert wenn HostEurope down ist?**
A: Worker können nicht neu starten, laufende Tests werden zu Ende geführt. Danach warten Worker bis Coordinator wieder online ist.

**Q: Wie viele Worker sind realistisch?**
A: Bei normalem Setup (MySQL auf Shared Hosting): ~50 Worker. Mit dediziertem Server: 500+.

**Q: Können Worker in verschiedenen Netzwerken sein?**
A: Ja, solange sie HTTPS-Zugriff auf HostEurope haben. Auch über VPN möglich.

**Q: Wie lange dauert ein typischer Test-Run?**
A: Mit 10 Workern @ 10 parallel = 100 Tests gleichzeitig. 1.000 Tests @ 30s/Test = 300s = **5 Minuten**.

---

## Kontakt & Support

**Projekt-Owner:** [Name]
**Tech-Lead:** [Name]
**Repository:** `GE-ECommerce-Testing`
**Dokumentation:** `/docs/remote-setup-feature.md`

---

**Status:** ✅ Ready for Implementation
**Letzte Aktualisierung:** 2026-02-01
