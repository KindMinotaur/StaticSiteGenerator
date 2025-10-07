from splt_nodes import markdown_to_blocks


def test_markdown_to_blocks_basic():
    md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
    blocks = markdown_to_blocks(md)
    assert blocks == [
        "This is **bolded** paragraph",
        "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
        "- This is a list\n- with items",
    ]


def test_markdown_to_blocks_excessive_newlines():
    md = "First paragraph\n\n\n\nSecond paragraph\n\n\nThird paragraph"
    blocks = markdown_to_blocks(md)
    assert blocks == ["First paragraph", "Second paragraph", "Third paragraph"]


def test_markdown_to_blocks_none_and_empty():
    assert markdown_to_blocks(None) == []
    assert markdown_to_blocks("") == []


def test_markdown_to_blocks_trailing_leading_whitespace():
    md = "\n\n  Hello world  \n\n"
    assert markdown_to_blocks(md) == ["Hello world"]


def test_markdown_to_blocks_preserve_single_newlines():
    md = "Line one\nLine two\n\nNext block"
    assert markdown_to_blocks(md) == ["Line one\nLine two", "Next block"]


def test_markdown_to_blocks_heading_and_list():
    md = "# Heading\n\n- item one\n- item two\n\nA final paragraph"
    assert markdown_to_blocks(md) == [
        "# Heading",
        "- item one\n- item two",
        "A final paragraph",
    ]