def print_bill(products, prices, quantities, total, gst_percent, final_total):
    print("\n------- Output -------")
    for i, (p, pr, qty) in enumerate(zip(products, prices, quantities), start=1):
        print(f"{i}. {p} ({qty} x {pr}) = {pr * qty}/-")
    print("-" * 20)
    print(f"Total = {total}")
    if gst_percent > 0:
        print(f"GST = {gst_percent}%")
    print("-" * 20)
    print(f"Final Total = {final_total:.0f}/-")
    print("-" * 20)
