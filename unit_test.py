import main


maxg = int(input("max generation : "))
f = float(input("desired fitness : "))
n = int(input("number of tests : "))

win = 0

for i in range(n):
    win += int(main.Game(None, maxg, True).result >= f)

print("success rate : {} %".format(100 * win/n))
