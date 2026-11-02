import re
from collections.abc import Iterable
from copy import copy
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag
from bs4.exceptions import ParserRejectedMarkup

from config import config
from utilities.logger import logger

TRIVY_GUIDE_HOST = 'avd.aquasec.com'
TRIVY_MAX_REFRESH_HOPS = 3
TRIVY_GUIDE_URL_PATTERN = re.compile(
    r"(?m)^\s*See\s+(https://avd\.aquasec\.com/\S*)"
)
CHECKOV_GUIDE_HOST = 'docs.prismacloud.io'
CHECKOV_GUIDE_URL_PATTERN = re.compile(
    r"(?m)^\s*Guide:\s+(https://docs\.prismacloud\.io/\S*)"
)
TFSEC_GUIDE_URL_PATTERN = re.compile(
    r"https://aquasecurity\.github\.io/tfsec/[^\s<>)\]]+"
)
TFLINT_GUIDE_HOST = 'github.com'
TFLINT_GUIDE_REPOSITORY = 'terraform-linters/tflint-ruleset-terraform'
TFLINT_GUIDE_URL_PATTERN = re.compile(
    r"https://github\.com/terraform-linters/tflint-ruleset-terraform/blob/"
    r"[^/\s]+/docs/rules/[A-Za-z0-9_.-]+\.md(?:[?#][^\s<>)\]]*)?"
)
HTML_PARSER = 'html.parser'
HEADING_TAGS = ['h2', 'h3']
TEXT_TAGS = ['p', 'h4', 'li']
PAGE_CHROME_TAGS = ['footer', 'nav', 'aside']
SUGGESTED_RESOLUTION_TITLE = 'Suggested Resolution'
GUIDE_SEPARATOR = '\n---\n'
TERRAFORM_CODE_PATTERN = re.compile(
    r"(?m)^\s*(?:"
    r"(?:resource|data|module|provider|variable|output|check)\s+\""
    r"|(?:locals|terraform|moved|import|check)\s*\{"
    r")"
)
CHECKOV_METADATA_LABEL_PATTERN = re.compile(r"^(?:Resource|Arguments):\s*", re.IGNORECASE)


def is_trivy_guide_url(url: str) -> bool:
    """Return whether a URL is an allowed Trivy guide URL.

    Args:
        url (str): URL to validate.

    Returns:
        bool: True for an HTTPS URL on the Trivy guide host without userinfo or
            a custom port; otherwise False.
    """
    try:
        parsed = urlparse(url)
        return (
                parsed.scheme == 'https'
                and parsed.hostname == TRIVY_GUIDE_HOST
                and parsed.port is None
                and parsed.username is None
        )
    except ValueError:
        return False


def is_checkov_guide_url(url: str) -> bool:
    """Return whether a URL is an allowed Checkov guide URL.

    Args:
        url (str): URL to validate.

    Returns:
        bool: True for an HTTPS URL on the Checkov guide host without userinfo
            or a custom port; otherwise False.
    """
    try:
        parsed = urlparse(url)
        return (
                parsed.scheme == 'https'
                and parsed.hostname == CHECKOV_GUIDE_HOST
                and parsed.port is None
                and parsed.username is None
        )
    except ValueError:
        return False


def extract_trivy_guide_urls(errors: str) -> list[str]:
    """Extract unique Trivy guide URLs in their order of appearance.

    Args:
        errors (str): Trivy output containing ``See`` guide references.

    Returns:
        list[str]: Unique Trivy guide URLs in occurrence order.
    """
    urls: list[str] = []
    seen: set[str] = set()

    for match in TRIVY_GUIDE_URL_PATTERN.finditer(errors):
        url = match.group(1)
        if url not in seen:
            seen.add(url)
            urls.append(url)

    return urls


def extract_checkov_guide_urls(errors: str) -> list[str]:
    """Extract unique, validated Checkov guide URLs in occurrence order.

    Args:
        errors (str): Checkov output containing ``Guide:`` references.

    Returns:
        list[str]: Unique HTTPS URLs on the configured Checkov guide host.
    """
    urls: list[str] = []
    seen: set[str] = set()

    for match in CHECKOV_GUIDE_URL_PATTERN.finditer(errors):
        url = match.group(1)
        if is_checkov_guide_url(url) and url not in seen:
            seen.add(url)
            urls.append(url)

    return urls


