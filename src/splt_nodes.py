from textnode import TextNode, TextType
from converters import extract_markdown_images, extract_markdown_links, text_node_to_html_node
from htmlnode import ParentNode, LeafNode
from enum import Enum


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    """Split any plain/text TextNode in old_nodes by the given delimiter.

    Arguments:
    - old_nodes: iterable of TextNode
    - delimiter: string delimiter to split on (e.g. '`')
    - text_type: TextType to apply to the delimited segments

    Returns a new list of TextNode where segments between delimiters are
    converted to the supplied text_type and other text remains as the
    original TextNode type.
    """
    new_nodes = []

    for node in old_nodes:
        # Only attempt splitting on TextNode instances
        if not isinstance(node, TextNode):
            new_nodes.append(node)
            continue

        # Only split nodes that are plain text (i.e., their type is the 'text' value)
        # We check by comparing the enum member's value so this works whether
        # TextType members or strings were used.
        if getattr(node.text_type, 'value', node.text_type) != 'text':
            new_nodes.append(node)
            continue

        # Fast path: if delimiter not in text or delimiter is empty, keep node as-is
        if delimiter == '' or delimiter not in node.text:
            new_nodes.append(node)
            continue

        # If delimiters are not properly paired (odd count), this is invalid
        count = node.text.count(delimiter)
        if count % 2 != 0:
            raise ValueError(f"Unmatched delimiter {delimiter!r} in text: {node.text!r}")

        parts = node.text.split(delimiter)
        built = []
        # parts alternate: outside (index even), inside (index odd)
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # outside delimiter -> plain text
                if part:
                    built.append(TextNode(part, node.text_type, url=node.url))
            else:
                # inside delimiter -> use provided text_type
                built.append(TextNode(part, text_type, url=node.url))

        # extend the main list with the nodes produced for this original node
        new_nodes.extend(built)

    return new_nodes


import re


def split_nodes_image(old_nodes):
    """Split plain text nodes on markdown image syntax and return new nodes.

    Image syntax matched: ![alt](url)
    """
    new_nodes = []

    for node in old_nodes:
        if not isinstance(node, TextNode):
            new_nodes.append(node)
            continue

        if getattr(node.text_type, 'value', node.text_type) != 'text':
            new_nodes.append(node)
            continue

        text = node.text
        matches = extract_markdown_images(text)
        if not matches:
            # No images -> return the original node unchanged
            new_nodes.append(node)
            continue

        remaining = text
        for alt, url in matches:
            snippet = f"![{alt}]({url})"
            parts = remaining.split(snippet, 1)
            # parts[0] is text before the image
            if parts[0]:
                new_nodes.append(TextNode(parts[0], node.text_type, url=node.url))
            # add the image node (alt text and src in url)
            new_nodes.append(TextNode(alt, TextType.IMAGE, url))
            # remaining becomes parts[1]
            remaining = parts[1] if len(parts) > 1 else ''

        # trailing text after last image
        if remaining:
            new_nodes.append(TextNode(remaining, node.text_type, url=node.url))

    return new_nodes


def split_nodes_link(old_nodes):
    """Split plain text nodes on markdown link syntax and return new nodes.

    Link syntax matched: [anchor](url) but not images (negative lookbehind).
    """
    new_nodes = []

    for node in old_nodes:
        if not isinstance(node, TextNode):
            new_nodes.append(node)
            continue

        if getattr(node.text_type, 'value', node.text_type) != 'text':
            new_nodes.append(node)
            continue

        text = node.text
        matches = extract_markdown_links(text)
        if not matches:
            new_nodes.append(node)
            continue

        remaining = text
        for anchor, url in matches:
            snippet = f"[{anchor}]({url})"
            parts = remaining.split(snippet, 1)
            if parts[0]:
                new_nodes.append(TextNode(parts[0], node.text_type, url=node.url))
            new_nodes.append(TextNode(anchor, TextType.LINK, url))
            remaining = parts[1] if len(parts) > 1 else ''

        if remaining:
            new_nodes.append(TextNode(remaining, node.text_type, url=node.url))

    return new_nodes


def text_to_textnodes(text: str):
    """Tokenize a raw markdown-ish string into a list of TextNode pieces.

    Uses the splitters in a fixed order to avoid splitting inside code blocks:
    1. code (`)
    2. bold (**)
    3. italic (_)
    4. images
    5. links
    """
    # start with a single plain text node
    nodes = [TextNode(text, TextType.PLAIN)]

    # protect code first so inner markup is not parsed
    nodes = split_nodes_delimiter(nodes, '`', TextType.CODE)
    # then bold and italic
    nodes = split_nodes_delimiter(nodes, '**', TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, '_', TextType.ITALIC)

    # now extract images and links
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)

    # filter out any empty-text nodes (defensive)
    result = [n for n in nodes if isinstance(n, TextNode) and n.text != '']
    return result

