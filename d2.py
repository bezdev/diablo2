import os
import sqlite3
import sys
import msvcrt

def MainMenu(showOptions):
    if (showOptions):
        Clear()
        print("Diablo 2 bez")
        print("")
        print("[s]earch")
        print("[g]rail")
        print("E[x]it")
        print("")

    input = msvcrt.getch().decode("utf-8", "ignore")
    if (input.upper() == "S"):
        Search(True)
    elif (input.upper() == "G"):
        Grail()
    elif (input.upper() == "X"):
        exit()

    MainMenu(False)

def Search(clear):
    if (clear):
        Clear()
    print("")
    item = input("Search> ")
    if (len(item) == 0):
        MainMenu(True)

    items = SearchItems(item)
    # for item in items:
    #     print(item)
    PrintItems(items)

    i = 0
    while True:
        try:
            i = input("> ")
            if (i.upper() == "X"):
                MainMenu(True)
            i = int(i)
            break
        except ValueError:
            continue

    i -= 1

    if (len(items) > 0):
        PrintItem(items[i])

    i = msvcrt.getch().decode("utf-8", "ignore")
    Search(False)

def Grail():
    # Clear()
    # print("Grail")
    # print("")
    # print("[p]rint")
    # print("[s]tats")
    # print("")

    # input = msvcrt.getch().decode("utf-8", "ignore")
    # if (input.upper() == "P"):
    #     PrintGrail()
    # elif (input.upper() == "S"):
    #     PrintGrailStats()

    print("")
    print("  GRAIL")
    print("")

    PrintGrailStats()

    input = msvcrt.getch().decode("utf-8", "ignore")
    MainMenu(True)

def SearchItems(item):
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()

    c.execute('''PRAGMA case_sensitive_like = off''')
    c.execute('''SELECT *
                 FROM item
                 WHERE item.name like ?
                    OR item.itemType like ?''', ("%" + item + "%", "%" + item + "%"))
    items = c.fetchall()

    conn.close()

    return items

def PrintItems(items):
    print("")
    i = 1
    for item in items:
        itemClassType = ""
        if (item[4] != None):
            if (item[4][-1] == "s"):
                itemClassType = item[4][:-1]
            else:
                itemClassType = item[4]
        if (itemClassType != ""):
            itemClassType = " (" + itemClassType + ")"

        print("  " + str(i) + ") " + item[1] + " - " + item[3] + itemClassType)

        i += 1
        # print(item[4])
        # for field in item:
        #     print(str(field), end = '')
    print("")

def PrintItem(item):
    itemClassType = ""
    if (item[4] != None):
        if (item[4][-1] == "s"):
            itemClassType = item[4][:-1]
        else:
            itemClassType = item[4]
    if (itemClassType != ""):
        itemClassType = " (" + itemClassType + ")"

    print("")
    print("  " + item[1] + " - " + item[3] + itemClassType)
    print("")
    print("  " + item[5].replace("\n", "\n  "))

    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    c.execute('''select * from grail where item = ?''', (item[0], ))
    grail = c.fetchall()[0]

    conn.close()

    print("")
    print("  GRAIL:")
    if (grail[2] == 0 and grail[3] == 0):
        print("  NOT FOUND")
        return

    if (grail[3] > 0):
        print ("  FOUND ETH")
    elif (grail[2] > 0):
        print("  FOUND")
    else:
        print("  NOT FOUND")

    if (grail[4].strip() == ""):
        return

    print("")
    print("  Details:")
    print("  " + grail[4].strip())
    print("")

def PrintGrail():
    os.system('cls' if os.name == 'nt' else 'clear')

    conn = sqlite3.connect(dbFile)
    c = conn.cursor()

    c.execute('''PRAGMA case_sensitive_like = off''')
    c.execute('''SELECT name, itemType, itemClass
                 FROM item
                 WHERE type = ?
                 ORDER BY itemClass''', ("Unique", ))

    print("\nUnique\n")
    currentItemClass = None
    rows = c.fetchall()
    for row in rows:
        if (currentItemClass != row[2]):
            currentItemClass = row[2]
            print("")
            print(currentItemClass)
            print("")

        print(row[0])

    c.execute('''PRAGMA case_sensitive_like = off''')
    c.execute('''SELECT name, itemType, itemClass
                 FROM item
                 WHERE type = ?
                 ORDER BY itemClass''', ("Set", ))

    print("\nSets\n")
    currentItemClass = None
    rows = c.fetchall()
    for row in rows:
        if (currentItemClass != row[2]):
            currentItemClass = row[2]
            print("")
            print(currentItemClass)
            print("")

        print(row[0])

    c.execute('''PRAGMA case_sensitive_like = off''')
    c.execute('''SELECT name, itemType, itemClass
                 FROM item
                 WHERE type = ?
                 ORDER BY itemClass''', ("Runeword", ))

    print("\nRuneword\n")
    rows = c.fetchall()
    for row in rows:
        print(row[0])

    c.execute('''PRAGMA case_sensitive_like = off''')
    c.execute('''SELECT name, itemType, itemClass
                 FROM item
                 WHERE type = ?
                 ORDER BY itemClass''', ("Rune", ))

    print("\nRune\n")
    rows = c.fetchall()
    for row in rows:
        print(row[0])


    conn.close()

