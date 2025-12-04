# Very minimal implementation
# Just getting the job done

def main():
    inv = {'v':50, 'c':50, 's':50, 'm':50}
    sld = {'v':0, 'c':0, 's':0, 'm':0}
    prc = [3, 4.5, 6]
    ttl = 0

    while 1:
        print("\n1-inv 2-sales 3-sell 4-price 5-$ 0-exit")
        x = input(">")

        if x=='1':
            for k in inv:
                print(k, inv[k])
        elif x=='2':
            for k in sld:
                print(k, sld[k])
        elif x=='3':
            f = input("flavor(v/c/s/m):")
            if inv[f]>0:
                sz = int(input("size(0/1/2):"))
                inv[f]-=1
                sld[f]+=1
                ttl+=prc[sz]
                print("ok")
            else:
                print("no stock")
        elif x=='4':
            sz = int(input("size(0/1/2):"))
            p = float(input("price:"))
            prc[sz]=p
        elif x=='5':
            print("$",ttl)
        elif x=='0':
            break

main()
