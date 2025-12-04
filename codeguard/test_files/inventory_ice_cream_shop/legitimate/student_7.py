"""
Ice cream shop using data classes and type hints
Modern Python approach
"""

from dataclasses import dataclass, field
from typing import Dict
from enum import Enum

class Size(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    XLARGE = "xlarge"

@dataclass
class Product:
    name: str
    quantity: int
    sold: int = 0

@dataclass
class PriceList:
    prices: Dict[Size, float] = field(default_factory=dict)

    def __post_init__(self):
        if not self.prices:
            self.prices = {
                Size.SMALL: 3.25,
                Size.MEDIUM: 4.75,
                Size.LARGE: 6.00,
                Size.XLARGE: 7.50
            }

@dataclass
class Shop:
    products: Dict[str, Product] = field(default_factory=dict)
    price_list: PriceList = field(default_factory=PriceList)
    revenue: float = 0.0

    def __post_init__(self):
        if not self.products:
            self.products = {
                'vanilla': Product('Vanilla', 80),
                'chocolate': Product('Chocolate', 70),
                'strawberry': Product('Strawberry', 60),
                'caramel': Product('Caramel', 55),
                'coconut': Product('Coconut', 45)
            }

    def display_inventory(self) -> None:
        print("\n=== INVENTORY ===")
        for key, product in self.products.items():
            print(f"{product.name}: {product.quantity} remaining")

    def display_sales(self) -> None:
        print("\n=== SALES ===")
        for key, product in self.products.items():
            print(f"{product.name}: {product.sold} sold")

    def display_revenue(self) -> None:
        print(f"\n=== REVENUE: ${self.revenue:.2f} ===")

    def sell_product(self) -> None:
        print("\n--- MAKE SALE ---")

        print("Products:")
        product_keys = list(self.products.keys())
        for idx, key in enumerate(product_keys, 1):
            print(f"{idx}. {self.products[key].name} ({self.products[key].quantity} left)")

        try:
            prod_choice = int(input("Product #: ")) - 1
            product_key = product_keys[prod_choice]
            product = self.products[product_key]

            if product.quantity <= 0:
                print("OUT OF STOCK!")
                return

            print("\nSizes:")
            sizes = list(Size)
            for idx, size in enumerate(sizes, 1):
                price = self.price_list.prices[size]
                print(f"{idx}. {size.value} - ${price:.2f}")

            size_choice = int(input("Size #: ")) - 1
            chosen_size = sizes[size_choice]

            product.quantity -= 1
            product.sold += 1
            sale_amount = self.price_list.prices[chosen_size]
            self.revenue += sale_amount

            print(f"\n✓ Sold {product.name} ({chosen_size.value}) for ${sale_amount:.2f}")

        except (ValueError, IndexError, KeyError):
            print("Invalid input!")

    def update_prices(self) -> None:
        print("\n--- UPDATE PRICES ---")
        print("Current prices:")
        for size, price in self.price_list.prices.items():
            print(f"  {size.value}: ${price:.2f}")

        print("\nSizes:")
        sizes = list(Size)
        for idx, size in enumerate(sizes, 1):
            print(f"{idx}. {size.value}")

        try:
            size_choice = int(input("Which size? ")) - 1
            chosen_size = sizes[size_choice]
            new_price = float(input(f"New price for {chosen_size.value}: $"))

            self.price_list.prices[chosen_size] = new_price
            print("Price updated!")

        except (ValueError, IndexError):
            print("Invalid input!")

def main():
    shop = Shop()

    while True:
        print("\n" + "="*30)
        print("ICE CREAM SHOP MANAGER")
        print("="*30)
        print("[1] View Inventory")
        print("[2] View Sales")
        print("[3] Sell Ice Cream")
        print("[4] Update Prices")
        print("[5] View Revenue")
        print("[0] Exit")

        choice = input("\n> ")

        if choice == '1':
            shop.display_inventory()
        elif choice == '2':
            shop.display_sales()
        elif choice == '3':
            shop.sell_product()
        elif choice == '4':
            shop.update_prices()
        elif choice == '5':
            shop.display_revenue()
        elif choice == '0':
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
