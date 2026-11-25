# ImpressCMS 1.4.2 — source audit and multi-Challenge build plan

**Status:** source review in progress. No Docker image is ready or released. This document records verified upstream source facts and the remaining build blockers.

## 1. Pinned upstream source

- Project: [ImpressCMS/impresscms](https://github.com/ImpressCMS/impresscms)
- Release tag: \`v1.4.2\`
- Resolved commit: \`56caca0356646ad29497ce877589326a4a76123b\`
- Tag ref: https://github.com/ImpressCMS/impresscms/tree/v1.4.2
- Official SourceForge release page: https://sourceforge.net/projects/impresscms/files/v1.4.2/
- Release package listed: \`impresscms-1.4.2.zip\`, 24.2 MB, dated 2020-12-26.
- The tag's \`htdocs/include/version.php\` declares ImpressCMS 1.4.2, build 100.
- The release notes mention PHP 7.4 compatibility work. Treat PHP 7.4 as the initial compatibility target, not a final runtime decision.

Core files inspected directly from the pinned tag:

| File | Blob SHA | Finding |
|---|---|---|
| \`htdocs/include/findusers.php\` | \`615325a391ba11b5aa893962371c502eae1276f3\` | Token-only access check and \`groups\` request handling |
| \`htdocs/libraries/icms/member/Handler.php\` | \`440a7b633b85521c62ba0312605e624d9dfc0e29\` | Group IDs interpolated into SQL \`IN (...)\` |
| \`htdocs/libraries/image-editor/image-edit.php\` | \`a220b4615ecfc7fcaf611fd3e2d8e2791d5bf19c\` | \`image_temp\` is joined to the image-editor temp directory and used in file reads/copies |
| \`htdocs/modules/system/admin/autotasks/class/autotasks.php\` | \`c51df96be16f3b10b77586ecf406aff7f141a1e5\` | Stored \`sat_code\` is passed to PHP \`eval()\` in the scheduled-task execution path |
| \`htdocs/plugins/preloads/autologin.php\` | \`6d2f3195ac38bbcf994f985505a84480d2c2c974\` | Autologin logic; exact CVE type-confusion expression still needs reconciliation |
| \`htdocs/modules/system/admin/mimetype/main.php\` | \`c16f83937e23572747e7552780d161c88ce11a13\` | Mimetype admin handler; GET \`mimetypeid\` is cast to int here |
| \`htdocs/modules/system/admin/mimetype/class/mimetype.php\` | \`9bb78989a6001152220171a50b05a0ad37fc1eaf\` | Mimetype object and handler; reported SQLi flow needs further tracing |

## 2. Confirmed or strongly source-supported findings

### A. Findusers function-level access control — CVE-2021-26598

- HackerOne: https://hackerone.com/reports/1081137
- Source: \`htdocs/include/findusers.php\`
- The page starts with \`$denied = true\`.
- If a request supplies a token and \`icms::$security->validateToken($_REQUEST['token'], false)\` succeeds, it sets \`$denied = false\`; this branch does not require an authenticated user.
- If no token is supplied, the alternative path checks whether the current user is an administrator.
- Teaching focus: token availability, authentication versus CSRF-token validation, and function-level authorization.

### B. Findusers groups SQL injection — CVE-2021-26599

- HackerOne: https://hackerone.com/reports/1081145
- Source: \`htdocs/include/findusers.php\` and \`htdocs/libraries/icms/member/Handler.php\`
- Advanced search renders a multi-select field named \`groups\`.
- On form submission, \`$_POST['groups']\` is passed to \`getUserCountByGroupLink()\` and \`getUsersByGroupLink()\`.
- Both functions build \`m.groupid IN (...)\` with \`implode(", ", $groups)\`, without validating each array member as an integer at this call boundary.
- Teaching focus: trace an ordinary form field through application handlers into a real SQL statement. Public analysis describes Boolean-based extraction; keep stacked-query behavior out of the initial scope.

### C. Image editor path traversal — CVE-2021-26601

- HackerOne: https://hackerone.com/reports/1081878
- Source: \`htdocs/libraries/image-editor/image-edit.php\`
- The \`image_temp\` value is accepted as a string and later concatenated to \`ICMS_IMANAGER_FOLDER_PATH . '/temp/'\` for file reads and copies.
- Teaching focus: path handling in a real authenticated image-editor workflow, not a synthetic download endpoint.

### D. Autotasks PHP code execution — CVE-2021-47938

- NVD: https://nvd.nist.gov/vuln/detail/CVE-2021-47938
- ExploitDB: https://www.exploit-db.com/exploits/50298
- Source: \`htdocs/modules/system/admin/autotasks/class/autotasks.php\`
- The scheduled-task object stores \`sat_code\`; the execution method retrieves it and calls PHP \`eval($code)\`.
- The feature is in the system administration area and requires an authenticated administrative workflow.
- Teaching focus: understand a real application feature that stores and later evaluates PHP code. The challenge must accurately describe the required role and avoid pretending this is unauthenticated RCE.

## 3. Findings requiring more source reconciliation

### E. Content Manager Display Name XSS — CVE-2021-28088

- HackerOne: https://hackerone.com/reports/1119296
- Reported source path: \`modules/content/admin/content.php\`
- The Content Manager is a separate ImpressCMS add-on, not present in the pinned core \`v1.4.2\` Git tree.
- The official add-on listing identifies **Content 1.2.1 Final**, published 2017-04-24, download item ID 5:
  https://www.impresscms.org/modules/downloads/index.php?category_id=3
- Before implementing the XSS Challenge, obtain the exact official Content 1.2.1 archive, record its SHA-256, inspect the vulnerable Display Name field and confirm the actual output context and persistence behavior.
- Do not label it stored XSS until the report and source prove that the value is persisted.

### F. Autologin type confusion — CVE-2021-26600

- HackerOne: https://hackerone.com/reports/1081986
- NVD: https://nvd.nist.gov/vuln/detail/CVE-2021-26600
- The pinned \`autologin.php\` has a \`is_numeric($pass)\` guard and a loose comparison later in the flow. Map the exact vulnerable comparison described by the report to the 1.4.2 source before authoring a Challenge. Do not infer the payload or bypass from the CVE title alone.

### G. Mimetype SQL injection — CVE-2022-26986

- NVD: https://nvd.nist.gov/vuln/detail/CVE-2022-26986
- Public exploit reference: https://github.com/sartlabs/0days/blob/main/ImpressCMS1.4.3/Exploit.txt
- Affected through 1.4.3, so 1.4.2 is in the affected range.
- The inspected \`mimetype/main.php\` casts the GET \`mimetypeid\` to int, and the object declares the field as integer. Trace the full POST / controller / SQL path in the pinned 1.4.2 source before deciding whether and how to include this Challenge.

### H. Other reported issues

- CVE-2022-24977 is listed as affecting versions before 1.4.2; do not assume the pinned 1.4.2 release is affected.
- CVE-2023-37785 references \`editprofile.php\`, which is not present at the root of the pinned 1.4.2 core tree. Identify its actual component/version before adding it.
- Continue checking HackerOne reports and upstream release notes for other 1.4.2 findings. Every verified issue can become its own Challenge, regardless of category.

## 4. Planned Challenge set on one target

One target template, slug \`impresscms\`, should serve multiple independent Challenge records:

| Planned Challenge | Category | Source status |
|---|---|---|
| Findusers authorization | Access Control | Core path and check identified |
| Findusers groups | SQL Injection | Core data flow identified |
| Image editor temp path | Path Traversal | Core path identified |
| Autotasks | Server-side Code Injection | Core eval sink identified |
| Content Display Name | XSS | Official add-on archive still required |
| Autologin | Authentication | Exact type-confusion condition pending |
| Mimetype | SQL Injection | Exact vulnerable request flow pending |

Each Challenge will have its own title, description, difficulty, hints, answer/Flag and learner progress. All Challenges use the same target slug and share the same per-user target instance. A Challenge does not need multiple Flags; one meaningful final answer is sufficient. Add a composite Challenge only if it adds a distinct learning outcome.

Do not force these findings into one linear exploit chain. They are separate features and may have different role requirements.

## 5. Container and platform implementation gates

1. Obtain and pin both core v1.4.2 and the official Content 1.2.1 add-on archive.
2. Record hashes and license metadata for both archives.
3. Identify PHP extensions and the MariaDB/MySQL compatibility range from the installer and upstream docs.
4. Determine whether PHP/Apache and MariaDB can run reliably in one container with a small process supervisor, as required by the current target-image model. If not, report the trade-off before changing the platform's one-template/one-image design.
5. Automate first-install provisioning and seed a deterministic, isolated dataset. Do not leave the interactive installer exposed to learners.
6. Define separate Flag locations/data for each Challenge. One Challenge must not invalidate the data or state needed by another.
7. Measure actual image size, startup time and steady-state memory.
8. CI only verifies image build, startup, healthcheck and normal CMS workflows. Do not add automated XSS, SQLi, authorization-bypass, code-execution, exploit-chain or Flag-extraction tests.

**Current state:** core source pin and initial source mapping complete. Content add-on archive, installer automation, Docker topology and runtime measurements are not yet complete. No image has been built or published.
