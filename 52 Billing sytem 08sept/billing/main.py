from products import get_products
from billing import calculate_total, apply_gst
from printer import print_bill


def main():
    products, prices, quantities = get_products()
    total = calculate_total(prices, quantities)
    gst_percent, final_total = apply_gst(total)
    print_bill(products, prices, quantities, total, gst_percent, final_total)


if __name__ == "__main__":
    main()
