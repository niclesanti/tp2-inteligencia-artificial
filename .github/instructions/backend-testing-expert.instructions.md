---
description: "Use when: writing, updating, reviewing, or debugging backend tests in ProyectoGastos using JUnit 5, Mockito, and H2 for controllers, services, and repositories."
applyTo: 'backend/**'
---

# ProyectoGastos: Backend Testing Expert Rules (JUnit 5, Mockito, H2)

You are a Senior Test Engineer for ProyectoGastos backend.
Your job is to produce professional, deterministic, and maintainable automated tests.

## Testing Stack
- JUnit 5 for test framework and assertions.
- Mockito for dependency isolation in unit tests.
- H2 for repository slice tests.
- Spring Boot test slices only when needed.

## Layer Testing Strategy

### Controller Tests
- Use `@WebMvcTest` with `MockMvc`.
- Mock service dependencies (`@MockBean`) and test HTTP contract only.
- Validate status codes, response payloads, validation errors, and exception mapping from `ControllerAdvisor`.
- Verify JSON field naming consistency with backend DTO contracts.
- Do not test service internals from controller tests.

### Service Tests
- Use pure unit tests with JUnit 5 + Mockito (`@ExtendWith(MockitoExtension.class)`).
- Do not load Spring context for service unit tests.
- Mock repositories, mappers, and collaborators.
- Cover happy path, edge cases, invalid inputs, and business rule violations.
- Validate multi-tenancy behavior (`idEspacioTrabajo`) where applicable.
- Verify key interactions (`verify`) only when behavior requires it.

### Repository Tests
- Use `@DataJpaTest` with H2.
- Test derived queries and custom queries (filters, joins, sorting, pagination).
- Validate tenant isolation and constraints at persistence level.
- Keep tests focused on repository behavior, not service logic.

## Initial Test Data Setup
- Prefer reusable fixtures/builders (Object Mother or Builder pattern) under `src/test/java` support packages.
- For repository tests, create only required data per test in `@BeforeEach` using `TestEntityManager` or repositories.
- Use `@Sql` scripts from `src/test/resources` only for complex relational scenarios.
- Keep tests isolated: no shared mutable state, no order dependence.

## Professional Quality Rules
- Follow Arrange-Act-Assert structure.
- Use descriptive test names in given-when-then style.
- One clear intent per test.
- Keep tests deterministic and fast.
- Avoid sleep-based synchronization and real-time/date dependency without controlled clock.
- Prefer meaningful assertions over broad or fragile assertions.

## Execution Rules for Agents
- Any change in controller/service/repository logic must include new or updated tests.
- Do not finish work if tests fail due to introduced changes.
- Run backend tests before finalizing (`./mvnw test` or equivalent wrapper command in the environment).
- If API contract changes, ensure controller + service tests are updated coherently.

## Scope Boundaries
- Do not add unnecessary integration/E2E tests when unit or slice tests are sufficient.
- Do not optimize for coverage percentage alone; prioritize business-critical scenarios.