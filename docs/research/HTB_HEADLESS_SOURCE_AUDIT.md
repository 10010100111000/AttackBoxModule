# HTB Headless — source audit and reconstruction notes

**Status:** Docker build and ordinary startup/health smoke checks passed; manual attack-path acceptance is pending. This is a reconstruction of the retired HTB machine's observable application and OS configuration, not the original VM image.

## Primary references

- Official machine page: https://www.hackthebox.com/machines/headless
- 0xdf write-up with disclosed application source: https://github.com/0xh7ml/htb-wiki/blob/38e5d0d0abc6bf85a52586b4221219b0e4b4eb2b/raw/htb-headless.md
- Write-up reproducing the full \`app.py\` and \`hackattempt.html\` source excerpt: https://github.com/ch3ng625/ch3ng625.github.io/blob/848c8e3e4d097515720a24c1600589705c8639ea/_posts/2024-07-21-headless.md
- Independent attack-path reference: https://writeups.csirt.muni.cz/content/htb/Machines/Headless/writeup/
- Independent \`syscheck\` source and sudo-path reference: https://github.com/evyatar9/Writeups/blob/3d40d78dd2cf9ce34cc48db405e1b46b076e5b72/HackTheBox/Headless/README.md

The official synopsis identifies a Python Werkzeug website, a support form vulnerable to blind XSS through the User-Agent header, admin cookie theft, dashboard command injection, and a Linux privilege escalation stage. Public references identify Python 3.11.2 and Werkzeug 2.2.2; they do not establish the exact Flask version. This reconstruction pins Flask 2.2.2 as a compatible implementation choice, not as a claim about the original package version.

## Observed target characteristics

| Item | Observed value |
|---|---|
| OS | Debian 12 |
| Web listener | TCP 5000 |
| SSH listener | TCP 22 |
| HTTP server | Werkzeug 2.2.2 |
| Python | 3.11.2 |
| Public pages | \`/\`, \`/support\` |
| Protected page | \`/dashboard\` |
| Report page | \`/hacking_reports/<integer>\` |
| Web identity | \`dvir\`, UID 1000 |
| User flag | \`/home/dvir/user.txt\` |
| Root flag | \`/root/root.txt\` |
| Root entry | \`sudo -n /usr/bin/syscheck\` |

## Source-backed application behavior

The following code is reproduced from public source excerpts in the references above. It is not a guessed generic Flask vulnerability.

### 1. Cookie creation and role selection

The root route checks whether the request originates from loopback. Local requests receive the signed \`admin\` value; other clients receive \`user\`. The cookie name is \`is_admin\`, and the original sets \`httponly=False\`.

The disclosed source uses:

- \`URLSafeSerializer\` from itsdangerous
- Secret key \`PcBE2u6tBomJmDMwUbRzO18I07A\`
- \`serializer.dumps(token)\`
- \`response.set_cookie('is_admin', serialized_value, httponly=False)\`

The exact public user-cookie example is \`InVzZXIi.uAlmXlTvm8vyihjNaPDWnvB_Zfs\`; the public admin-cookie example is \`ImFkbWluIg.dmzDkZNEm6CK0oyL1fbM-SnXpH0\`. These are reference values only, not challenge Flags.

### 2. Support form and header reflection

The disclosed \`POST /support\` handler checks the \`message\` field for either angle-bracket pairs or a double-curly-brace pair. When the condition is met, it records:

- request method;
- full request URL;
- request headers, including User-Agent.

The code formats the headers into HTML, renders \`hackattempt.html\`, writes the resulting HTML to a randomly named file in \`/home/dvir/app/hacking_reports\`, and returns the report page.

The disclosed template uses \`{{ request_info | safe }}\`. This is the actual HTML output context: the report intentionally renders request-header values without escaping. The browser review process then opens the stored report, which is why a User-Agent payload can execute in the administrator's browser context.

### 3. Admin report review

The original application directory contains \`inspect_reports.py\` and \`hacking_reports/\`; independent write-ups document an automated process that reviews newly stored reports. The reconstruction uses a real headless Chromium browser process, not a JavaScript interpreter or a simulated callback. It first visits the site through loopback to obtain the signed admin cookie, then opens each newly stored report URL.

The browser reviewer is a separate process from the Flask application. It does not evaluate a supplied payload itself; Chromium renders the same stored HTML report page that an administrator reviews.

### 4. Dashboard command injection

The disclosed \`POST /dashboard\` handler reads the \`date\` form field and passes it to:

\`\`\`python
script_output = os.popen(f"bash report.sh {date}").read()
\`\`\`

The command is executed by Bash as the Flask service account, \`dvir\`. The accompanying \`report.sh\` is a small helper that prints the normal system-health message. The vulnerable string construction is retained; no fake command endpoint is introduced.

### 5. Linux privilege boundary

The public \`/usr/bin/syscheck\` script checks for EUID 0, prints kernel/disk/load information, then tests for an \`initdb.sh\` process. If one is not running, it executes:

\`\`\`bash
./initdb.sh 2>/dev/null
\`\`\`

That is a relative path resolved against the caller's current working directory. The original sudo rule is:

\`\`\`
dvir ALL=(ALL) NOPASSWD: /usr/bin/syscheck
\`\`\`

The reconstruction retains the actual script logic and sudo boundary. The intended working directory for the exercise is \`/home/dvir/app\`, which is writable by dvir.

## Reconstruction choices and boundaries

- The Flask route behavior, signed cookie logic, unsafe report template, report helper and sudo script are sourced from disclosed original-machine code or repeated independent observations.
- The exact original CSS and every original template asset were not publicly recovered. The page styling is a compact visual reconstruction; the route names, form fields, data flow and vulnerable contexts are preserved.
- The original Flask version is not confirmed by the available public source excerpt. Flask 2.2.2 is pinned for the reconstruction; Python 3.11.2 and Werkzeug 2.2.2 are the publicly observed runtime versions.
- The original report-review Python source was not fully recovered. The replacement uses real Chromium to visit the real stored report page, preserving the browser trust boundary and observable blind-XSS behavior.
- The original root stage does not require container escape. It is an ordinary relative-path execution flaw in a root-run shell script.
- The target runs the real Flask/Werkzeug app, Chromium browser, OpenSSH daemon, sudo and Bash. It does not emulate command output or fake a shell.

## Container and flag model

One target template, slug \`htb-headless\`, exposes TCP 5000 and TCP 22. The Worker injects a per-instance User Flag and Root Flag:

- \`HEADLESS_USER_FLAG\` → \`/home/dvir/user.txt\`, owner dvir, mode 0400.
- \`HEADLESS_ROOT_FLAG\` → \`/root/root.txt\`, owner root, mode 0600.

The image contains no default production Flag values. Startup fails if the Worker does not provide both values. No persistent volume is declared, so a new target instance starts with clean report storage and new Worker-provided Flags.

## Acceptance policy

CI is intentionally limited to image build, container startup, health, homepage, support form, SSH listener and admin-review process availability. It must not automate XSS exploitation, cookie theft, command injection, reverse shells, sudo exploitation or Flag extraction.

Manual review must verify the full observed path against a fresh target instance before release. Worker deployment, network isolation and resource limits are separate release gates.
