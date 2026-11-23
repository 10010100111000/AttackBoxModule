<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bounty Report System - Beta</title><link rel="stylesheet" href="/resources/site.css"></head>
<body><main class="mainform"><h1>Bounty Report System - Beta</h1>
<form id="bounty-report">
<input id="exploitTitle" name="exploitTitle" aria-label="Exploit Title" placeholder="Exploit Title" required>
<input id="cwe" name="cwe" aria-label="CWE" placeholder="CWE" required>
<input id="cvss" name="cvss" aria-label="CVSS Score" placeholder="CVSS Score" required>
<input id="reward" name="reward" aria-label="Bounty Reward" placeholder="Bounty Reward ($)" required>
<button class="button" type="submit">Submit</button></form>
<div id="return" class="result" aria-live="polite"></div>
</main><script src="/resources/bountylog.js"></script></body></html>
