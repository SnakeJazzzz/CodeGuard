"""
Ice Cream Management using Dictionary Comprehensions
Functional style with comprehensions
"""

def create_shop():
    return {
        'flavors': {f: {'stock': 60, 'sold': 0} for f in ['Vanilla', 'Chocolate', 'Strawberry', 'Pistachio']},
        'sizes': {s: p for s, p in [('XS', 2.5), ('S', 4.0), ('M', 5.5), ('L', 7.0), ('XL', 9.0)]},
        'revenue': 0.0
    }

def menu_display():
    return "\n".join([
        "",
        "~" * 40,
        "ICE CREAM SHOP DASHBOARD",
        "~" * 40,
        "Commands:",
        "  i - Inventory",
        "  s - Sales",
        "  t - Transaction",
        "  p - Pricing",
        "  r - Revenue",
        "  q - Quit",
        "~" * 40
    ])

def show_inventory(shop):
    print("\n=== INVENTORY ===")
    print("\n".join([f"{name}: {data['stock']} scoops" for name, data in shop['flavors'].items()]))

def show_sales(shop):
    print("\n=== SALES ===")
    print("\n".join([f"{name}: {data['sold']} scoops" for name, data in shop['flavors'].items()]))
    total = sum([data['sold'] for data in shop['flavors'].values()])
    print(f"\nTotal: {total} scoops")

def transaction(shop):
    print("\n=== TRANSACTION ===")

    flavor_list = list(shop['flavors'].keys())
    print("\n".join([f"{i+1}. {fl} ({shop['flavors'][fl]['stock']} left)" for i, fl in enumerate(flavor_list)]))

    try:
        fl_idx = int(input("\nFlavor #: ")) - 1
        if not (0 <= fl_idx < len(flavor_list)):
            print("Invalid!")
            return shop

        flavor = flavor_list[fl_idx]

        if shop['flavors'][flavor]['stock'] <= 0:
            print("Out of stock!")
            return shop

        size_list = list(shop['sizes'].keys())
        print("\nSizes:")
        print("\n".join([f"{i+1}. {sz}: ${shop['sizes'][sz]:.2f}" for i, sz in enumerate(size_list)]))

        sz_idx = int(input("\nSize #: ")) - 1
        if not (0 <= sz_idx < len(size_list)):
            print("Invalid!")
            return shop

        size = size_list[sz_idx]
        price = shop['sizes'][size]

        shop['flavors'][flavor]['stock'] -= 1
        shop['flavors'][flavor]['sold'] += 1
        shop['revenue'] += price

        print(f"\nTransaction complete: {flavor} ({size}) - ${price:.2f}")

    except (ValueError, KeyError):
        print("Error in transaction!")

    return shop

def update_pricing(shop):
    print("\n=== UPDATE PRICING ===")

    size_list = list(shop['sizes'].keys())
    print("Current:")
    print("\n".join([f"{i+1}. {sz}: ${shop['sizes'][sz]:.2f}" for i, sz in enumerate(size_list)]))

    try:
        sz_idx = int(input("\nSize #: ")) - 1
        if not (0 <= sz_idx < len(size_list)):
            print("Invalid!")
            return shop

        size = size_list[sz_idx]
        new_price = float(input(f"New price for {size}: $"))

        shop['sizes'][size] = new_price
        print(f"{size} updated to ${new_price:.2f}")

    except (ValueError, KeyError):
        print("Error updating price!")

    return shop

def show_revenue(shop):
    print(f"\n=== REVENUE: ${shop['revenue']:.2f} ===")

def run():
    shop = create_shop()

    commands = {
        'i': lambda s: (show_inventory(s), s)[1],
        's': lambda s: (show_sales(s), s)[1],
        't': transaction,
        'p': update_pricing,
        'r': lambda s: (show_revenue(s), s)[1]
    }

    while True:
        print(menu_display())
        cmd = input("\n> ").lower()

        if cmd == 'q':
            print("Goodbye!")
            break
        elif cmd in commands:
            shop = commands[cmd](shop)
        else:
            print("Unknown command!")

if __name__ == "__main__":
    run()
