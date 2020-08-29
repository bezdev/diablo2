import os
import sqlite3
import sys

class Item:
    def __init__(self, type, name, itemType, itemClassType):
        self.type = type.strip().replace("*", "")
        self.name = name.strip().replace("*", "")
        self.itemType = itemType.strip().replace("*", "")
        self.itemClassType = itemClassType.split(":")[0].strip()
        self.info = ""

    def __str__(self):
        toString = "--startitem--\n"
        toString += self.type + "," + self.name + "," + self.classType + "\n"
        toString += self.info + "\n"
        toString += "--enditem--\n"

        return toString

class Set:
    def __init__(self, name):
        self.name = name.strip()
        self.bonus = ""
        self.items = []

    def __str__(self):
        toString = "--startset--\n"
        toString += self.name + "\n"
        toString += self.bonus

        for item in self.items:
            toString += str(item)

        toString += "--endset--\n"
        return toString

class Rune:
    def __init__(self, name, weaponEffect, armorEffect, shieldEffect, level):
        self.name = name.strip()
        self.weaponEffect = weaponEffect.strip()
        self.armorEffect = armorEffect.strip()
        self.shieldEffect = shieldEffect.strip()
        self.level = level.strip()

    def __str__(self):
        return self.name + "|" + self.weaponEffect + "|" + self.armorEffect + "|" + self.shieldEffect + "|" + self.level

class Runeword:
    def __init__(self, name, numSockets, itemTypes, runes):
        self.name = name.strip().replace("*", "")
        self.numSockets = numSockets
        self.itemTypes = itemTypes
        self.runes = runes
        self.effects = ""

    def addEffect(self, effect):
        self.effects += effect.strip() + "\n"

    def __str__(self):
        toString = self.name + ": " + self.numSockets + " Sockets "
        toString += "(" + ",".join(self.itemTypes) + ") "
        toString += "[" + ",".join(self.runes) + "]\n"
        for effect in self.effects:
            toString += "  " + effect

        return toString

def parseRunes(filePath):
    runes = []
    f = open(filePath, "r")
    for line in f:
        splitLine = line.split("|")
        if (len(splitLine) == 4):
            r = Rune(splitLine[0], splitLine[1], splitLine[2], splitLine[2], splitLine[3])
        elif (len(splitLine) == 5):
            r = Rune(splitLine[0], splitLine[1], splitLine[2], splitLine[3], splitLine[4])
        else:
            raise ValueError

        runes.append(r)
    f.close()

    return runes

def parseRunewords(filePath):
    runewords = []
    currentRuneword = None
    f = open(filePath, "r")
    for line in f:
        splitLine = line.split(",")
        if (splitLine[0] != ''):
            if currentRuneword != None:
                runewords.append(currentRuneword)
                #print(currentRuneword)

            splitItem = splitLine[1].split(" Socket ")

            currentRuneword = Runeword(splitLine[0], splitItem[0], splitItem[1].split("/"), splitLine[2].split(" + "))
            currentRuneword.addEffect(splitLine[3])
        else:
            currentRuneword.addEffect(splitLine[3])
    f.close()

    return runewords

def parseUniques(filePath):
    items = []
    currentItem = None

    isItemMeta = False
    isItemDetail = False

    f = open(filePath, "r")
    for line in f:
        if (line.strip() == ""):
            continue

        if (line.startswith("--startitem--")):
            isItemMeta = True
            continue

        if (line.startswith("--enditem--")):
            isItemMeta = False
            isItemDetail = False
            items.append(currentItem)
            continue

        if (isItemDetail):
            currentItem.info += line.strip() + "\n"

        if (isItemMeta):
            split = line.split(",")
            currentItem = Item(split[0], split[1], split[2], split[3])
            isItemMeta = False
            isItemDetail = True
    f.close()

    return items

