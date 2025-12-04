#!/usr/bin/env python3
# Ice cream shop with error handling and input validation
# Professional approach

import sys

class ValidationError(Exception):
    pass

class OutOfStockError(Exception):
    pass

class IceCreamShop:
    def __init__(self):
        self.inventory = {
            'Classic Vanilla': 100,
            'Rich Chocolate': 90,
            'Sweet Strawberry': 85,
            'Cool Mint': 75,
            'Nutty Pecan': 70,
            'Tangy Lemon': 65
        }

        self.sales_record = {flavor: 0 for flavor in self.inventory.keys()}

        self.price_structure = {
            'Cup-Small': 3.50,
            'Cup-Medium': 5.00,
            'Cup-Large': 6.50,
            'Cone-Small': 3.75,
            'Cone-Medium': 5.25,
            'Cone-Large': 6.75
        }

        self.total_revenue = 0.0

    def validate_choice(self, choice, max_value):
        try:
            choice_int = int(choice)
            if 1 <= choice_int <= max_value:
                return choice_int
            raise ValidationError(f"Choice must be between 1 and {max_value}")
        except ValueError:
            raise ValidationError("Invalid input. Please enter a number.")

    def display_main_menu(self):
        print("\n" + "=" * 50)
        print("ICE CREAM SHOP INVENTORY SYSTEM".center(50))
        print("=" * 50)
        print("\nMain Menu:")
        print("  1. Display Inventory")
        print("  2. Display Sales Statistics")
        print("  3. Record Sale")
        print("  4. Modify Prices")
        print("  5. Display Revenue")
        print("  6. Exit Program")
        print("=" * 50)

    def display_inventory(self):
        print("\n" + "-" * 50)
        print("CURRENT INVENTORY".center(50))
        print("-" * 50)

        for flavor, quantity in self.inventory.items():
            status = "[LOW]" if quantity < 30 else "[OK]"
            print(f"{flavor:<30} {quantity:>5} scoops {status:>8}")

        print("-" * 50)

    def display_sales_statistics(self):
        print("\n" + "-" * 50)
        print("SALES STATISTICS".center(50))
        print("-" * 50)

        total_scoops = 0
        for flavor, count in self.sales_record.items():
            print(f"{flavor:<30} {count:>5} scoops")
            total_scoops += count

        print("-" * 50)
        print(f"{'TOTAL SCOOPS SOLD':<30} {total_scoops:>5}")
        print("-" * 50)

    def record_sale(self):
        print("\n" + "-" * 50)
        print("RECORD NEW SALE".center(50))
        print("-" * 50)

        try:
            # Select flavor
            flavors = list(self.inventory.keys())
            print("\nAvailable Flavors:")
            for idx, flavor in enumerate(flavors, 1):
                stock = self.inventory[flavor]
                print(f"  {idx}. {flavor} ({stock} in stock)")

            flavor_choice = input("\nSelect flavor number: ")
            flavor_idx = self.validate_choice(flavor_choice, len(flavors)) - 1
            selected_flavor = flavors[flavor_idx]

            # Check stock
            if self.inventory[selected_flavor] <= 0:
                raise OutOfStockError(f"{selected_flavor} is currently out of stock!")

            # Select size/type
            options = list(self.price_structure.keys())
            print("\nAvailable Options:")
            for idx, option in enumerate(options, 1):
                price = self.price_structure[option]
                print(f"  {idx}. {option} - ${price:.2f}")

            option_choice = input("\nSelect option number: ")
            option_idx = self.validate_choice(option_choice, len(options)) - 1
            selected_option = options[option_idx]

            # Process sale
            price = self.price_structure[selected_option]
            self.inventory[selected_flavor] -= 1
            self.sales_record[selected_flavor] += 1
            self.total_revenue += price

            print("\n" + "=" * 50)
            print("SALE COMPLETED".center(50))
            print("=" * 50)
            print(f"Product: {selected_flavor}")
            print(f"Option: {selected_option}")
            print(f"Price: ${price:.2f}")
            print(f"Remaining stock: {self.inventory[selected_flavor]}")
            print("=" * 50)

        except ValidationError as e:
            print(f"\nValidation Error: {e}")
        except OutOfStockError as e:
            print(f"\nStock Error: {e}")
        except Exception as e:
            print(f"\nUnexpected Error: {e}")

    def modify_prices(self):
        print("\n" + "-" * 50)
        print("MODIFY PRICES".center(50))
        print("-" * 50)

        try:
            options = list(self.price_structure.keys())
            print("\nCurrent Pricing:")
            for idx, option in enumerate(options, 1):
                price = self.price_structure[option]
                print(f"  {idx}. {option:<20} ${price:.2f}")

            option_choice = input("\nSelect option to modify: ")
            option_idx = self.validate_choice(option_choice, len(options)) - 1
            selected_option = options[option_idx]

            new_price_str = input(f"Enter new price for {selected_option}: $")
            new_price = float(new_price_str)

            if new_price < 0:
                raise ValidationError("Price cannot be negative")

            self.price_structure[selected_option] = new_price

            print(f"\nSuccess! {selected_option} price updated to ${new_price:.2f}")

        except ValidationError as e:
            print(f"\nValidation Error: {e}")
        except ValueError:
            print("\nError: Invalid price format. Please enter a valid number.")
        except Exception as e:
            print(f"\nUnexpected Error: {e}")

    def display_revenue(self):
        print("\n" + "=" * 50)
        print(f"TOTAL REVENUE: ${self.total_revenue:.2f}".center(50))
        print("=" * 50)

    def run(self):
        print("Initializing Ice Cream Shop Inventory System...")

        while True:
            try:
                self.display_main_menu()
                choice = input("\nEnter your choice: ")

                if choice == '1':
                    self.display_inventory()
                elif choice == '2':
                    self.display_sales_statistics()
                elif choice == '3':
                    self.record_sale()
                elif choice == '4':
                    self.modify_prices()
                elif choice == '5':
                    self.display_revenue()
                elif choice == '6':
                    print("\nShutting down system...")
                    print("Thank you for using Ice Cream Shop Inventory System!")
                    sys.exit(0)
                else:
                    print("\nError: Invalid choice. Please select 1-6.")

            except KeyboardInterrupt:
                print("\n\nInterrupt detected. Exiting...")
                sys.exit(0)

if __name__ == "__main__":
    shop = IceCreamShop()
    shop.run()
