import xml.etree.ElementTree as ET
import sys
import os

def process_svg(filepath):
    # Register the default namespace
    ET.register_namespace('', 'http://www.w3.org/2000/svg')

    tree = ET.parse(filepath)
    root = tree.getroot()

    # Namespaces dict for findall
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    # The SVG structure has text elements for language names.
    # The language names are PHP, CSS, HTML, Python, JavaScript.
    # The percentages in metrics.bottom.svg were:
    # PHP: 56.3%, CSS: 7.04%, JavaScript: 33.16%, Hack: 3.5%
    # But wait, 1-repos-per-language has PHP, CSS, HTML, Python, JavaScript.
    # We should calculate percentage directly from the SVG paths if possible.

    # Or just read metrics.bottom.svg if that's what the user prefers?
    # No, let's extract them from the SVG pie chart path elements.

    # The paths have a shape. The path d attributes for an arc look like:
    # d="MstartX,startY A rx,ry x-axis-rotation large-arc-flag sweep-flag endX,endY L... Z"

    paths = root.findall('.//svg:path', ns)
    texts = root.findall('.//svg:text', ns)

    # Get all text values that are likely language names.
    # They are the texts starting from the second one (first one is the title).

    lang_texts = texts[1:]

    # For a circle, total angle is 360 degrees.
    # The action github-profile-summary-cards uses d3-shape arc.
    # The paths are sorted in the same order as the legend texts!
    import re
    import math

    total_angle = 2 * math.pi

    for i, path in enumerate(paths):
        d = path.get('d')
        # d="M-1.1021821192326178e-14,-60A60,60,0,0,1,59.398420329586706,8.475120196772503L34.649078525592245,4.94382011478396A35,35,0,0,0,-6.429395695523604e-15,-35Z"
        # The first A command: A rx,ry x-axis-rotation large-arc-flag sweep-flag endX,endY
        match = re.search(r'M([^,]+),([^A]+)A60,60,0,([01]),([01]),([^,]+),([^L]+)L', d)
        if match:
            startX, startY = float(match.group(1)), float(match.group(2))
            large_arc = int(match.group(3))
            sweep = int(match.group(4))
            endX, endY = float(match.group(5)), float(match.group(6))

            # calculate angles
            angle1 = math.atan2(startY, startX)
            angle2 = math.atan2(endY, endX)

            # Adjust angles because y is downwards in SVG, but atan2 assumes normal cartesian.
            # actually atan2(y, x) is fine.
            diff = angle2 - angle1
            if diff < 0:
                diff += 2 * math.pi

            if large_arc == 1 and diff < math.pi:
                diff = 2 * math.pi - diff
            elif large_arc == 0 and diff > math.pi:
                diff = 2 * math.pi - diff

            percentage = (diff / total_angle) * 100
            if percentage > 99.9:
                percentage = 100.0

            # format to 1 decimal place
            perc_str = f"{percentage:.1f}%"

            # Add to the corresponding text
            if i < len(lang_texts):
                original_text = lang_texts[i].text
                if "%" not in original_text:
                    lang_texts[i].text = f"{original_text} {perc_str}"

    tree.write(filepath, encoding='utf-8', xml_declaration=True)
    print(f"Processed {filepath}")

def main():
    files = [
        "profile-summary-card-output/algolia/1-repos-per-language.svg",
        "profile-summary-card-output/algolia/2-most-commit-language.svg"
    ]
    for f in files:
        if os.path.exists(f):
            process_svg(f)
        else:
            print(f"File {f} not found!")

if __name__ == "__main__":
    main()
