"""Ice cream shop - using JSON-style data structure"""

import json

DATA = {
    "products": [
        {"id": 1, "name": "Vanilla", "qty": 55, "sold": 0},
        {"id": 2, "name": "Chocolate", "qty": 60, "sold": 0},
        {"id": 3, "name": "Strawberry", "qty": 45, "sold": 0},
        {"id": 4, "name": "Mint", "qty": 40, "sold": 0},
    ],
    "pricing": [
        {"code": "A", "desc": "Mini", "amount": 2.99},
        {"code": "B", "desc": "Regular", "amount": 4.49},
        {"code": "C", "desc": "Large", "amount": 6.49},
        {"code": "D", "desc": "Jumbo", "amount": 8.99},
    ],
    "cash_register": 0.0
}

def find_product_by_id(pid):
    for p in DATA["products"]:
        if p["id"] == pid:
            return p
    return None

def find_pricing_by_code(code):
    for pr in DATA["pricing"]:
        if pr["code"] == code:
            return pr
    return None

def print_banner(text):
    print("\n" + "*" * 60)
    print(f"* {text:^56} *")
    print("*" * 60)

def menu():
    print("\n[1] Stock Report")
    print("[2] Sales Report")
    print("[3] Make Sale")
    print("[4] Price Manager")
    print("[5] Cash Register")
    print("[0] Exit")

def stock_report():
    print_banner("STOCK REPORT")
    for p in DATA["products"]:
        print(f"ID {p['id']}: {p['name']:<15} Qty: {p['qty']}")

def sales_report():
    print_banner("SALES REPORT")
    for p in DATA["products"]:
        print(f"ID {p['id']}: {p['name']:<15} Sold: {p['sold']}")

def make_sale():
    print_banner("MAKE SALE")

    print("\nProducts:")
    for p in DATA["products"]:
        print(f"  [{p['id']}] {p['name']} (Available: {p['qty']})")

    try:
        pid = int(input("\nProduct ID: "))
        product = find_product_by_id(pid)

        if not product:
            print("Product not found!")
            return

        if product["qty"] <= 0:
            print("OUT OF STOCK!")
            return

        print("\nSizes:")
        for pr in DATA["pricing"]:
            print(f"  [{pr['code']}] {pr['desc']} - ${pr['amount']:.2f}")

        code = input("\nSize Code: ").upper()
        pricing = find_pricing_by_code(code)

        if not pricing:
            print("Invalid size!")
            return

        product["qty"] -= 1
        product["sold"] += 1
        DATA["cash_register"] += pricing["amount"]

        print(f"\nSALE COMPLETE: {product['name']} ({pricing['desc']}) - ${pricing['amount']:.2f}")

    except ValueError:
        print("Invalid input!")

def price_manager():
    print_banner("PRICE MANAGER")

    print("\nCurrent Prices:")
    for pr in DATA["pricing"]:
        print(f"  [{pr['code']}] {pr['desc']}: ${pr['amount']:.2f}")

    try:
        code = input("\nCode to update: ").upper()
        pricing = find_pricing_by_code(code)

        if not pricing:
            print("Invalid code!")
            return

        new_amount = float(input(f"New price for {pricing['desc']}: $"))
        pricing["amount"] = new_amount

        print(f"{pricing['desc']} updated to ${new_amount:.2f}")

    except ValueError:
        print("Invalid price!")

def cash_register():
    print_banner("CASH REGISTER")
    print(f"\nTotal: ${DATA['cash_register']:.2f}")

def main():
    print_banner("ICE CREAM SHOP")

    while True:
        menu()
        choice = input("\nOption: ")

        if choice == "1":
            stock_report()
        elif choice == "2":
            sales_report()
        elif choice == "3":
            make_sale()
        elif choice == "4":
            price_manager()
        elif choice == "5":
            cash_register()
        elif choice == "0":
            print("\nClosing shop. Goodbye!")
            break
        else:
            print("Invalid option!")

if __name__ == "__main__":
    main()
