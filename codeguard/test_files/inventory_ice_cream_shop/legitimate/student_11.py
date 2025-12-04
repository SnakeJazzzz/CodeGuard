#!/usr/bin/env python3
# Command pattern implementation
# Using lambda functions for menu dispatch

class InventoryManager:
    def __init__(self):
        self.flavors = ['Vanilla', 'Chocolate', 'Strawberry', 'Pistachio', 'Cookies']
        self.quantities = [75, 75, 60, 50, 65]
        self.sales = [0, 0, 0, 0, 0]
        self.size_pricing = [('Mini', 2.25), ('Regular', 3.75), ('Super', 5.25), ('Mega', 7.00)]
        self.money = 0.0

        # Command dispatch table
        self.commands = {
            '1': lambda: self.cmd_show_inventory(),
            '2': lambda: self.cmd_show_sales(),
            '3': lambda: self.cmd_make_sale(),
            '4': lambda: self.cmd_change_prices(),
            '5': lambda: self.cmd_show_money(),
            'q': lambda: False
        }

    def cmd_show_inventory(self):
        print("\n*** INVENTORY ***")
        for i in range(len(self.flavors)):
            print(f"{self.flavors[i]}: {self.quantities[i]} scoops")
        return True

    def cmd_show_sales(self):
        print("\n*** SALES ***")
        for i in range(len(self.flavors)):
            print(f"{self.flavors[i]}: {self.sales[i]} scoops")
        return True

    def cmd_make_sale(self):
        print("\n*** MAKE SALE ***")
        for i in range(len(self.flavors)):
            print(f"{i+1}. {self.flavors[i]} ({self.quantities[i]} left)")

        try:
            idx = int(input("Flavor #: ")) - 1

            if idx < 0 or idx >= len(self.flavors):
                print("Invalid!")
                return True

            if self.quantities[idx] == 0:
                print("Out of stock!")
                return True

            print("\nSizes:")
            for i in range(len(self.size_pricing)):
                name, price = self.size_pricing[i]
                print(f"{i+1}. {name} - ${price}")

            size_idx = int(input("Size #: ")) - 1

            if size_idx < 0 or size_idx >= len(self.size_pricing):
                print("Invalid!")
                return True

            self.quantities[idx] -= 1
            self.sales[idx] += 1
            _, price = self.size_pricing[size_idx]
            self.money += price

            print(f"Sold for ${price}!")

        except ValueError:
            print("Invalid input!")

        return True

    def cmd_change_prices(self):
        print("\n*** CHANGE PRICES ***")
        for i in range(len(self.size_pricing)):
            name, price = self.size_pricing[i]
            print(f"{i+1}. {name}: ${price}")

        try:
            idx = int(input("Which size? ")) - 1

            if idx < 0 or idx >= len(self.size_pricing):
                print("Invalid!")
                return True

            new_price = float(input("New price: "))
            name, _ = self.size_pricing[idx]
            self.size_pricing[idx] = (name, new_price)
            print("Updated!")

        except ValueError:
            print("Invalid input!")

        return True

    def cmd_show_money(self):
        print(f"\n*** TOTAL: ${self.money:.2f} ***")
        return True

    def show_menu(self):
        print("\n" + "="*35)
        print("ICE CREAM SHOP MANAGER")
        print("="*35)
        print("1. Show inventory")
        print("2. Show sales")
        print("3. Make sale")
        print("4. Change prices")
        print("5. Show money")
        print("q. Quit")

    def run(self):
        running = True
        while running:
            self.show_menu()
            choice = input("\n> ").lower()

            if choice in self.commands:
                running = self.commands[choice]()
            else:
                print("Unknown command!")

        print("Shutting down...")

if __name__ == '__main__':
    manager = InventoryManager()
    manager.run()
