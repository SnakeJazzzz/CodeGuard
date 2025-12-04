# Ice cream inventory - dictionary-based simple version
# I'm keeping it super simple!

def main():
    flavors = {
        'v': {'name': 'Vanilla', 'stock': 100, 'sold': 0},
        'c': {'name': 'Chocolate', 'stock': 95, 'sold': 0},
        's': {'name': 'Strawberry', 'stock': 80, 'sold': 0},
        'm': {'name': 'Mint Chip', 'stock': 70, 'sold': 0}
    }

    sizes = {1: ('Small', 2.50), 2: ('Medium', 4.00), 3: ('Large', 5.50)}

    earnings = [0.0]  # using list so it's mutable

    def menu():
        print("\n" + "-"*40)
        print("MENU:")
        print("  i = inventory")
        print("  s = sales")
        print("  b = buy")
        print("  p = prices")
        print("  e = earnings")
        print("  q = quit")
        print("-"*40)

    def show_inv():
        print("\nInventory:")
        for k, v in flavors.items():
            print(f"  [{k}] {v['name']}: {v['stock']} scoops")

    def show_sales():
        print("\nSales:")
        for k, v in flavors.items():
            print(f"  [{k}] {v['name']}: {v['sold']} scoops")

    def buy():
        show_inv()
        f = input("Flavor? ")
        if f not in flavors:
            print("Nope!")
            return

        if flavors[f]['stock'] <= 0:
            print("Out!")
            return

        print("\nSizes:")
        for num, (name, price) in sizes.items():
            print(f"  {num}. {name} ${price}")

        sz = int(input("Size? "))
        if sz not in sizes:
            print("Invalid size")
            return

        flavors[f]['stock'] -= 1
        flavors[f]['sold'] += 1
        earnings[0] += sizes[sz][1]
        print(f"Done! Charged ${sizes[sz][1]}")

    def change_price():
        print("\nCurrent:")
        for num, (name, price) in sizes.items():
            print(f"  {num}. {name} ${price}")

        sz = int(input("Change which? "))
        new = float(input("New price? "))
        sizes[sz] = (sizes[sz][0], new)
        print("Changed!")

    def show_earn():
        print(f"\nTotal: ${earnings[0]:.2f}")

    while True:
        menu()
        cmd = input("> ").lower()

        if cmd == 'i':
            show_inv()
        elif cmd == 's':
            show_sales()
        elif cmd == 'b':
            buy()
        elif cmd == 'p':
            change_price()
        elif cmd == 'e':
            show_earn()
        elif cmd == 'q':
            print("Bye!")
            break

if __name__ == '__main__':
    main()
