import xml.etree.ElementTree as ET
import xml.dom.minidom

# Define the input and output file paths
input_file = "/mnt/sso/two_78/alps/.repo/manifests/yocto.xml"
output_file = "/home/gaoyx/yocto.xml"

# Parse the input XML file
tree = ET.parse(input_file)
root = tree.getroot()

# Create a new XML tree for the output file
new_root = ET.Element("paths")

# Extract all 'path' attributes from 'project' elements
for project in root.findall(".//project"):
    path = project.get("path")
    if path:
        # Create a new element with the path attribute and add it to the new XML tree
        path_element = ET.Element("path")
        path_element.set("value", path)
        new_root.append(path_element)

# Create a new XML tree
new_tree = ET.ElementTree(new_root)

# Convert the tree to a string
xml_str = ET.tostring(new_root, encoding="utf-8")

# Parse the string with minidom for pretty printing
dom = xml.dom.minidom.parseString(xml_str)
pretty_xml_str = dom.toprettyxml(indent="  ")

# Write the pretty XML string to the output file
with open(output_file, "w", encoding="utf-8") as f:
    f.write(pretty_xml_str)

print(f"Extracted paths have been written to {output_file}")
