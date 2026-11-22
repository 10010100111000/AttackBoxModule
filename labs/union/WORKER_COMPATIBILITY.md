# Union — production Worker compatibility audit

Audit target: main branch of the separate `10010100111000/attackbox` repository, read November 2026. This file records verified compatibility rather than implying that a standalone Docker CI proves Worker deployability.

## Confirmed by code inspection

- `worker/node/labnetwork/docker.go`: per-target Docker networks are internal bridge networks; IPv6 is disabled and host IP masquerade is disabled. Target and owner identities are tracked through network labels.
- `worker/node/targets/model.go`: target deployment definitions carry an image, environment variables, CPU, memory, PID limits and network selectors; there is no per-target capability policy or `NET_ADMIN` option in the model.
- `worker/node/targets/engine.go`: `ContainerCreate` passes `HostConfig.NetworkMode` and resource limits, but no `CapAdd`. Union's `entrypoint.sh` uses genuine iptables to enforce its initial SSH block and explicitly fails when `NET_ADMIN` is missing.
- `web/server/labs/credentials.ts`: the web layer seals configured deployment variables using AES-256-GCM at rest. This does **not** mean Docker container environment values are hidden from privileged host administrators.

## Current determination

**Union is not Worker-compatible in the unchanged production Worker.** The standalone lab tests supply `--cap-add NET_ADMIN` themselves, which the Worker does not. This is a real deployment gap, not an HTTP-test bug; do not mark the Worker gate as complete.

## Required design before production enablement

1. Introduce an explicit per-deployment capability requirement checked against a trusted server-side allowlist. Neither learner-controlled variables nor untrusted image metadata may grant additional capabilities.
2. Transport and validate the approved permission consistently through the web/API protocol, the Worker `Bundle` and `Definition`, and finally `DockerEngine.Up`. Only the Union image can request `NET_ADMIN` under this policy; all other targets keep the default capability policy.
3. Maintain separate internal per-instance networks with no host network mode, privileged containers or host filesystem mounts. Test that rules cannot affect other tenants, the Worker host network or the AttackBox management plane.
4. Verify that native sudo works without enabling `--privileged`; fail the target start if the host security profile applies `no-new-privileges` to this specific challenge.
5. Add an actual Worker-engine integration test for starting Union, SSH deny-before/allow-after, per-instance network isolation and destroy/reset cleanup. Use a real Docker daemon and assert the exact resulting HostConfig.
6. Keep private per-instance answers outside the image and inject via the controlled deployment variables. Ensure only the Worker and authorized admins can read container configuration.

Do not copy the standalone `docker run` flags into a generic Worker default. A capability misconfiguration here would affect every target and materially weaken tenant isolation.
