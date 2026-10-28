#!/usr/bin/env python3
"""Build policy-free Loon subscriptions using Python 3.11+ standard library."""
import argparse
import fnmatch
import hashlib
import io
import ipaddress
import json
from pathlib import Path
import re
import tarfile
import tomllib
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def domain(value):
    value = value.lower().rstrip('.')
    if len(value) > 253 or '.' not in value or not all(
        re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label)
        for label in value.split('.')
    ):
        raise ValueError(f'Invalid domain: {value!r}')
    return value


def split_top(value):
    """Split only commas outside nested logical expressions."""
    depth, start, parts = 0, 0, []
    for i, char in enumerate(value):
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
            if depth < 0:
                raise ValueError('Unbalanced parentheses')
        elif char == ',' and depth == 0:
            parts.append(value[start:i].strip())
            start = i + 1
    if depth:
        raise ValueError('Unbalanced parentheses')
    return parts + [value[start:].strip()]


def loon_rule(line):
    parts = split_top(line)
    kind = parts[0].upper()
    if kind in {'AND', 'OR'}:
        if len(parts) != 2 or not parts[1].startswith('(') or not parts[1].endswith(')'):
            raise ValueError(f'Invalid logical rule: {line}')
        children = split_top(parts[1][1:-1])
        if len(children) < 2:
            raise ValueError(f'Invalid logical arity: {line}')
        normalized = []
        for child in children:
            if not child.startswith('(') or not child.endswith(')'):
                raise ValueError(f'Invalid child: {child}')
            normalized.append('(' + loon_rule(child[1:-1]) + ')')
        return kind + ',(' + ','.join(normalized) + ')'
    if kind in {'DOMAIN', 'DOMAIN-SUFFIX'} and len(parts) == 2:
        return kind + ',' + domain(parts[1])
    if kind == 'DOMAIN-KEYWORD' and len(parts) == 2 and re.fullmatch(r'[a-zA-Z0-9._-]+', parts[1]):
        return kind + ',' + parts[1].lower()
    if kind == 'GEOIP' and len(parts) in {2, 3} and re.fullmatch(r'[A-Za-z]{2}', parts[1]):
        if len(parts) == 3 and parts[2] != 'no-resolve':
            raise ValueError(f'Unexpected GEOIP option: {line}')
        return ','.join([kind, parts[1].upper()] + parts[2:])
    if kind == 'PROTOCOL' and len(parts) == 2 and parts[1].upper() in {'HTTP', 'HTTPS', 'TCP', 'QUIC', 'STUN', 'UDP'}:
        return kind + ',' + parts[1].upper()
    if kind in {'DEST-PORT', 'SRC-PORT'} and len(parts) == 2:
        value = parts[1]
        if not re.fullmatch(r'(?:[<>]=?)?\d+|\d+-\d+', value):
            raise ValueError(f'Invalid port expression: {line}')
        numbers = [int(n) for n in re.findall(r'\d+', value)]
        if any(n < 1 or n > 65535 for n in numbers) or (len(numbers) == 2 and numbers[0] > numbers[1]):
            raise ValueError(f'Invalid port range: {line}')
        return kind + ',' + value
    if kind in {'IP-CIDR', 'IP-CIDR6'} and len(parts) in {2, 3}:
        network = ipaddress.ip_network(parts[1], strict=True)
        if network.version != (6 if kind == 'IP-CIDR6' else 4):
            raise ValueError(f'IP version mismatch: {line}')
        if len(parts) == 3 and parts[2] != 'no-resolve':
            raise ValueError(f'Unexpected policy or option: {line}')
        return ','.join([kind, str(network)] + parts[2:])
    raise ValueError(f'Unsupported or policy-bearing Loon rule: {line}')


def text_rules(text, format):
    result = []
    for number, line in enumerate(text.splitlines(), 1):
        line = line.strip().lstrip('\ufeff')
        if not line or line.startswith(('#', '//', ';')):
            continue
        try:
            if format == 'domain-list':
                prefix = 'DOMAIN-SUFFIX,' if line.startswith('+.') else 'DOMAIN,'
                result.append(prefix + domain(line[2:] if line.startswith('+.') else line))
            elif format == 'loon':
                result.append(loon_rule(line))
            else:
                raise ValueError(f'Unknown format: {format}')
        except ValueError as error:
            raise ValueError(f'Line {number}: {error}') from error
    return result


