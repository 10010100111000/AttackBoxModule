#!/bin/sh
set -eu

# Seeding uses WonderCMS's own unmodified Wcms constructor and createDb().
php /usr/local/bin/wcms-seed.php

# Do not give the web server access to the instance's administrative password
# via its process environment after first boot.
unset WONDERCMS_ADMIN_PASSWORD WONDERCMS_STATIC_XSS_FLAG WONDERCMS_REQUIRE_PRIVATE_FLAGS

exec php -S 0.0.0.0:8080 -t /srv/wcms /srv/wcms/router.php
