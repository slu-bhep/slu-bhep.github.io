from bs4 import BeautifulSoup, Tag

# Overall style of the file
style_p = "<style>p {margin: 0;padding: 0; font-family: Calibri, sans-serif;}</style>"
style_h2 = "<style>h2 {margin-bottom: 0.2em; margin-top: 0; padding: 0; font-size: 20px; font-family: Calibri, sans-serif;}</style>"
style_h3 = "<style>h3 {margin-bottom: 0.2em; margin-top: 0; padding: 0; font-family: Calibri, sans-serif;}</style>"
style_li = """
<style>
    li { 
        margin: 0; 
        padding: 0; 
        font-family: Calibri, sans-serif;
    }
    .indented-li {
        margin: 0 0 0 45px;
        padding: 0;
        font-family: Calibri, sans-serif;
    }
</style>
"""
email_style =  style_p + style_h2 + style_h3 + style_li

# Agents listed style (very specific)
def style_agents_listed(text):
    if text == "-":
        return f'<p style="margin: 0 0 0 45px; font-size: 14px; font-family: Calibri, sans-serif;"><span style="color: #44546A;">Agents Listed:</span> {text}</p><br>'

    else:
        lines = text.split('\n')
        
        # Wrap each line in a <li> tag
        list_items = ''.join(f'<li style="margin: 0 0 0 20px; font-size: 14px; font-family: Calibri, sans-serif;">{line}</li>' for line in lines if line.strip())
        
        # Combine the list items into a <ul> element
        formatted_text = f'<ul style="margin: 0 0 0 20px; font-size: 14px; font-family: Calibri, sans-serif;">{list_items}</ul>'
        
        # Return the final HTML with the formatted list
        return f'<p style="margin: 0 0 0 45px; font-size: 14px; font-family: Calibri, sans-serif;"><span style="color: #44546A;">Agents Listed:</span><br>{formatted_text}</p><br>'


def custom_prettify(element, indent=0):
    INLINE_TAGS = ['b', 'span', 'li', 'u', 'br']
    
    result = ""
    if isinstance(element, Tag):
        # Start tag
        result += '  ' * indent + '<' + element.name
        for attr, value in element.attrs.items():
            result += f' {attr}="{value}"'
        result += '>'
        
        if element.name in INLINE_TAGS:
            # Handle inline tags
            for child in element:
                if isinstance(child, Tag):
                    result += custom_prettify(child, 0)  # Do not increase the indentation for inline tags
                else:
                    result += child  # If child is NavigableString (i.e., text), add it directly
            result += f'</{element.name}>'
            # Add newline after the inline tag unless it's a <li>
            if element.name in ['br', 'li']:
                result += '\n'
        else:
            result += '\n'
            # Recursively format child elements
            for child in element.children:
                result += custom_prettify(child, indent + 1)
            # End tag
            result += '  ' * indent + f'</{element.name}>\n'
    elif element.strip():
        # Text nodes
        result += '  ' * indent + element.strip() + '\n'
    return result


def format_html(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    return custom_prettify(soup)


def write_string_to_file(filename, string):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(string)

# Function to read contents from a file
def read_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()
