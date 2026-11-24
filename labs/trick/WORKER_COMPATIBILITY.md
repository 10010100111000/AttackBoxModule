# Trick — Worker compatibility requirements

Trick's Fail2ban jail uses the real iptables action. The target therefore requires NET_ADMIN inside its own network namespace.

Required target policy:

- Grant NET_ADMIN to the Trick container only.
- Keep the container on its per-instance private bridge network.
- Do not use host networking, privileged mode, host filesystem mounts, Docker socket mounts or NET_RAW unless a later measured test proves it necessary.
- Do not add NET_ADMIN to the generic target defaults or to other lab images.
- Preserve the Worker role as scheduling/start/stop only. The Worker does not inspect target files or judge Flags.
- Pass TRICK_STATIC_USER_FLAG and TRICK_STATIC_ROOT_FLAG as opaque per-instance environment values. The Web backend remains responsible for answer validation.

The standalone GitHub Actions test uses --cap-add NET_ADMIN and verifies the actual resulting container configuration. The real Worker engine and multi-tenant isolation still require separate verification; keep .release-blocked in place until that test passes.
