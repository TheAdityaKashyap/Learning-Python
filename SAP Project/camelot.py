import camelot

# Path to your PDF file
file_path = r"C:\Users\LENOVO\Documents\PerformaInvoices WO- 3136 LARSEN & TOUBRO LIMITED.pdf"

# Read tables from the PDF (try 'lattice' first for bordered tables)
tables = camelot.read_pdf(file_path, pages='all', flavor='lattice')

# Check how many tables were found
print(f"Total tables found: {tables.n}")

# If tables were found, show and export them
if tables.n > 0:
    print("\nFirst table preview:")
    print(tables[0].df.head())  # shows first few rows of first table
    
    # Export all tables to Excel
    output_path = r"C:\Users\LENOVO\Documents\Extracted_Tables.xlsx"
    tables.export(output_path, f='excel')
    print(f"\n✅ All tables exported successfully to:\n{output_path}")
else:
    print("⚠️ No tables detected. Try changing the flavor to 'stream' below:\n")
    print("tables = camelot.read_pdf(file_path, pages='all', flavor='stream')")
