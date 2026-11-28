# Lab Production Playbook

**Purpose:** durable handoff for continuing the existing trytopwn Labs one at a time. Read this file before acting on any request such as “下一台靶机” or “继续”.

## 1. Source of truth and current position

- Repository: `10010100111000/AttackBoxModule`
- Work only from the current `main` inventory. Do not start a new Lab while existing main-branch Labs remain in the agreed queue.
- `catalog/web-curriculum.json` is the structured source of truth for Lab state, E2E status, workflow path, evidence URL and commit SHA.
- `docs/EXISTING_WEB_LAB_RELEASE_INVENTORY.md` is the human-readable inventory and next-Lab queue.
- `docs/WEB_LAB_DESIGN.md` is the broader curriculum and design plan.
- `catalog/web-competencies.json` is the canonical skill taxonomy.
- This playbook defines the execution procedure and user constraints.

### Current status and handoff

The live machine inventory and all per-Lab evidence are maintained only in [`docs/EXISTING_WEB_LAB_RELEASE_INVENTORY.md`](EXISTING_WEB_LAB_RELEASE_INVENTORY.md) and [`catalog/web-curriculum.json`](../catalog/web-curriculum.json). Do not duplicate the completed-Lab table here.

At the 2026-11-28 main snapshot, fourteen Labs have passed the current independent-attacker E2E: Bike, Precious, GoodGames, Devvortex, Base, Intense, Alert, Cursed Stale Policy, Editorial, Nibbles, Shocker, Bashed, BountyHunter and Cap. Thirteen existing Labs remain pending under the current E2E field. This is a CI-status distinction, not a claim that all pending Labs are unimplemented.

**Next action:** Alert is complete; choose one remaining pending Web Lab after inspecting its actual implementation, challenge files and workflow. Cursed Stale Policy and Editorial are complete; Shocker and Bashed are complete; BountyHunter and Cap are complete; next inspect the existing OpenAdmin xajax RCE and internal-service chain before proceeding. Funnel is a non-Web service chain; Trick is a larger multi-service target and should remain deferred until its scope is inspected. Do not assume the next target from an old prose queue—re-read the catalog and inventory first.

## 2. Non-negotiable user requirements

1. Work **one Lab at a time**. Do not batch several Labs; long sessions may be interrupted.
2. Prioritize Labs already present on `main`; do not invent or add unrelated new Labs.
3. Preserve real affected components and versions. No simulated vulnerable endpoints, fake interfaces, mock command execution, test backdoors or fabricated privilege-escalation chains.
4. If the original vulnerability cannot be reproduced with a real affected version/component, stop and explain the gap. Do not claim completion.
5. Follow the player's natural path: reconnaissance → normal browsing → observe requests/responses → discover clues → identify the component/version → exploit → retrieve the intended Flag. The player-facing Challenge must not reveal the vulnerability location or payload.
6. Reuse an existing front end or upstream project where appropriate; do not needlessly rebuild a page that already exists. Keep backend behavior faithful to the intended source.
7. Keep the scope appropriate to this platform: Linux Docker Labs. No Windows Labs, nested containers, container escape or host compromise. Do not force SSH/root stages onto a Web-only Lab.
8. Use Flag count according to each Challenge's intended objective. A Web-only Challenge normally has one Web Flag; only add a Root Flag to a Challenge that genuinely tests a real Linux privilege-escalation stage. Multiple Challenges may reuse the same Lab image and may each have their own Flag.
9. Keep images small: multi-stage builds where useful, minimal runtime packages, remove caches/build tools, use a non-root runtime user, healthchecks and resource limits.
10. Include a clear `README.md` and a discovery-led `writeup.md` for the Lab. Keep filenames compatible with the existing AttackBox parser; use simple names without spaces.
11. Do not ask the user to manually walk through the Lab or verify it. The Lab-specific GitHub Actions E2E must do this.
12. Do not manage or validate Worker synchronization, platform deployment, user accounts, or production runtime. The user explicitly does not want those tasks mixed into Lab completion.

### Challenge and Lab reuse

A **Challenge is a learning/assessment unit; a Lab is the reusable runtime environment**. They are not one-to-one.

- One Lab image/container may serve multiple Challenge Markdown files. Each Challenge links to the Lab through its `lab: <slug>` front matter.
- Each Challenge should test a defined subset of skills and have its own objective and Flag answer(s). Different Challenges may use different Flags, or intentionally reuse a Flag when the learning design is cumulative.
- A Challenge may combine several skills when the intended exercise is an integrated path. A separate focused Challenge may reuse the same Lab to isolate one part of that path.
- Do not create another Docker image, copy of the vulnerable application, or near-duplicate Lab merely because a new Challenge targets a different skill.
- Keep the Lab README and technical implementation evidence at the Lab level; keep learner-facing objectives and hints in each Challenge file. A Lab-level writeup may cover the full chain and link the relevant focused Challenges.

