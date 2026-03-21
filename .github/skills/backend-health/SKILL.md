---
name: backend-health
description: Recursive workflow to compile, deploy, and test the backend, automatically fixing errors until everything passes.
---

# Backend Self-Healing Instructions

When this skill is activated, run the following sequential execution loop:

## Phase 1: Clean Compilation
1. Navigate to `backend/`.
2. Run `./mvnw clean compile`.
3. **Fix Loop:** If compilation fails (exit code != 0):
   - Read the terminal error logs.
   - Apply the required fixes in Java code following `backend-expert.instructions.md`.
   - Retry step 2 until it succeeds.

## Phase 2: Infrastructure Deployment
1. Run `docker compose up -d --build`.
2. Run `docker ps` to verify container status.
3. **Fix Loop:** If any service (`db`, `backend`) is not "Up":
   - Run `docker logs [container_name]`.
   - Analyze whether the issue is configuration, port conflict, or connectivity.
   - Apply the required fixes.
   - Retry step 1.

## Phase 3: Logic Validation
1. Run `./mvnw test`.
2. **Fix Loop:** If there are failing tests:
   - Read the JUnit report in the console.
   - Fix the affected service logic following `backend-expert.instructions.md`, or fix the test if the test is incorrect.
   - Retry step 1 until 100% of tests pass.

## Final Objective
Do not mark the task as complete until all phases succeed fully. Do not ask for permission to fix obvious errors found in logs.