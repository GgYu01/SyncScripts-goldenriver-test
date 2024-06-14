import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from collections import defaultdict

def extract_values(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    values = {
        'path': set(),
        'copyfile': set(),
        'linkfile': set()
    }
    
    for project in root.findall(".//project"):
        path = project.attrib.get('path')
        if not path:
            path = project.attrib.get('name')
        if path:
            values['path'].add(path)
    
    for copyfile in root.findall(".//copyfile"):
        dest = copyfile.attrib.get('dest')
        if dest:
            values['copyfile'].add(dest)
    
    for linkfile in root.findall(".//linkfile"):
        dest = linkfile.attrib.get('dest')
        if dest:
            values['linkfile'].add(dest)
    
    return values

def find_added(values1, values2):
    added = defaultdict(set)
    for key in values2:
        added[key] = values2[key] - values1[key]
    return added

def find_removed(values1, values2):
    removed = defaultdict(set)
    for key in values1:
        removed[key] = values1[key] - values2[key]
    return removed

def compare_files(file1, file2):
    values1 = extract_values(file1)
    values2 = extract_values(file2)
    
    result = {
        'added': find_added(values1, values2),
        'removed': find_removed(values1, values2)
    }
    
    return result

def write_comparison_to_xml(result, output_file):
    root = ET.Element("comparison")

    for change_type, changes in result.items():
        change_element = ET.SubElement(root, change_type)
        for key, items in changes.items():
            key_element = ET.SubElement(change_element, key)
            for item in items:
                item_element = ET.SubElement(key_element, "item")
                item_element.text = item

    # Convert to string and parse with minidom for pretty printing
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml_as_string = reparsed.toprettyxml(indent="  ")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_as_string)

# Example usage:
file1 = '/mnt/sso/san_78/alps/.repo/manifests/alps.xml'
file2 = '/home/gaoyx/t-alps-release-u0.mp1-liber.auto-spm-pre3-of.p52.20240520.xml'
output_file = '/mnt/sso/san_78/SyncScripts-goldenriver-test/differences.xml'

comparison_result = compare_files(file1, file2)
write_comparison_to_xml(comparison_result, output_file)
