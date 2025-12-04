#!/usr/bin/env python3
"""
Ice Cream Inventory - Using state machine pattern
Each state handles specific operations
"""

from enum import Enum, auto

class State(Enum):
    MENU = auto()
    VIEW_INVENTORY = auto()
    VIEW_SALES = auto()
    PROCESS_SALE = auto()
    UPDATE_PRICES = auto()
    VIEW_EARNINGS = auto()
    EXIT = auto()

class StateMachine:
    def __init__(self):
        self.state = State.MENU
        self.data = {
            'inventory': {
                'French Vanilla': 95,
                'Belgian Chocolate': 85,
                'Fresh Strawberry': 70,
                'Mint Blast': 60,
                'Salted Caramel': 75
            },
            'sold': {
                'French Vanilla': 0,
                'Belgian Chocolate': 0,
                'Fresh Strawberry': 0,
                'Mint Blast': 0,
                'Salted Caramel': 0
            },
            'prices': {
                'Tiny': 2.75,
                'Small': 4.25,
                'Medium': 5.75,
                'Large': 7.25
            },
            'earnings': 0.0
        }

    def transition(self, new_state):
        self.state = new_state

    def handle_menu(self):
        print("\n" + "=" * 45)
        print("MAIN MENU")
        print("=" * 45)
        print("[1] View Inventory")
        print("[2] View Sales")
        print("[3] Process Sale")
        print("[4] Update Prices")
        print("[5] View Earnings")
        print("[0] Exit")

        choice = input("\nSelect: ")

        if choice == '1':
            self.transition(State.VIEW_INVENTORY)
        elif choice == '2':
            self.transition(State.VIEW_SALES)
        elif choice == '3':
            self.transition(State.PROCESS_SALE)
        elif choice == '4':
            self.transition(State.UPDATE_PRICES)
        elif choice == '5':
            self.transition(State.VIEW_EARNINGS)
        elif choice == '0':
            self.transition(State.EXIT)
        else:
            print("Invalid choice!")

    def handle_view_inventory(self):
        print("\n>>> INVENTORY <<<")
        for flavor, qty in self.data['inventory'].items():
            print(f"  {flavor}: {qty} scoops")

        input("\nPress Enter to continue...")
        self.transition(State.MENU)

    def handle_view_sales(self):
        print("\n>>> SALES <<<")
        for flavor, qty in self.data['sold'].items():
            print(f"  {flavor}: {qty} scoops")

        total_sold = sum(self.data['sold'].values())
        print(f"\nTotal Sold: {total_sold} scoops")

        input("\nPress Enter to continue...")
        self.transition(State.MENU)

    def handle_process_sale(self):
        print("\n>>> PROCESS SALE <<<")

        flavors = list(self.data['inventory'].keys())
        print("\nFlavors:")
        for i, flavor in enumerate(flavors, 1):
            qty = self.data['inventory'][flavor]
            print(f"  {i}. {flavor} ({qty} available)")

        try:
            flavor_choice = int(input("\nFlavor: ")) - 1
            if flavor_choice < 0 or flavor_choice >= len(flavors):
                print("Invalid!")
                input("Press Enter...")
                self.transition(State.MENU)
                return

            selected_flavor = flavors[flavor_choice]

            if self.data['inventory'][selected_flavor] <= 0:
                print(f"{selected_flavor} is OUT OF STOCK!")
                input("Press Enter...")
                self.transition(State.MENU)
                return

            sizes = list(self.data['prices'].keys())
            print("\nSizes:")
            for i, size in enumerate(sizes, 1):
                price = self.data['prices'][size]
                print(f"  {i}. {size} - ${price:.2f}")

            size_choice = int(input("\nSize: ")) - 1
            if size_choice < 0 or size_choice >= len(sizes):
                print("Invalid!")
                input("Press Enter...")
                self.transition(State.MENU)
                return

            selected_size = sizes[size_choice]
            price = self.data['prices'][selected_size]

            self.data['inventory'][selected_flavor] -= 1
            self.data['sold'][selected_flavor] += 1
            self.data['earnings'] += price

            print(f"\n*** SALE COMPLETE ***")
            print(f"{selected_flavor} ({selected_size}) - ${price:.2f}")
            input("\nPress Enter...")

        except ValueError:
            print("Invalid input!")
            input("Press Enter...")

        self.transition(State.MENU)

    def handle_update_prices(self):
        print("\n>>> UPDATE PRICES <<<")

        sizes = list(self.data['prices'].keys())
        print("\nCurrent Prices:")
        for i, size in enumerate(sizes, 1):
            price = self.data['prices'][size]
            print(f"  {i}. {size}: ${price:.2f}")

        try:
            size_choice = int(input("\nUpdate which size? ")) - 1
            if size_choice < 0 or size_choice >= len(sizes):
                print("Invalid!")
                input("Press Enter...")
                self.transition(State.MENU)
                return

            selected_size = sizes[size_choice]
            new_price = float(input(f"New price for {selected_size}: $"))

            self.data['prices'][selected_size] = new_price
            print(f"\n{selected_size} price updated to ${new_price:.2f}")
            input("Press Enter...")

        except ValueError:
            print("Invalid input!")
            input("Press Enter...")

        self.transition(State.MENU)

    def handle_view_earnings(self):
        print("\n>>> EARNINGS <<<")
        print(f"Total: ${self.data['earnings']:.2f}")
        input("\nPress Enter...")
        self.transition(State.MENU)

    def handle_exit(self):
        print("\nThank you! Goodbye!")

    def run(self):
        handlers = {
            State.MENU: self.handle_menu,
            State.VIEW_INVENTORY: self.handle_view_inventory,
            State.VIEW_SALES: self.handle_view_sales,
            State.PROCESS_SALE: self.handle_process_sale,
            State.UPDATE_PRICES: self.handle_update_prices,
            State.VIEW_EARNINGS: self.handle_view_earnings,
            State.EXIT: self.handle_exit
        }

        while self.state != State.EXIT:
            handler = handlers[self.state]
            handler()

if __name__ == "__main__":
    machine = StateMachine()
    machine.run()