CI should build the Lab image once and verify the relevant Challenge objectives against that same image where practical. A normal Lab E2E uses **one fresh instance** and checks the exact Flag(s) for the selected objective(s). Do not launch a second full instance merely to prove Flag randomness or isolation; only add multi-instance tests when the specific vulnerability or isolation requirement genuinely needs them.

## 3. Required implementation workflow

### A. Inspect before editing

For the selected Lab, inspect:

- All current files and directory layout on `main`.
- Existing Dockerfile, base image, runtime user, exposed ports, healthcheck and resource use.
- Actual vulnerable application routes, database schema, dependencies and exact versions.
- Existing Challenge front matter, Flag count and answer format.
- Existing smoke/build workflows and catalog entry.
- Supplied PDFs, writeups and authoritative upstream source where relevant.

Do not assume the inventory summary is fully current. Read the actual source files and compare them with the original writeup/source. Keep the task limited to the selected Lab.

### B. Define the real objective

Write down, before implementation:

- The normal user-visible application flow.
- The actual vulnerable component and affected version.
- The exact input/request that reaches the vulnerable code.
- The intended attack chain and its boundaries.
- The OS identity of the vulnerable process.
- The exact Flag path(s), ownership and permissions.
- Explicitly excluded stages (for example SSH, container escape, Root or host access).

The Challenge should describe the scenario and objective, not give away the vulnerability, route, parameter, payload, credentials or exploit sequence.

### C. Implement the Lab and player materials

- Preserve genuine source components and versions; pin dependencies.
- Keep the original application behavior and visual assets where appropriate.
- Ensure the intended vulnerability is reachable through the normal exposed interface.
- Store the Flag at the natural target of the vulnerability: an existing database/business record, protected page/API response, application data, uploaded object or filesystem path as appropriate. Do not force every Flag into a local file. CI must bake the generated release value into the image at that location.
- Add a standalone `exploit.py` or equivalent independent player only when useful for the real intended route.
- Write a complete `writeup.md` that starts with reconnaissance and normal behavior, then explains discovery, exploitation, Flag retrieval, root cause and remediation.
- Do not put the answer or payload in the player-facing Challenge.

### D. CI-baked Flag and release consistency

The default trytopwn release model is **one versioned Flag set baked into the target image and synchronized to the bound Challenge**. Worker does not inject or generate Flags.

For each Lab release version:

- The CI/release generator creates cryptographically random Flag value(s) once for that version.
- Store the values in a versioned Manifest. Re-running or rebuilding the same version must reuse the same values; only a new release version may rotate them.
- During image build, place each Flag in the natural location required by the vulnerability and learning objective: database seed/business row, protected page data, application configuration, or a file when file access is actually the intended skill.
- Synchronize the exact same value(s) from that Manifest to every relevant Challenge `quiz.answer`. A focused Challenge may reuse the integrated Challenge's Flag when it intentionally tests the same stage.
- Build and publish the target image and Challenge metadata as one release unit. Do not independently hand-edit the image seed and Challenge answer.
- Container startup initializes services and imports the baked data; it must not generate a new Flag on every start. Restarting an instance or rebuilding the same release must preserve answer consistency.
- Mask generated Flag values in CI logs. Do not print secrets unnecessarily.
- The release workflow must build the target and run the real network-only exploit to retrieve the exact baked Flag **before** committing/publishing release artifacts.

Worker only receives the image binding and manages container lifecycle, resource limits and networking. It does not receive Flag environment variables, generate or rotate Flags, synchronize Challenge answers, or judge submissions.

A future per-instance dynamic-Flag model would require an explicit Web-backend protocol associating each running instance with its expected answer. That is not the current architecture and must not be implemented by silently adding Worker-side Flag injection.

Do not leave static placeholder answers such as `HTB{replace_this...}` in a completed Challenge.

### E. Lab-specific end-to-end CI is mandatory

Every Lab needs a dedicated E2E workflow that:

