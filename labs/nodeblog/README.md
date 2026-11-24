# NodeBlog — Web-only authentic attack-chain reconstruction

**Status:** implementation pending independent full-chain CI. Not an official Hack The Box image. Do not deploy to the public Internet.

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

The `flags/user.txt` is a clearly labelled static development placeholder. The optional `NODEBLOG_USER_FLAG` variable replaces it on target startup and is unset before the web process is launched; the Worker only forwards variables and manages lifecycle, never performs challenge-specific flag judgement. The Web backend remains responsible for verifying the correct answer for an instance.

With no external volume, deleting the instance deletes the MongoDB data and article changes; recreating it with a different injected flag resets all state. When an external volume is used, explicitly delete that volume to reset the database.

## Independent full-chain testing

`.github/workflows/nodeblog.yml` builds both the target and a separate Python attacker container, places them on an internal Docker network, and attempts the Web sequence over HTTP without `docker exec`. The attacker must prove *actual native MongoDB* NoSQLi, XML entity substitution, OS command execution through the vulnerable npm package, and unique per-instance Flag retrieval across two rebuilt instances.

```bash
docker build -t nodeblog-attacker -f labs/nodeblog/tests/Dockerfile.attacker labs/nodeblog/tests
# Launch attacker on the same isolated test network as the target:
docker run --rm --network nodeblog-ci \
  -e TARGET_URL=http://nodeblog-target:5000 \
  -e EXPECTED_USER_FLAG='TTP{example_web_flag}' nodeblog-attacker
```

**Acceptance gate:** a successful GitHub Actions run (including reset, resource metrics and no extra capability) is necessary before claiming verified and removing the release block. This README is not evidence of successful execution.
