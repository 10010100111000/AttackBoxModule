# NodeBlog — Web-only authentic attack-chain reconstruction

**Status:** independent black-box full Web chain CI **PASS** on two fresh isolated instances; Worker release not yet assessed. Not an official Hack The Box image. Do not deploy to the public Internet.

## Scope and source fidelity

This reproduces the observable **Web** sequence documented for the retired HTB NodeBlog machine, created by ippsec (2022):

1. Discover a simple Express blog and its login form.
2. Send structured JSON to the form endpoint; native **MongoDB** interprets an injected query operator, bypassing the account password check.
3. The signed account cookie unlocks a blog article editor and **XML upload**.
4. The real **libxml2** parser, called with `noent: true`, resolves an external entity and discloses `/opt/blog/server.js`.
5. Source reveals `node-serialize@0.0.4`, which executes an IIFE during deserialization of an untrusted `auth` cookie **before** verifying its signature (CVE-2017-5941).
6. The Web process runs as `nodeblog` and can obtain `/home/nodeblog/user.txt` through actual OS command execution.

**No** SSH, sudo, Linux root, privileged containers, or container escape. This is deliberate: the training objective is Web exploitation.

**Differences from the retired machine:** The original private application sources were not released; HTML/EJS and app glue are reconstructed from public writeups, not an asserted byte-identical copy. Original writeups show a `libxmljs` binding and MongoDB of its era; this build uses real `libxmljs2 0.37.0` libxml2 bindings and the officially packaged MongoDB 8 server. The intentional `node-serialize 0.0.4` vulnerable implementation is the actual upstream package. No fake MongoDB, XXE regex, mock file-read route, or hand-written deserializer is used.

Original references:
- https://www.hackthebox.com/machines/nodeblog
- https://0xdf.gitlab.io/2022/01/10/htb-nodeblog.html
- https://7rocky.github.io/en/htb/nodeblog/
- https://github.com/advisories/GHSA-q4v7-4rhw-9hqm

## Build and local start

```bash
docker build -t ttp-nodeblog:local -f labs/nodeblog/Dockerfile labs/nodeblog
docker run -d --name nodeblog-local \
  --cap-drop ALL --security-opt no-new-privileges \
  --memory 1024m --cpus 1.5 --pids-limit 192 \
  -e NODEBLOG_USER_FLAG='TTP{example_web_flag}' \
  -p 127.0.0.1:5000:5000 ttp-nodeblog:local
docker inspect -f '{{.State.Health.Status}}' nodeblog-local
```

The container bundles genuine `mongod`, bound to `127.0.0.1:27017` **inside the same network namespace**. Only TCP 5000 is exposed. The process and database run as UID 10001; no Docker capabilities are requested. The runtime image is Debian Bookworm-based, not Ubuntu. Build/download stages and C++ toolchain remain outside the final image.

MongoDB 8 has x86-64 CPU requirements and a nontrivial memory footprint. Actual image bytes and RSS must be measured by CI. Do not assume suitability for a VPS smaller than the tested limit. A service-start healthcheck verifies the HTTP service **and** native MongoDB ping.

## Flag and reset

CI generates three short random Flags per NodeBlog release version and writes the versioned manifest plus the matching Challenge Markdown. Re-running the same version reuses the existing manifest; a new version receives a new set. Flag 01 is seeded into a genuinely private MongoDB article and its temporary seed file is removed after seeding. Flag 02 is stored in a local challenge-data file and retrieved through the real XXE parser. Flag 03 remains the service-account Web goal at /home/nodeblog/user.txt and is retrieved through the real deserialization execution path. The Worker only manages target lifecycle; it does not generate, inject or judge Challenge Flags. The Web backend syncs the generated Markdown answers and performs grading.

With no external volume, deleting the instance deletes the MongoDB data and article changes; recreating it with a different injected flag resets all state. When an external volume is used, explicitly delete that volume to reset the database.

## Independent full-chain testing

`.github/workflows/nodeblog-dev-acceptance.yml` is a manual-only development workflow. It generates or reuses versioned Flags, commits the matching Challenge Markdown, builds the target on an ephemeral GitHub-hosted runner, and uses a separate HTTP-only test client on an internal Docker network. It does not run on every PR and is not a general offensive CI gate. The attacker must prove *actual native MongoDB* NoSQLi, XML entity substitution, OS command execution through the vulnerable npm package, and unique per-instance Flag retrieval across two rebuilt instances.

```bash
docker build -t nodeblog-attacker -f labs/nodeblog/tests/Dockerfile.attacker labs/nodeblog/tests
# Launch attacker on the same isolated test network as the target:
docker run --rm --network nodeblog-ci \
  -e TARGET_URL=http://nodeblog-target:5000 \
  -e EXPECTED_USER_FLAG='TTP{example_web_flag}' nodeblog-attacker
```

The manual development workflow validates all three Challenge Flags over HTTP: NoSQL authentication bypass and protected article access; native libxml2 XXE and the local challenge-data Flag; node-serialize 0.0.4 command execution and the final Web Flag. No Docker socket or target-side exec is available to the test client.

**Measured resources:** target image **165,215,162 bytes** (~157.6 MiB), memory **136.2 MiB** and **135.4 MiB** respectively during the two CI runs, ~65 PIDs. Both instances used `--cap-drop ALL` and `--security-opt no-new-privileges`; no privileged mode, extra Linux capabilities, or volume mounts.

**Release boundary:** successful lab CI confirms a working standalone Web target, **not** a production Worker deployment or flag-judging integration. Keep the explicit release block until the separate platform checks are completed.
