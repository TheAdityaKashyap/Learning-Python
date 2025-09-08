def bill_without_gst(price, Quantity):
    Total_Bill = price * Quantity
    print("The total bill without gst is: ", Total_Bill)
    return Total_Bill


def bill_with_gst(price, Quantity, gst):
    Total_Bill = price * Quantity
    print("The total bill without gst is: ", Total_Bill)
    gst_amount = (Total_Bill * gst) / 100
    print("The gst percentage is: ", gst)
    print("The gst amount is: ", gst_amount)
    Total_Bill_with_gst = Total_Bill + gst_amount
    print("The total bill with gst is: ", Total_Bill_with_gst)
    return Total_Bill_with_gst