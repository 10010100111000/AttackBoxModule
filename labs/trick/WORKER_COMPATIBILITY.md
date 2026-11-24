# Trick — Worker compatibility requirements

Trick does not require NET_ADMIN or any other additional Linux capability.

The challenge's privilege-escalation path modifies the real Fail2ban action configuration and restarts the real Fail2ban service. The acceptance test replaces the inherited actionban command with a root-run file operation; that operation does not modify firewall rules. The target is explicitly run with NET_ADMIN dropped.

The Worker remains responsible only for target lifecycle and opaque Flag environment variables. It does not need NET_ADMIN, does not inspect target files, and does not judge Flags.

Keep the target on its per-instance private network. Do not use host networking, privileged mode, host filesystem mounts or a Docker socket. Do not add NET_ADMIN to the target or generic Worker defaults.
