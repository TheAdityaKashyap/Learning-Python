def calculate_total(prices, quantities):
    """Calculate total = sum of price * quantity"""
    total = 0
    for price, qty in zip(prices, quantities):
        total += price * qty
    return total


def apply_gst(total):
    choice = input("Do You Want to add GST [Y/N] : ").strip().upper()
    gst_percent = 0
    gst_amount = 0
    final_total = total

    if choice == "Y":
        gst_percent = float(input("Enter GST % = "))
        gst_amount = (total * gst_percent) / 100
        final_total = total + gst_amount

    return gst_percent, final_total
