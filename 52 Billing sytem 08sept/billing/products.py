def get_products():
    """Takes product names, prices, and quantities from user"""
    products = []
    prices = []
    quantities = []

    count = 1
    while True:
        product = input(f"Enter Product {count} - ")
        products.append(product)

        qty = int(input(f"Enter {product} Quantity : "))
        price = float(input(f"Enter {product} Price : "))

        quantities.append(qty)
        prices.append(price)

        more = input("Do you Want to add more [Y/N] : ").strip().upper()
        if more == "N":
            break
        count += 1

    return products, prices, quantities
