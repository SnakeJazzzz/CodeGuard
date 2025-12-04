"""
Ice Cream Shop - Using recursive menu approach
Interesting way to handle menu navigation
"""

def initialize_data():
    global STOCK, SOLD, PRICES, CASH
    STOCK = {'Vanilla': 50, 'Chocolate': 50, 'Mint': 50, 'Caramel': 50}
    SOLD = {'Vanilla': 0, 'Chocolate': 0, 'Mint': 0, 'Caramel': 0}
    PRICES = {'S': 3.00, 'M': 4.50, 'L': 6.00}
    CASH = 0.0

def display_stock():
    print("\n>>> STOCK LEVELS <<<")
    for flavor, qty in STOCK.items():
        print(f"{flavor}: {qty}")
    return menu()

def display_sold():
    print("\n>>> SALES RECORD <<<")
    for flavor, qty in SOLD.items():
        print(f"{flavor}: {qty}")
    total = sum(SOLD.values())
    print(f"TOTAL: {total}")
    return menu()

def process_sale():
    global CASH
    print("\n>>> PROCESS SALE <<<")

    flavors = list(STOCK.keys())
    for i, f in enumerate(flavors):
        print(f"{i+1}. {f} ({STOCK[f]} available)")

    try:
        choice = int(input("Flavor: "))
        if choice < 1 or choice > len(flavors):
            print("Bad choice!")
            return menu()

        flavor = flavors[choice - 1]

        if STOCK[flavor] == 0:
            print("SOLD OUT!")
            return menu()

        print("Sizes: S/M/L")
        for sz, pr in PRICES.items():
            print(f"  {sz}: ${pr}")

        size = input("Size: ").upper()
        if size not in PRICES:
            print("Bad size!")
            return menu()

        STOCK[flavor] -= 1
        SOLD[flavor] += 1
        CASH += PRICES[size]

        print(f"SALE: {flavor} ({size}) - ${PRICES[size]}")

    except:
        print("Error!")

    return menu()

def adjust_pricing():
    print("\n>>> ADJUST PRICING <<<")
    print("Current:")
    for sz, pr in PRICES.items():
        print(f"{sz}: ${pr}")

    try:
        size = input("Size: ").upper()
        if size not in PRICES:
            print("Invalid!")
            return menu()

        price = float(input("New price: "))
        PRICES[size] = price
        print("Updated!")

    except:
        print("Error!")

    return menu()

def show_cash():
    print(f"\n>>> TOTAL CASH: ${CASH:.2f} <<<")
    return menu()

def menu():
    print("\n" + "=" * 30)
    print("ICE CREAM SHOP")
    print("=" * 30)
    print("[1] Stock")
    print("[2] Sales")
    print("[3] Sell")
    print("[4] Pricing")
    print("[5] Cash")
    print("[0] Exit")

    cmd = input("> ")

    if cmd == '1':
        return display_stock()
    elif cmd == '2':
        return display_sold()
    elif cmd == '3':
        return process_sale()
    elif cmd == '4':
        return adjust_pricing()
    elif cmd == '5':
        return show_cash()
    elif cmd == '0':
        print("Goodbye!")
        return
    else:
        print("Invalid!")
        return menu()

if __name__ == '__main__':
    initialize_data()
    menu()