def extract_tfsec_guide_urls(errors: str) -> list[str]:
    """Extract unique AquaSecurity TFSec guide URLs in occurrence order.

    Args:
        errors (str): TFSec output containing guide URLs.

    Returns:
        list[str]: Unique TFSec guide URLs in occurrence order.
    """
    urls: list[str] = []
    seen: set[str] = set()

    for match in TFSEC_GUIDE_URL_PATTERN.finditer(errors):
        url = match.group(0)
        if url not in seen:
            seen.add(url)
            urls.append(url)

    return urls


def extract_tfsec_guide_url(errors: str) -> str | None:
    """Return the first AquaSecurity TFSec guide URL in the output.

    Args:
        errors (str): TFSec output containing guide URLs.

    Returns:
        str | None: The first referenced guide URL, or None when no URL is
            present.
    """
    return next(iter(extract_tfsec_guide_urls(errors)), None)


def is_tflint_guide_url(url: str) -> bool:
    """Return whether a URL is an official TFLint ruleset Markdown URL.

    Args:
        url (str): URL to validate.

    Returns:
        bool: True for an HTTPS URL addressing a Markdown rule in the official
            TFLint Terraform ruleset repository; otherwise False.
    """
    try:
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        return (
                parsed.scheme == 'https'
                and parsed.hostname == TFLINT_GUIDE_HOST
                and parsed.port is None
                and parsed.username is None
                and not parsed.query
                and not parsed.fragment
                and len(path_parts) == 7
                and '/'.join(path_parts[:2]) == TFLINT_GUIDE_REPOSITORY
                and path_parts[2] == 'blob'
                and path_parts[4:6] == ['docs', 'rules']
                and path_parts[6].endswith('.md')
        )
    except ValueError:
        return False


def extract_tflint_guide_urls(errors: str) -> list[str]:
    """Extract unique official TFLint guide URLs in occurrence order.

    Args:
        errors (str): TFLint output containing ``Reference:`` URLs.

    Returns:
        list[str]: Unique validated TFLint rule URLs in occurrence order.
    """
    urls: list[str] = []
    seen: set[str] = set()

    for match in TFLINT_GUIDE_URL_PATTERN.finditer(errors):
        url = match.group(0)
        if is_tflint_guide_url(url) and url not in seen:
            seen.add(url)
            urls.append(url)

    return urls


def _join_unique(texts: Iterable[str]) -> str:
    """Join non-empty texts with newlines while preserving first occurrence order.

    Args:
        texts (Iterable[str]): Text values to filter and join.

    Returns:
        str: Joined text with duplicate and empty values removed.
    """
    return '\n'.join(dict.fromkeys(text for text in texts if text))


def _text_blocks(node: Tag) -> list[str]:
    """Return outermost text blocks under a BeautifulSoup node.

    A block and its descendants are never returned together, and ``pre`` nodes
    are skipped while traversing child elements.

    Args:
        node (Tag): BeautifulSoup node to inspect.

    Returns:
        list[str]: Visible text from the outermost supported text blocks.
    """
    if node.name in TEXT_TAGS:
        return [node.get_text(' ', strip=True)]
    texts: list[str] = []
    for child in node.find_all(recursive=False):
        if child.name != 'pre':
            texts.extend(_text_blocks(child))
    return texts


def _text_after(heading: Tag) -> str:
    """Return readable text that follows a heading in document order, up to the next h2/h3.

    Only the outermost text blocks are taken, so a block is never repeated through its
    descendants, and code inside ``pre`` and page chrome (footer, nav, aside) are skipped.

    Args:
        heading (Tag): Heading whose following content should be collected.

    Returns:
        str: Unique readable text until the next supported heading.
    """
    texts: list[str] = []
    for tag in heading.find_all_next():
        if tag.name in HEADING_TAGS:
            break
        if tag.name in TEXT_TAGS and not tag.find_parent([*TEXT_TAGS, 'pre', *PAGE_CHROME_TAGS]):
            texts.append(tag.get_text(' ', strip=True))
    return _join_unique(texts)


def _find_heading(soup: BeautifulSoup, title: str) -> Tag | None:
    """Find a section heading by its visible title.

    Args:
        soup (BeautifulSoup): Parsed guide document.
        title (str): Heading text to find, compared case-insensitively.

    Returns:
        Tag | None: Matching h2 or h3 element, or None when absent.
    """
    normalized_title = title.casefold()
    return soup.find(
        lambda element: element.name in HEADING_TAGS
                        and element.get_text(' ', strip=True).casefold() == normalized_title
    )


def _section_elements(heading: Tag) -> Iterable[Tag]:
    """Yield elements in a section without crossing its boundary.

    Args:
        heading (Tag): Section heading that defines the traversal start.

    Yields:
        Tag: Elements following the heading until the next heading or parent
            container boundary.
    """
    for element in heading.find_all_next():
        if element.name in HEADING_TAGS:
            break
        if heading.parent not in element.parents:
            break
        yield element


