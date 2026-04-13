# Engineering Runbook — Deployment & Infrastructure

## Deployment Process

All deployments to production must go through the standard release pipeline. Direct pushes to `main` are disabled. The process:

1. Create a feature branch from `main` using the naming convention `feat/TICKET-description`.
2. Open a Pull Request. All PRs require at least 1 approving review from a senior engineer.
3. CI must pass (unit tests, lint, type checks). Failing CI blocks merge.
4. After merge to `main`, the CD pipeline automatically deploys to **staging** within ~5 minutes.
5. Manual promotion to **production** is triggered via the `#deployments` Slack channel by tagging `@deploy-bot promote`.
6. Monitor Datadog dashboards for 15 minutes post-deploy. Roll back with `/rollback <service>` in `#deployments` if error rate exceeds 1%.

## Environments

| Environment | URL                        | Auto-deploy |
|-------------|----------------------------|-------------|
| dev         | dev.internal.company.com   | On push     |
| staging     | staging.internal.company.com | On merge to main |
| production  | app.company.com            | Manual only |

## Database Migrations

- Run migrations locally before committing: `make db-migrate`
- Migrations are applied automatically on staging during deploy
- Production migrations require a change request in Linear tagged `db-migration`
- Never run destructive migrations (DROP, TRUNCATE) without a backup snapshot

## Secrets Management

All secrets are stored in AWS Secrets Manager. Never commit secrets to Git. Use the pattern:

```bash
aws secretsmanager get-secret-value --secret-id prod/service/DB_PASSWORD
```

Rotate secrets quarterly. Compromised secrets must be rotated within 2 hours and reported to `#security`.

## On-Call Rotation

Engineering on-call rotates weekly. The current on-call schedule is in PagerDuty. On-call engineers are expected to:
- Respond to P1 alerts within 15 minutes
- Respond to P2 alerts within 1 hour
- Post an incident report in Notion within 24 hours of any P1 incident

## Monitoring & Alerting

- **Datadog**: Application performance, error rates, latency
- **PagerDuty**: Alert routing and on-call management
- **CloudWatch**: AWS infrastructure metrics
- **Sentry**: Frontend and backend error tracking

SLO targets: 99.9% availability, p99 latency < 500ms.