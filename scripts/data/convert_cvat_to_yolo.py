import xml.etree.ElementTree as ET
import os


def convert_cvat_xml_to_yolo():
    input_xml = r"C:\Workspace\projects\ml\real-world-telecom-infrastructure-object-detection\data\synthetic\labels\synthetic.xml"
    output_folder = r"C:\Workspace\projects\ml\real-world-telecom-infrastructure-object-detection\data\synthetic\labels"

    class_mapping = {
        "Indihome": 0,
        "Indosat": 1,
        "MyRepublic": 2,
        "Lintasarta": 3,
        "CBN": 4
    }

    if not os.path.exists(input_xml):
        print(f"ERROR: XML File not found: {input_xml}")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Output folder created: {output_folder}")

    print("Start processing XML...")
    tree = ET.parse(input_xml)
    root = tree.getroot()

    processed_count = 0

    for image in root.findall('image'):
        image_name = image.get('name')
        width = float(image.get('width'))
        height = float(image.get('height'))

        base_name = os.path.splitext(os.path.basename(image_name))[0]
        txt_filename = base_name + ".txt"
        output_path = os.path.join(output_folder, txt_filename)

        yolo_lines = []

        for box in image.findall('box'):
            label = box.get('label')

            if label not in class_mapping:
                print(f"SKIP: Label '{label}' is not recognized in the image {image_name}")
                continue

            class_id = class_mapping[label]

            xtl = float(box.get('xtl'))
            ytl = float(box.get('ytl'))
            xbr = float(box.get('xbr'))
            ybr = float(box.get('ybr'))

            box_w = xbr - xtl
            box_h = ybr - ytl
            x_center = xtl + (box_w / 2)
            y_center = ytl + (box_h / 2)

            norm_x = x_center / width
            norm_y = y_center / height
            norm_w = box_w / width
            norm_h = box_h / height

            line = f"{class_id} {norm_x:.6f} {norm_y:.6f} {norm_w:.6f} {norm_h:.6f}"
            yolo_lines.append(line)

        with open(output_path, 'w') as f:
            f.write("\n".join(yolo_lines))

        processed_count += 1
        print(f"Generated: {txt_filename} ({len(yolo_lines)} labels)")

    print(f"\nDone! A total of {processed_count} .txt files have been created in the output folder.")


if __name__ == "__main__":
    convert_cvat_xml_to_yolo()