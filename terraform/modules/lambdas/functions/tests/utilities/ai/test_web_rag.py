import pytest


def test_extract_trivy_guide_urls_preserves_order_and_deduplicates(
        patched_environment, log_file_text_trivy, expected_trivy_guide_urls
):
    from utilities.ai.web_rag import extract_trivy_guide_urls

    urls = extract_trivy_guide_urls(log_file_text_trivy)

    assert urls == expected_trivy_guide_urls


def test_extract_checkov_guide_urls_preserves_order_and_deduplicates(
        patched_environment, log_file_text_checkov, expected_checkov_guide_urls
):
    from utilities.ai.web_rag import extract_checkov_guide_urls

    urls = extract_checkov_guide_urls(log_file_text_checkov)

    assert urls == expected_checkov_guide_urls


def test_extract_tfsec_guide_urls_preserves_order_and_deduplicates(
        patched_environment, log_file_text_tfsec, expected_tfsec_guide_urls
):
    from utilities.ai.web_rag import extract_tfsec_guide_urls

    urls = extract_tfsec_guide_urls(log_file_text_tfsec)

    assert urls == expected_tfsec_guide_urls


def test_extract_tflint_guide_urls_preserves_order_and_deduplicates(
        patched_environment, log_file_text_tflint, expected_tflint_guide_urls
):
    from utilities.ai.web_rag import extract_tflint_guide_urls

    urls = extract_tflint_guide_urls(log_file_text_tflint)

    assert urls == expected_tflint_guide_urls


def test_extract_tflint_guide_urls_rejects_untrusted_urls(patched_environment, tflint_untrusted_errors):
    from utilities.ai.web_rag import extract_tflint_guide_urls

    assert extract_tflint_guide_urls(tflint_untrusted_errors) == []


@pytest.mark.parametrize(
    ("validator_name", "url"),
    [
        ("is_trivy_guide_url", "http://avd.aquasec.com/misconfig/aws-0104"),
        ("is_trivy_guide_url", "https://avd.aquasec.com:8080/misconfig/aws-0104"),
        ("is_trivy_guide_url", "https://avd.aquasec.com:not-a-port/misconfig/aws-0104"),
        ("is_checkov_guide_url", "http://docs.prismacloud.io/checkov-guide"),
        ("is_checkov_guide_url", "https://docs.prismacloud.io.evil.example/checkov-guide"),
        ("is_checkov_guide_url", "https://docs.prismacloud.io:not-a-port/checkov-guide"),
        (
                "is_tflint_guide_url",
                "https://github.com:8080/terraform-linters/tflint-ruleset-terraform/blob/v0.13.0/docs/rules/rule.md"
        ),
        (
                "is_tflint_guide_url",
                "https://github.com:not-a-port/terraform-linters/tflint-ruleset-terraform/blob/v0.13.0/docs/rules/rule.md"
        ),
        ("is_tflint_guide_url", "https://github.com/other/project/blob/v0.13.0/docs/rules/rule.md"),
        (
                "is_tflint_guide_url",
                "https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.13.0/docs/rules/rule.md?download=1"
        )
    ]
)
def test_guide_url_validators_reject_untrusted_or_malformed_urls(patched_environment, validator_name, url):
    from utilities.ai import web_rag

    assert not getattr(web_rag, validator_name)(url)


def test_parse_tflint_guide_extracts_focused_remediation(
        patched_environment, tflint_required_version_url, tflint_guide_markdown
):
    from utilities.ai.web_rag import parse_tflint_guide

    result = parse_tflint_guide(tflint_required_version_url, tflint_guide_markdown)

    assert result.startswith(f"{tflint_required_version_url}\nterraform_required_version")
    assert "Disallow `terraform` declarations without `required_version`." in result
    assert "The required version constrains which Terraform CLI versions can be used." in result
    assert "Add the `required_version` attribute" in result
    assert "```hcl\nterraform {" in result
    assert 'rule "terraform_required_version"' not in result
    assert "$ tflint" not in result
    assert (
            result
            == f'{tflint_required_version_url}\nterraform_required_version\nDisallow `terraform` declarations without `required_version`.\nThis rule is enabled by the recommended preset.\nThe required version constrains which Terraform CLI versions can be used.\nAdd the `required_version` attribute to the Terraform configuration block.\n```hcl\nterraform {{\n  required_version = ">= 1.0"\n}}\n```'
    )


