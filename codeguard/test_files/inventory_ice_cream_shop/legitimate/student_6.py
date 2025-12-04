#!/usr/bin/env python3
# Procedural approach - Simple and straightforward

inventory = {'vanilla': 45, 'chocolate': 60, 'strawberry': 30, 'lemon': 40}
sold = {'vanilla': 0, 'chocolate': 0, 'strawberry': 0, 'lemon': 0}
prices = {'s': 3.0, 'm': 4.5, 'l': 6.0}
total_money = 0

def print_menu():
    print("\n*** ICE CREAM SHOP ***")
    print("1) Show inventory")
    print("2) Show sales")
    print("3) Make a sale")
    print("4) Change prices")
    print("5) Show total money")
    print("0) Quit")

def show_inventory():
    print("\nCurrent inventory:")
    for flavor in inventory:
        print(f"  {flavor}: {inventory[flavor]}")

def show_sales():
    print("\nSales so far:")
    for flavor in sold:
        print(f"  {flavor}: {sold[flavor]}")

def make_sale():
    global total_money
    print("\nFlavors available:")
    flavors = list(inventory.keys())
    for i in range(len(flavors)):
        print(f"{i+1}. {flavors[i]}")

    choice = int(input("Pick flavor: "))
    flavor = flavors[choice-1]

    if inventory[flavor] == 0:
        print("Sorry, out of stock")
        return

    print("Sizes: s/m/l")
    size = input("Size: ")

    inventory[flavor] = inventory[flavor] - 1
    sold[flavor] = sold[flavor] + 1
    total_money = total_money + prices[size]
    print(f"Sold! Price: ${prices[size]}")

def change_prices():
    print("\nCurrent prices:")
    print(f"s: ${prices['s']}")
    print(f"m: ${prices['m']}")
    print(f"l: ${prices['l']}")

    size = input("Which size? ")
    new_price = float(input("New price: "))
    prices[size] = new_price
    print("Updated!")

def show_money():
    print(f"\nTotal money earned: ${total_money}")

while True:
    print_menu()
    option = input("\nChoice: ")

    if option == '1':
        show_inventory()
    elif option == '2':
        show_sales()
    elif option == '3':
        make_sale()
    elif option == '4':
        change_prices()
    elif option == '5':
        show_money()
    elif option == '0':
        print("Bye!")
        break