def _section_text(soup: BeautifulSoup, title: str) -> str:
    """Return readable text under a named h2 or h3 heading.

    Args:
        soup (BeautifulSoup): Parsed guide document.
        title (str): Heading text to locate.

    Returns:
        str: Section text up to the next supported heading, or an empty string
            when the heading is absent.
    """
    heading = _find_heading(soup, title)
    return _text_after(heading) if heading else ''


def _section_text_in_container(soup: BeautifulSoup, title: str) -> str:
    """Return section text while staying inside its content container.

    Args:
        soup (BeautifulSoup): Parsed guide document.
        title (str): Heading text to locate.

    Returns:
        str: Unique readable text from the section, or an empty string when
            the heading is absent.
    """
    heading = _find_heading(soup, title)
    if not heading:
        return ''

    container = heading.parent
    texts: list[str] = []
    for tag in _section_elements(heading):
        if container not in tag.parents:
            break
        if tag.name in TEXT_TAGS and not tag.find_parent([*TEXT_TAGS, 'pre', *PAGE_CHROME_TAGS]):
            texts.append(tag.get_text(' ', strip=True))

    return _join_unique(texts)


def _terraform_text_line(tag: Tag) -> str:
    """Return one visible Terraform line from a paragraph or list item.

    Args:
        tag (Tag): Paragraph or list item to read.

    Returns:
        str: Visible text for a supported tag, or an empty string otherwise.
    """
    if tag.name == 'li' or (tag.name == 'p' and not tag.find_parent('li')):
        return tag.get_text(' ', strip=True)
    return ''


def _section_terraform_examples(soup: BeautifulSoup, title: str) -> list[str]:
    """Extract Terraform examples under a named section heading.

    Args:
        soup (BeautifulSoup): Parsed guide document.
        title (str): Heading text whose examples should be collected.

    Returns:
        list[str]: Terraform code blocks and reconstructed examples from the
            selected section.
    """
    heading = _find_heading(soup, title)
    if not heading:
        return []

    examples: list[str] = []
    terraform_lines: list[str] = []

    for tag in _section_elements(heading):
        if tag.name == 'pre':
            code = _extract_code_block(tag)
            if TERRAFORM_CODE_PATTERN.search(code):
                examples.append(code)
        elif tag.name in ('li', 'p'):
            text = _terraform_text_line(tag)
            if text:
                terraform_lines.append(text)

    return examples + _terraform_examples_from_lines(terraform_lines)


def _terraform_examples_from_lines(lines: list[str]) -> list[str]:
    """Group rendered Checkov list-item lines into Terraform examples.

    Args:
        lines (list[str]): Visible lines extracted from a rendered guide.

    Returns:
        list[str]: Reconstructed Terraform examples grouped by brace balance.
    """
    examples: list[str] = []
    current_lines: list[str] = []
    brace_balance = 0

    for line in lines:
        if not current_lines:
            if TERRAFORM_CODE_PATTERN.search(line):
                current_lines = [line]
                brace_balance = line.count('{') - line.count('}')
                if brace_balance <= 0 and '{' in line:
                    examples.append('\n'.join(current_lines))
                    current_lines = []
            continue

        current_lines.append(line)
        brace_balance += line.count('{') - line.count('}')
        if brace_balance <= 0 and '{' in '\n'.join(current_lines):
            examples.append('\n'.join(current_lines))
            current_lines = []

    if current_lines:
        examples.append('\n'.join(current_lines))

    return examples


def _extract_code_block(pre: Tag) -> str:
    """Extract a code block while preserving source whitespace.

    Args:
        pre (Tag): BeautifulSoup ``pre`` element containing the code.

    Returns:
        str: Code text with ``br`` elements converted to line breaks. The
            original HTML tree is not modified.
    """
    pre_copy = copy(pre)
    for line_break in pre_copy.find_all('br'):
        line_break.replace_with('\n')

    return pre_copy.get_text('', strip=False).strip()


def _terraform_line_segments(line: str) -> list[str]:
    """Split a Terraform line around structural braces.

    Args:
        line (str): Terraform source line to split.

    Returns:
        list[str]: Text and brace segments, preserving braces inside quoted
            strings as part of the surrounding text.
    """
    segments: list[str] = []
    current: list[str] = []
    in_string = False
    escaped = False

    for character in line.strip():
        if character == '"' and not escaped:
            in_string = not in_string

        if character in '{}' and not in_string:
            text = ''.join(current).strip()
            if text:
                segments.append(text)
            segments.append(character)
            current = []
        else:
            current.append(character)

        escaped = character == '\\' and in_string and not escaped
        if character != '\\':
            escaped = False

    text = ''.join(current).strip()
    if text:
        segments.append(text)
    return segments


