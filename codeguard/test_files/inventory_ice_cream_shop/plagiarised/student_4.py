# Ice Cream Shop Inventory Management System
# My original implementation using OOP principles

class ShopManager:
    def __init__(self):
        # Stock levels for each ice cream type
        self.stock = {
            'vanilla': 50,
            'chocolate': 50,
            'strawberry': 50,
            'mint': 50,
            'cookie_dough': 50
        }
        # Sales tracking dictionary
        self.sales_count = {
            'vanilla': 0,
            'chocolate': 0,
            'strawberry': 0,
            'mint': 0,
            'cookie_dough': 0
        }
        # Pricing information
        self.size_prices = {
            'small': 3.50,
            'medium': 5.00,
            'large': 6.50
        }
        # Revenue tracker
        self.money_earned = 0.0

    def show_menu(self):
        # Main menu display
        print("\n=== Ice Cream Shop Management ===")
        print("1. View Inventory")
        print("2. View Sales")
        print("3. Sell Ice Cream")
        print("4. Change Prices")
        print("5. View Earnings")
        print("6. Exit")
        print("=" * 35)

    def show_stock(self):
        # Display current inventory levels
        print("\n--- Current Inventory ---")
        for ice_cream, amount in self.stock.items():
            print(f"{ice_cream.replace('_', ' ').title()}: {amount} scoops")

    def show_sales(self):
        # Show sales statistics
        print("\n--- Total Sales by Flavor ---")
        for ice_cream, amount in self.sales_count.items():
            print(f"{ice_cream.replace('_', ' ').title()}: {amount} scoops")

    def make_sale(self):
        # Process a sale transaction
        print("\n--- Sell Ice Cream ---")
        print("Available flavors:")
        for i, ice_cream in enumerate(self.stock.keys(), 1):
            print(f"{i}. {ice_cream.replace('_', ' ').title()}")

        try:
            selection = int(input("Select flavor (number): "))
            ice_cream_list = list(self.stock.keys())
            if selection < 1 or selection > len(ice_cream_list):
                print("Invalid choice!")
                return

            ice_cream = ice_cream_list[selection - 1]

            print("\nSizes: 1. Small 2. Medium 3. Large")
            size_selection = int(input("Select size: "))
            size_options = ['small', 'medium', 'large']
            if size_selection < 1 or size_selection > 3:
                print("Invalid size!")
                return

            selected_size = size_options[size_selection - 1]

            if self.stock[ice_cream] > 0:
                self.stock[ice_cream] -= 1
                self.sales_count[ice_cream] += 1
                self.money_earned += self.size_prices[selected_size]
                print(f"\nSold 1 {selected_size} {ice_cream.replace('_', ' ')} for ${self.size_prices[selected_size]:.2f}")
            else:
                print("Out of stock!")
        except ValueError:
            print("Invalid input!")

    def modify_prices(self):
        # Update pricing structure
        print("\n--- Change Prices ---")
        print("Current Prices:")
        for container_size, cost in self.size_prices.items():
            print(f"{container_size.title()}: ${cost:.2f}")

        try:
            container_size = input("\nEnter size to change (small/medium/large): ").lower()
            if container_size not in self.size_prices:
                print("Invalid size!")
                return

            updated_cost = float(input(f"Enter new price for {container_size}: $"))
            self.size_prices[container_size] = updated_cost
            print(f"Price updated successfully!")
        except ValueError:
            print("Invalid price!")

    def show_revenue(self):
        # Display total earnings
        print(f"\n--- Total Earnings: ${self.money_earned:.2f} ---")

    def start(self):
        # Main application loop
        while True:
            self.show_menu()
            try:
                user_choice = input("\nEnter choice: ")

                if user_choice == '1':
                    self.show_stock()
                elif user_choice == '2':
                    self.show_sales()
                elif user_choice == '3':
                    self.make_sale()
                elif user_choice == '4':
                    self.modify_prices()
                elif user_choice == '5':
                    self.show_revenue()
                elif user_choice == '6':
                    print("Thank you! Goodbye!")
                    break
                else:
                    print("Invalid choice! Please try again.")
            except Exception as error:
                print(f"Error: {error}")

if __name__ == "__main__":
    manager = ShopManager()
    manager.start()
