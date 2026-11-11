from types import SimpleNamespace

import pytest

from tests.data.logs_s3 import (
    LOG_TEXT_CHECKOV,
    LOG_TEXT_TFLINT,
    LOG_TEXT_TFSEC,
    LOG_TEXT_TRIVY,
)


@pytest.fixture
def log_file_text_tflint():
    return LOG_TEXT_TFLINT


@pytest.fixture
def log_file_text_checkov():
    return LOG_TEXT_CHECKOV


@pytest.fixture
def log_file_text_tfsec():
    return LOG_TEXT_TFSEC


@pytest.fixture
def log_file_text_trivy():
    return LOG_TEXT_TRIVY


@pytest.fixture
def expected_trivy_guide_urls():
    return [
        'https://avd.aquasec.com/misconfig/aws-0104',
        'https://avd.aquasec.com/misconfig/aws-0107',
        'https://avd.aquasec.com/misconfig/aws-0086',
        'https://avd.aquasec.com/misconfig/aws-0087',
        'https://avd.aquasec.com/misconfig/aws-0091',
        'https://avd.aquasec.com/misconfig/aws-0093',
        'https://avd.aquasec.com/misconfig/aws-0132'
    ]


@pytest.fixture
def expected_checkov_guide_urls():
    return [
        'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/general-6',
        'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/bc-aws-52',
        'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/ensure-that-s3-buckets-are-encrypted-with-kms-by-default',
        'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-logging-policies/bc-aws-2-62',
        'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/s3-bucket-should-have-public-access-blocks-defaults-to-false-if-the-public-access-block-is-not-attached',
        'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3-13-enable-logging',
        'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-logging-policies/bc-aws-2-61',
        'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3-16-enable-versioning',
        'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/ensure-that-s3-bucket-has-cross-region-replication-enabled',
        'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/bc-aws-general-31',
        'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/ensure-that-ec2-is-ebs-optimized',
        'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-logging-policies/ensure-that-detailed-monitoring-is-enabled-for-ec2-instances',
        'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/general-13',
        'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/networking-31',
        'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/bc-aws-382',
        'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-iam-policies/ensure-an-iam-role-is-attached-to-ec2-instance',
        'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/ensure-that-security-groups-are-attached-to-ec2-instances-or-elastic-network-interfaces-enis'
    ]


@pytest.fixture
def expected_tfsec_guide_urls():
    return [
        'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/enable-at-rest-encryption/',
        'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/enable-recovery/',
        'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/table-customer-key/',
        'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/block-public-acls/',
        'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/block-public-policy/',
        'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/ignore-public-acls/',
        'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/no-public-buckets/',
        'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/encryption-customer-key/',
        'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/enable-bucket-logging/',
        'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/enable-versioning/',
        'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/specify-public-access-block/',
        'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/no-public-egress-sgr/',
        'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/enforce-http-token-imds/',
        'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/enable-at-rest-encryption/',
        'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/add-description-to-security-group-rule/'
    ]


@pytest.fixture
def expected_tflint_guide_urls():
    return [
        'https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.11.0/docs/rules/terraform_required_providers.md',
        'https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.11.0/docs/rules/terraform_required_version.md'
    ]


@pytest.fixture
def tflint_required_version_url():
    return (
        'https://github.com/terraform-linters/tflint-ruleset-terraform/blob/'
        'v0.13.0/docs/rules/terraform_required_version.md'
    )


@pytest.fixture
def tflint_untrusted_errors():
    return '''
Reference: http://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.13.0/docs/rules/rule.md
Reference: https://github.com.evil.example/terraform-linters/tflint-ruleset-terraform/blob/v0.13.0/docs/rules/rule.md
Reference: https://github.com/other/project/blob/v0.13.0/docs/rules/rule.md
Reference: https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.13.0/docs/rules/rule.md?download=1
'''


@pytest.fixture
def tflint_guide_markdown():
    return '''
# terraform_required_version

Disallow `terraform` declarations without `required_version`.

> This rule is enabled by the recommended preset.

## Configuration

```hcl
rule "terraform_required_version" {
  enabled = true
}
```

## Example

```hcl
terraform {
  required_version = ">= 1.0"
}
```

```
$ tflint
1 issue(s) found
```

## Why

The required version constrains which Terraform CLI versions can be used.

## How To Fix

Add the `required_version` attribute to the Terraform configuration block.

```tf
terraform {
  required_version = ">= 1.0"
}
```
'''


