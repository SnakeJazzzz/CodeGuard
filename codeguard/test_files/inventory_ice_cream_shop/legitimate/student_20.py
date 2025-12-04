"""
Ice Cream Shop - Using global state and simple functions
Quick and dirty but it works!
"""

# Global variables - easy to access everywhere
stock_vanilla = 70
stock_choc = 65
stock_straw = 55
stock_mint = 50

sold_vanilla = 0
sold_choc = 0
sold_straw = 0
sold_mint = 0

price_small = 3.25
price_med = 4.75
price_large = 6.25

money = 0.0

def show_menu():
    print("\n### MENU ###")
    print("1 = inventory")
    print("2 = sales")
    print("3 = sell")
    print("4 = prices")
    print("5 = money")
    print("q = quit")

def show_inv():
    global stock_vanilla, stock_choc, stock_straw, stock_mint
    print("\nINVENTORY:")
    print(f"  vanilla: {stock_vanilla}")
    print(f"  chocolate: {stock_choc}")
    print(f"  strawberry: {stock_straw}")
    print(f"  mint: {stock_mint}")

def show_sales():
    global sold_vanilla, sold_choc, sold_straw, sold_mint
    print("\nSALES:")
    print(f"  vanilla: {sold_vanilla}")
    print(f"  chocolate: {sold_choc}")
    print(f"  strawberry: {sold_straw}")
    print(f"  mint: {sold_mint}")
    total = sold_vanilla + sold_choc + sold_straw + sold_mint
    print(f"TOTAL: {total}")

def sell():
    global stock_vanilla, stock_choc, stock_straw, stock_mint
    global sold_vanilla, sold_choc, sold_straw, sold_mint
    global price_small, price_med, price_large, money

    print("\nFLAVORS:")
    print("1 = vanilla")
    print("2 = chocolate")
    print("3 = strawberry")
    print("4 = mint")

    flav = input("? ")

    # Check stock and sell
    if flav == "1":
        if stock_vanilla > 0:
            stock_vanilla -= 1
            sold_vanilla += 1
        else:
            print("OUT!")
            return
    elif flav == "2":
        if stock_choc > 0:
            stock_choc -= 1
            sold_choc += 1
        else:
            print("OUT!")
            return
    elif flav == "3":
        if stock_straw > 0:
            stock_straw -= 1
            sold_straw += 1
        else:
            print("OUT!")
            return
    elif flav == "4":
        if stock_mint > 0:
            stock_mint -= 1
            sold_mint += 1
        else:
            print("OUT!")
            return
    else:
        print("BAD INPUT")
        return

    # Size
    print("\nSIZES:")
    print(f"1 = small ${price_small}")
    print(f"2 = medium ${price_med}")
    print(f"3 = large ${price_large}")

    sz = input("? ")

    if sz == "1":
        money += price_small
        print(f"SOLD ${price_small}")
    elif sz == "2":
        money += price_med
        print(f"SOLD ${price_med}")
    elif sz == "3":
        money += price_large
        print(f"SOLD ${price_large}")
    else:
        print("BAD SIZE")

def change_prices():
    global price_small, price_med, price_large

    print("\nCURRENT:")
    print(f"1 = small ${price_small}")
    print(f"2 = medium ${price_med}")
    print(f"3 = large ${price_large}")

    sz = input("change? ")
    p = float(input("new price? "))

    if sz == "1":
        price_small = p
    elif sz == "2":
        price_med = p
    elif sz == "3":
        price_large = p

    print("CHANGED")

def show_money():
    global money
    print(f"\nMONEY: ${money:.2f}")

# Main loop
while True:
    show_menu()
    cmd = input("> ")

    if cmd == "1":
        show_inv()
    elif cmd == "2":
        show_sales()
    elif cmd == "3":
        sell()
    elif cmd == "4":
        change_prices()
    elif cmd == "5":
        show_money()
    elif cmd == "q":
        print("BYE")
        break
    else:
        print("HUH?")
