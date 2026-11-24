# Trick acceptance test

Dockerfile.attacker builds a small independent learner container. acceptance.py performs the public attack path over DNS, HTTP and SSH; it does not inspect target files through Docker or use the Worker.

The target is reachable as trick-target on the isolated CI bridge. The attacker uses only the services a learner can reach.
