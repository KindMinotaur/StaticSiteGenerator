from enum import Enum

# Functional-style Enum declaration with explicit values
TextType = Enum('TextType', [
	('PLAIN', 'text'),    # plain text
	('BOLD', 'bold'),     # **Bold text**
	('ITALIC', 'italic'), # _Italic text_
	('CODE', 'code'),     # `Code text`
	('LINK', 'link'),     # [anchor text](url)
	('IMAGE', 'image'),   # ![alt text](url)
])
from dataclasses import dataclass
from typing import Optional


@dataclass
class TextNode:
	"""A simple container for pieces of text and their type.

	text_type may be provided either as a TextType member or as a string
	matching the enum value (e.g. 'link'). We normalize to the TextType value.
	"""
	text: str
	text_type: TextType
	url: Optional[str] = None

	def __post_init__(self):
		# Allow passing the text_type as a string like 'link' for convenience
		if not isinstance(self.text_type, TextType):
			# find the enum member with matching value
			for member in TextType:
				if member.value == self.text_type:
					self.text_type = member
					break

	def __eq__(self, other):
		if not isinstance(other, TextNode):
			return False
		return (self.text, self.text_type, self.url) == (other.text, other.text_type, other.url)

	def __repr__(self):
		# Use the enum's .value so the repr shows the plain names like 'link'
		return f"TextNode({self.text!r}, {self.text_type.value!r}, {self.url!r})"