def parseSets(filePath):
    sets = []
    currentSet = None
    currentItem = None

    isSetMeta = False
    isSetBonus = False
    isItemMeta = False
    isItemDetail = False

    f = open(filePath, "r")
    for line in f:
        if (line.strip() == ""):
            continue

        if (line.startswith("--startset--")):
            isSetMeta = True
            continue

        if (line.startswith("--startitem--")):
            isSetBonus = False
            isItemMeta = True
            continue

        if (line.startswith("--enditem--")):
            isItemMeta = False
            isItemDetail = False
            currentSet.items.append(currentItem)
            continue

        if (line.startswith("--endset--")):
            isSetMeta = False
            isSetBonus = False
            isItemMeta = False
            isItemDetail = False
            sets.append(currentSet)
            continue

        if (isSetBonus):
            currentSet.bonus += line.strip() + "\n"

        if (isItemDetail):
            currentItem.info += line.strip() + "\n"

        if (isSetMeta):
            currentSet = Set(line)
            isSetMeta = False
            isSetBonus = True

        if (isItemMeta):
            split = line.split(",")
            currentItem = Item(split[0], split[1], split[2], currentSet.name)
            isItemMeta = False
            isItemDetail = True

    f.close()

    return sets

def main():
    print("diablo 2 data importer")

    scriptPath = os.path.dirname(__file__)

    print("parsing files...")

    print("parsing uniques...")
    uniques = parseUniques(os.path.join(scriptPath, "data\\uniques.txt"))

    print("parsing sets...")
    sets = parseSets(os.path.join(scriptPath, "data\\sets.txt"))

    print("parsing runes...")
    runes = parseRunes(os.path.join(scriptPath, "data\\runes.csv"))

    print("parsing runewords...")
    runewords = []
    runewords += parseRunewords(os.path.join(scriptPath, "data\\originalrw.csv"))
    runewords += parseRunewords(os.path.join(scriptPath, "data\\110rw.csv"))
    runewords += parseRunewords(os.path.join(scriptPath, "data\\111rw.csv"))

    print("creating db...")
    dbFile = os.path.join(scriptPath, "diablo2.db")
    if os.path.exists(dbFile):
        os.remove(dbFile)

    conn = sqlite3.connect(dbFile)
    c = conn.cursor()

    print("creating tables...")
    c.execute('''CREATE TABLE item (id integer PRIMARY KEY, name text NOT NULL, type text NOT NULL, itemType text, itemClass text, info text)''')
    c.execute('''CREATE TABLE setz (id integer PRIMARY KEY, name text NOT NULL, bonus text NOT NULL)''')
    c.execute('''CREATE TABLE setitem (id integer PRIMARY KEY, setz integer NOT NULL, item integer NOT NULL, FOREIGN KEY (setz) REFERENCES setz (id) FOREIGN KEY (item) REFERENCES item (id))''')
    c.execute('''CREATE TABLE runewordrunes (id integer PRIMARY KEY, runeword integer NOT NULL, rune integer NOT NULL, runeorder integer NOT NULL, FOREIGN KEY (runeword) REFERENCES item (id) FOREIGN KEY (rune) REFERENCES item (id))''')

    print("populating tables...")
    for unique in uniques:
        c.execute('''INSERT INTO item(name, type, itemType, itemClass, info) VALUES(?,?,?,?,?)''', (unique.name, unique.type, unique.itemType, unique.itemClassType, unique.info))

    for set in sets:
        c.execute('''INSERT INTO setz(name, bonus) VALUES(?,?)''', (set.name, set.bonus))
        setId = c.execute('''SELECT id FROM setz WHERE name=?''', (set.name,)).fetchall()[0][0]

        for item in set.items:
            c.execute('''INSERT INTO item(name, type, itemType, itemClass, info) VALUES(?,?,?,?,?)''', (item.name, item.type, item.itemType, item.itemClassType, item.info))
            itemId = c.execute('''SELECT id FROM item WHERE name=?''', (item.name,)).fetchall()[0][0]

            c.execute('''INSERT INTO setitem(setz, item) VALUES(?,?)''', (setId,itemId,))

    for rune in runes:
        info = "Required Level: " + str(rune.level) + "\nWeapons: " + rune.weaponEffect + "\nArmors: " + rune.armorEffect + "\nShields: " + rune.shieldEffect + "\n"
        c.execute('''INSERT INTO item(name, type, itemType, itemClass, info) VALUES(?,?,?,?,?)''', (rune.name, "Rune", "Rune", "Runes", info))

    for runeword in runewords:
        c.execute('''INSERT INTO item(name, type, itemType, itemClass, info) VALUES(?,?,?,?,?)''', (runeword.name, "Runeword", ",".join(runeword.itemTypes), "Runewords", runeword.effects))
        rwId = c.execute('''SELECT id FROM item WHERE name=? and type=? and itemType=?''', (runeword.name, "Runeword", ",".join(runeword.itemTypes))).fetchall()[0][0]

        runeorder = 1
        for rune in runeword.runes:
            runeId = c.execute('''SELECT id FROM item WHERE name=? and type="Rune"''', (rune,)).fetchall()[0][0]
            c.execute('''INSERT INTO runewordrunes(runeword, rune, runeorder) VALUES(?,?,?)''', (rwId, runeId, runeorder))
            runeorder += 1

    print("done.\n")

    print("results:")

    # UNIQUES
    c.execute('''SELECT item.name
                 FROM item
                 WHERE item.type = ?''', ("Unique",))

    rows = c.fetchall()
    print(str(len(rows)) + " uniques")

    # [sample] get info of item
    # itemName = "oculus"
    # c.execute('''PRAGMA case_sensitive_like = off''')
    # c.execute('''SELECT item.info
    #              FROM item
    #              WHERE item.name like ?''', ("%" + itemName + "%",))
    # print(c.fetchall()[0][0])

    # SETS
    c.execute('''SELECT item.name
                 FROM item
                 WHERE item.type = ?''', ("Set",))

    rows = c.fetchall()
    print(str(len(rows)) + " set item")

    # [sample] get set item and bonus
    # itemName = "Lidless Eye"
    # c.execute('''PRAGMA case_sensitive_like = off''')
    # c.execute('''SELECT item.name, item.info, setz.bonus
    #              FROM item
    #              JOIN setitem on setitem.item = item.id
    #              JOIN setz on setz.id = setitem.setz
    #              WHERE item.name like ?''', ("%" + itemName + "%",))
    # rows = c.fetchall()
    # print(rows[0][0])
    # print(rows[0][1])
    # print(rows[0][2])

    # Runes
    c.execute('''SELECT item.name
                 FROM item
                 WHERE item.type = ?''', ("Rune",))

    rows = c.fetchall()
    print(str(len(rows)) + " runes")

    # [sample] find rune properties
    # itemName = "cham"
    # c.execute('''PRAGMA case_sensitive_like = off''')
    # c.execute('''SELECT *
    #              FROM item
    #              WHERE item.name like ?''', ("%" + itemName + "%",))
    # rows = c.fetchall()
    # for row in rows:
    #     for col in row:
    #         print(str(col))

    # Runewords
    c.execute('''SELECT item.name
                 FROM item
                 WHERE item.type = ?''', ("Runeword",))

    rows = c.fetchall()
    print(str(len(rows)) + " runewords")

    # [sample] find runeword properties
    # itemName = "spirit"
    # c.execute('''PRAGMA case_sensitive_like = off''')
    # c.execute('''SELECT *
    #              FROM item
    #              WHERE item.type = "Runeword" and item.name like ?''', ("%" + itemName + "%",))
    # rows = c.fetchall()
    # for row in rows:
    #     c.execute('''SELECT i1.name
    #                  FROM runewordrunes
    #                  JOIN item as i1 on i1.id = runewordrunes.rune
    #                  JOIN item as i2 on i2.id = runewordrunes.runeword
    #                  WHERE i2.id = ?
    #                  ORDER BY runewordrunes.runeorder''', (row[0], ))
    #     runes = c.fetchall()
    #     print(",".join("%s" % r[0] for r in runes))

    #     for col in row:
    #         print(str(col))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
