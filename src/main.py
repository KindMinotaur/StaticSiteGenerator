from textnode import TextNode, TextType

print("hello world")

def main():
    # construct using the enum member
    node = TextNode('This is a link', TextType.LINK, 'https://google.com')
    print(node)


if __name__ == "__main__":
    main()
