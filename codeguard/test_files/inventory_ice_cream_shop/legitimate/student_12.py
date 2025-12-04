# Ice cream shop with nested classes and inner functions
# Trying out some advanced Python features

class IceCreamBusiness:

    class Flavor:
        def __init__(self, name, initial_stock):
            self.name = name
            self.stock = initial_stock
            self.units_sold = 0

        def sell_unit(self):
            if self.stock > 0:
                self.stock -= 1
                self.units_sold += 1
                return True
            return False

        def get_info(self):
            return f"{self.name}: {self.stock} in stock, {self.units_sold} sold"

    class PricingTier:
        def __init__(self, tier_name, price):
            self.tier_name = tier_name
            self.price = price

        def update_price(self, new_price):
            self.price = new_price

        def __str__(self):
            return f"{self.tier_name}: ${self.price:.2f}"

    def __init__(self):
        self.flavors = [
            self.Flavor("Vanilla", 88),
            self.Flavor("Chocolate", 92),
            self.Flavor("Strawberry", 76),
            self.Flavor("Mint Chocolate Chip", 64),
            self.Flavor("Cookie Dough", 58)
        ]

        self.pricing = [
            self.PricingTier("Junior", 2.50),
            self.PricingTier("Standard", 4.00),
            self.PricingTier("Premium", 5.50),
            self.PricingTier("Family", 9.00)
        ]

        self.register = 0.0

    def display_options(self):
        def header():
            print("\n" + "*" * 40)
            print("*" + " " * 38 + "*")
            print("*" + "   ICE CREAM SHOP MANAGEMENT   ".center(38) + "*")
            print("*" + " " * 38 + "*")
            print("*" * 40)

        def options():
            print("\nOptions:")
            print("  [I] Inventory")
            print("  [S] Sales Report")
            print("  [T] Transaction")
            print("  [P] Pricing")
            print("  [R] Register")
            print("  [Q] Quit")

        header()
        options()

    def show_inventory(self):
        print("\n--- INVENTORY ---")
        for flavor in self.flavors:
            print(f"  {flavor.get_info()}")

    def show_sales(self):
        print("\n--- SALES REPORT ---")

        def calculate_total():
            return sum(f.units_sold for f in self.flavors)

        for flavor in self.flavors:
            print(f"  {flavor.name}: {flavor.units_sold}")

        print(f"\nTotal units sold: {calculate_total()}")

    def make_transaction(self):
        print("\n--- NEW TRANSACTION ---")

        def select_flavor():
            print("\nFlavors:")
            for i, flavor in enumerate(self.flavors, 1):
                print(f"  {i}. {flavor.name} ({flavor.stock} available)")

            try:
                choice = int(input("Select: ")) - 1
                if 0 <= choice < len(self.flavors):
                    return self.flavors[choice]
            except ValueError:
                pass

            return None

        def select_pricing():
            print("\nSizes:")
            for i, tier in enumerate(self.pricing, 1):
                print(f"  {i}. {tier}")

            try:
                choice = int(input("Select: ")) - 1
                if 0 <= choice < len(self.pricing):
                    return self.pricing[choice]
            except ValueError:
                pass

            return None

        flavor = select_flavor()
        if flavor is None:
            print("Invalid flavor!")
            return

        if not flavor.sell_unit():
            print("Out of stock!")
            return

        tier = select_pricing()
        if tier is None:
            print("Invalid size!")
            flavor.stock += 1  # refund
            flavor.units_sold -= 1
            return

        self.register += tier.price
        print(f"\nSuccess! {flavor.name} ({tier.tier_name}) - ${tier.price:.2f}")

    def modify_pricing(self):
        print("\n--- MODIFY PRICING ---")
        print("\nCurrent pricing:")

        for i, tier in enumerate(self.pricing, 1):
            print(f"  {i}. {tier}")

        try:
            choice = int(input("\nModify which? ")) - 1
            if 0 <= choice < len(self.pricing):
                new_price = float(input("New price: $"))
                self.pricing[choice].update_price(new_price)
                print("Updated!")
            else:
                print("Invalid!")
        except ValueError:
            print("Invalid input!")

    def show_register(self):
        print(f"\n--- REGISTER: ${self.register:.2f} ---")

    def operate(self):
        active = True

        while active:
            self.display_options()
            command = input("\nCommand: ").upper().strip()

            if command == 'I':
                self.show_inventory()
            elif command == 'S':
                self.show_sales()
            elif command == 'T':
                self.make_transaction()
            elif command == 'P':
                self.modify_pricing()
            elif command == 'R':
                self.show_register()
            elif command == 'Q':
                print("\nClosing shop. Goodbye!")
                active = False
            else:
                print("Unknown command!")

def main():
    business = IceCreamBusiness()
    business.operate()

if __name__ == "__main__":
    main()
