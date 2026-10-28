import io
import json
import re
from pathlib import Path
import tarfile
import tempfile
import unittest

from scripts.build import ROOT, build, loon_rule, model_rules, selected_text_rules, text_rules


class RuleTests(unittest.TestCase):
    def test_carrier_rules_use_explicit_operator_domains(self):
        rules = text_rules((ROOT / 'rules/carrier/HK-Carrier-App.list').read_text(), 'loon')
        shared = {'appsflyer.com', 'appsflyersdk.com', 'branch.io', 'adjust.com',
                  'crashlytics.com', 'firebaseio.com', 'googleapis.com', 'gstatic.com'}
        for rule in rules:
            kind, host = rule.split(',')
            self.assertIn(kind, {'DOMAIN', 'DOMAIN-SUFFIX'})
            self.assertFalse(any(host == d or host.endswith('.' + d) for d in shared), rule)
        self.assertIn('DOMAIN-SUFFIX,mylinkapp.hk', rules)
        self.assertIn('DOMAIN,mylink.komect.com', rules)
        self.assertNotIn('DOMAIN-SUFFIX,komect.com', rules)

    def test_wifi_rules_do_not_force_shared_services_to_carrier_regions(self):
        blocked = {
            'UK': ['gspe1-ssl.ls.apple.com'],
            'US': ['mzstatic.com', 'cohere.com', 'ip-api.com', 'optimizely.com',
                   'crashlytics.com', 'mobilefuse.com', 'inmobi.com', 'kochava.com',
                   'agkn.com', 'inner-active.mobi'],
        }
        config = json.loads((ROOT / 'sources.json').read_text())
        for country, domains in blocked.items():
            collection = config['collections'][f'wificall/Wifi-Call-{country}']
            rules = text_rules((ROOT / collection['output']).read_text(), 'loon')
            for domain in domains:
                # Exclusions apply after merging every source, including future upstream refreshes.
                self.assertIn('DOMAIN-SUFFIX,' + domain, collection['exclude_rules'])
                for rule in rules:
                    kind, host, *_ = rule.split(',')
                    if kind in {'DOMAIN', 'DOMAIN-SUFFIX'}:
                        self.assertFalse(host == domain or host.endswith('.' + domain), rule)

    def test_slim_uk_keeps_banks_without_shared_or_separate_services(self):
        rules = text_rules((ROOT / 'rules/bank/UK-Banks.list').read_text(), 'loon')
        for domain in ['co.uk', 'stripe.com', 'stripe.uk', 'lemfi.com', 'trading212.com',
                       'appsflyer.com', 'branch.io', 'amazontrust.com', 'dynatrace.com', 'omtrdc.net']:
            self.assertFalse(any(rule.split(',')[1] == domain for rule in rules), domain)
        for rule in ['DOMAIN-SUFFIX,wise.com', 'DOMAIN-SUFFIX,monzo.com',
                     'DOMAIN-SUFFIX,barclays.co.uk', 'DOMAIN-KEYWORD,halifax']:
            self.assertIn(rule, rules)

    def test_migrated_collections_preserve_baseline_rules(self):
        config = json.loads((ROOT / 'sources.json').read_text())
        for name, collection in config['collections'].items():
            if 'preserve_source' not in collection:
                continue
            with self.subTest(collection=name):
                baseline = set(text_rules((ROOT / collection['preserve_source']).read_text(), 'loon'))
                generated = set(text_rules((ROOT / collection['output']).read_text(), 'loon'))
                self.assertFalse(baseline - generated)

    def test_wifi_collections_do_not_add_cross_country_mcc_or_n26(self):
        allowed = {'UK': {'234', '235'}, 'HK': {'454'}, 'DE': {'262'}, 'US': {str(n) for n in range(310, 317)}}
        for country, mccs in allowed.items():
            text = (ROOT / f'rules/wificall/Wifi-Call-{country}.list').read_text()
            with self.subTest(country=country):
                self.assertLessEqual(set(re.findall(r'\bmcc(\d{3})\b', text)), mccs)
                self.assertNotIn('DOMAIN-SUFFIX,n26.com', text)
                self.assertNotIn('DOMAIN-SUFFIX,tech26.de', text)

    def test_published_rules_preserve_all_local_snapshot_rules(self):
        baseline = set(text_rules((ROOT / 'snapshots/KeLee-AI-20261028.list').read_text(), 'loon'))
        published = set(text_rules((ROOT / 'rules/AI-Combined.list').read_text(), 'loon'))
        self.assertEqual(baseline - published, set())
        self.assertEqual(sum(r.startswith('AND,') for r in baseline), 3)
        self.assertNotIn('DOMAIN-SUFFIX,azurefd.net', published)
        self.assertNotIn('DOMAIN-SUFFIX,run.app', published)

    def test_domain_semantics_and_case(self):
        self.assertEqual(text_rules('# comment\n+.Muse.AI\napi.example.com\n', 'domain-list'),
                         ['DOMAIN-SUFFIX,muse.ai', 'DOMAIN,api.example.com'])

    def test_logical_rule_is_not_flattened(self):
        rule = 'AND, ((DOMAIN-KEYWORD, openaicom-api-), (DOMAIN-SUFFIX, azurefd.net))'
        expected = 'AND,((DOMAIN-KEYWORD,openaicom-api-),(DOMAIN-SUFFIX,azurefd.net))'
        self.assertEqual(text_rules(rule, 'loon'), [expected])
        self.assertEqual(loon_rule(expected), expected)

    def test_rejects_html_policies_bad_ips_and_broken_logic(self):
        for line in ['<!DOCTYPE html>', 'DOMAIN,muse.ai,DIRECT', 'IP-CIDR,10.0.0.1/8',
                     'AND,((DOMAIN,a.example),(DOMAIN,b.example)', 'DOMAIN-SUFFIX,*.ai']:
            with self.subTest(line=line), self.assertRaises(ValueError):
                text_rules(line, 'loon')

    def test_ip_options_preserved(self):
        self.assertEqual(loon_rule('IP-CIDR6, 2607:6bc0::/48, no-resolve'),
                         'IP-CIDR6,2607:6bc0::/48,no-resolve')

    def test_asn_and_tld_suffix_preserved(self):
        self.assertEqual(loon_rule('IP-ASN, 399358, no-resolve'), 'IP-ASN,399358,no-resolve')
        self.assertEqual(loon_rule('DOMAIN-SUFFIX,java'), 'DOMAIN-SUFFIX,java')
        self.assertEqual(loon_rule('DOMAIN-SUFFIX,oracle'), 'DOMAIN-SUFFIX,oracle')
        for bad in ['IP-ASN,0', 'IP-ASN,4294967296', 'IP-ASN,-1',
                    'IP-ASN,399358,DIRECT', 'DOMAIN,oracle', 'DOMAIN-SUFFIX,-bad']:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                loon_rule(bad)

    def test_vowifi_nested_logic_preserves_country_udp_and_ports(self):
        rule = 'AND,((GEOIP,GB),(AND,((PROTOCOL,UDP),(OR,((DEST-PORT,500),(DEST-PORT,4500))))))'
        self.assertEqual(loon_rule(rule), rule)
        for bad in ['DEST-PORT,0', 'DEST-PORT,65536', 'DEST-PORT,4500-500', 'GEOIP,GB,DIRECT', 'PROTOCOL,UDP,DIRECT']:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                loon_rule(bad)

    def test_source_selection_rejects_known_bad_or_unrelated_entries(self):
        rules, skipped = selected_text_rules(
            'DOMAIN-SUFFIX,bank.example\nDOMAIN,api.bank.example\n'
            'DOMAIN-SUFFIX,unrelated.example\nUSER-AGENT,Bank*\n'
            'IP-CIDR,62.141.11.56/24,no-resolve\n',
            {'format': 'loon', 'exclude_lines': ['IP-CIDR,62.141.11.56/24,no-resolve'],
             'include_rule_types': ['DOMAIN', 'DOMAIN-SUFFIX'], 'include_domains': ['bank.example']})
        self.assertEqual(rules, ['DOMAIN-SUFFIX,bank.example', 'DOMAIN,api.bank.example'])
        self.assertEqual(len(skipped), 3)

    def test_models_only_explicit_remote_api_hosts(self):
        providers = {
            'real': 'api = "https://api.example.com/v1"\ndoc = "https://docs.example.com"',
            'path-variable': 'api = "https://api.example.com/${ACCOUNT}/v1"',
            'local': 'api = "http://127.0.0.1:1234/v1"',
            'template': 'api = "https://${ACCOUNT}.example.com/v1"',
            'sdk': 'name = "Only SDK defaults"',
            'domestic-cn': 'api = "https://cn.example.com/v1"',
            'shared': 'api = "https://api.shared.com/accounts/ai/v1"',
        }
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode='w:gz') as archive:
            for provider, text in providers.items():
                raw = text.encode()
                entry = tarfile.TarInfo(f'repo/providers/{provider}/provider.toml')
                entry.size = len(raw)
                archive.addfile(entry, io.BytesIO(raw))
        rules, skipped = model_rules(buffer.getvalue(), {
            'exclude_providers': ['*-cn'], 'exclude_hosts': ['api.shared.com']})
        self.assertEqual(rules, ['DOMAIN,api.example.com', 'DOMAIN,api.example.com'])
        self.assertEqual(set(skipped), {'local', 'template', 'sdk', 'domestic-cn', 'shared'})

    def test_merge_is_stable_and_failed_upstream_keeps_published_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = {'collections': {'Test': {'output': 'rules/Test.list', 'sources': [
                {'name': 'one', 'path': 'one.list', 'format': 'loon'},
                {'name': 'two', 'path': 'two.list', 'format': 'loon'}],
                'exclude_rules': ['DOMAIN,exclude.example'],
                'required_rules': ['DOMAIN-SUFFIX,muse.ai']}}}
            (root / 'sources.json').write_text(json.dumps(config))
            (root / 'one.list').write_text('DOMAIN-SUFFIX,muse.ai\nDOMAIN,exclude.example\n')
            (root / 'two.list').write_text('DOMAIN-SUFFIX,muse.ai\nDOMAIN,api.example.com\n')
            report = build(root)
            self.assertEqual(report['collections']['Test']['rules'], 2)
            output = root / 'rules/Test.list'
            previous, modified = output.read_bytes(), output.stat().st_mtime_ns
            self.assertEqual(report, build(root))
            self.assertEqual(modified, output.stat().st_mtime_ns)
            (root / 'one.list').write_text('DOMAIN,new.example\n')
            (root / 'two.list').write_text('<html>upstream error</html>')
            with self.assertRaises(ValueError):
                build(root)
            self.assertEqual(output.read_bytes(), previous)

    def test_empty_upstream_is_not_published(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'sources.json').write_text(json.dumps({'collections': {'Test': {
                'output': 'rules/Test.list', 'sources': [
                    {'name': 'empty', 'path': 'empty.list', 'format': 'loon'}]}}}))
            (root / 'empty.list').write_text('# empty\n')
            with self.assertRaises(ValueError):
                build(root)
            self.assertFalse((root / 'rules/Test.list').exists())


if __name__ == '__main__':
    unittest.main()
