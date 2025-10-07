import unittest

from splt_nodes import split_nodes_image, split_nodes_link, text_to_textnodes
from textnode import TextNode, TextType


class TestSplitNodes(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.PLAIN),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.PLAIN),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_split_images_no_match(self):
        node = TextNode("no images here", TextType.PLAIN)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.PLAIN),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.PLAIN),
                TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
            ],
            new_nodes,
        )

    def test_split_links_no_match(self):
        node = TextNode("no links here", TextType.PLAIN)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_mixed_nodes_passthrough(self):
        # Non-TextNode items should pass through unchanged
        class Obj:
            pass

        o = Obj()
        node = TextNode("prefix ![img](https://i.imgur.com/a.png) suffix", TextType.PLAIN)
        new_nodes = split_nodes_image([o, node])
        # first element remains the same type instance
        self.assertIs(new_nodes[0], o)

    def test_images_and_links_combined(self):
        node = TextNode(
            "Start ![img](https://i.imgur.com/a.png) middle [link](https://x.com) end",
            TextType.PLAIN,
        )
        # split_links only handles links, split_images handles images; do them sequentially
        step1 = split_nodes_image([node])
        step2 = []
        for n in step1:
            step2.extend(split_nodes_link([n]))
        # Ensure final nodes contain separate image and link nodes
        self.assertTrue(any(n.text_type == TextType.IMAGE for n in step2))
        self.assertTrue(any(n.text_type == TextType.LINK for n in step2))

    def test_text_to_textnodes_example(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.PLAIN),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.PLAIN),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.PLAIN),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.PLAIN),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.PLAIN),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_code_protects(self):
        text = "Here is `code with **not bold** and _not italic_` and outside **bold**"
        nodes = text_to_textnodes(text)
        # ensure the inner markers are treated as code, not bold/italic
        # find the code node
        code_nodes = [n for n in nodes if n.text_type == TextType.CODE]
        self.assertEqual(len(code_nodes), 1)
        self.assertIn("**not bold**", code_nodes[0].text)
        self.assertIn("_not italic_", code_nodes[0].text)


if __name__ == "__main__":
    unittest.main()
