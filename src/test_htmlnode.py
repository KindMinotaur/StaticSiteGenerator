import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):

    def test_props_to_html_empty(self):
        node = HTMLNode(tag='div', value=None, props={})
        self.assertEqual(node.props_to_html(), '')

    def test_props_to_html_single(self):
        node = HTMLNode(tag='span', value='hello', props={'class': 'btn'})
        self.assertEqual(node.props_to_html(), 'class="btn"')

    def test_props_to_html_multiple(self):
        node = HTMLNode(tag='a', value='link', props={'id': 'main', 'href': '/home'})
        # dict insertion order is preserved in Python 3.7+, so this exact string is expected
        self.assertEqual(node.props_to_html(), 'id="main" href="/home"')


class TestLeafNode(unittest.TestCase):
    def test_raw_text_when_no_tag(self):
        node = LeafNode(None, "raw text")
        self.assertEqual(node.to_html(), "raw text")

    def test_render_with_tag(self):
        node = LeafNode("p", "This is a paragraph.")
        self.assertEqual(node.to_html(), "<p>This is a paragraph.</p>")

    def test_render_with_props(self):
        node = LeafNode("a", "link", props={"href": "/home"})
        self.assertEqual(node.to_html(), '<a href="/home">link</a>')

    def test_missing_value_raises(self):
        with self.assertRaises(ValueError):
            LeafNode("p", None).to_html()

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_parent_missing_tag_raises(self):
        child = LeafNode("span", "child")
        with self.assertRaises(ValueError):
            ParentNode(None, [child]).to_html()

    def test_parent_missing_children_raises(self):
        # Explicitly pass children=None to trigger the children missing error
        with self.assertRaises(ValueError):
            ParentNode("div", None).to_html()

    def test_mixed_children_raw_and_tagged(self):
        # Mix raw text leaf (tag=None) with tagged leaf
        children = [LeafNode(None, "normal "), LeafNode("b", "bold"), LeafNode(None, " text")]
        parent = ParentNode("p", children)
        self.assertEqual(parent.to_html(), "<p>normal <b>bold</b> text</p>")


if __name__ == "__main__":
    unittest.main()