def _format_terraform_code(code: str) -> str:
    """Format Terraform code whose source page discarded indentation or line breaks.

    Args:
        code (str): Terraform source text to format.

    Returns:
        str: Terraform text reconstructed with indentation based on braces.
    """
    formatted: list[str] = []
    indentation = 0
    for source_line in code.splitlines():
        if not source_line.strip():
            continue

        for segment in _terraform_line_segments(source_line):
            if segment == '{':
                if formatted:
                    formatted[-1] += ' {'
                else:
                    formatted.append('  ' * indentation + '{')
                indentation += 1
            elif segment == '}':
                indentation = max(0, indentation - 1)
                formatted.append('  ' * indentation + '}')
            else:
                formatted.append('  ' * indentation + segment)

    return '\n'.join(formatted)


def _remove_checkov_metadata_labels(section: str) -> str:
    """Keep Checkov metadata values while removing noisy labels.

    Args:
        section (str): Checkov section text containing metadata labels.

    Returns:
        str: Section text with ``Resource:`` and ``Arguments:`` labels and
            source suffixes removed.
    """
    lines: list[str] = []
    for line in section.splitlines():
        line = CHECKOV_METADATA_LABEL_PATTERN.sub('', line)
        source_suffix_start = line.casefold().rfind(' [source,')
        if source_suffix_start >= 0 and line.rstrip().endswith(']'):
            line = line[:source_suffix_start].rstrip()
        if line:
            lines.append(line)
    return '\n'.join(lines)


def _terraform_examples(scope: Tag | BeautifulSoup) -> list[tuple[str, str]]:
    """Return each Terraform block and its preceding heading under ``scope``.

    The heading must sit inside scope; a heading outside it may belong to unrelated
    content, so the label is left empty rather than misleading.

    Args:
        scope (Tag | BeautifulSoup): Parsed HTML node whose descendants should
            be searched.

    Returns:
        list[tuple[str, str]]: Pairs containing the nearest heading label and
            Terraform code for each matching block.
    """
    examples: list[tuple[str, str]] = []
    for pre in scope.find_all('pre'):
        code = _extract_code_block(pre)
        if TERRAFORM_CODE_PATTERN.search(code):
            heading = pre.find_previous(HEADING_TAGS)
            label = ''
            if heading is not None and scope in heading.parents:
                label = heading.get_text(' ', strip=True)
            examples.append((label, code))
    return examples


def _terraform_tab(soup: BeautifulSoup) -> Tag | None:
    """Return the Terraform tab from a tabbed Trivy remediation.

    Args:
        soup (BeautifulSoup): Parsed Trivy guide document.

    Returns:
        Tag | None: Terraform tab content when a valid tab mapping exists, or
            None when the page has no Terraform tab.
    """
    for panel in soup.select('div.tab-panel'):
        labels = [button.get_text(strip=True).casefold() for button in panel.select('.tab-nav button')]
        items = panel.select('.tab-content > .tab-item')
        if 'terraform' in labels and len(labels) == len(items):
            return items[labels.index('terraform')]
    return None


def _guide_header(url: str, soup: BeautifulSoup) -> list[str]:
    """Start a formatted guide with its URL and page title.

    Args:
        url (str): Source URL for the guide.
        soup (BeautifulSoup): Parsed guide document.

    Returns:
        list[str]: Guide parts containing the source URL and, when available,
            the page's h1 text.
    """
    parts = [url]
    title = soup.find('h1')
    if title:
        parts.append(title.get_text(' ', strip=True))
    return parts