def test_fetch_tflint_guide_uses_raw_github_url(
        patched_environment, monkeypatch, tflint_required_version_url, tflint_fetch_response
):
    from utilities.ai import web_rag

    requested_urls = []

    def request_page(requested_url):
        requested_urls.append(requested_url)
        return tflint_fetch_response

    monkeypatch.setattr(web_rag, "_request_page", request_page)

    result = web_rag._fetch_tflint_guide(tflint_required_version_url)

    assert requested_urls == [
        "https://raw.githubusercontent.com/terraform-linters/tflint-ruleset-terraform/v0.13.0/docs/rules/terraform_required_version.md"
    ]
    assert result.startswith(f"{tflint_required_version_url}\nterraform_required_version")


def test_extract_tflint_guides_skips_failed_requests(
        patched_environment, monkeypatch, caplog, tflint_required_version_url
):
    import requests

    from utilities.ai import web_rag

    def raise_request_error(_url):
        raise requests.RequestException("connection failed")

    monkeypatch.setattr(web_rag, "_fetch_tflint_guide", raise_request_error)

    assert web_rag.extract_tflint_guides(f"Reference: {tflint_required_version_url}") == ""
    assert "Unable to retrieve TFLint guide" in caplog.text


def test_parse_trivy_guide_preserves_hcl_formatting(patched_environment, web_rag_documents):
    from utilities.ai.web_rag import parse_trivy_guide

    result = parse_trivy_guide(
        "https://avd.aquasec.com/misconfig/aws/ec2/aws-0104/", web_rag_documents["trivy_formatting"]
    )

    assert 'resource "aws_security_group" "good_example" {' in result
    assert '    cidr_blocks = ["1.2.3.4/32"]' in result
    assert 'resource\n"aws_security_group"' not in result
    assert (
            result
            == 'https://avd.aquasec.com/misconfig/aws/ec2/aws-0104/\nNo Public Egress SGR\nSet a more restrictive cidr range.\n```hcl\nresource "aws_security_group" "good_example" {\n  egress {\n    cidr_blocks = ["1.2.3.4/32"]\n  }\n}\n```'
    )


def test_extract_trivy_guides_parses_terraform_remediation(patched_environment, monkeypatch, web_rag_documents):
    from utilities.ai import web_rag

    monkeypatch.setattr(
        web_rag,
        "_fetch_trivy_guide",
        lambda url: web_rag.parse_trivy_guide(url, web_rag_documents["trivy_remediation"])
    )

    result = web_rag.extract_trivy_guides("See https://avd.aquasec.com/misconfig/aws/ec2/aws-0104")

    assert "No Public Egress SGR" in result
    assert "Set a more restrictive cidr range." in result
    assert 'resource "aws_security_group" "good_example"' in result
    assert "Do not include this unrelated section." not in result


def test_extract_trivy_guides_skips_failed_requests(patched_environment, monkeypatch, caplog):
    import requests

    from utilities.ai import web_rag

    def raise_request_error(_url):
        raise requests.RequestException("connection failed")

    monkeypatch.setattr(web_rag, "_fetch_trivy_guide", raise_request_error)

    result = web_rag.extract_trivy_guides("See https://avd.aquasec.com/misconfig/aws/ec2/aws-0104")

    assert result == ""
    assert "Unable to retrieve Trivy guide" in caplog.text


