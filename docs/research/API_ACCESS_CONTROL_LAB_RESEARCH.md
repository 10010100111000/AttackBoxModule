# API / Access Control Lab — source research and candidate decision

**Date:** 2026-11-27  
**Status:** research only; no runtime code or challenge files changed.

## Decision summary

Recommend **VAmPI (erev0s/VAmPI)** as the first lightweight API / Access Control Lab candidate. Keep **OWASP crAPI** as a later, broader API capstone/reference, not the first implementation.

Why VAmPI first:
- It is an existing open-source Flask + Connexion REST API with a published OpenAPI 3 document and Swagger UI; it is not a scenario invented for trytopwn.
- The upstream repository provides the vulnerable application code, Dockerfile, OpenAPI spec and Postman collection.
- The author published a detailed article identifying the exact source functions responsible for BOLA, mass assignment, unauthorized password change, excessive data exposure and SQL injection.
- It is a single application container with SQLite, so it better matches the current one-target-container / Worker lifecycle model and small-resource preference.
- The application is API-first; Swagger UI is the native discovery interface. A separate custom frontend is not required.

Pinned source reviewed:
- Repository: https://github.com/erev0s/VAmPI
- Reviewed commit: \`f16052dce83f05847133ec98f01c5193a41de7d8\` (2026-04-07)
- License: MIT (confirm and retain upstream notices when vendoring).
- Upstream Dockerfile uses a Python 3.11 Alpine builder/runtime multi-stage layout.
- Runtime dependencies in \`requirements.txt\`: Connexion 2.14.2, Flask 2.2.2, Flask-SQLAlchemy 3.0.3, SQLAlchemy 2.0.2, PyJWT 2.6.0, jsonschema 4.17.3 and Swagger UI bundle.

## Candidate comparison

| Candidate | Source and learning evidence | Runtime fit | Decision |
| --- | --- | --- | --- |
| VAmPI | Upstream source, OpenAPI 3, Swagger UI, author vulnerability analysis and independent walkthrough | One Flask API container + SQLite; small and simple | **First candidate** |
| OWASP crAPI | OWASP project; official challenge list and challenge solutions cover BOLA, BFLA, mass assignment, JWT, SSRF and business flows | Microservices; minimal compose documents ~800 MB reservations, ~3.2 GB limits and around 2 CPUs | Later advanced reference; too heavy for first single-target Lab |

crAPI references:
- https://github.com/OWASP/crAPI
- https://owasp.github.io/www-project-crapi/
- https://github.com/OWASP/crAPI/blob/develop/docs/challenges.md
- https://github.com/OWASP/crAPI/blob/develop/docs/challengeSolutions.md
- https://github.com/OWASP/crAPI/blob/develop/deploy/docker/docker-compose.minimal.yml

VAmPI references and walkthroughs:
- https://github.com/erev0s/VAmPI
- https://erev0s.com/blog/vampi-vulnerable-api-security-testing/
- https://zerodayhacker.com/vampi-walkthrough/
- https://github.com/erev0s/VAmPI/blob/master/openapi_specs/openapi3.yml

## Verified real vulnerability locations in VAmPI source

These are source-level findings from the pinned upstream code, not proposed fake routes.

### 1. BOLA — cross-user book secret

- File: \`api_views/books.py\`
- Function: \`get_by_title(book_title)\`
- Vulnerable query: \`Book.query.filter_by(book_title=str(book_title)).first()\`
- The vulnerable branch does not scope the book lookup to the authenticated user. The non-vulnerable branch includes \`user=user\`.
- A valid Bearer token is required, but another user's book secret can be read by title.
- This is a clean API1/BOLA objective with a natural data object and secret field.

### 2. Mass assignment — self-register as administrator

- File: \`api_views/users.py\`
- Function: \`register_user()\`
- The OpenAPI registration schema only declares username, password and email.
- The implementation nevertheless accepts an extra \`admin\` property when \`vuln=1\`, and uses it to set the new account's administrator boolean.
- The behavior can be observed through the genuine \`/me\` endpoint, which returns the authenticated account's \`admin\` property.
- This is a distinct API3/Broken Object Property Level Authorization / mass-assignment learning objective.

### 3. Unauthorized password change — cross-user object authorization

- File: \`api_views/users.py\`
- Function: \`update_password(username)\`
- A valid Bearer token is checked, but the vulnerable branch selects the account using the URL's \`username\` parameter rather than the authenticated token subject.
- The secure branch selects the user from \`resp['sub']\`.
- This is a second independent cross-user authorization failure and can be validated by changing a second test account's password, then authenticating as that account.

### 4. Excessive data exposure / unauthenticated debug endpoint

- File: \`api_views/users.py\`
- Function: \`debug()\`
- Returns \`User.get_all_users_debug()\`, including username, password and admin fields, without an authentication check.
- The route is explicitly present in the OpenAPI spec; the author notes it could be removed from the spec for discovery practice.
- This is a separate information-disclosure challenge, not a prerequisite for the three access-control objectives.

### 5. Additional candidates (not in first scope)

- SQL injection: \`models/user_model.py::User.get_user()\` uses string interpolation into a SQLAlchemy text query.
- User/password enumeration: \`api_views/users.py::login_user()\` returns different messages for unknown username and incorrect password.
- Weak JWT signing secret: \`config.py\` sets \`SECRET_KEY = 'random'\`; \`models/user_model.py\` signs HS256 tokens using this value.
- Regex denial of service and missing rate limits are documented by the upstream author, but should not be included in the initial Lab because they create unnecessary availability/resource risk.

## Proposed Challenge layout

One VAmPI Lab, multiple independent Challenge folders, all bound to \`lab: vampi\`. Do not add cross-Challenge auto-unlock. Do not force unrelated objectives into a cumulative chain.

| Proposed display name | Main objective | Upstream mechanism | Relationship |
| --- | --- | --- | --- |
| Quiet Shelf | Read another user's book secret | BOLA in \`get_by_title\` | Independent |
| Paper Crown | Register an account with an elevated role and verify the role | Mass assignment in \`register_user\` | Independent |
| Borrowed Identity | Change a different account's password using the authenticated API session | \`update_password\` uses path username instead of token subject | Independent |
| Debug Drawer | Discover the debug response exposing all account properties | Unauthenticated \`debug()\` | Independent |

A later integrated assessment can be considered only if there is a genuine workflow joining these objectives. Do not create an artificial dependency simply to increase Flag count.

Flag design should follow the already-approved CI versioning convention:
- short random \`TTP{16-lowercase-base32}\` values;
- generated once per Lab release version and reused for repeat builds of that version;
- injected into real application data fields that are already returned by the vulnerable behavior;
- Challenge Markdown answers generated from the same version manifest;
- no Worker-side Flag generation or grading.

Potential natural Flag placement needs one design pass before implementation:
- Quiet Shelf: store Flag in a seeded victim-owned book's existing \`secret_content\` field.
- Paper Crown: store a Flag in an existing admin-only business object or use a question checkpoint for the \`admin=true\` observation if the upstream app has no natural privileged data response. Do not invent an unrelated endpoint just to expose a Flag.
- Borrowed Identity: place a Flag in a victim account's existing protected book secret or account data and make the unauthorized password change the necessary access step; validate the path end-to-end.
- Debug Drawer: use a seeded account field returned by the real debug response, if this is selected as a Challenge.

## Important implementation cautions

1. **Do not blindly copy the latest upstream branch.** Pin the reviewed commit and inspect the complete dependency graph and license before vendoring.
2. **The upstream app has debug mode enabled** in \`app.py\` (\`vuln_app.run(..., debug=True)\`). Decide whether to disable only the interactive debugger in the training wrapper while retaining the documented API flaws; never expose Flask's interactive debugger to a shared/public network.
3. The app uses a fixed weak JWT secret \`random\`, stores plaintext passwords, and has a database initialization route \`/createdb\` that drops and recreates tables. These are upstream behaviors. Keep the target isolated; do not make \`/createdb\` part of normal player workflow.
4. The API is pure REST with Swagger UI, not a rich consumer-facing website. This is appropriate for an API-specialist Lab; do not spend time inventing a fake storefront frontend.
5. Preserve upstream vulnerable functions. Any changes should be limited to deterministic seed data, generated Flags, safe startup/health handling, and disabling dangerous debug tooling where it is not part of the intended objective.
6. Do not add DoS, RegexDOS or brute-force exercises to the first release.
7. Validate each Challenge over HTTP using two real accounts. Use the upstream API behavior; no fake endpoints or simulated authorization logic.

## Next work sequence

1. Finish Alert's outstanding end-to-end Web Flag acceptance. Current evidence proves genuine Chromium stored-XSS execution and local source disclosure, but the README still marks final Flag extraction as pending. Do not mark Alert complete until the actual Flag reaches the external test player on two clean instances and the result is submitted to the platform.
2. Create a separate VAmPI Lab implementation branch from the pinned upstream commit.
3. Build the smallest viable one-container image, preserve the actual Flask/Connexion app and Swagger UI, and add deterministic startup/health checks.
4. Implement only the approved access-control Challenge set and versioned Flag generation.
5. Add a manual GitHub-hosted Linux Runner acceptance that exercises each objective with separate user accounts and verifies the generated Flag answers.
6. Sync separate Challenge Markdown files into AttackBox; all share one target template and user-selected progress remains per Challenge.

**No runtime code, challenge content, Dockerfile or Flag has been changed by this research document.**