@pytest.fixture
def checkov_guide_urls():
    return [
        'https://docs.prismacloud.io/first',
        'https://docs.prismacloud.io/second'
    ]


@pytest.fixture
def tfsec_guide_urls():
    return [
        'https://aquasecurity.github.io/tfsec/v1.28.14/checks/aws/s3/block-public-acls/',
        'https://aquasecurity.github.io/tfsec/v1.28.14/checks/aws/s3/block-public-policy/'
    ]


@pytest.fixture
def tfsec_dynamodb_guide_url():
    return 'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/enable-at-rest-encryption/'


@pytest.fixture
def checkov_guide_url():
    return 'https://docs.prismacloud.io/checkov-guide'


@pytest.fixture
def trivy_untrusted_errors():
    return '''
See http://127.0.0.1:8080/admin
See http://169.254.169.254/latest/meta-data/
See http://avd.aquasec.com/misconfig/aws-0104
See https://avd.aquasec.com.evil.com/x
See https://avd.aquasec.com@evil.com/x
See https://avd.aquasec.com:8080/x
See https://avd.aquasec.com/misconfig/aws-0104
'''


@pytest.fixture
def web_rag_documents():
    return {
        'tflint_fetch_response': '# terraform_required_version\n\n## Why\nUse a Terraform version constraint.',
        'trivy_formatting': '''
<html>
  <h1>No Public Egress SGR</h1>
  <h3>Recommended Actions</h3>
  <p>Set a more restrictive cidr range.</p>
  <pre><code><span>resource</span> <span>"aws_security_group"</span> <span>"good_example"</span> <span>{</span>
  <span>egress</span> <span>{</span>
    <span>cidr_blocks</span> <span>=</span> <span>["1.2.3.4/32"]</span>
  <span>}</span>
<span>}</span></code></pre>
  <h3>Links</h3>
</html>
''',
        'trivy_remediation': '''
<html>
  <h1>No Public Egress SGR</h1>
  <h3>Recommended Actions</h3>
  <p>Set a more restrictive cidr range.</p>
  <pre><code>AWSTemplateFormatVersion: "2010-09-09"</code></pre>
  <pre><code>resource "aws_security_group" "good_example" {
  egress {
    cidr_blocks = ["1.2.3.4/32"]
  }
}</code></pre>
  <h3>Links</h3>
  <p>Do not include this unrelated section.</p>
</html>
''',
        'trivy_refresh': '''
<!doctype html>
<html><head>
  <meta http-equiv="refresh" content="0; url=https://avd.aquasec.com/misconfig/aws/ec2/aws-0104/">
</head></html>
''',
        'trivy_refresh_guide': '''
<html>
  <h1>No Public Egress SGR</h1>
  <h3>Recommended Actions</h3>
  <p>Set a more restrictive cidr range.</p>
  <pre><code>resource "aws_security_group" "good_example" {}</code></pre>
  <h3>Links</h3>
</html>
''',
        'trivy_untrusted_refresh': (
            '<html><head><meta http-equiv="refresh" '
            'content="0; url=http://169.254.169.254/latest/meta-data/"></head>'
            '<body><h1>No Public Egress SGR</h1>'
            '<h3>Recommended Actions</h3><p>Keep the already-fetched guide.</p>'
            '<pre><code>resource "aws_security_group" "good_example" {}</code></pre>'
            '</body></html>'
        ),
        'trivy_stub': '''<!doctype html>
<html lang=en-us>
<head>
    <title>https://avd.aquasec.com/misconfig/aws/ec2/aws-0104/</title>
    <link rel=canonical href=https://avd.aquasec.com/misconfig/aws/ec2/aws-0104 />
    <meta name=robots content="noindex">
    <meta charset=utf-8>
    <meta http-equiv=refresh content="0; url=https://avd.aquasec.com/misconfig/aws/ec2/aws-0104/">
</head>
</html>''',
        'trivy_stub_guide': '''<html><h1>No Public Egress SGR</h1>
<h3>Recommended Actions</h3><p>Restrict the cidr range.</p>
<pre><code>resource "aws_security_group" "good_example" {}</code></pre></html>''',
        'tfsec_formatting': '''
<html>
  <h1>S3 Access block should block public ACL</h1>
  <p>Default Severity: high</p>
  <h2>Explanation</h2><p>S3 buckets should block public ACLs.</p>
  <h2>Possible Impact</h2><p>PUT calls with public ACLs specified can make objects public</p>
  <h2>Suggested Resolution</h2><p>Enable blocking any PUT calls with a public ACL specified</p>
  <h2>Insecure Example</h2>
  <pre><code><span>resource</span> <span>"aws_s3_bucket"</span> <span>"bad_example"</span> <span>{</span>
  <span>bucket</span> <span>=</span> <span>"mybucket"</span>
<span>}</span></code></pre>
  <h2>Secure Example</h2>
  <pre><code>resource "aws_s3_bucket_public_access_block" "good_example" {
  bucket = aws_s3_bucket.good_example.id
  block_public_acls = true
}</code></pre>
</html>
''',
        'checkov_formatting': '''
<html>
  <h1>AWS security group allows unrestricted SSH</h1>
  <h2>Rule Details</h2><p>Severity</p><p>HIGH</p>
  <h2>Impact</h2><p>Public SSH access exposes the server.</p>
  <h2>How to Fix</h2>
  <p>Restrict the source CIDR range.</p>
  <p>Resource: aws_security_group</p>
  <p>Arguments: ingress.cidr_blocks [source,go]</p>
  <pre><code>resource "aws_security_group" "fixed" {
  ingress {
    cidr_blocks = ["10.0.0.0/8"]
  }
}</code></pre>
  <h2>References</h2><p>Exclude this unrelated section.</p>
</html>
''',
        'checkov_prose': '''
<html>
  <h1>S3 versioning is disabled</h1>
  <h2>Impact</h2><p>Objects can be overwritten without recovery.</p>
  <h2>How to Fix</h2><ul><li>Enable bucket versioning.</li></ul>
</html>
''',
        'checkov_redirect': '''
<html>
  <h1>S3 versioning is disabled</h1>
  <h2>How to Fix</h2><p>Enable bucket versioning.</p>
</html>
''',
        'tfsec_retry': '''
<h1>S3 Access block should block public ACL</h1>
<h2>Suggested Resolution</h2><p>Enable blocking public ACLs.</p>
''',
        'tfsec_labels': '''
<h1>S3 Access block should block public ACL</h1>
<h3>Suggested Resolution</h3><p>Enable blocking public ACLs.</p>
<h3>Insecure Example</h3>
<pre>resource "aws_s3_bucket" "bad_example" {}</pre>
<h3>Secure Example</h3>
<pre>resource "aws_s3_bucket" "good_example" {}</pre>
<h3>Links</h3><p>Do not include this unrelated section.</p>
''',
        'trivy_tab': '''
<h1>Block Public ACLs</h1>
<h3>Recommended Actions</h3>
<p>Follow the appropriate remediation steps below.</p>
<div class="tab-panel">
  <div class="tab-nav"><button>CloudFormation</button><button>Management Console</button><button>Terraform</button></div>
  <div class="tab-content">
    <div class="tab-item"><p>CFN text.</p><pre>Resources: {}</pre></div>
    <div class="tab-item"><ol><li>Log in to the AWS Management Console.</li></ol></div>
    <div class="tab-item"><p>Enable blocking PUT calls.</p><pre>resource "aws_s3_bucket" "good_example" {}</pre></div>
  </div>
</div>
<h3>Links</h3>
''',
        'trivy_description': '''
<h1>No Public Egress SGR</h1>
<div class="content vulnerability_content">
  <h3 id="summary">A security group rule should not allow unrestricted egress.</h3>
  <p>Opening up ports to the public internet is generally to be avoided.</p>
  <h3 id="impact">Impact</h3>
  <h3 id="recommended-actions">Recommended Actions</h3>
  <p>Set a more restrictive cidr range</p>
  <pre>resource "aws_security_group" "good_example" {}</pre>
  <h3 id="links">Links</h3>
</div>
''',
        'section_nested': '''
<h2>Explanation</h2>
<ul><li>Use encryption.<p>Enable encryption at rest.</p></li></ul>
<h2>Suggested Resolution</h2>
''',
        'section_container': '''
<article><h2>Suggested Resolution</h2><p>Enable it.</p></article>
<footer><p>Copyright footer</p></footer>
''',
        'checkov_rendered_examples': '''
<html>
  <h1>Rendered Terraform remediation</h1>
  <h2>How to Fix</h2>
  <ul>
    <li><p>resource "aws_s3_bucket" "fixed" {</p></li>
    <li>  versioning {</li>
    <li>    enabled = true</li>
    <li>  }</li>
    <li>}</li>
    <li>data "aws_caller_identity" "current" {}</li>
  </ul>
</html>
''',
        'section_heading': '<h2>Explanation</h2><div><p>Important explanation text.</p><h3>Details</h3><p>More.</p></div>',
        'section_wrapped': '<div><h2>Explanation</h2></div><div><p>Explanation text.</p></div><h2>Next</h2><p>Other.</p>',
        'terraform_tab': '''
<h2>Insecure Example</h2>
<div class="tab-panel">
  <div class="tab-nav"><button>CloudFormation</button><button>Terraform</button></div>
  <div class="tab-content">
    <div class="tab-item"><pre>Resources: {}</pre></div>
    <div class="tab-item"><pre>resource "aws_s3_bucket" "good" {}</pre></div>
  </div>
</div>
''',
        'terraform_examples': '''
<h2>Insecure Example</h2>
<pre>resource "aws_s3_bucket" "bad" {}</pre>
<h2>Secure Example</h2>
<div class="code-wrapper"><pre>resource "aws_s3_bucket" "good" {}</pre></div>
''',
        'code_block': '<div><pre>resource "a" "b" {<br>  x = 1<br/>}</pre></div>'
    }