def PrintGrailStats():
    scriptPath = os.path.dirname(__file__)
    f = open(os.path.join(scriptPath, "data\\grail.csv"), "r")

    conn = sqlite3.connect(dbFile)

    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS grail (id integer PRIMARY KEY, item integer NOT NULL, found integer NOT NULL, foundEth integer NOT NULL, notes text, FOREIGN KEY (item) REFERENCES item (id))''')
    c.execute('''DELETE FROM grail''')

    for line in f:
        line = line.strip()
        fullline = line
        if (line == "" or line == ",,,,"):
            #print(fullline)
            continue

        items = line.split(",")
        if (len(items) != 5):
            #print(fullline)
            continue

        c.execute('''PRAGMA case_sensitive_like = off''')
        c.execute('''SELECT *
                     FROM item
                     WHERE item.id = ?''', (items[0],))

        foundItem = c.fetchall()

        if (foundItem == []):
            #print(fullline)
            continue

        found = 0
        try:
            found = int(items[2])
        except ValueError:
            found = 0

        foundEth = 0
        try:
            foundEth = int(items[3])
        except ValueError:
            foundEth = 0

        c.execute('''INSERT INTO grail(item, found, foundEth, notes) VALUES(?,?,?,?)''', (int(foundItem[0][0]), found, foundEth, items[4]))
        #print(str(foundItem[0][0]) + "," + foundItem[0][1] + "," + str(found) + "," + str(foundEth) + "," + items[3])

    conn.commit()

    c.execute('''PRAGMA case_sensitive_like = off''')
    c.execute('''SELECT *
                 FROM grail''')

    c.execute('''select count(id) from item where type = "Unique"''')
    numUniques = c.fetchall()[0][0]
    c.execute('''select count(id) from item where type = "Set"''')
    numSets = c.fetchall()[0][0]
    c.execute('''select count(id) from item where type = "Rune"''')
    numRunes = c.fetchall()[0][0]
    c.execute('''select count(id) from item where type = "Runeword"''')
    numRunewords = c.fetchall()[0][0]

    c.execute('''select * from grail join item on item.id = grail.item where item.type = "Unique" and (grail.found == 0 and grail.foundEth == 0) order by item.itemClass''')
    uniquesNotFound = c.fetchall()
    c.execute('''select * from grail join item on item.id = grail.item where item.type = "Set" and (grail.found == 0 and grail.foundEth == 0) order by item.itemClass''')
    setsNotFound = c.fetchall()
    c.execute('''select * from grail join item on item.id = grail.item where item.type = "Rune" and (grail.found == 0 and grail.foundEth == 0) order by item.itemClass''')
    runesNotFound = c.fetchall()
    c.execute('''select * from grail join item on item.id = grail.item where item.type = "Runeword" and (grail.found == 0 and grail.foundEth == 0) order by item.itemClass''')
    runewordsNotFound = c.fetchall()

    print("  Uniques:")
    for row in uniquesNotFound:
        print("    " + str(row[6]) + " - " + str(row[8]))
    print("")
    print("  Sets:")
    for row in setsNotFound:
        print("    " + str(row[6]) + " - " + str(row[8]))
    print("")
    print("  Runes:")
    for row in runesNotFound:
        print("    " + str(row[6]) + " - " + str(row[8]))
    print("")
    # print("  Runewords:")
    # for row in runewordsNotFound:
    #     print("    " + str(row[6]) + " - " + str(row[8]))
    # print("")

    uniquesFound = numUniques - len(uniquesNotFound)
    setsFound = numSets - len(setsNotFound)
    runesFound = numRunes - len(runesNotFound)
    runewordsFound = numRunewords - len(runewordsNotFound)
    totalFound = uniquesFound + setsFound + runesFound # + runewordsFound
    total = numUniques + numSets + numRunes # + numRunewords
    print("  Uniques: " + str(uniquesFound) + "/" + str(numUniques))
    print("  Sets: " + str(setsFound) + "/" + str(numSets))
    print("  Runes: " + str(runesFound) + "/" + str(numRunes))
    print("  Runewords: " + str(runewordsFound) + "/" + str(numRunewords))
    print("")
    print("  TOTAL: " + str(totalFound) + "/" + str(total) + " (" + str(total - totalFound) + " remaining)")

    conn.close()

def Clear():
    os.system('cls' if os.name == 'nt' else 'clear')

dbFile = "diablo2.db"

def main():
    Clear()
    print("diablo 2 bez")

    scriptPath = os.path.dirname(__file__)

    global dbFile
    dbFile = os.path.join(scriptPath, dbFile)
    if not os.path.exists(dbFile):
        return

    MainMenu(True)

if __name__ == "__main__":
    main()
