import sys
from collections import defaultdict

class IceCreamInventory:
    """
    Manages ice cream shop inventory with comprehensive features
    """

    def __init__(self):
        self._flavors = {
            'Vanilla Bean': 150,
            'Dark Chocolate': 120,
            'Strawberry Swirl': 100,
            'Pistachio': 90,
            'Rocky Road': 110,
            'Mango Sorbet': 80
        }

        self._sales_data = defaultdict(int)

        self._price_chart = {
            'kiddie': 1.99,
            'regular': 3.49,
            'large': 4.99,
            'party': 8.99
        }

        self._total_revenue = 0.0

    def run_application(self):
        """Main application loop"""
        print("Welcome to Ice Cream Inventory Manager v1.0")

        while True:
            self._render_menu()
            selection = input("\nEnter selection: ").strip()

            if selection == '1':
                self._handle_inventory_view()
            elif selection == '2':
                self._handle_sales_view()
            elif selection == '3':
                self._handle_transaction()
            elif selection == '4':
                self._handle_price_adjustment()
            elif selection == '5':
                self._handle_revenue_view()
            elif selection == '6':
                self._handle_exit()
                break
            else:
                print("[ERROR] Invalid selection. Try again.")

    def _render_menu(self):
        """Renders the main menu"""
        print("\n" + "=" * 50)
        print("MAIN MENU".center(50))
        print("=" * 50)
        print("1. Display Current Inventory")
        print("2. Display Sales Statistics")
        print("3. Process New Transaction")
        print("4. Adjust Pricing")
        print("5. Display Revenue")
        print("6. Exit Application")
        print("=" * 50)

    def _handle_inventory_view(self):
        """Display current inventory"""
        print("\n" + "-" * 50)
        print("CURRENT INVENTORY".center(50))
        print("-" * 50)

        for flavor, quantity in self._flavors.items():
            status = "LOW STOCK" if quantity < 50 else "OK"
            print(f"{flavor:<25} {quantity:>5} scoops [{status}]")

        print("-" * 50)

    def _handle_sales_view(self):
        """Display sales statistics"""
        print("\n" + "-" * 50)
        print("SALES STATISTICS".center(50))
        print("-" * 50)

        if not self._sales_data:
            print("No sales recorded yet.")
        else:
            for flavor, count in self._sales_data.items():
                print(f"{flavor:<25} {count:>5} units")

        print("-" * 50)

    def _handle_transaction(self):
        """Process a sale transaction"""
        print("\n--- NEW TRANSACTION ---")

        flavor_list = list(self._flavors.keys())
        print("\nAvailable Flavors:")
        for idx, flavor in enumerate(flavor_list, 1):
            stock = self._flavors[flavor]
            print(f"  {idx}. {flavor} (Stock: {stock})")

        try:
            flavor_idx = int(input("\nSelect flavor number: ")) - 1

            if flavor_idx < 0 or flavor_idx >= len(flavor_list):
                print("[ERROR] Invalid flavor selection")
                return

            selected_flavor = flavor_list[flavor_idx]

            if self._flavors[selected_flavor] <= 0:
                print(f"[ERROR] {selected_flavor} is out of stock!")
                return

            print("\nAvailable Sizes:")
            size_list = list(self._price_chart.keys())
            for idx, size in enumerate(size_list, 1):
                price = self._price_chart[size]
                print(f"  {idx}. {size.title()} - ${price:.2f}")

            size_idx = int(input("\nSelect size number: ")) - 1

            if size_idx < 0 or size_idx >= len(size_list):
                print("[ERROR] Invalid size selection")
                return

            selected_size = size_list[size_idx]
            price = self._price_chart[selected_size]

            self._flavors[selected_flavor] -= 1
            self._sales_data[selected_flavor] += 1
            self._total_revenue += price

            print(f"\n[SUCCESS] Transaction complete!")
            print(f"  Product: {selected_flavor} ({selected_size})")
            print(f"  Price: ${price:.2f}")

        except ValueError:
            print("[ERROR] Invalid input format")
        except Exception as e:
            print(f"[ERROR] Transaction failed: {e}")

    def _handle_price_adjustment(self):
        """Adjust pricing for sizes"""
        print("\n--- PRICE ADJUSTMENT ---")
        print("\nCurrent Pricing:")

        size_list = list(self._price_chart.keys())
        for idx, size in enumerate(size_list, 1):
            price = self._price_chart[size]
            print(f"  {idx}. {size.title()}: ${price:.2f}")

        try:
            size_idx = int(input("\nSelect size to adjust: ")) - 1

            if size_idx < 0 or size_idx >= len(size_list):
                print("[ERROR] Invalid size selection")
                return

            selected_size = size_list[size_idx]
            new_price = float(input(f"Enter new price for {selected_size}: $"))

            if new_price < 0:
                print("[ERROR] Price cannot be negative")
                return

            self._price_chart[selected_size] = new_price
            print(f"[SUCCESS] Price for {selected_size} updated to ${new_price:.2f}")

        except ValueError:
            print("[ERROR] Invalid price format")

    def _handle_revenue_view(self):
        """Display total revenue"""
        print("\n" + "=" * 50)
        print(f"TOTAL REVENUE: ${self._total_revenue:.2f}".center(50))
        print("=" * 50)

    def _handle_exit(self):
        """Exit application"""
        print("\nThank you for using Ice Cream Inventory Manager!")
        print("Goodbye!")

if __name__ == "__main__":
    app = IceCreamInventory()
    app.run_application()
