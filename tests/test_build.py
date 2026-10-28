import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from scripts.build import ROOT, build, loon_rule, model_rules, text_rules


class RuleTests(unittest.TestCase):
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