def model_rules(raw, source):
    """Read explicit provider API hosts; never extract or execute archive files."""
    result, skipped = [], {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
        for entry in sorted(archive.getmembers(), key=lambda x: x.name):
            parts = entry.name.split('/')
            if not entry.isfile() or len(parts) != 4 or parts[1] != 'providers' or parts[3] != 'provider.toml':
                continue
            provider = parts[2]
            data = tomllib.loads(archive.extractfile(entry).read().decode('utf-8'))
            api = data.get('api')
            if any(fnmatch.fnmatchcase(provider, p) for p in source.get('exclude_providers', [])):
                skipped[provider] = 'excluded provider'
                continue
            if api is None:
                skipped[provider] = 'SDK default; no explicit API URL'
                continue
            if not isinstance(api, str):
                raise ValueError(f'{provider}: api field is no longer a string')
            host = urlsplit(api).hostname
            if not host or any(c in host for c in '${}'):
                skipped[provider] = 'hostname requires user configuration'
                continue
            try:
                ipaddress.ip_address(host)
                skipped[provider] = 'IP address; no domain rule'
                continue
            except ValueError:
                pass
            if host == 'localhost' or host.endswith('.localhost'):
                skipped[provider] = 'localhost'
                continue
            host = domain(host)
            if host in source.get('exclude_hosts', []) or any(host == d or host.endswith('.' + d) for d in source.get('exclude_suffixes', [])):
                skipped[provider] = 'excluded host'
                continue
            result.append('DOMAIN,' + host)
    return result, skipped


def fetch(source, root):
    if 'path' in source:
        return (root / source['path']).read_bytes()
    request = Request(source['url'], headers={'User-Agent': 'couai-loon-rules/1.0'})
    with urlopen(request, timeout=60) as response:
        return response.read()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def selected_text_rules(text, source):
    """Apply explicitly configured source filters before parsing unsupported lines."""
    keep, skipped = [], {}
    exclusions = {re.sub(r'\s+', '', x) for x in source.get('exclude_lines', [])}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(('#', '//', ';')):
            continue
        if re.sub(r'\s+', '', stripped) in exclusions:
            skipped[stripped] = 'explicit source exclusion'
            continue
        types = source.get('include_rule_types')
        if types and stripped.split(',', 1)[0].strip().upper() not in types:
            skipped[stripped] = 'rule type outside source selection'
            continue
        parsed = text_rules(stripped, source['format'])
        for rule in parsed:
            domains = source.get('include_domains')
            if domains:
                parts = rule.split(',')
                if parts[0] not in {'DOMAIN', 'DOMAIN-SUFFIX'} or not any(
                    parts[1] == d or parts[1].endswith('.' + d) for d in domains
                ):
                    skipped[stripped] = 'domain outside reviewed source selection'
                    continue
            keep.append(rule)
    return keep, skipped


def build(root=ROOT, loader=fetch):
    config = json.loads((root / 'sources.json').read_text())
    outputs, report = {}, {'collections': {}}
    for name, collection in config['collections'].items():
        rules, seen, sources = [], set(), []
        excluded = {loon_rule(x) for x in collection.get('exclude_rules', [])}
        for source in collection['sources']:
            raw = loader(source, root)
            if source['format'] == 'models-tar':
                parsed, skipped = model_rules(raw, source)
            else:
                parsed, skipped = selected_text_rules(raw.decode('utf-8-sig'), source)
            if len(parsed) < source.get('min_rules', 1):
                raise ValueError(f"{source['name']}: only {len(parsed)} rules; refusing partial publication")
            added = 0
            for rule in parsed:
                if rule not in seen and rule not in excluded:
                    seen.add(rule)
                    rules.append(rule)
                    added += 1
            record = {'name': source['name'], 'source': source.get('url', source.get('path')),
                      'parsed': len(parsed), 'added': added,
                      'rules_sha256': digest(('\n'.join(parsed) + '\n').encode())}
            if skipped:
                record['skipped'] = skipped
            sources.append(record)
        for required in collection.get('required_rules', []):
            if loon_rule(required) not in seen:
                raise ValueError(f'{name}: required rule missing: {required}')
        body = f'# {name} — generated; edit sources.json or overrides instead.\n'
        body += '# Sources and attribution: https://github.com/couai/loon-rules/blob/main/NOTICE.md\n'
        body += f'# Rules: {len(rules)}\n' + '\n'.join(rules) + '\n'
        outputs[collection['output']] = body
        report['collections'][name] = {'output': collection['output'], 'rules': len(rules), 'sha256': digest(body.encode()), 'sources': sources}
    # Every upstream and every collection must pass before writing any output.
    outputs['reports/manifest.json'] = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    for path, body in outputs.items():
        destination = root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists() or destination.read_text() != body:
            temporary = destination.with_suffix(destination.suffix + '.tmp')
            temporary.write_text(body, encoding='utf-8')
            temporary.replace(destination)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    report = build(args.root)
    for name, details in report['collections'].items():
        print(f"{name}: {details['rules']} rules -> {details['output']}")