def markdown_to_blocks(markdown: str):
    # Return an empty list for None or empty input
    if markdown is None:
        return []

    # Trim leading/trailing whitespace so stray newlines at start/end are ignored
    text = markdown.strip()
    if not text:
        return []

    # Split on one or more blank lines (handles excessive newlines), then trim each block
    blocks = re.split(r'\n\s*\n+', text)
    return [b.strip() for b in blocks if b.strip() != '']


BlockType = Enum('BlockType', [
    ('PARAGRAPH', 'paragraph'),
    ('HEADING', 'heading'),
    ('CODE', 'code'),
    ('QUOTE', 'quote'),
    ('UNORDERED_LIST', 'unordered_list'),
    ('ORDERED_LIST', 'ordered_list')
])


def block_to_blocktype(block: str):
    """Determine the BlockType for a single markdown block string."""
    if block is None:
        return BlockType.PARAGRAPH

    s = block.strip()
    if not s:
        return BlockType.PARAGRAPH

    ls = s.lstrip()

    # Fenced code block must both start and end with ```
    if s.startswith("```") and s.endswith("```"):
        return BlockType.CODE

    # Heading (starts with # after optional leading space)
    if ls.startswith("#"):
        return BlockType.HEADING

    # Quote (starts with > after optional leading space)
    if ls.startswith(">"):
        return BlockType.QUOTE

    # Ordered list (e.g. "1. item" or "  23. item")
    if re.match(r"^\d+\.\s+", ls):
        return BlockType.ORDERED_LIST

    # Unordered list using -, * or +
    if re.match(r"^[-\*\+]\s+", ls):
        return BlockType.UNORDERED_LIST

    # Default to paragraph
    return BlockType.PARAGRAPH


def text_to_children(text: str):
    """Convert an inline markdown-ish text string to a list of HTMLNode children.

    Uses text_to_textnodes to get TextNode pieces, then converts each to an HTML
    LeafNode via text_node_to_html_node.
    """
    tnodes = text_to_textnodes(text)
    return [text_node_to_html_node(tn) for tn in tnodes]


def markdown_to_html_node(markdown: str):
    """Convert a full markdown document string into a single ParentNode (div).

    Each block becomes a child node (p, pre>code, ul/ol with li children, etc).
    """
    root_children = []

    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        btype = block_to_blocktype(block)

        if btype == BlockType.PARAGRAPH:
            node = ParentNode("p", text_to_children(block))

        elif btype == BlockType.HEADING:
            # simple single-level heading (h1)
            # strip leading '#' characters and surrounding space
            content = block.lstrip().lstrip('#').strip()
            node = ParentNode("h1", text_to_children(content))

        elif btype == BlockType.QUOTE:
            content = block.lstrip().lstrip('>').strip()
            node = ParentNode("blockquote", text_to_children(content))

        elif btype == BlockType.CODE:
            # Extract the inner code text without parsing inline markdown.
            m = re.match(r"^```(?:.*)?\n([\s\S]*?)\n?```$", block.strip())
            inner = ""
            if m:
                inner = m.group(1)
            else:
                # Fallback: try naive strip of fences
                inner = block.strip()
                if inner.startswith("```"):
                    inner = inner[3:]
                if inner.endswith("```"):
                    inner = inner[:-3]
                inner = inner.strip("\n")

            # Ensure a trailing newline inside <code> as in the example expectations
            if not inner.endswith("\n"):
                inner = inner + "\n"

            # Create a TextNode for the raw code and convert to a HTML leaf (raw text)
            code_textnode = TextNode(inner, TextType.TEXT)
            code_leaf = text_node_to_html_node(code_textnode)
            code_node = ParentNode("code", [code_leaf])
            node = ParentNode("pre", [code_node])

        elif btype == BlockType.UNORDERED_LIST:
            # split lines and create li children
            items = []
            for line in block.splitlines():
                # remove leading list marker (-, *, +) and whitespace
                m = re.match(r'^\s*[-\*\+]\s+(.*)$', line)
                if m:
                    item_text = m.group(1)
                else:
                    item_text = line
                items.append(ParentNode("li", text_to_children(item_text)))
            node = ParentNode("ul", items)

        elif btype == BlockType.ORDERED_LIST:
            items = []
            for line in block.splitlines():
                m = re.match(r'^\s*\d+\.\s+(.*)$', line)
                if m:
                    item_text = m.group(1)
                else:
                    item_text = line
                items.append(ParentNode("li", text_to_children(item_text)))
            node = ParentNode("ol", items)

        else:
            # Fallback to paragraph
            node = ParentNode("p", text_to_children(block))

        root_children.append(node)

    return ParentNode("div", root_children)