# AGENTS.md — Repo Guide for OpenCode

## Architecture

Full-stack personal finance manager: `backend/` (Java 21, Spring Boot 3.5.3, Maven) + `frontend/` (React 18, TypeScript, Vite 5).

## Key Commands

| Scope | Command | Notes |
|-------|---------|-------|
| Backend tests | `cd backend && ./mvnw clean test` (or `.\mvnw.cmd test` on Windows) | Uses Maven wrapper; H2 in-memory DB for tests |
| Backend build | `cd backend && .\mvnw.cmd package -DskipTests` | |
| Frontend dev | `cd frontend && npm run dev` | Port 3000; proxies `/api` to `localhost:8080` |
| Frontend build | `cd frontend && npm run build` | Runs `tsc` then `vite build` |
| Frontend lint | `cd frontend && npm run lint` | ESLint with `--max-warnings 0` |
| Frontend test | `cd frontend && npm test` (vitest watch) or `npm run test:run` (single) | jsdom env; `src/test/setup.ts` |
| Frontend coverage | `cd frontend && npm run test:coverage` | |
| Full Docker | `docker-compose up -d --build` | Uses `.env` for secrets; frontend at `:3100`, backend at `:8080` |
| Rebuild single service | `docker-compose up -d --build backend` | Hot-reload frontend via volume mount in dev |
| RAG ingester (auto en startup) | `docker compose up -d --build` (automático) | Indexa `agente/docs RAG/` en Qdrant al primer inicio. Re-ejecutar manualmente si cambia el contenido: `docker compose exec agente python -m app.rag.ingester` |

## Monorepo Boundaries

```
backend/     — Java / Spring Boot (Maven)
frontend/    — React / TypeScript / Vite (npm)
docs/        — UML, Docker guide, observability, CI docs
```

Backend is **not a Maven multi-module** — single `pom.xml`. Frontend is a single Vite app. No monorepo tooling (no Turborepo, no Nx).

## Framework / Toolchain Quirks

- **JWT dual auth**: Backend JWT filter accepts `Authorization: Bearer <token>` header OR query param `?token=<token>` (needed for native EventSource SSE — `GET /api/notificaciones/stream?token=...`).
- **Flyway migrations**: All in `backend/src/main/resources/db/migration/`. Named `V{version}__{description}.sql`. `spring.jpa.hibernate.ddl-auto=none` — schema fully managed by Flyway.
- **MapStruct + Lombok**: Maven compiler plugin configures annotation processors for both. `lombok-mapstruct-binding` prevents compilation order issues.
- **Money precision**: Frontend uses `MoneyDecimal` wrapper over `decimal.js`. 24 monetary fields auto-transformed via Axios interceptor (`money-transformer.ts`). Never use raw JS floats for money.
- **shadcn/ui**: Components in `frontend/src/components/ui/`. Config in `frontend/components.json` — style `new-york`, base `neutral`, CSS variables enabled. They are local copies, not an npm package.
- **Zustand cache**: State store with 5-minute TTL cache per workspace. Call `load*` with `forceRefresh=true` to bypass.

## Testing Quirks

- **Backend**: JUnit 5 + Mockito. Spring Security Test available. H2 for integration tests.
- **Frontend**: Vitest + Testing Library. `jsdom` environment. Setup at `src/test/setup.ts`. Money system has 128 tests targeting 100% coverage on core components.
- **CI**: Only backend tests run in CI (`./mvnw clean test`). No frontend tests in CI pipeline.

## CI / CD

- **CI** (`.github/workflows/ci.yml`): On push/PR to `develop` or `main` — runs backend tests only.
- **CD** (`.github/workflows/cd.yml`): On push to `main` — tests → Docker build & push to Docker Hub → SSH deploy to Oracle Cloud VPS.

## Conventions

- **Branch naming**: `feature/`, `fix/`, `docs/`, `refactor/`, `test/`.
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, etc.).
- **Java**: Services defined as interfaces + `@Service` `Impl` classes. Constructor injection with `@RequiredArgsConstructor` (Lombok). MapStruct for entity↔DTO mapping.
- **React**: Functional components + hooks. PascalCase for components. Feature-based structure under `src/features/`. `@/` path alias to `src/`.
- **SQL migrations**: Always use `BEGIN; ... COMMIT;` for transactional migrations.

## Important Constraints

- `.env` is gitignored. Must copy `.env.example` manually. Google OAuth2 credentials required for auth to work.
- Frontend containerized uses port **3000** internally (`Dockerfile.dev`) but compose override maps to **3100** externally.
- Frontend production Docker image serves via Nginx on port 80.
- PWA manifest and multi-resolution icons in `frontend/public/`. Regenerate with `npm run generate-icons`.
