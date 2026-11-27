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

### Current completed Labs

| Lab | Actual target path | E2E status |
|---|---|---|
| Bike | Handlebars 4.1.1 SSTI → command execution → one Web Flag | `passed` |
| Precious | PDFKit 0.8.6 / CVE-2022-25765 → command execution as ruby → one Web Flag | `passed` |
| GoodGames | SQLite login SQLi → weak MD5 recovery → reused admin credential → stored Jinja2 SSTI as augustus → one Web Flag | `passed` |
| Devvortex | Joomla 4.2.6 CVE-2023-23752 → admin template editor → www-data → one Web Flag; release `0.1.0` verified | `passed` |

Do not reinterpret these as Worker, platform synchronization or production deployment acceptance. Those are explicitly outside this workflow.

### Next Lab

Base has passed its full PHP 7.2 / Apache / OpenSSH / sudo find E2E with independently retrieved User and Root Flags. Do not rebuild it unless a regression is found. **Trick** is now the active Lab: its multi-service reconstruction and independent acceptance.py already exist; add/run the isolated DNS/HTTP/SSH E2E and random dual-Flag synchronization without performing Worker acceptance. Intense is deferred because it is an advanced SQLi/cryptographic composite. Devvortex has completed its Joomla 4.2.6 Web-only E2E path; do not re-open it unless a later regression is found.

After Base, follow the order in `docs/EXISTING_WEB_LAB_RELEASE_INVENTORY.md`: then evaluate Intense / Trick as their scope and readiness permit. Always re-read the live inventory because the order may change after a Lab is completed.

## 2. Non-negotiable user requirements

1. Work **one Lab at a time**. Do not batch several Labs; long sessions may be interrupted.
2. Prioritize Labs already present on `main`; do not invent or add unrelated new Labs.
3. Preserve real affected components and versions. No simulated vulnerable endpoints, fake interfaces, mock command execution, test backdoors or fabricated privilege-escalation chains.
4. If the original vulnerability cannot be reproduced with a real affected version/component, stop and explain the gap. Do not claim completion.
5. Follow the player's natural path: reconnaissance → normal browsing → observe requests/responses → discover clues → identify the component/version → exploit → retrieve the intended Flag. The player-facing Challenge must not reveal the vulnerability location or payload.
6. Reuse an existing front end or upstream project where appropriate; do not needlessly rebuild a page that already exists. Keep backend behavior faithful to the intended source.
7. Keep the scope appropriate to this platform: Linux Docker Labs. No Windows Labs, nested containers, container escape or host compromise. Do not force SSH/root stages onto a Web-only Lab.
8. Use one or two Flags according to the actual intended objective. A Web-only foothold Lab normally has one Web Flag; only create a Root Flag when the Lab genuinely includes a real, intended Linux privilege-escalation stage.
9. Keep images small: multi-stage builds where useful, minimal runtime packages, remove caches/build tools, use a non-root runtime user, healthchecks and resource limits.
10. Include a clear `README.md` and a discovery-led `writeup.md` for the Lab. Keep filenames compatible with the existing AttackBox parser; use simple names without spaces.
11. Do not ask the user to manually walk through the Lab or verify it. The Lab-specific GitHub Actions E2E must do this.
12. Do not manage or validate Worker synchronization, platform deployment, user accounts, or production runtime. The user explicitly does not want those tasks mixed into Lab completion.

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
- Keep Flag files outside application source code; copy/inject them into the target with deliberate ownership and permissions.
- Add a standalone `exploit.py` or equivalent independent player only when useful for the real intended route.
- Write a complete `writeup.md` that starts with reconnaissance and normal behavior, then explains discovery, exploitation, Flag retrieval, root cause and remediation.
- Do not put the answer or payload in the player-facing Challenge.

### D. Random Flag and release consistency

For Labs using generated Flags:

- Generate a cryptographically random Flag per CI instance/version.
- Keep a same-version manifest deterministic: re-running the same version must reuse the same Flag.
- A new release version may rotate the Flag.
- Synchronize exactly the same value across the target seed, release manifest and Challenge answer.
- Validate Flag format, number of quiz answers, `kind: flag`, and `lab:` metadata.
- Mask the Flag in CI logs. Never print secrets unnecessarily.
- The release workflow must build the target and run the same real network-only exploit to retrieve the exact Flag **before** committing release artifacts.

Do not leave static placeholder answers such as `HTB{replace_this...}` in a completed Challenge.

### E. Lab-specific end-to-end CI is mandatory

Every Lab needs a dedicated E2E workflow that:

1. Generates a fresh CI Flag and checks target seed = manifest = Challenge answer.
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

**Current handoff at creation:** Bike, Precious, GoodGames and Devvortex are the four Labs recorded as E2E-passed. Base is now complete under the current E2E standard. Re-read the design plan and inventory to choose the next single Lab. Re-check main before relying on this snapshot.
