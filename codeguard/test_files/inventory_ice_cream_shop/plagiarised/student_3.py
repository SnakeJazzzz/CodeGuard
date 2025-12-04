# Ice Cream Shop Inventory Management System
# Student 1 - Object-Oriented Approach

# This is my implementation of the ice cream shop system
# I used object-oriented programming to make it clean and organized

class IceCreamShop:
    def __init__(self):
        # Initialize inventory with starting quantities
        self.inventory = {
            'vanilla': 50,
            'chocolate': 50,
            'strawberry': 50,
            'mint': 50,
            'cookie_dough': 50
        }
        # Track what we've sold
        self.sold = {
            'vanilla': 0,
            'chocolate': 0,
            'strawberry': 0,
            'mint': 0,
            'cookie_dough': 0
        }
        # Price structure for different sizes
        self.prices = {
            'small': 3.50,
            'medium': 5.00,
            'large': 6.50
        }
        # Keep track of total money made
        self.total_earnings = 0.0

    def display_menu(self):
        # Display the main menu options
        print("\n=== Ice Cream Shop Management ===")
        print("1. View Inventory")
        print("2. View Sales")
        print("3. Sell Ice Cream")
        print("4. Change Prices")
        print("5. View Earnings")
        print("6. Exit")
        print("=" * 35)

    def view_inventory(self):
        # Show current stock levels
        print("\n--- Current Inventory ---")
        for flavor, quantity in self.inventory.items():
            print(f"{flavor.replace('_', ' ').title()}: {quantity} scoops")

    def view_sales(self):
        # Display sales data
        print("\n--- Total Sales by Flavor ---")
        for flavor, quantity in self.sold.items():
            print(f"{flavor.replace('_', ' ').title()}: {quantity} scoops")

    def sell_ice_cream(self):
        # Handle selling ice cream
        print("\n--- Sell Ice Cream ---")
        print("Available flavors:")
        for i, flavor in enumerate(self.inventory.keys(), 1):
            print(f"{i}. {flavor.replace('_', ' ').title()}")

        try:
            choice = int(input("Select flavor (number): "))
            flavors = list(self.inventory.keys())
            if choice < 1 or choice > len(flavors):
                print("Invalid choice!")
                return

            flavor = flavors[choice - 1]

            print("\nSizes: 1. Small 2. Medium 3. Large")
            size_choice = int(input("Select size: "))
            sizes = ['small', 'medium', 'large']
            if size_choice < 1 or size_choice > 3:
                print("Invalid size!")
                return

            size = sizes[size_choice - 1]

            # Check if we have stock and process the sale
            if self.inventory[flavor] > 0:
                self.inventory[flavor] -= 1
                self.sold[flavor] += 1
                self.total_earnings += self.prices[size]
                print(f"\nSold 1 {size} {flavor.replace('_', ' ')} for ${self.prices[size]:.2f}")
            else:
                print("Out of stock!")
        except ValueError:
            print("Invalid input!")

    def change_prices(self):
        # Allow price modifications
        print("\n--- Change Prices ---")
        print("Current Prices:")
        for size, price in self.prices.items():
            print(f"{size.title()}: ${price:.2f}")

        try:
            size = input("\nEnter size to change (small/medium/large): ").lower()
            if size not in self.prices:
                print("Invalid size!")
                return

            new_price = float(input(f"Enter new price for {size}: $"))
            self.prices[size] = new_price
            print(f"Price updated successfully!")
        except ValueError:
            print("Invalid price!")

    def view_earnings(self):
        # Show total revenue
        print(f"\n--- Total Earnings: ${self.total_earnings:.2f} ---")

    def run(self):
        # Main program loop
        while True:
            self.display_menu()
            try:
                choice = input("\nEnter choice: ")

                if choice == '1':
                    self.view_inventory()
                elif choice == '2':
                    self.view_sales()
                elif choice == '3':
                    self.sell_ice_cream()
                elif choice == '4':
                    self.change_prices()
                elif choice == '5':
                    self.view_earnings()
                elif choice == '6':
                    print("Thank you! Goodbye!")
                    break
                else:
                    print("Invalid choice! Please try again.")
            except Exception as e:
                print(f"Error: {e}")

# Entry point
if __name__ == "__main__":
    shop = IceCreamShop()
    shop.run()
