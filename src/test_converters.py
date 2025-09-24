import unittest

from converters import text_node_to_html_node
from textnode import TextNode, TextType


class TestConverters(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.PLAIN)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("bold", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "bold")

    def test_italic(self):
        node = TextNode("it", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "it")

    def test_code(self):
        node = TextNode("c", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "c")

    def test_link(self):
        node = TextNode("anchor", TextType.LINK, url="https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "anchor")
        self.assertEqual(html_node.props.get("href"), "https://example.com")

    def test_image(self):
        node = TextNode("alt text", TextType.IMAGE, url="/img.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props.get("src"), "/img.png")
        self.assertEqual(html_node.props.get("alt"), "alt text")

    def test_invalid_input_type(self):
        with self.assertRaises(TypeError):
            text_node_to_html_node("not a textnode")


if __name__ == "__main__":
    unittest.main()