def parse_trivy_guide(url: str, html: str) -> str:
    """Extract Terraform-oriented remediation guidance from a Trivy guide page.

    Args:
        url (str): Source URL for the guide.
        html (str): Retrieved Trivy guide HTML.

    Returns:
        str: Compact guide text containing the finding description, remediation
            guidance, and Terraform examples, or an empty string when no useful
            remediation content is present.
    """
    soup = BeautifulSoup(html, HTML_PARSER)

    for heading in soup.find_all('h4', string=re.compile(r"^\s*Remediation Links\s*$", re.IGNORECASE)):
        if links := heading.find_next_sibling('ul'):
            links.decompose()
        heading.decompose()

    # Newer pages split remediation into CloudFormation / Console / Terraform tabs.
    tab = _terraform_tab(soup)
    if tab:
        action_text = _join_unique(_text_blocks(tab))
    else:
        action_text = _section_text(soup, 'Recommended Actions')
    examples = _terraform_examples(tab or soup)

    # The rule's summary is the page's first h3, followed by its description.
    summary = soup.select_one('.vulnerability_content > h3')
    description = ''
    if summary:
        description = _join_unique([summary.get_text(' ', strip=True), _text_after(summary)])

    if not action_text and not examples:
        return ''

    guide_parts = _guide_header(url, soup)
    if description:
        guide_parts.append(description)
    if action_text:
        guide_parts.append(action_text)
    if examples:
        code = '\n'.join(code for _, code in examples)
        guide_parts.append(f"```hcl\n{code}\n```")

    return '\n'.join(guide_parts)


def parse_tfsec_guide(url: str, html: str) -> str:
    """Extract remediation guidance and Terraform examples from a TFSec page.

    Args:
        url (str): Source URL for the guide.
        html (str): Retrieved TFSec guide HTML.

    Returns:
        str: Compact guide text containing selected remediation sections and
            labeled Terraform examples, or an empty string when no useful
            content is present.
    """
    soup = BeautifulSoup(html, HTML_PARSER)
    sections = {
        title: _section_text(soup, title)
        for title in ('Explanation', 'Possible Impact', SUGGESTED_RESOLUTION_TITLE)
    }
    examples = _terraform_examples(soup)

    if not any(sections.values()) and not examples:
        return ''

    guide_parts = _guide_header(url, soup)
    guide_parts.extend(text for text in sections.values() if text)
    # Keep the page's own "Insecure Example" / "Secure Example" labels so the
    # model can tell the broken snippet from the fix.
    guide_parts.extend(
        f"{label}\n```hcl\n{code}\n```" if label else f"```hcl\n{code}\n```"
        for label, code in examples
    )

    return '\n'.join(guide_parts)


def parse_checkov_guide(url: str, html: str) -> str:
    """Extract Checkov rule context and Terraform remediation guidance.

    Args:
        url (str): Source URL for the guide.
        html (str): Retrieved Checkov guide HTML.

    Returns:
        str: Compact guide text containing relevant impact, description, fix
            guidance, and Terraform examples, or an empty string when no useful
            content is present.
    """
    soup = BeautifulSoup(html, HTML_PARSER)
    guide_parts = _guide_header(url, soup)

    sections: list[str] = []
    for title in ('Impact', 'Description', 'How to Fix', 'Remediation', SUGGESTED_RESOLUTION_TITLE):
        section = _section_text_in_container(soup, title) or _section_text(soup, title)
        if section and section not in sections:
            sections.append(section)

    examples: list[str] = []
    for title in ('How to Fix', 'Remediation', SUGGESTED_RESOLUTION_TITLE):
        examples.extend(_section_terraform_examples(soup, title))

    code_lines = {
        line.strip()
        for example in examples
        for line in example.splitlines()
        if line.strip()
    }
    if code_lines:
        sections = [
            '\n'.join(line for line in section.splitlines() if line.strip() not in code_lines)
            for section in sections
        ]
        sections = [section for section in sections if section]

    cleaned_sections: list[str] = []
    for section in sections:
        cleaned_section = _remove_checkov_metadata_labels(section)
        if cleaned_section:
            cleaned_sections.append(cleaned_section)
    sections = cleaned_sections

    if not sections and not examples:
        return ''

    guide_parts.extend(sections)
    if examples:
        code = '\n'.join(dict.fromkeys(examples))
        guide_parts.append(f"```hcl\n{_format_terraform_code(code)}\n```")

    return '\n'.join(guide_parts)


def _parse_markdown_sections(markdown: str) -> tuple[str, list[str], dict[str, list[str]]]:
    """Split a Markdown document into its title, header, and named sections.

    Args:
        markdown (str): Markdown document to parse.

    Returns:
        tuple[str, list[str], dict[str, list[str]]]: The first h1 title, lines
            before the first section, and section contents keyed by normalized
            heading title.
    """
    title = ''
    header: list[str] = []
    sections: dict[str, list[str]] = {}
    current_lines = header

    for line in markdown.splitlines():
        stripped_line = line.strip()
        heading_level = len(stripped_line) - len(stripped_line.lstrip('#'))
        heading_title = ''
        if (
                1 <= heading_level <= 6
                and len(stripped_line) > heading_level
                and stripped_line[heading_level].isspace()
        ):
            heading_title = stripped_line[heading_level:].strip().rstrip('#').rstrip()

        if heading_title:
            if heading_level == 1 and not title:
                title = heading_title
                current_lines = header
            elif heading_level >= 2:
                current_lines = sections.setdefault(heading_title.casefold(), [])
            continue

        current_lines.append(line)

    return title, header, sections


