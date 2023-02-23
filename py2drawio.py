import os
import ast

def get_class_definitions(file_path):
    """Returns a list of class definitions in a Python file."""
    with open(file_path, "r",encoding = 'utf8') as f:
        tree = ast.parse(f.read())
    return [node for node in tree.body if isinstance(node, ast.ClassDef)]

def get_method_calls(node):
    """Returns a list of method calls in a node."""
    return [n.name for n in ast.walk(node) if  isinstance(n, ast.FunctionDef)]

def get_attribute_names(node):
    """Returns a list of attribute names in a node."""
    return [n.targets[0].attr for n in ast.walk(node) if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Attribute)]

def get_classes(directory):
    """Returns a list of class definitions and their relationships in a directory."""
    classes = {}
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".py"):
                file_path = os.path.join(root, file_name)
                for class_node in get_class_definitions(file_path):
                    class_name = class_node.name
                    if class_name not in classes:
                        classes[class_name] = {"methods": [], "attributes": []}
                    for method_call in get_method_calls(class_node):
                        if method_call not in classes[class_name]["methods"]:
                            classes[class_name]["methods"].append(method_call)
                    for attribute_name in get_attribute_names(class_node):
                        if attribute_name not in classes[class_name]["attributes"]:
                            classes[class_name]["attributes"].append(attribute_name)
    class_list = []
    for class_name, class_info in classes.items():
        class_list.append((class_name, class_info["methods"], class_info["attributes"]))
    return class_list

def generate_class_file(class_list, output_file):
    """Generates a xml file which can be imported with drawio to render a class diagramm."""
    # set initial y coordinates
    y_coord = 1
    x_coord = 1
    buffer_size = 10
    # set initial swimlane height
    swimlane_width = 160
    component_hight = 26
    # open output file
    with open(output_file, "w") as f:
        # write xml header
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
        f.write('<mxfile>\n')
        f.write('<diagram>\n')
        f.write('<mxGraphModel>\n')
        f.write('<root>\n')
        f.write('<mxCell id="0" />\n')
        f.write('<mxCell id="1" parent="0" />\n')
        # loop through classes
        class_id = 1
        for class_name, methods, attributes in class_list:
            y = y_coord
            swimlane_height = 26 * (len(attributes) + len(methods) + 2)
            
            # write swimlane
            f.write(f'<mxCell id="{class_name}" value="{class_name}" style="swimlane;" vertex="1" parent="1">\n')
            f.write(f'<mxGeometry x="{x_coord}" y="{y}" width="{swimlane_width}" height="{swimlane_height}" as="geometry" />\n')
            f.write('</mxCell>\n')
            # loop through attributes
            field_id = 1
            for attribute in attributes:
                field_name = class_name+attribute
                y = y + component_hight
                # write attribute
                f.write(f'<mxCell id="{field_name}" value="+ {attribute}" style="text;" vertex="1" parent="{class_name}">\n')
                f.write(f'<mxGeometry y="{y}" width="{swimlane_width}" height="{component_hight}" as="geometry" />\n')
                f.write('</mxCell>\n')
                # increment field id
            
            # write line
            y = y + component_hight
            line_name = class_name + "_line"
            f.write(f'<mxCell id="{line_name}" value="" style="line;" vertex="1" parent="{class_name}">\n')
            f.write(f'<mxGeometry y="{y}" width="160" height="{component_hight}" as="geometry" />\n')
            f.write('</mxCell>\n')
            # increment field id
            field_id += 1


            # loop through methods
            for method in methods:
                field_name = method + class_name
                y = y + component_hight
                # write method
                f.write(f'<mxCell id="{field_name}" value="+ {method}()" style="text;" vertex="1" parent="{class_name}">\n')
                f.write(f'<mxGeometry y="{y}" width="{swimlane_width}" height="{component_hight}" as="geometry" />\n')
                f.write('</mxCell>\n')
                # increment field id
            # update x coordinates for new class
            x_coord += swimlane_width*class_id + buffer_size*class_id
        # write closing tags
        f.write('</root>\n')
        f.write('</mxGraphModel>\n')
        f.write('</diagram>\n')
        f.write('</mxfile>\n')

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        directory = sys.argv[1]
        class_list = get_classes(directory)
        generate_class_file(class_list, "classes.drawio")
        print("Finished")
        print("--> classes.drawio")
    else:
        raise Exception("Please provide a directory")