class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.props = props if props else {}
        self.children = children if children else []

    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        return ' '.join(f'{key}="{value}"' for key, value in self.props.items())

    def __repr__(self):
        return f"HTMLNode(tag={self.tag}, value={self.value}, children={self.children}, props={self.props})"


class LeafNode(HTMLNode):
    """A leaf node: no children allowed, tag and value required (value must not be None).

    The tag parameter itself may be None (meaning raw text), but it must be provided
    as an explicit argument to the constructor. Props is optional.
    """
    def __init__(self, tag, value, props=None):
        # tag is required (but may be None), value is required
        super().__init__(tag=tag, value=value, children=[], props=props)

    def to_html(self):
        if self.value is None:
            raise ValueError("LeafNode must have a value")

        text = str(self.value)
        # If tag is None, return raw text
        if self.tag is None:
            return text

        attrs = self.props_to_html()
        if attrs:
            return f"<{self.tag} {attrs}>{text}</{self.tag}>"
        return f"<{self.tag}>{text}</{self.tag}>"


class ParentNode(HTMLNode):
    """A parent node: tag and children are required, value is not used, props optional."""
    def __init__(self, tag, children, props=None):
        # tag and children are required; children should be an iterable/list of HTMLNode
        # Call super with an empty children list to initialize props and other fields,
        # but preserve the original `children` argument so we can detect an explicit
        # `None` (missing) value.
        super().__init__(tag=tag, value=None, children=[], props=props)
        self.children = children

    def to_html(self):
        if self.tag is None:
            raise ValueError("ParentNode must have a tag")

        if self.children is None:
            raise ValueError("ParentNode must have children")

        # Render children recursively
        rendered_children = ''.join(child.to_html() for child in self.children)

        attrs = self.props_to_html()
        if attrs:
            return f"<{self.tag} {attrs}>{rendered_children}</{self.tag}>"
        return f"<{self.tag}>{rendered_children}</{self.tag}>"