def _clean_markdown_text(lines: Iterable[str]) -> str:
    """Return readable prose from Markdown lines.

    Fenced code blocks, separators, empty lines, and Markdown link destinations
    are removed while preserving the visible prose.

    Args:
        lines (Iterable[str]): Markdown lines to clean.

    Returns:
        str: Deduplicated readable prose joined by newlines.
    """
    cleaned: list[str] = []
    in_code_block = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block or stripped in {'', '* * *', '---'}:
            continue

        line = re.sub(r'^\s*>\s?', '', line).strip()
        line = re.sub(r'\[([^]]+)]\([^)]*\)', r'\1', line)
        if line:
            cleaned.append(line)

    return '\n'.join(dict.fromkeys(cleaned))


def _markdown_fence_language(line: str) -> str | None:
    """Return a fenced block's language.

    Args:
        line (str): Markdown line to inspect.

    Returns:
        str | None: Fence language, including an empty string for an unlabeled
            fence, or None when the line is not a valid fence.
    """
    stripped_line = line.strip()
    if not stripped_line.startswith('```'):
        return None

    language = stripped_line[3:].strip()
    valid_characters = all(
        character.isascii() and (character.isalnum() or character in '_-')
        for character in language
    )
    return language if valid_characters else None


def _append_markdown_terraform_example(
        examples: list[str],
        language: str,
        current_lines: list[str],
) -> None:
    """Append a completed Terraform/HCL block when its content is useful.

    Args:
        examples (list[str]): Collection receiving accepted examples.
        language (str): Fence language for the completed block.
        current_lines (list[str]): Source lines from the completed block.
    """
    if language.casefold() in {'hcl', 'tf', 'terraform'} and current_lines:
        examples.append('\n'.join(current_lines).strip())


def _markdown_section_terraform_examples(section_lines: list[str]) -> list[str]:
    """Extract Terraform/HCL fenced code blocks from one Markdown section.

    Args:
        section_lines (list[str]): Lines belonging to one Markdown section.

    Returns:
        list[str]: Terraform/HCL code blocks from the section.
    """
    examples: list[str] = []
    in_code_block = False
    language = ''
    current_lines: list[str] = []

    for line in section_lines:
        fence_language = _markdown_fence_language(line)
        if fence_language is not None:
            if in_code_block:
                _append_markdown_terraform_example(examples, language, current_lines)
                in_code_block = False
                language = ''
                current_lines = []
            else:
                in_code_block = True
                language = fence_language
            continue

        if in_code_block:
            current_lines.append(line)

    return examples


def _markdown_terraform_examples(sections: Iterable[list[str]]) -> list[str]:
    """Extract unique Terraform/HCL blocks from selected Markdown sections.

    Args:
        sections (Iterable[list[str]]): Markdown section line collections to
            inspect.

    Returns:
        list[str]: Unique Terraform/HCL examples in occurrence order.
    """
    examples = [
        example
        for section_lines in sections
        for example in _markdown_section_terraform_examples(section_lines)
        if example
    ]
    return list(dict.fromkeys(examples))


def parse_tflint_guide(url: str, markdown: str) -> str:
    """Extract focused Terraform remediation guidance from a TFLint rule.

    Args:
        url (str): Original GitHub source URL for the rule document.
        markdown (str): Retrieved TFLint rule Markdown.

    Returns:
        str: Compact guide text containing the rule summary, Why and How To Fix
            prose, and Terraform examples, or an empty string when no useful
            content is present.
    """
    title, header, sections = _parse_markdown_sections(markdown)
    summary = _clean_markdown_text(header)
    why = _clean_markdown_text(sections.get('why', []))
    how_to_fix = _clean_markdown_text(sections.get('how to fix', []))
    examples = _markdown_terraform_examples(
        sections.get(section_name, [])
        for section_name in ('example', 'examples', 'how to fix')
    )

    if not any((title, summary, why, how_to_fix, examples)):
        return ''

    guide_parts = [url]
    if title:
        guide_parts.append(title)
    guide_parts.extend(text for text in (summary, why, how_to_fix) if text)
    if examples:
        code = '\n\n'.join(examples)
        guide_parts.append(f"```hcl\n{code}\n```")

    return '\n'.join(guide_parts)