1. Loads the selected release version's deterministic Flag Manifest and checks baked target data = manifest = every relevant Challenge answer. A disposable test-only Flag may be used for isolated test runs, but it must not be confused with the published release answer.
2. Builds the real target image.
3. Starts the target with its actual runtime restrictions, healthcheck and resource limits.
4. Starts a separate attacker container/process on an isolated temporary Docker network.
5. Uses only the target's normal exposed network interface to perform the real intended reconnaissance/exploit path.
6. Verifies meaningful intermediate checkpoints where appropriate (for example service identity, recovered credential, template evaluation or command execution).
7. Retrieves the exact Flag through the intended vulnerability path and compares it byte-for-byte with the current CI Flag.
8. Fails on any broken stage, unexpected identity, missing Flag, mismatch, unhealthy service or timeout.
9. Captures useful diagnostics and always cleans up the target, attacker and temporary network.

Strict prohibitions for the attacker test:

- No target filesystem bind mount or shared volume to read the answer.
- No Docker socket.
- No `docker exec` to retrieve the Flag or perform the exploit.
- No direct database/file inspection that bypasses the player path.
- No mock vulnerability, fake callback endpoint or test-only backdoor.
- Never expose the intentionally vulnerable target to the public Internet.

A passing build, smoke test or healthcheck is **not** an E2E pass.

### F. Engineering smoke and curriculum consistency

Keep the existing build/start/health/smoke checks. Add the Lab's paths to the relevant workflow path filters so unrelated Labs are not rebuilt unnecessarily.

Update `web-curriculum.yml` to check the selected Lab's Flag generator determinism and target/Challenge consistency. Avoid duplicating unrelated test logic or changing unrelated Labs.

### G. Evidence and status

Only after the actual E2E workflow passes:

- Set `e2e_ci_status` to `passed`.
- Record the exact workflow path, successful run URL and tested commit SHA in `catalog/web-curriculum.json`.
- Update `lab_ci_status` and validated skills only when supported by that run.
- Update the inventory counts, completed-Lab section and next-Lab order.
- Update the design plan if its summary or current position changed.
- Never mark `passed` based only on code review, syntax checks, smoke tests or a historical run from another commit.

Use these E2E states consistently:

- `pending`: no dedicated Lab E2E workflow yet.
- `configured`: workflow exists but the latest relevant run has not passed.
- `passed`: the actual isolated attacker completed the intended path and retrieved the exact Flag.
- `failed`: the latest relevant E2E run failed; preserve the failure reason and fix it before merge.

## 4. GitHub collaboration and merge procedure

- Create one focused branch from the current `main` for the selected Lab.
- Keep the PR limited to that Lab, its Challenge/Writeup, its dedicated workflows, and the necessary catalog/inventory documentation.
- Run the actual PR checks. Read job steps and logs for failures; do not infer success from workflow creation or queued status.
- Fix failures in the same Lab branch. Re-run the checks after the final code change.
- Merge only when the Lab-specific E2E, image build/start/smoke and curriculum consistency checks pass.
- After merge, verify the main-branch E2E run and curriculum consistency run. Update the final evidence to the main commit/run.
- Do not claim the Lab is complete until the main-branch evidence is successful.
- Leave unrelated branches and PRs alone unless explicitly asked to clean them up.

## 5. Known lessons from completed Labs

- **Bike:** Handlebars 4.1.2 was not the vulnerable version for the reproduced chain; the Lab was corrected to affected 4.1.1. Verify dependency advisories and upstream versions before pinning a vulnerable package.
- **Precious:** a normal PDF conversion smoke test did not prove command injection. The independent HTTP attacker had to execute the actual PDFKit 0.8.6 path and read the exact Flag.
- **GoodGames:** the first E2E attempt exposed two real integration defects: the read-only target's `/data` tmpfs was not writable by UID/GID 1000, and the Flag response included a trailing newline not handled by the attacker's initial matcher. Fix the runtime mount ownership and parse the actual rendered output; do not weaken the Flag comparison.
- A failed CI run is useful evidence. Read its logs, identify the exact failed stage, fix the real cause and rerun. Do not conceal or relabel failures as passes.

## 6. Handoff checklist for a new conversation

When continuing this project in a new conversation:

1. Read this playbook.
2. Read the current `main` version of `catalog/web-curriculum.json` and `docs/EXISTING_WEB_LAB_RELEASE_INVENTORY.md`.
3. Confirm the current main commit and the next Lab in the inventory.
4. Inspect that Lab's actual files and original source/writeup before making changes.
5. Work on that one Lab only.
6. Do not ask the user to repeat the requirements in this document.
7. At the end, report only the meaningful result: what changed, E2E evidence, merge/main status, and the next Lab.

**Handoff rule:** always read the live catalog and inventory at the start of a session. They are the only source for completed/pending status and next-Lab selection.\n