import re
import fitz  # PyMuPDF

def read_pdf_text(path):
    text = ''
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def parse_flexible_work_order(text, debug=False):
    def log(msg):
        if debug:
            print(msg)

    lines = text.split('\n')
    items = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if re.match(r'^\d+\s+[A-Z0-9./\-]+', line):  # Starts with a number and item code
            parts = line.split()
            sr_no = parts[0]
            item_code = parts[1]
            description_parts = parts[2:]

            # Try to collect more description lines below if needed
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if re.match(r'^\d+\s+[A-Z0-9./\-]+', next_line):  # New item starts
                    break
                if next_line.lower().startswith('dispatch details'):
                    break
                description_parts.append(next_line)
                j += 1

            item_description = ' '.join(description_parts).strip()
            items.append((item_code, item_description))
            log(f"[ITEM] {item_code} -> {item_description}")
            i = j
        else:
            i += 1

    return items

# Run it
file_path = r"C:/Users/LENOVO/Documents/PerformaInvoices/WO- 3249 APCO INFRATECH PRIVATE LIMITED.pdf"
text = read_pdf_text(file_path)
parsed_items = parse_flexible_work_order(text, debug=True)

# Print results
for code, desc in parsed_items:
    print(f"\nItem Code: {code}\nDescription: {desc}\n")
