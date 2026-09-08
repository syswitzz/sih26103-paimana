--permissions for ml and backend roles to access things

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'paimana_backend') THEN
        CREATE ROLE paimana_backend LOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'paimana_ml_readonly') THEN
        CREATE ROLE paimana_ml_readonly LOGIN;
    END IF;
END
$$;

REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO paimana_backend, paimana_ml_readonly;

GRANT SELECT, INSERT, UPDATE, DELETE ON projects, milestones, progress_reports, risk_scores, alerts, users, interventions, audit_log TO paimana_backend;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO paimana_backend;
GRANT SELECT ON project_overview TO paimana_backend;

GRANT SELECT ON projects, milestones, progress_reports, risk_scores, alerts, users, interventions, audit_log, project_overview TO paimana_ml_readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO paimana_backend;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO paimana_ml_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO paimana_backend;