def test_fetch_trivy_guide_follows_html_refresh(patched_environment, monkeypatch, trivy_refresh_response_iterator):
    from utilities.ai import web_rag

    requested_urls = []

    def request_page(url):
        requested_urls.append(url)
        return next(trivy_refresh_response_iterator)

    monkeypatch.setattr(web_rag, "_request_page", request_page)

    result = web_rag._fetch_trivy_guide("https://avd.aquasec.com/misconfig/aws-0104")

    assert requested_urls == [
        "https://avd.aquasec.com/misconfig/aws-0104",
        "https://avd.aquasec.com/misconfig/aws/ec2/aws-0104/"
    ]
    assert "```hcl" in result
    assert 'resource "aws_security_group" "good_example"' in result


def test_extract_trivy_guide_urls_rejects_other_hosts(patched_environment, trivy_untrusted_errors):
    from utilities.ai.web_rag import extract_trivy_guide_urls

    assert extract_trivy_guide_urls(trivy_untrusted_errors) == ["https://avd.aquasec.com/misconfig/aws-0104"]


def test_fetch_trivy_guide_refuses_refresh_to_other_host(patched_environment, monkeypatch, trivy_untrusted_response):
    from utilities.ai import web_rag

    requested_urls = []

    def request_page(url):
        requested_urls.append(url)
        return trivy_untrusted_response

    monkeypatch.setattr(web_rag, "_request_page", request_page)

    result = web_rag._fetch_trivy_guide("https://avd.aquasec.com/misconfig/aws-0104")

    assert "Keep the already-fetched guide." in result
    assert 'resource "aws_security_group" "good_example" {}' in result
    assert requested_urls == ["https://avd.aquasec.com/misconfig/aws-0104"]


def test_fetch_trivy_guide_follows_relative_canonical_link(patched_environment, monkeypatch, web_rag_documents):
    from types import SimpleNamespace

    from utilities.ai import web_rag

    initial_url = "https://avd.aquasec.com/misconfig/aws-0104"
    canonical_url = "https://avd.aquasec.com/misconfig/aws/ec2/aws-0104/"
    responses = {
        initial_url: SimpleNamespace(
            text='<html><link rel="canonical" href="/misconfig/aws/ec2/aws-0104/"></html>',
            raise_for_status=lambda: None
        ),
        canonical_url: SimpleNamespace(text=web_rag_documents["trivy_refresh_guide"], raise_for_status=lambda: None)
    }
    requested_urls = []

    def request_page(url):
        requested_urls.append(url)
        return responses[url]

    monkeypatch.setattr(web_rag, "_request_page", request_page)

    result = web_rag._fetch_trivy_guide(initial_url)

    assert requested_urls == [initial_url, canonical_url]
    assert result.startswith(f"{canonical_url}\nNo Public Egress SGR")


def test_fetch_trivy_guide_stops_refresh_loop_and_parses_current_page(patched_environment, monkeypatch):
    from types import SimpleNamespace

    from utilities.ai import web_rag

    first_url = "https://avd.aquasec.com/misconfig/aws-0104"
    second_url = "https://avd.aquasec.com/misconfig/aws/ec2/aws-0104/"
    responses = {
        first_url: SimpleNamespace(
            text=f'<meta http-equiv="refresh" content="0; url={second_url}">', raise_for_status=lambda: None
        ),
        second_url: SimpleNamespace(
            text=(
                f'<meta http-equiv="refresh" content="0; url={first_url}">'
                "<h1>Looped guide</h1><h3>Recommended Actions</h3>"
                "<p>Use the already-fetched page.</p>"
            ),
            raise_for_status=lambda: None
        )
    }
    requested_urls = []

    def request_page(url):
        requested_urls.append(url)
        return responses[url]

    monkeypatch.setattr(web_rag, "_request_page", request_page)

    result = web_rag._fetch_trivy_guide(first_url)

    assert requested_urls == [first_url, second_url]
    assert result == f"{second_url}\nLooped guide\nUse the already-fetched page."


