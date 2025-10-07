from splt_nodes import block_to_blocktype, BlockType


def test_heading_block():
    assert block_to_blocktype("# Heading") == BlockType.HEADING


def test_heading_with_leading_spaces():
    assert block_to_blocktype("   # Title") == BlockType.HEADING


def test_fenced_code_block_multiline():
    block = "```\nprint('hello')\n```"
    assert block_to_blocktype(block) == BlockType.CODE


def test_unclosed_fenced_block_is_not_code():
    block = "```\nprint('oops')"
    assert block_to_blocktype(block) == BlockType.PARAGRAPH


def test_quote_block():
    assert block_to_blocktype("> this is a quote") == BlockType.QUOTE


def test_unordered_list_dash():
    assert block_to_blocktype("- item") == BlockType.UNORDERED_LIST


def test_unordered_list_star_plus():
    assert block_to_blocktype("* item") == BlockType.UNORDERED_LIST
    assert block_to_blocktype("+ item") == BlockType.UNORDERED_LIST


def test_ordered_list():
    assert block_to_blocktype("1. first") == BlockType.ORDERED_LIST
    assert block_to_blocktype("  23. numbered") == BlockType.ORDERED_LIST


def test_paragraph_default():
    assert block_to_blocktype("This is a paragraph.") == BlockType.PARAGRAPH