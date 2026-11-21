# Pebbles Debian-only test (NOT production)

Experimental branch: `test/pebbles-debian-runtime`

- Real Debian Jessie Slim base, no Ubuntu anywhere in the build
- Debian Jessie Backports **ZoneMinder 1.29.0** real binary package
- Oracle Debian 8 **MySQL 5.7.30** real .deb binaries, SHA-256 locked using upstream Packages index
- Historical PHP 5.6 (a deviation from the Ubuntu original PHP 7.0; must verify exploit compatibility)
- Java 8 from Debian Jessie Backports for the genuine Tomcat 9.0.30 service

The first gate is **package installability** in `Dockerfile.debian-probe`. This deliberately does not start an insecure target, does not invent vulnerabilities, and is not part of the image publishing workflow. Only after this builds and version probes pass should the actual Debian runtime and exploit acceptance be implemented. No modified official Pebbles `Dockerfile` is included in this experiment.

References: 
- https://archive.debian.org/debian/pool/main/z/zoneminder/
- https://repo.mysql.com/apt/debian/dists/jessie/mysql-5.7/binary-amd64/Packages
- https://hub.docker.com/r/debian/eol/tags
