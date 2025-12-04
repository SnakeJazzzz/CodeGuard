#!/usr/bin/env python3
# Using inheritance and abstract base classes
# Advanced OOP approach

from abc import ABC, abstractmethod

class MenuItem(ABC):
    def __init__(self, name, initial_stock):
        self._name = name
        self._stock = initial_stock
        self._units_sold = 0

    @property
    def name(self):
        return self._name

    @property
    def stock(self):
        return self._stock

    @property
    def units_sold(self):
        return self._units_sold

    @abstractmethod
    def sell_unit(self):
        pass

    @abstractmethod
    def display_info(self):
        pass

class IceCreamFlavor(MenuItem):
    def sell_unit(self):
        if self._stock > 0:
            self._stock -= 1
            self._units_sold += 1
            return True
        return False

    def display_info(self):
        return f"{self._name}: {self._stock} in stock, {self._units_sold} sold"

class PriceManager:
    def __init__(self):
        self._prices = {}

    def add_price_tier(self, tier_name, price):
        self._prices[tier_name] = price

    def get_price(self, tier_name):
        return self._prices.get(tier_name, 0.0)

    def update_price(self, tier_name, new_price):
        if tier_name in self._prices:
            self._prices[tier_name] = new_price
            return True
        return False

    def get_all_tiers(self):
        return list(self._prices.items())

class CashRegister:
    def __init__(self):
        self._total = 0.0

    def add_transaction(self, amount):
        self._total += amount

    def get_total(self):
        return self._total

class ShopManager:
    def __init__(self):
        self._menu_items = []
        self._price_manager = PriceManager()
        self._cash_register = CashRegister()

        self._initialize_shop()

    def _initialize_shop(self):
        # Add flavors
        flavors = [
            ('Madagascar Vanilla', 85),
            ('Swiss Chocolate', 90),
            ('Wild Strawberry', 70),
            ('Peppermint Swirl', 65),
            ('Butter Pecan', 55)
        ]

        for name, stock in flavors:
            self._menu_items.append(IceCreamFlavor(name, stock))

        # Add price tiers
        tiers = [
            ('Junior', 2.75),
            ('Single', 4.25),
            ('Double', 6.00),
            ('Triple', 7.75)
        ]

        for tier, price in tiers:
            self._price_manager.add_price_tier(tier, price)

    def show_menu(self):
        print("\n" + "=" * 55)
        print("ICE CREAM SHOP MANAGEMENT SYSTEM".center(55))
        print("=" * 55)
        print("1. View Inventory")
        print("2. View Sales Report")
        print("3. Process Transaction")
        print("4. Manage Pricing")
        print("5. View Cash Register")
        print("0. Exit")
        print("=" * 55)

    def view_inventory(self):
        print("\n--- INVENTORY ---")
        for idx, item in enumerate(self._menu_items, 1):
            print(f"{idx}. {item.display_info()}")

    def view_sales_report(self):
        print("\n--- SALES REPORT ---")
        total_sold = 0
        for idx, item in enumerate(self._menu_items, 1):
            print(f"{idx}. {item.name}: {item.units_sold} units")
            total_sold += item.units_sold
        print(f"\nTotal Units Sold: {total_sold}")

    def process_transaction(self):
        print("\n--- PROCESS TRANSACTION ---")

        # Select item
        print("\nAvailable Items:")
        for idx, item in enumerate(self._menu_items, 1):
            print(f"{idx}. {item.name} ({item.stock} available)")

        try:
            item_choice = int(input("\nSelect item: ")) - 1

            if item_choice < 0 or item_choice >= len(self._menu_items):
                print("Invalid selection!")
                return

            selected_item = self._menu_items[item_choice]

            if selected_item.stock <= 0:
                print(f"{selected_item.name} is out of stock!")
                return

            # Select price tier
            print("\nAvailable Tiers:")
            tiers = self._price_manager.get_all_tiers()
            for idx, (tier, price) in enumerate(tiers, 1):
                print(f"{idx}. {tier}: ${price:.2f}")

            tier_choice = int(input("\nSelect tier: ")) - 1

            if tier_choice < 0 or tier_choice >= len(tiers):
                print("Invalid selection!")
                return

            tier_name, price = tiers[tier_choice]

            # Process
            if selected_item.sell_unit():
                self._cash_register.add_transaction(price)
                print(f"\nTransaction Successful!")
                print(f"Item: {selected_item.name}")
                print(f"Tier: {tier_name}")
                print(f"Price: ${price:.2f}")
            else:
                print("Transaction failed!")

        except (ValueError, IndexError):
            print("Invalid input!")

    def manage_pricing(self):
        print("\n--- MANAGE PRICING ---")

        tiers = self._price_manager.get_all_tiers()
        print("\nCurrent Pricing:")
        for idx, (tier, price) in enumerate(tiers, 1):
            print(f"{idx}. {tier}: ${price:.2f}")

        try:
            tier_choice = int(input("\nSelect tier to update: ")) - 1

            if tier_choice < 0 or tier_choice >= len(tiers):
                print("Invalid selection!")
                return

            tier_name, _ = tiers[tier_choice]
            new_price = float(input(f"Enter new price for {tier_name}: $"))

            if self._price_manager.update_price(tier_name, new_price):
                print(f"Price updated: {tier_name} = ${new_price:.2f}")
            else:
                print("Failed to update price!")

        except (ValueError, IndexError):
            print("Invalid input!")

    def view_cash_register(self):
        print(f"\n--- CASH REGISTER: ${self._cash_register.get_total():.2f} ---")

    def run(self):
        while True:
            self.show_menu()
            choice = input("\nYour choice: ").strip()

            if choice == '1':
                self.view_inventory()
            elif choice == '2':
                self.view_sales_report()
            elif choice == '3':
                self.process_transaction()
            elif choice == '4':
                self.manage_pricing()
            elif choice == '5':
                self.view_cash_register()
            elif choice == '0':
                print("\nExiting system. Goodbye!")
                break
            else:
                print("Invalid choice!")

def main():
    manager = ShopManager()
    manager.run()

if __name__ == "__main__":
    main()