def test_fetch_trivy_guide_stops_after_maximum_refresh_hops(patched_environment, monkeypatch):
    from types import SimpleNamespace

    from utilities.ai import web_rag

    urls = [f"https://avd.aquasec.com/misconfig/hop-{index}" for index in range(web_rag.TRIVY_MAX_REFRESH_HOPS + 2)]
    responses = {
        url: SimpleNamespace(
            text=f'<meta http-equiv="refresh" content="0; url={urls[index + 1]}">', raise_for_status=lambda: None
        )
        for index, url in enumerate(urls[:-1])
    }
    requested_urls = []

    def request_page(url):
        requested_urls.append(url)
        return responses[url]

    monkeypatch.setattr(web_rag, "_request_page", request_page)

    assert web_rag._fetch_trivy_guide(urls[0]) == ""
    assert requested_urls == urls[: web_rag.TRIVY_MAX_REFRESH_HOPS + 1]


def test_fetch_trivy_guide_accepts_unquoted_same_domain_stub(patched_environment, monkeypatch, trivy_guide_pages):
    from utilities.ai import web_rag

    requested_urls = []

    def request_page(url):
        requested_urls.append(url)
        return trivy_guide_pages[url]

    monkeypatch.setattr(web_rag, "_request_page", request_page)

    result = web_rag._fetch_trivy_guide("https://avd.aquasec.com/misconfig/aws-0104")

    assert requested_urls == list(trivy_guide_pages)
    assert 'resource "aws_security_group" "good_example"' in result


def test_extract_tfsec_guide_url_uses_only_first_aquasecurity_source(
        patched_environment, tfsec_untrusted_first_source, tfsec_dynamodb_guide_url
):
    from utilities.ai.web_rag import extract_tfsec_guide_url

    assert extract_tfsec_guide_url(tfsec_untrusted_first_source) == tfsec_dynamodb_guide_url


def test_parse_tfsec_guide_preserves_hcl_formatting(patched_environment, tfsec_guide_urls, web_rag_documents):
    from utilities.ai.web_rag import parse_tfsec_guide

    result = parse_tfsec_guide(tfsec_guide_urls[0], web_rag_documents["tfsec_formatting"])

    assert "Default Severity" not in result
    assert "high" not in result
    assert 'resource "aws_s3_bucket" "bad_example" {' in result
    assert "  block_public_acls = true" in result
    assert 'resource\n"aws_s3_bucket"' not in result
    assert result == "\n".join(
        [
            tfsec_guide_urls[0],
            "S3 Access block should block public ACL",
            "S3 buckets should block public ACLs.",
            "PUT calls with public ACLs specified can make objects public",
            "Enable blocking any PUT calls with a public ACL specified",
            "Insecure Example",
            "```hcl",
            ('resource "aws_s3_bucket" "bad_example" {\n  bucket = "mybucket"\n}'),
            "```",
            "Secure Example",
            "```hcl",
            (
                'resource "aws_s3_bucket_public_access_block" "good_example" {\n'
                "  bucket = aws_s3_bucket.good_example.id\n"
                "  block_public_acls = true\n"
                "}"
            ),
            "```"
        ]
    )


def test_parse_checkov_guide_includes_impact_fix_and_terraform_example(patched_environment, web_rag_documents):
    from utilities.ai.web_rag import parse_checkov_guide

    result = parse_checkov_guide(
        "https://docs.prismacloud.io/en/enterprise-edition/policy-reference/checkov-guide",
        web_rag_documents["checkov_formatting"]
    )

    assert "AWS security group allows unrestricted SSH" in result
    assert "Public SSH access exposes the server." in result
    assert "Restrict the source CIDR range." in result
    assert "aws_security_group" in result
    assert "ingress.cidr_blocks" in result
    assert "Resource:" not in result
    assert "Arguments:" not in result
    assert "[source,go]" not in result
    assert 'resource "aws_security_group" "fixed"' in result
    assert '```hcl\nresource "aws_security_group" "fixed"' in result
    assert "\n  ingress {" in result
    assert '\n    cidr_blocks = ["10.0.0.0/8"]' in result
    assert result.endswith("\n```")
    assert "HIGH" not in result
    assert "Exclude this unrelated section." not in result