def _request_page(url: str) -> requests.Response:
    """Fetch a guide page with the configured timeout.

    Args:
        url (str): Page URL to request.

    Returns:
        requests.Response: Response returned by ``requests``. The response
            status is left for the caller to validate.

    Raises:
        requests.RequestException: If the request cannot be completed.
    """
    return requests.get(url, timeout=config.default_timeout)


def _get_refresh_target(url: str, html: str) -> str | None:
    """Return a page's HTML refresh or canonical target, when present.

    Args:
        url (str): URL of the fetched page, used to resolve relative targets.
        html (str): Retrieved page HTML.

    Returns:
        str | None: Absolute refresh or canonical target URL, or None when the
            page does not declare one.
    """
    soup = BeautifulSoup(html, HTML_PARSER)

    refresh_tag = soup.find(
        'meta',
        attrs={'http-equiv': lambda value: value and value.casefold() == 'refresh'},
    )
    if refresh_tag:
        content = str(refresh_tag.get('content') or '')
        match = re.search(r"url\s*=\s*[\"']?([^\"'\s]+)", content, flags=re.IGNORECASE)
        if match:
            return urljoin(url, match.group(1))

    for link in soup.find_all('link'):
        raw_rel = link.get('rel')
        if isinstance(raw_rel, str):
            rel = {raw_rel.casefold()}
        elif raw_rel:
            rel = {str(value).casefold() for value in raw_rel}
        else:
            rel = set()

        href = link.get('href')
        if 'canonical' in rel and href:
            return urljoin(url, str(href))

    return None


def _fetch_trivy_guide(url: str) -> str:
    """Fetch a Trivy guide, following HTML refresh/canonical stubs that stay on the Trivy host.

    At most TRIVY_MAX_REFRESH_HOPS hops are followed. A refused hop (other host or scheme,
    or a loop) parses the page already fetched instead of dropping the guide.

    Args:
        url (str): Initial Trivy guide URL.

    Returns:
        str: Parsed Trivy guide text, or an empty string when the refresh limit
            is exceeded.

    Raises:
        requests.RequestException: If a guide request fails.
        ValueError: If a refresh URL cannot be parsed.
        ParserRejectedMarkup: If BeautifulSoup rejects the retrieved markup.
    """
    current_url = url
    seen = {url.rstrip('/')}

    for _ in range(TRIVY_MAX_REFRESH_HOPS + 1):
        response = _request_page(current_url)
        response.raise_for_status()

        refresh_target = _get_refresh_target(current_url, response.text)
        if not refresh_target or refresh_target.rstrip('/') == current_url.rstrip('/'):
            return parse_trivy_guide(current_url, response.text)

        if not is_trivy_guide_url(refresh_target):
            logger.warning(f"Refusing to follow Trivy guide refresh to {refresh_target}")
            return parse_trivy_guide(current_url, response.text)

        if refresh_target.rstrip('/') in seen:
            logger.warning(f"Trivy guide refresh loop from {current_url} to {refresh_target}")
            return parse_trivy_guide(current_url, response.text)

        logger.debug(f"Following Trivy guide refresh from {current_url} to {refresh_target}")
        seen.add(refresh_target.rstrip('/'))
        current_url = refresh_target

    logger.warning(f"Too many refresh redirects while retrieving Trivy guide {url}")
    return ''


def _tfsec_latest_url(url: str) -> str:
    """Replace a version segment in a TFSec guide URL with ``latest``.

    Args:
        url (str): Versioned TFSec guide URL.

    Returns:
        str: URL with the first TFSec version segment replaced by ``latest``.
    """
    return re.sub(r"(/tfsec/)[^/]+(/)", r"\1latest\2", url, count=1)


def _fetch_tfsec_guide(url: str) -> str:
    """Fetch a TFSec guide, retrying with ``latest`` after a versioned 404.

    Args:
        url (str): Initial versioned TFSec guide URL.

    Returns:
        str: Parsed TFSec guide text.

    Raises:
        requests.RequestException: If the initial or retry request fails.
        ValueError: If a derived URL cannot be parsed.
        ParserRejectedMarkup: If BeautifulSoup rejects the retrieved markup.
    """
    response = _request_page(url)
    if response.status_code == 404:
        latest_url = _tfsec_latest_url(url)
        if latest_url != url:
            logger.debug(f"Retrying TFSec guide with latest version: {latest_url}")
            response = _request_page(latest_url)
            url = latest_url

    response.raise_for_status()
    return parse_tfsec_guide(url, response.text)


