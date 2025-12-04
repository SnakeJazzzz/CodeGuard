"""
Ice Cream Shop Inventory Manager
Student 2 - Functional Programming Approach
"""

from functools import reduce

# Initial state
def create_initial_state():
    return {
        'stock': {
            'Vanilla': 100,
            'Chocolate': 100,
            'Strawberry': 75,
            'Pistachio': 60,
            'Mango': 80
        },
        'sales': {
            'Vanilla': 0,
            'Chocolate': 0,
            'Strawberry': 0,
            'Pistachio': 0,
            'Mango': 0
        },
        'pricing': {
            'S': 2.99,
            'M': 4.49,
            'L': 5.99,
            'XL': 7.49
        },
        'revenue': 0.0
    }

def show_main_menu():
    menu_options = [
        "Ice Cream Inventory System",
        "1 - Show Stock",
        "2 - Show Sales Report",
        "3 - Process Sale",
        "4 - Update Pricing",
        "5 - Revenue Summary",
        "0 - Exit System"
    ]
    print("\n" + "=" * 40)
    for option in menu_options:
        print(option)
    print("=" * 40)

def display_stock(state):
    print("\n** CURRENT STOCK **")
    for flavor, qty in state['stock'].items():
        print(f"  {flavor}: {qty} units")
    return state

def display_sales(state):
    print("\n** SALES REPORT **")
    total_units = reduce(lambda acc, x: acc + x, state['sales'].values(), 0)
    for flavor, qty in state['sales'].items():
        print(f"  {flavor}: {qty} units sold")
    print(f"\nTotal Units Sold: {total_units}")
    return state

def display_revenue(state):
    print(f"\n** TOTAL REVENUE: ${state['revenue']:.2f} **")
    return state

def process_sale(state):
    print("\n-- Process New Sale --")
    flavors = list(state['stock'].keys())

    for idx, flavor in enumerate(flavors):
        print(f"{idx + 1}. {flavor} (Stock: {state['stock'][flavor]})")

    try:
        flavor_idx = int(input("\nSelect flavor number: ")) - 1
        if flavor_idx < 0 or flavor_idx >= len(flavors):
            print("Invalid selection")
            return state

        selected_flavor = flavors[flavor_idx]

        if state['stock'][selected_flavor] <= 0:
            print(f"Sorry, {selected_flavor} is out of stock!")
            return state

        print("\nSize Options:")
        sizes = list(state['pricing'].keys())
        for size in sizes:
            print(f"  {size} - ${state['pricing'][size]:.2f}")

        size_input = input("\nEnter size: ").upper()
        if size_input not in state['pricing']:
            print("Invalid size")
            return state

        # Update state
        new_state = state.copy()
        new_state['stock'] = state['stock'].copy()
        new_state['sales'] = state['sales'].copy()

        new_state['stock'][selected_flavor] -= 1
        new_state['sales'][selected_flavor] += 1
        new_state['revenue'] += state['pricing'][size_input]

        print(f"\nSale completed! {selected_flavor} ({size_input}) - ${state['pricing'][size_input]:.2f}")
        return new_state

    except (ValueError, IndexError):
        print("Invalid input")
        return state

def update_pricing(state):
    print("\n-- Update Pricing --")
    print("Current Prices:")
    for size, price in state['pricing'].items():
        print(f"  {size}: ${price:.2f}")

    try:
        size = input("\nEnter size to update: ").upper()
        if size not in state['pricing']:
            print("Invalid size")
            return state

        new_price = float(input(f"Enter new price for {size}: $"))

        new_state = state.copy()
        new_state['pricing'] = state['pricing'].copy()
        new_state['pricing'][size] = new_price

        print(f"Price updated: {size} is now ${new_price:.2f}")
        return new_state

    except ValueError:
        print("Invalid price format")
        return state

def main_loop(state):
    while True:
        show_main_menu()
        choice = input("\nYour choice: ").strip()

        if choice == '1':
            state = display_stock(state)
        elif choice == '2':
            state = display_sales(state)
        elif choice == '3':
            state = process_sale(state)
        elif choice == '4':
            state = update_pricing(state)
        elif choice == '5':
            state = display_revenue(state)
        elif choice == '0':
            print("\nClosing shop... Goodbye!")
            break
        else:
            print("Invalid option. Try again.")

    return state

if __name__ == "__main__":
    initial_state = create_initial_state()
    final_state = main_loop(initial_state)
