"""
Ice cream shop - using lists and indices
Beginner friendly approach
"""

flavors = []
stock = []
sold = []

prices = []
price_names = []

total = 0

def setup():
    global flavors, stock, sold, prices, price_names, total

    flavors = ["vanilla", "chocolate", "strawberry", "lemon"]
    stock = [40, 50, 35, 30]
    sold = [0, 0, 0, 0]

    price_names = ["small", "medium", "large"]
    prices = [3.0, 4.5, 6.0]

    total = 0

def menu():
    print("\n### ICE CREAM SHOP ###")
    print("1 - view stock")
    print("2 - view sales")
    print("3 - sell")
    print("4 - prices")
    print("5 - total")
    print("0 - exit")

def view_stock():
    print("\nSTOCK:")
    for i in range(len(flavors)):
        print(flavors[i] + ": " + str(stock[i]))

def view_sales():
    print("\nSALES:")
    for i in range(len(flavors)):
        print(flavors[i] + ": " + str(sold[i]))

def sell():
    global total

    print("\nFLAVORS:")
    for i in range(len(flavors)):
        print(str(i+1) + " - " + flavors[i] + " (" + str(stock[i]) + ")")

    f = int(input("pick: "))
    f = f - 1

    if f < 0 or f >= len(flavors):
        print("wrong number")
        return

    if stock[f] <= 0:
        print("out of stock")
        return

    print("\nSIZES:")
    for i in range(len(price_names)):
        print(str(i+1) + " - " + price_names[i] + " $" + str(prices[i]))

    s = int(input("pick: "))
    s = s - 1

    if s < 0 or s >= len(prices):
        print("wrong number")
        return

    stock[f] = stock[f] - 1
    sold[f] = sold[f] + 1
    total = total + prices[s]

    print("sold!")

def change_prices():
    print("\nCURRENT PRICES:")
    for i in range(len(price_names)):
        print(str(i+1) + " - " + price_names[i] + " $" + str(prices[i]))

    s = int(input("change: "))
    s = s - 1

    if s < 0 or s >= len(prices):
        print("wrong number")
        return

    p = float(input("new price: "))
    prices[s] = p
    print("done")

def show_total():
    print("\nTOTAL: $" + str(total))

setup()

while True:
    menu()
    c = input("> ")

    if c == "1":
        view_stock()
    elif c == "2":
        view_sales()
    elif c == "3":
        sell()
    elif c == "4":
        change_prices()
    elif c == "5":
        show_total()
    elif c == "0":
        print("bye")
        break
    else:
        print("?")