def test_parse_checkov_guide_keeps_prose_without_terraform_example(
        patched_environment, checkov_guide_url, web_rag_documents
):
    from utilities.ai.web_rag import parse_checkov_guide

    result = parse_checkov_guide(checkov_guide_url, web_rag_documents["checkov_prose"])

    assert "Objects can be overwritten without recovery." in result
    assert "Enable bucket versioning." in result


def test_parse_checkov_guide_extracts_rendered_terraform_lines(patched_environment, web_rag_documents):
    from utilities.ai.web_rag import parse_checkov_guide

    result = parse_checkov_guide(
        "https://docs.prismacloud.io/checkov-rendered-guide", web_rag_documents["checkov_rendered_examples"]
    )

    assert (
            result
            == 'https://docs.prismacloud.io/checkov-rendered-guide\nRendered Terraform remediation\n```hcl\nresource "aws_s3_bucket" "fixed" {\n  versioning {\n    enabled = true\n  }\n}\ndata "aws_caller_identity" "current" {\n}\n```'
    )


@pytest.mark.parametrize(
    "parser_name", ["parse_trivy_guide", "parse_tfsec_guide", "parse_checkov_guide", "parse_tflint_guide"]
)
def test_guide_parsers_return_empty_for_empty_documents(patched_environment, parser_name):
    from utilities.ai import web_rag

    parser = getattr(web_rag, parser_name)

    assert parser("https://example.com/guide", "") == ""


def test_extract_checkov_guides_fetches_all_sources(patched_environment, monkeypatch, checkov_guide_urls):
    from utilities.ai import web_rag

    fetched_urls = []

    def fetch_guide(url):
        fetched_urls.append(url)
        return f"Guide content for {url}"

    monkeypatch.setattr(web_rag, "_fetch_checkov_guide", fetch_guide)

    result = web_rag.extract_checkov_guides("\n".join(f"Guide: {url}" for url in checkov_guide_urls))

    assert fetched_urls == checkov_guide_urls
    assert result == "\n---\n".join(f"Guide content for {url}" for url in checkov_guide_urls)


def test_extract_checkov_guides_skips_failed_requests(patched_environment, monkeypatch, caplog):
    import requests

    from utilities.ai import web_rag

    def raise_request_error(_url):
        raise requests.RequestException("connection failed")

    monkeypatch.setattr(web_rag, "_fetch_checkov_guide", raise_request_error)

    result = web_rag.extract_checkov_guides("Guide: https://docs.prismacloud.io/checkov-guide")

    assert result == ""
    assert "Unable to retrieve Checkov guide" in caplog.text


def test_fetch_checkov_guide_preserves_original_url_after_redirect(
        patched_environment, monkeypatch, checkov_guide_url, checkov_redirect_response
):
    from utilities.ai import web_rag

    monkeypatch.setattr(web_rag, "_request_page", lambda url: checkov_redirect_response)

    result = web_rag._fetch_checkov_guide(checkov_guide_url)

    assert result.startswith(f"{checkov_guide_url}\n")
    assert "https://cortex-docs.paloaltonetworks.com" not in result


def test_fetch_tfsec_guide_retries_latest_after_404(
        patched_environment, monkeypatch, tfsec_guide_urls, tfsec_retry_response_iterator
):
    from utilities.ai import web_rag

    requested_urls = []

    def request_page(url):
        requested_urls.append(url)
        return next(tfsec_retry_response_iterator)

    monkeypatch.setattr(web_rag, "_request_page", request_page)

    result = web_rag._fetch_tfsec_guide(tfsec_guide_urls[0])

    assert requested_urls == [
        tfsec_guide_urls[0],
        "https://aquasecurity.github.io/tfsec/latest/checks/aws/s3/block-public-acls/"
    ]
    assert "Enable blocking public ACLs." in result
    assert "Suggested Resolution" not in result


def test_extract_tfsec_guide_skips_failed_requests(patched_environment, monkeypatch, caplog):
    import requests

    from utilities.ai import web_rag

    def raise_request_error(_url):
        raise requests.RequestException("connection failed")

    monkeypatch.setattr(web_rag, "_fetch_tfsec_guide", raise_request_error)

    result = web_rag.extract_tfsec_guide(
        "https://aquasecurity.github.io/tfsec/v1.28.14/checks/aws/s3/block-public-acls/"
    )

    assert result == ""
    assert "Unable to retrieve TFSec guide" in caplog.text