@pytest.fixture
def trivy_guide_pages(web_rag_documents):
    return {
        'https://avd.aquasec.com/misconfig/aws-0104': SimpleNamespace(
            text=web_rag_documents['trivy_stub'],
            raise_for_status=lambda: None
        ),
        'https://avd.aquasec.com/misconfig/aws/ec2/aws-0104/': SimpleNamespace(
            text=web_rag_documents['trivy_stub_guide'],
            raise_for_status=lambda: None
        )
    }


@pytest.fixture
def tflint_fetch_response(web_rag_documents):
    return SimpleNamespace(
        text=web_rag_documents['tflint_fetch_response'],
        raise_for_status=lambda: None
    )


@pytest.fixture
def trivy_refresh_responses(web_rag_documents):
    return [
        SimpleNamespace(text=web_rag_documents['trivy_refresh'], raise_for_status=lambda: None),
        SimpleNamespace(text=web_rag_documents['trivy_refresh_guide'], raise_for_status=lambda: None)
    ]


@pytest.fixture
def trivy_untrusted_response(web_rag_documents):
    return SimpleNamespace(
        text=web_rag_documents['trivy_untrusted_refresh'],
        raise_for_status=lambda: None
    )


@pytest.fixture
def checkov_redirect_response(web_rag_documents):
    return SimpleNamespace(
        url='https://cortex-docs.paloaltonetworks.com/appsec-rules/checkov-guide',
        text=web_rag_documents['checkov_redirect'],
        raise_for_status=lambda: None
    )


@pytest.fixture
def tfsec_retry_responses(web_rag_documents):
    return [
        SimpleNamespace(status_code=404, text='', raise_for_status=lambda: None),
        SimpleNamespace(
            status_code=200,
            text=web_rag_documents['tfsec_retry'],
            raise_for_status=lambda: None
        )
    ]


@pytest.fixture
def trivy_refresh_response_iterator(trivy_refresh_responses):
    return iter(trivy_refresh_responses)


@pytest.fixture
def tfsec_retry_response_iterator(tfsec_retry_responses):
    return iter(tfsec_retry_responses)


@pytest.fixture
def tfsec_untrusted_first_source(log_file_text_tfsec, tfsec_dynamodb_guide_url):
    return log_file_text_tfsec.replace(
        tfsec_dynamodb_guide_url,
        f'https://example.com/first {tfsec_dynamodb_guide_url}',
        1
    )
