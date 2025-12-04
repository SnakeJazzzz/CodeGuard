"""
Ice Cream Shop Management System
Combining different approaches for robust solution
"""

from functools import reduce

# My custom implementation
class IceCreamShop:
    def __init__(self):
        # Initialize stock using dictionary
        self.stock = {
            'Vanilla': 100,
            'Chocolate': 100,
            'Strawberry': 75,
            'mint': 50,
            'cookie_dough': 50
        }
        # Sales tracking
        self.sales_count = {
            'Vanilla': 0,
            'Chocolate': 0,
            'Strawberry': 0,
            'mint': 0,
            'cookie_dough': 0
        }
        # Pricing structure
        self.size_prices = {
            'S': 2.99,
            'M': 4.49,
            'L': 5.99,
            'small': 3.50,
            'medium': 5.00,
            'large': 6.50
        }
        # Revenue tracking
        self.money_earned = 0.0

    def show_menu(self):
        # Display main menu options
        menu_items = [
            "Ice Cream Inventory System",
            "1 - Show Stock",
            "2 - Show Sales Report",
            "3 - Process Sale",
            "4 - Update Pricing",
            "5 - Revenue Summary",
            "0 - Exit System"
        ]
        print("\n" + "=" * 40)
        for item in menu_items:
            print(item)
        print("=" * 40)

    def show_stock(self):
        # Display inventory levels
        print("\n** CURRENT STOCK **")
        for ice_cream, amount in self.stock.items():
            print(f"  {ice_cream}: {amount} units")

    def show_sales(self):
        # Show sales report with total calculation
        print("\n** SALES REPORT **")
        total_sold = reduce(lambda acc, x: acc + x, self.sales_count.values(), 0)
        for ice_cream, amount in self.sales_count.items():
            print(f"  {ice_cream}: {amount} units sold")
        print(f"\nTotal Units Sold: {total_sold}")

    def make_sale(self):
        # Process a new sale
        print("\n-- Process New Sale --")
        ice_cream_list = list(self.stock.keys())

        for idx, ice_cream in enumerate(ice_cream_list):
            print(f"{idx + 1}. {ice_cream} (Stock: {self.stock[ice_cream]})")

        try:
            selection = int(input("\nSelect flavor number: ")) - 1
            if selection < 0 or selection >= len(ice_cream_list):
                print("Invalid selection")
                return

            ice_cream = ice_cream_list[selection]

            if self.stock[ice_cream] <= 0:
                print(f"Sorry, {ice_cream} is out of stock!")
                return

            print("\nSize Options:")
            available_sizes = list(self.size_prices.keys())
            for container_size in available_sizes:
                print(f"  {container_size} - ${self.size_prices[container_size]:.2f}")

            selected_size = input("\nEnter size: ")
            if selected_size not in self.size_prices:
                print("Invalid size")
                return

            # Process the transaction
            self.stock[ice_cream] -= 1
            self.sales_count[ice_cream] += 1
            self.money_earned += self.size_prices[selected_size]

            print(f"\nSale completed! {ice_cream} ({selected_size}) - ${self.size_prices[selected_size]:.2f}")

        except (ValueError, IndexError):
            print("Invalid input")

    def modify_prices(self):
        # Update pricing
        print("\n-- Update Pricing --")
        print("Current Prices:")
        for container_size, cost in self.size_prices.items():
            print(f"  {container_size}: ${cost:.2f}")

        try:
            container_size = input("\nEnter size to update: ")
            if container_size not in self.size_prices:
                print("Invalid size")
                return

            updated_cost = float(input(f"Enter new price for {container_size}: $"))
            self.size_prices[container_size] = updated_cost
            print(f"Price updated: {container_size} is now ${updated_cost:.2f}")

        except ValueError:
            print("Invalid price format")

    def show_revenue(self):
        # Display earnings
        print(f"\n** TOTAL REVENUE: ${self.money_earned:.2f} **")

    def start(self):
        # Main program loop
        while True:
            self.show_menu()
            user_choice = input("\nYour choice: ").strip()

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
            elif user_choice == '0':
                print("\nClosing shop... Goodbye!")
                break
            else:
                print("Invalid option. Try again.")

if __name__ == "__main__":
    manager = IceCreamShop()
    manager.start()