def test_extract_tfsec_guide_fetches_all_aquasecurity_sources(patched_environment, monkeypatch, tfsec_guide_urls):
    from utilities.ai import web_rag

    fetched_urls = []

    def fetch_guide(url):
        fetched_urls.append(url)
        return f"Guide: {url}"

    monkeypatch.setattr(web_rag, "_fetch_tfsec_guide", fetch_guide)

    result = web_rag.extract_tfsec_guide(
        "\n".join(tfsec_guide_urls)
        + "\nhttps://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket"
    )

    assert fetched_urls == tfsec_guide_urls
    assert result == "\n---\n".join(f"Guide: {url}" for url in tfsec_guide_urls)


def test_extract_tflint_guides_fetches_all_sources(patched_environment, monkeypatch, expected_tflint_guide_urls):
    from utilities.ai import web_rag

    fetched_urls = []

    def fetch_guide(url):
        fetched_urls.append(url)
        return f"Guide content for {url}"

    monkeypatch.setattr(web_rag, "_fetch_tflint_guide", fetch_guide)

    result = web_rag.extract_tflint_guides("\n".join(f"Reference: {url}" for url in expected_tflint_guide_urls))

    assert fetched_urls == expected_tflint_guide_urls
    assert result == "\n---\n".join(f"Guide content for {url}" for url in expected_tflint_guide_urls)


def test_parse_tfsec_guide_labels_insecure_and_secure_examples(patched_environment, web_rag_documents):
    from utilities.ai.web_rag import parse_tfsec_guide

    result = parse_tfsec_guide("https://aquasecurity.github.io/tfsec/latest/", web_rag_documents["tfsec_labels"])

    assert result.index("Insecure Example") < result.index("bad_example")
    assert result.index("\nSecure Example") < result.index("good_example")
    assert result.index("bad_example") < result.index("\nSecure Example")
    assert "Do not include this unrelated section." not in result


def test_parse_trivy_guide_prefers_terraform_tab(patched_environment, web_rag_documents):
    from utilities.ai.web_rag import parse_trivy_guide

    result = parse_trivy_guide("https://avd.aquasec.com/misconfig/aws/s3/aws-0086/", web_rag_documents["trivy_tab"])

    assert "Enable blocking PUT calls." in result
    assert 'resource "aws_s3_bucket" "good_example"' in result
    assert "Management Console" not in result
    assert "CFN text." not in result


def test_parse_trivy_guide_includes_rule_description(patched_environment, web_rag_documents):
    from utilities.ai.web_rag import parse_trivy_guide

    result = parse_trivy_guide(
        "https://avd.aquasec.com/misconfig/aws/ec2/aws-0104/", web_rag_documents["trivy_description"]
    )

    assert "\nA security group rule should not allow unrestricted egress.\n" in result
    assert "Opening up ports to the public internet is generally to be avoided." in result
    assert result.index("A security group rule") < result.index("Set a more restrictive cidr range")


def test_parse_trivy_guide_removes_remediation_links(patched_environment):
    from utilities.ai.web_rag import parse_trivy_guide

    result = parse_trivy_guide(
        "https://avd.aquasec.com/misconfig/aws-0104/",
        """
<h1>No Public Egress SGR</h1>
<h3>Recommended Actions</h3><p>Set a restrictive egress range.</p>
<h4>Remediation Links</h4><ul><li>https://example.com/remediation</li></ul>
<h3>Links</h3><p>Do not include this section.</p>
"""
    )

    assert (
            result == "https://avd.aquasec.com/misconfig/aws-0104/\nNo Public Egress SGR\nSet a restrictive egress range."
    )


def test_section_text_does_not_duplicate_nested_text_blocks(patched_environment, web_rag_documents):
    from bs4 import BeautifulSoup

    from utilities.ai.web_rag import _section_text

    soup = BeautifulSoup(web_rag_documents["section_nested"], "html.parser")

    assert _section_text(soup, "Explanation") == "Use encryption. Enable encryption at rest."


