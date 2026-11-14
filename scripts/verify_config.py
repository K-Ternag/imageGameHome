"""Check policy/contact publication boundaries without a browser."""
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_site import Site, validate_config, missing_policy_fields


class FormButton(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.submit_buttons=[]
        self.feed(source)

    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='button' and attrs.get('type')=='submit': self.submit_buttons.append(attrs)


config=json.loads((ROOT/'site-config.json').read_text(encoding='utf-8'))
validate_config(config)
fixture=dict(config,developerName='Operator <&>',supportEmail='help@example.org',
             policyEffectiveDate='2026-11-14',policiesApproved=True,
             supportRetention={'ko':'문의 완료 후 30일','en':'30 days after resolution'},
             supportResponseTime={'ko':'7일 이내','en':'Within 7 days'})
assert not missing_policy_fields(fixture)
checks=[]
for lang in ['ko','en']:
    site=Site(lang,fixture)
    policy=site.render('privacy')
    support=site.render('support')
    assert 'class="policy-notice"' not in policy
    assert 'Operator &lt;&amp;&gt;' in policy
    assert 'mailto:help@example.org' in policy and 'mailto:help@example.org' in support
    assert fixture['supportRetention'][lang] in policy
    assert all('disabled' in attrs for attrs in FormButton(support).submit_buttons)
    assert 'class="store-link"' not in support
    partial=dict(fixture,supportRetention={'ko':'30일','en':''})
    assert missing_policy_fields(partial)==['supportRetention.en']
    assert 'class="policy-notice"' in Site(lang,partial).render('privacy')
    checks.append(f'{lang}: static identity, HTML escaping, contact, retention, draft readiness, no-JS form protection')
for field,value in [('supportEmail','user@example.org?body=leak'),('supportEmail','user@example.org\nBcc: other@example.org'),('playStoreUrl','javascript:alert(1)'),('siteUrl','http://example.org/')]:
    invalid=dict(config,**{field:value})
    try:
        validate_config(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid configuration was accepted: '+field)
checks.append('Unsafe contact and publication URLs rejected')
print(json.dumps({'configuration_checks':checks,'passed':True},ensure_ascii=False,indent=2))
