# BountyHunter — PHP XXE and Skytrain ticket validation

This is an **independent reconstruction** of the retired 2021 Hack The Box BountyHunter (Linux/Easy). The original source code and static site assets were not released; routes, layout and behavior are based on archived observations. No claim of byte-for-byte fidelity.

## Recon and discovery

The target exposes a real Apache/PHP service on TCP 80 and OpenSSH on TCP 22. The landing page is a Bounty Hunters program website, not an exploit demonstration. Visitors can follow Portal to an under-development reporting system, whose form loads resources/bountylog.js. The JavaScript transmits base64-encoded XML to tracker_diRbPr00f314.php.

The backend uses genuine PHP SimpleXML/libxml parsing with intentionally unsafe entity expansion. The /db.php configuration source remains blank when accessed as a normal PHP page. Public writeups show how the original parser could read local files and recover the test database credential, also reused for the development account's SSH password. The production database is not actually active in this retired beta-flow reconstruction; the original website likewise advertised that database integration was unfinished.

Inside the development account, Skytrain's ticketValidator.py is a real Python script. The dedicated sudoers rule allows that exact command. It evaluates a field in a Markdown ticket, reproducing the original unsafe Python eval behavior rather than a mock privilege-escalation endpoint. Its system Python version is the Alpine-supplied Python 3 (not the original Ubuntu Python 3.8).

## Fidelity and limitations

- **Original observations:** Apache 2.4.41 on Ubuntu 20.04; two open ports (22, 80); portal.php; log_submit.php; tracker_diRbPr00f314.php; resources/bountylog.js; db.php; development user; /opt/skytrain_inc/ticketValidator.py
- **This reconstruction:** Alpine 3.20, Apache, PHP 8.3 FPM and genuine libxml, native OpenSSH, sudo and Python.
- Page markup/CSS and report confirmation text are independently authored to preserve the published user flow while keeping the Docker image compact.
- Static demo flags are only placeholders. Instance startup accepts BOUNTYHUNTER_STATIC_USER_FLAG and BOUNTYHUNTER_STATIC_ROOT_FLAG, with BOUNTYHUNTER_REQUIRE_PRIVATE_FLAGS=1 in Worker/CI.
- Avoid publishing these purposely vulnerable ports on the Internet. Each instance needs a dedicated isolated internal bridge and no privileged Docker mode.

Independent public evidence:
- https://pencer.io/ctf/ctf-htb-bountyhunter/
- https://khaoticdev.net/hack-the-box-bountyhunter/
- https://www.youtube.com/watch?v=5axsDhumfhU

## Build and health

    docker build -f labs/bountyhunter/Dockerfile -t ttp-bountyhunter:dev labs/bountyhunter

Example isolated instance:

    docker network create --internal bountyhunter-dev
    docker run -d --name bountyhunter-target --network bountyhunter-dev \
      --memory 192m --pids-limit 128 \
      -e BOUNTYHUNTER_REQUIRE_PRIVATE_FLAGS=1 \
      -e BOUNTYHUNTER_STATIC_USER_FLAG='TTP{private_user}' \
      -e BOUNTYHUNTER_STATIC_ROOT_FLAG='TTP{private_root}' \
      ttp-bountyhunter:dev

The CI workflow checks the image build, HTTP flow, genuine PHP XML parsing with harmless data, SSH banner, the PHP config page's normal behavior, private flag initialization and recreation/reset. **Full independent web-to-root exploitation testing and Worker rollout are separate release gates; a green smoke CI does not signify completed fidelity validation.**