def test_section_text_stays_inside_heading_container(patched_environment, web_rag_documents):
    from bs4 import BeautifulSoup

    from utilities.ai.web_rag import _section_text

    soup = BeautifulSoup(web_rag_documents["section_container"], "html.parser")

    assert _section_text(soup, "Suggested Resolution") == "Enable it."


def test_section_text_keeps_text_before_nested_heading(patched_environment, web_rag_documents):
    from bs4 import BeautifulSoup

    from utilities.ai.web_rag import _section_text

    soup = BeautifulSoup(web_rag_documents["section_heading"], "html.parser")

    assert _section_text(soup, "Explanation") == "Important explanation text."


def test_section_text_follows_heading_wrapped_in_its_own_container(patched_environment, web_rag_documents):
    from bs4 import BeautifulSoup

    from utilities.ai.web_rag import _section_text

    soup = BeautifulSoup(web_rag_documents["section_wrapped"], "html.parser")

    assert _section_text(soup, "Explanation") == "Explanation text."


def test_terraform_examples_ignore_heading_outside_scope(patched_environment, web_rag_documents):
    from bs4 import BeautifulSoup

    from utilities.ai.web_rag import _terraform_examples, _terraform_tab

    soup = BeautifulSoup(web_rag_documents["terraform_tab"], "html.parser")
    terraform_tab = _terraform_tab(soup)
    assert terraform_tab is not None

    assert _terraform_examples(terraform_tab) == [("", 'resource "aws_s3_bucket" "good" {}')]


def test_terraform_examples_keep_heading_inside_scope(patched_environment, web_rag_documents):
    from bs4 import BeautifulSoup

    from utilities.ai.web_rag import _terraform_examples

    soup = BeautifulSoup(web_rag_documents["terraform_examples"], "html.parser")

    assert _terraform_examples(soup) == [
        ("Insecure Example", 'resource "aws_s3_bucket" "bad" {}'),
        ("Secure Example", 'resource "aws_s3_bucket" "good" {}')
    ]


@pytest.mark.parametrize(
    "code",
    [
        'terraform {\n  required_version = ">= 1.5.0"\n}',
        "locals {\n  common_tags = {}\n}",
        'variable "bucket_name" {\n  type = string\n}',
        'output "bucket_id" {\n  value = aws_s3_bucket.example.id\n}',
        "moved {\n  from = a.b\n  to = a.c\n}",
        'import {\n  to = a.b\n  id = "x"\n}',
        'check "health" {\n}',
        '  resource "aws_s3_bucket" "example" {}',
        '# comment\ndata "aws_caller_identity" "current" {}'
    ]
)
def test_terraform_code_pattern_matches_valid_blocks(patched_environment, code):
    from utilities.ai.web_rag import TERRAFORM_CODE_PATTERN

    assert TERRAFORM_CODE_PATTERN.search(code)


@pytest.mark.parametrize(
    "code",
    [
        "terraform init",
        "import os\ncheck = 1",
        'import "fmt"\nfunc main() {}',
        "Resources:\n  Bucket:\n    Type: AWS::S3::Bucket"
    ]
)
def test_terraform_code_pattern_ignores_other_languages(patched_environment, code):
    from utilities.ai.web_rag import TERRAFORM_CODE_PATTERN

    assert not TERRAFORM_CODE_PATTERN.search(code)


def test_extract_code_block_converts_line_breaks_without_modifying_tree(patched_environment, web_rag_documents):
    from bs4 import BeautifulSoup

    from utilities.ai.web_rag import _extract_code_block

    soup = BeautifulSoup(web_rag_documents["code_block"], "html.parser")
    original = str(soup)
    pre = soup.pre
    assert pre is not None

    assert _extract_code_block(pre) == 'resource "a" "b" {\n  x = 1\n}'
    assert str(soup) == original
    assert len(pre.find_all("br")) == 2
