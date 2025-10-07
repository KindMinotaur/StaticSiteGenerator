from typing import Any

from textnode import TextNode, TextType
from htmlnode import LeafNode
import re


def text_node_to_html_node(text_node: Any) -> LeafNode:
    """Convert a TextNode to an HTML LeafNode according to TextType.

    Raises ValueError for unsupported input.
    """
    if not isinstance(text_node, TextNode):
        raise TypeError("text_node must be a TextNode")

    ttype = text_node.text_type

    if ttype == TextType.PLAIN:
        # raw text, no tag
        return LeafNode(None, text_node.text)

    if ttype == TextType.BOLD:
        return LeafNode("b", text_node.text)

    if ttype == TextType.ITALIC:
        return LeafNode("i", text_node.text)

    if ttype == TextType.CODE:
        return LeafNode("code", text_node.text)

    if ttype == TextType.LINK:
        # expect url in text_node.url
        return LeafNode("a", text_node.text, props={"href": text_node.url})

    if ttype == TextType.IMAGE:
        # image: use empty string for value, src and alt props
        return LeafNode("img", "", props={"src": text_node.url, "alt": text_node.text})

    raise ValueError(f"Unsupported TextType: {ttype}")


def extract_markdown_images(text: str):
    """Return list of (alt, url) tuples for markdown images in text.

    Matches patterns like: ![alt text](url)
    """
    # Matches images like: ![alt](url)
    # Use provided stricter pattern to avoid nested brackets/parentheses inside groups
    pattern = re.compile(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)")
    return [(m.group(1), m.group(2)) for m in pattern.finditer(text)]


def extract_markdown_links(text: str):
    """Return list of (anchor, url) tuples for markdown links in text.

    Matches patterns like: [anchor text](url)
    """
    # Matches links like: [anchor](url) but not images (negative lookbehind for '!')
    pattern = re.compile(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)")
    return [(m.group(1), m.group(2)) for m in pattern.finditer(text)]
