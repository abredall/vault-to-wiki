#!/usr/bin/env python3
import re
from unittest import case

# PAGE LINK CONVERSION
# [[file name|link text]] --> [[link text|file-name]]
def switch_fn_linktext(m):
    # Groups are now: 1: '[[', 2: pagename, 3: linktext, 4: ']]'
    linktext = m.group(3)
    pagename = m.group(2).replace(" ", "-")
    sub = f"{m.group(1)}{linktext}|{pagename}{m.group(4)}"
    return sub

def transform_page_links(text):
    # This regex now specifically looks for links that are NOT image links (![[...]])
    # and not header links ([[#...]]) by checking the first characters.
    return re.sub(r"(?<!!)(\[\[)([^#\[\]][^\[\]]*?)\|([^\[\]|]+?)(\]\])", switch_fn_linktext, text)

# HEADER LINK CONVERSION
# [[#Some header in the page|some text]] --> [some text](#some-header-in-the-page)
def links_to_header(m):
    linktext = m.group(2)
    pagename = m.group(1).replace(" ", "-").lower()
    sub = f"[{linktext}]({pagename})"
    return sub

def transform_header_links(text):
    return re.sub(r"\[\[(#[^#|\[\]]+?)\|([^\[\]|]+?)\]\]", links_to_header, text)

# IMAGE LINK CONVERSION
# ![[some image.png]] --> [[some image.png]]
def remove_exclamation_mark(m):
    sub = " " + m.group(2)
    return sub

def transform_image_links(text):
    return re.sub(r"(!)(\[\[.+\]\])", remove_exclamation_mark, text)

def modified_property(m):
    modified_date = m.group(2)
    sub = f"<sub>last modified: {modified_date}</sub>\n"
    return sub

def transform_modified_property(text):
    return re.sub(r"---\n(?:.+\:.*\n)*created\: (.*)\n(?:.+\:.*\n)*last modified\: (.*)\n(?:.+\:.*\n)*---", modified_property, text)

def table_of_contents(m):
    toc_settings = {}
    toc_settings_lines = m.group(1).splitlines()
    for line in toc_settings_lines:
        key, value = line.split(': ')
        toc_settings[key] = value
    
    toc_text = f"{toc_settings['title']}\n"

    remaining_content = m.group(2)

    # GitHub Markdown supports 6 heading levels
    hl_1 = 1
    hl_2 = 1
    hl_3 = 1
    hl_4 = 1
    hl_5 = 1
    hl_6 = 1

    for line in remaining_content.splitlines():
        match line.strip():
            case s if s.startswith("# "):
                toc_text += f"{hl_1}. [{s[2:]}](#{s[2:].replace(' ', '-').lower()})\n"
                hl_1 += 1
                # Reset lower levels
                hl_2 = 1
                hl_3 = 1
                hl_4 = 1
                hl_5 = 1
                hl_6 = 1
            case s if s.startswith("## "):
                toc_text += f"    {hl_2}. [{s[3:]}](#{s[3:].replace(' ', '-').lower()})\n"
                hl_2 += 1
                # Reset lower levels
                hl_3 = 1
                hl_4 = 1
                hl_5 = 1
                hl_6 = 1
            case s if s.startswith("### "):
                toc_text += f"        {hl_3}. [{s[4:]}](#{s[4:].replace(' ', '-').lower()})\n"
                hl_3 += 1
                # Reset lower levels
                hl_4 = 1
                hl_5 = 1
                hl_6 = 1
            case s if s.startswith("#### "):
                toc_text += f"            {hl_4}. [{s[5:]}](#{s[5:].replace(' ', '-').lower()})\n"
                hl_4 += 1
                # Reset lower levels
                hl_5 = 1
                hl_6 = 1
            case s if s.startswith("##### "):
                toc_text += f"                {hl_5}. [{s[6:]}](#{s[6:].replace(' ', '-').lower()})\n"
                hl_5 += 1
                # Reset lower levels
                hl_6 = 1
            case s if s.startswith("###### "):
                toc_text += f"                    {hl_6}. [{s[7:]}](#{s[7:].replace(' ', '-').lower()})\n"
                hl_6 += 1
    
    toc_text += remaining_content
    return toc_text

def transform_table_of_contents(text):
    return re.sub(r"(?s:```table-of-contents\n(.*)```\n(.*))", table_of_contents, text)

def run_all_transformations(text):
    text = transform_page_links(text)
    text = transform_header_links(text)
    text = transform_image_links(text)
    text = transform_modified_property(text)
    text = transform_table_of_contents(text)
    return text