def _fetch_checkov_guide(url: str) -> str:
    """Fetch and parse a Checkov guide while preserving its source URL.

    Args:
        url (str): Checkov guide URL to fetch.

    Returns:
        str: Parsed Checkov guide text using the original source URL.

    Raises:
        requests.RequestException: If the request fails or returns an error
            status.
        ParserRejectedMarkup: If BeautifulSoup rejects the retrieved markup.
    """
    response = _request_page(url)
    response.raise_for_status()
    return parse_checkov_guide(url, response.text)


def _tflint_raw_url(url: str) -> str:
    """Convert an approved TFLint GitHub blob URL to a raw Markdown URL.

    Args:
        url (str): Validated GitHub blob URL for a TFLint rule document.

    Returns:
        str: Corresponding ``raw.githubusercontent.com`` URL.
    """
    path_parts = urlparse(url).path.strip('/').split('/')
    repository = '/'.join(path_parts[:2])
    ref = path_parts[3]
    document_path = '/'.join(path_parts[4:])
    return f'https://raw.githubusercontent.com/{repository}/{ref}/{document_path}'


def _fetch_tflint_guide(url: str) -> str:
    """Fetch and parse a TFLint rule while preserving its GitHub source URL.

    Args:
        url (str): Validated GitHub blob URL for the TFLint rule.

    Returns:
        str: Parsed TFLint guide text using the original GitHub URL.

    Raises:
        requests.RequestException: If the raw Markdown request fails or returns
            an error status.
    """
    response = _request_page(_tflint_raw_url(url))
    response.raise_for_status()
    return parse_tflint_guide(url, response.text)


def extract_trivy_guides(errors: str) -> str:
    """Fetch and format Terraform remediation guides referenced by Trivy errors.

    Failed guide requests are logged and skipped so one unavailable page does
    not prevent other guides from reaching the prompt.

    Args:
        errors (str): Trivy output containing guide references.

    Returns:
        str: Guides joined with ``GUIDE_SEPARATOR``.
    """
    guides: list[str] = []

    for url in extract_trivy_guide_urls(errors):
        try:
            guide = _fetch_trivy_guide(url)
        except (requests.RequestException, ValueError, ParserRejectedMarkup) as error:
            logger.warning(f"Unable to retrieve Trivy guide {url}: {error}")
            continue

        if guide:
            guides.append(guide)

    return GUIDE_SEPARATOR.join(guides)


def extract_tfsec_guide(errors: str) -> str:
    """Fetch and format Terraform remediation guides referenced by TFSec.

    Failed guide requests are logged and skipped so one unavailable page does
    not prevent other guides from reaching the prompt.

    Args:
        errors (str): TFSec output containing guide references.

    Returns:
        str: Guides joined with ``GUIDE_SEPARATOR``.
    """
    guides: list[str] = []

    for url in extract_tfsec_guide_urls(errors):
        try:
            guide = _fetch_tfsec_guide(url)
        except (requests.RequestException, ValueError, ParserRejectedMarkup) as error:
            logger.warning(f"Unable to retrieve TFSec guide {url}: {error}")
            continue

        if guide:
            guides.append(guide)

    return GUIDE_SEPARATOR.join(guides)


def extract_checkov_guides(errors: str) -> str:
    """Fetch and format remediation guides referenced by Checkov errors.

    Failed guide requests are logged and skipped so one unavailable page does
    not prevent other guides from reaching the prompt.

    Args:
        errors (str): Checkov output containing guide references.

    Returns:
        str: Guides joined with ``GUIDE_SEPARATOR``.
    """
    guides: list[str] = []

    for url in extract_checkov_guide_urls(errors):
        try:
            guide = _fetch_checkov_guide(url)
        except (requests.RequestException, ValueError, ParserRejectedMarkup) as error:
            logger.warning(f"Unable to retrieve Checkov guide {url}: {error}")
            continue

        if guide:
            guides.append(guide)

    return GUIDE_SEPARATOR.join(guides)


def extract_tflint_guides(errors: str) -> str:
    """Fetch and format Terraform remediation guides referenced by TFLint errors.

    Failed guide requests are logged and skipped so one unavailable page does
    not prevent other guides from reaching the prompt.

    Args:
        errors (str): TFLint output containing guide references.

    Returns:
        str: Guides joined with ``GUIDE_SEPARATOR``.
    """
    guides: list[str] = []

    for url in extract_tflint_guide_urls(errors):
        try:
            guide = _fetch_tflint_guide(url)
        except (requests.RequestException, ValueError) as error:
            logger.warning(f"Unable to retrieve TFLint guide {url}: {error}")
            continue

        if guide:
            guides.append(guide)

    return GUIDE_SEPARATOR.join(guides)
