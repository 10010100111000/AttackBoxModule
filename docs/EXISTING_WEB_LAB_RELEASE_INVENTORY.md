# Existing Web Lab Inventory and Release Readiness

**Snapshot:** 2026-11-27  
**Scope:** Existing Labs only. No new Lab research or implementation is authorized by this inventory.

## Executive summary

The curriculum catalog currently contains 27 Lab records:

| Catalog CI state | Count | Meaning |
| --- | ---: | --- |
| \`full_chain_ci\` | 17 | README/catalog records independent end-to-end CI evidence |
| \`partial\` | 5 | Some real behavior is tested, but the complete intended chain is not proven |
| \`unverified\` | 5 | No sufficient end-to-end CI evidence recorded |

Important cross-cutting status:
- **Worker integration:** all 27 catalog records currently say \`not_verified\`.
- **Manual acceptance:** all 27 records currently say \`not_reviewed\`.
- **Platform challenge sync:** must be checked per Challenge; a Lab CI pass does not prove Markdown import, Flag grading, target binding or user progress.
- **Release markers:** 10 Labs currently have \`.release-blocked\` markers: Alert, Editorial, Precious, WonderCMS XSS, Usage, NodeBlog, Zipping, Soccer, Trick and Intense.
- A \`full_chain_ci\` label means the documented disposable CI path passed; it does not mean the Lab is ready for public release.

## A. First candidates for platform onboarding

These have full-chain CI evidence in the catalog and no current release-block marker. They are the best candidates for the next platform integration pass, subject to reviewing each workflow and confirming the evidence still matches the current main commit.

| Lab | Main Web learning objective | Recorded CI evidence | Remaining gate / note |
| --- | --- | --- | --- |
| Nibbles | Nibbleblog plugin upload / CMS RCE | [Run 44954697830](https://github.com/10010100111000/AttackBoxModule/actions/runs/44954697830) | Worker lifecycle, target resource/network profile, platform Flag submission |
| Bashed | Exposed phpbash interface discovery | [Run 45073735584](https://github.com/10010100111000/AttackBoxModule/actions/runs/45073735584) | Worker lifecycle and platform grading |
| Cap | IDOR / direct object access | [Run 45073735596](https://github.com/10010100111000/AttackBoxModule/actions/runs/45073735596) | Worker lifecycle and platform grading |
| Photobomb | ImageMagick command injection | [Run 45073735570](https://github.com/10010100111000/AttackBoxModule/actions/runs/45073735570) | Worker lifecycle and platform grading |
| Shocker | Bash CGI Shellshock | [Run 44955028484](https://github.com/10010100111000/AttackBoxModule/actions/runs/44955028484) | Worker lifecycle and platform grading |
| Bountyhunter | Real SimpleXML XXE | [Run 45166657846](https://github.com/10010100111000/AttackBoxModule/actions/runs/45166657846) | Worker lifecycle and platform grading |
| OpenAdmin | ONA xajax RCE / service pivot | [Run 45166657718](https://github.com/10010100111000/AttackBoxModule/actions/runs/45166657718) | Worker lifecycle and platform grading |
| Validation | Second-order SQLi / MariaDB FILE | [Run 45166657712](https://github.com/10010100111000/AttackBoxModule/actions/runs/45166657712) | Worker lifecycle and platform grading |
| Pebbles | ZoneMinder SQLi / DB file operations | [Workflow evidence](../.github/workflows/pebbles-full.yml) | Historical stack and Worker compatibility need careful review |
| Django Debug XSS | Django technical-500 XSS / authenticated headless editor | [Run 45233000605](https://github.com/10010100111000/AttackBoxModule/actions/runs/45233000605) | Worker browser/network/resource profile and platform grading |

**Suggested order:** Nibbles, Cap, Bashed, Photobomb, Shocker, Bountyhunter, OpenAdmin, Validation, Django Debug XSS, then Pebbles. This order favours focused Web objectives and avoids beginning with the more unusual resource/capability profile.

## B. Full-chain CI passed, but release marker remains

These are not new-development candidates. Their next work is specific release-gate closure.

| Lab | Verified Web path | Recorded evidence | Explicit remaining issue |
| --- | --- | --- | --- |
| Editorial | SSRF → internal API → SSH/Git history → GitPython UID 0 | [Run 45180593763](https://github.com/10010100111000/AttackBoxModule/actions/runs/45180593763) | Worker network isolation and required target capability/resource profile |
| Usage | Boolean/time SQLi → Laravel Admin upload → Web/Linux chain | [Run 45386437038](https://github.com/10010100111000/AttackBoxModule/actions/runs/45386437038) | Worker integration; reconstruction differences must remain visible in challenge notes |
| NodeBlog | NoSQLi → XXE → node-serialize RCE | [Historical run 45466022851](https://github.com/10010100111000/AttackBoxModule/actions/runs/45466022851) | New three-Flag acceptance passed manually in run [45809898571](https://github.com/10010100111000/AttackBoxModule/actions/runs/45809898571); sync three Challenges and verify platform binding/progress |
| Zipping | ZIP symlink → SQLi/FILE → PHP include | [Run 45471673982](https://github.com/10010100111000/AttackBoxModule/actions/runs/45471673982) | Confirm the direct symlink Flag path is reflected in the intended Challenge; retain documented extractor divergence |
| Soccer | Tiny File Manager → vhost discovery → WebSocket blind SQLi | [Run 45478649027](https://github.com/10010100111000/AttackBoxModule/actions/runs/45478649027) | Worker network/port exposure and platform grading |
| WonderCMS XSS | Real WonderCMS reflected attribute XSS → admin browser → Flag callback | [Run 45229393592](https://github.com/10010100111000/AttackBoxModule/actions/runs/45229393592) | Worker browser sandbox/network/resource acceptance |
| Alert | Stored Markdown XSS → Chromium → loopback reader | [Run 45474730425](https://github.com/10010100111000/AttackBoxModule/actions/runs/45474730425) | Actual Web Flag extraction is not yet proven; must finish before onboarding |
| Precious | Native PDFKit 0.8.6 command injection | Pending | Full HTTP-only Flag extraction acceptance not yet passed |
| Trick | DNS/SQLi/LFI/SSH/Fail2ban chain | Pending | Independent CI and Worker verification |
| Intense | SQLite conditional-error SQLi → session forgery → path traversal | Pending | Initial implementation only; build and complete acceptance required |

## C. Partial implementation: finish or consciously narrow scope

| Lab | Existing real implementation | What is missing |
| --- | --- | --- |
| Bike | Handlebars 4.1.2 SSTI | Independent full-chain test of the intended expression/object-access path |
| GoodGames | Login SQLi → stored Jinja2 SSTI | Complete independent Web Flag acceptance; keep its deliberate Web-only scope |
| Devvortex | Joomla 4.2.6 information disclosure | Complete the actual intended Web path; Apport Root is not yet accepted |
| Base | PHP 7.2 strcmp authentication and upload | Independent test proving the real login/upload sequence and Flag reachability |
| Funnel | FTP/SSH/PostgreSQL tunnel | Decide whether to keep in Web catalogue or classify under network services; verify its actual objective |

## D. Unverified / not yet suitable for onboarding

| Lab | Catalog observation | Next action |
| --- | --- | --- |
| Cursed Stale Policy | CSP/XSS/WebSocket code exists; no confirmed browser attack-chain acceptance | Inspect the real intended flow; do not count CSP bypass as covered until proven |
| Precious | Native PDFKit code is implemented, but no successful independent acceptance recorded | Run the dedicated manual acceptance before any release decision |
| Trick | Full reconstruction exists, but no independent CI evidence recorded | Build and validate the actual chain in a disposable runner |
| Intense | Initial Web-only implementation; no build/manual/Worker acceptance | Finish basic startup, then HTTP-only end-to-end test |
| Base | Basic implementation, no full acceptance | Add an external test client and verify the actual login/upload route |

Note: Precious, Trick and Intense are also listed in the blocked-marker section above; this section describes their technical acceptance state, not an additional Lab count. Base is listed under partial implementation because the source/catalog records a concrete implementation but no CI proof.

## E. Current coverage gaps using existing Labs

Before creating anything new, reuse and split existing targets into multiple Challenges where the real application surfaces support it:

- **XSS:** Alert, WonderCMS XSS, Django Debug XSS. Add separate Challenges for distinct real contexts only after each path is validated.
- **SQLi:** Usage, NodeBlog, Zipping, Soccer, Union, Validation, Pebbles, GoodGames. Prefer distinct variants (blind, second-order, file operations, WebSocket) over more generic SQLi Labs.
- **SSRF:** Editorial already covers basic and internal enumeration. Do not create another basic SSRF target before a distinct bypass/Blind SSRF candidate is necessary.
- **SSTI:** Bike and GoodGames already provide two different real template engines/contexts; finish them before adding another.
- **XXE:** Bountyhunter and NodeBlog already cover distinct PHP/libxml2 paths; NodeBlog also has its own cumulative Challenge model.
- **IDOR:** Cap is an existing candidate; inspect whether its current Challenge and Flag expose the authorization boundary clearly.
- **File upload / file read:** Nibbles, Zipping, Soccer and Base offer different parser, CMS, and foothold contexts.

The current backlog has 35 tracked learning objectives, including several already implemented by these Labs. Do not create a new Lab simply because a backlog item exists; first map it to an existing Lab and determine whether a separate Challenge can teach it.

## F. Standard onboarding checklist

A Lab is eligible for platform onboarding only when its relevant checks are complete:

1. **Source fidelity:** affected real component/version and any reconstruction differences documented.
2. **Build/start:** deterministic image build, service health, no hidden manual setup.
3. **Player proof:** a separate HTTP/VPN-only player reaches the actual Flag through the intended vulnerable path. No target \`docker exec\`, no fake exploit endpoint.
4. **Flag contract:** Flag is placed in a real application/business data location appropriate to the vulnerability (database row, user/order record, API response, admin-visible content, template context, uploaded object or local file); generated/seeded value equals the Challenge answer; restart/reset semantics are known. Local-file Flags are only required when file access is part of the learning objective.
5. **Resource profile:** image size, idle/active memory, CPU/process use and required ports measured.
6. **Worker smoke:** start, inspect, stop, reset, per-user isolation and special capabilities checked against the real Worker.
7. **AttackBox sync:** Challenge Markdown imports; correct target template; expected Flag stage count; independent per-user/per-Challenge progress.
8. **Release decision:** remove \`.release-blocked\` only after the above gates pass.

CI policy:
- Ordinary PR CI: syntax, taxonomy, build, startup, health and non-offensive regression only.
- Dedicated manual disposable-runner acceptance: real intended player path, using an isolated test client and fresh targets.
- No production server is used for development acceptance.

## G. Immediate execution plan

1. Finish Alert's actual Flag extraction acceptance.
2. Complete the NodeBlog three-Challenge content sync already designed; its manual three-Flag acceptance has passed.
3. Select the first 3–5 Labs from section A and verify Worker lifecycle/resource compatibility.
4. Import those Challenge documents into AttackBox and confirm target template + Flag grading.
5. Continue in batches; do not start Open WebUI, VAmPI or other new Lab implementations until the existing inventory has been triaged.

