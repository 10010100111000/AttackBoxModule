# Precious — real Ruby PDFKit command injection

Status: **implementation pending independent full Web-chain CI**. Do not release or merge without a verified attack from an external HTTP-only player.

The application uses real Ruby `pdfkit 0.8.6` with native `wkhtmltopdf`. A user-submitted URL is converted to a PDF by PDFKit itself, preserving the historically vulnerable command construction (CVE-2022-25765). There is no mock command-execution handler, simulated PDF, or fake response.

## Scope
- Original-style URL-to-PDF Web application, discoverable PDF metadata
- Real PDFKit 0.8.6 command injection into non-root Ruby Web process
- One Web goal: /home/ruby/user.txt
- **No** SSH credential reuse, sudo, YAML deserialization or Linux Root escalation: those are original post-Web stages and deliberately out of scope
- Original site sources were not public; HTML is a functional reconstruction, not an exact copy

## Local
```sh
docker build -t ttp-precious:local -f labs/precious/Dockerfile labs/precious
docker run --rm -p 127.0.0.1:8080:8080 --memory 700m --pids-limit 150 \
  --security-opt no-new-privileges \
  -e PRECIOUS_USER_FLAG='TTP{example_web_flag}' ttp-precious:local
```

## Primary sources
- https://0xdf.gitlab.io/2023/05/20/htb-precious.html
- https://www.hackthebox.com/machines/precious

Release gate: two fresh instance runs, separate HTTP-only attacker, real PDF generated from attacker-hosted HTML, real PDFKit code execution and recovered per-instance Web flag. Production Worker/grading remains separate.
