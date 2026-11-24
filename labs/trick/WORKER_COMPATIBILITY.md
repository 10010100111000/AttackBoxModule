# Trick — Worker compatibility requirements

Trick's Fail2ban jail uses the real iptables-multiport action. That action creates and removes firewall chains inside the target's network namespace, so the target container needs CAP_NET_ADMIN.

This is a capability on the Trick target container, not on the Worker process and not on the host network namespace. The Worker only needs to request this one capability when creating this specific target.

Required target policy:

- Grant CAP_NET_ADMIN to the Trick container only.
- Keep the container on its per-instance private bridge/network namespace.
- Do not use host networking, privileged mode, host filesystem mounts or a Docker socket.
- Do not add NET_ADMIN to generic target defaults or other lab images.
- Worker continues to schedule/start/stop targets and pass opaque Flag values; it does not inspect target files or judge Flags.
- The Web backend validates User/Root Flag submissions.

The independent CI verifies that the target has only the intended extra capability, no privileged mode, no host mounts and no published ports. The real Worker deployment still needs to apply the same per-target policy before release.
