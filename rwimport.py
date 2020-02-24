import os
import sqlite3
import sys

class Rune:
    def __init__(self, name, weaponEffect, armorEffect, shieldEffect, level):
        self.name = name
        self.weaponEffect = weaponEffect
        self.armorEffect = armorEffect
        self.shieldEffect = shieldEffect
        self.level = level

    def __str__(self):
        return self.name + "|" + self.weaponEffect + "|" + self.armorEffect + "|" + self.shieldEffect + "|" + self.level

class Runeword:
    def __init__(self, name, numSockets, itemTypes, runes):
        self.name = name
        self.numSockets = numSockets
        self.itemTypes = itemTypes
        self.runes = runes
        self.effects = []

    def addEffect(self, effect):
        self.effects.append(effect.strip())

    def __str__(self):
        toString = self.name + ": " + self.numSockets + " Sockets "
        toString += "(" + ",".join(self.itemTypes) + ") "
        toString += "[" + ",".join(self.runes) + "]\n"
        for effect in self.effects:
            toString += "  " + effect + "\n"

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

def main():
    print("diablo 2 importer")

    scriptPath = os.path.dirname(__file__)

    ### Parse files ###
    print("parsing files...")

    # parse runes
    runes = parseRunes(os.path.join(scriptPath, "runewords\\runes.csv"))

    # parse runewords
    runewords = []
    runewords += parseRunewords(os.path.join(scriptPath, "runewords\\originalrw.csv"))
    runewords += parseRunewords(os.path.join(scriptPath, "runewords\\110rw.csv"))
    runewords += parseRunewords(os.path.join(scriptPath, "runewords\\111rw.csv"))

    ### Populate database ###
    print("create db...")

    # remove db if exists
    dbFile = os.path.join(scriptPath, "runes.db")
    if os.path.exists(dbFile):
        os.remove(dbFile)

    conn = sqlite3.connect(dbFile)
    c = conn.cursor()

    ### Create tables ###
    c.execute('''CREATE TABLE runeword (id integer PRIMARY KEY, name text NOT NULL)''')
    c.execute('''CREATE TABLE item (id integer PRIMARY KEY, name text NOT NULL)''')
    c.execute('''CREATE TABLE rune (id integer PRIMARY KEY, name text NOT NULL, level integer NOT NULL)''')
    c.execute('''CREATE TABLE runewordItem (id integer PRIMARY KEY, runeword integer NOT NULL, item integer NOT NULL, FOREIGN KEY (runeword) REFERENCES runeword (id) FOREIGN KEY (item) REFERENCES item (id))''')
    c.execute('''CREATE TABLE runewordRune (id integer PRIMARY KEY, runeword integer NOT NULL, rune integer NOT NULL, FOREIGN KEY (runeword) REFERENCES runeword (id) FOREIGN KEY (rune) REFERENCES rune (id))''')
    c.execute('''CREATE TABLE effect (id integer PRIMARY KEY, text text NOT NULL, runeword integer NOT NULL, FOREIGN KEY (runeword) REFERENCES runeword (id))''')

    print("insert in db...")
    for rune in runes:
        c.execute('''INSERT INTO rune(name, level) VALUES(?,?)''', (rune.name, rune.level))

    for runeword in runewords:
        c.execute('''INSERT INTO runeword(name) VALUES(?)''', (runeword.name,))
        runewordId = c.lastrowid

        for itemType in runeword.itemTypes:
            itemId = -1
            c.execute('''SELECT id FROM item WHERE name=?''', (itemType,))
            itemIds = c.fetchall()
            if (len(itemIds) > 0):
                itemId = itemIds[0][0]
            else:
                c.execute('''INSERT INTO item(name) VALUES(?)''', (itemType,))
                itemId = c.lastrowid

            c.execute('''INSERT INTO runewordItem(runeword, item) VALUES(?,?)''', (runewordId,itemId,))

        for rune in runeword.runes:
            c.execute('''SELECT id FROM rune WHERE name=?''', (rune,))
            c.execute('''INSERT INTO runewordRune(runeword, rune) VALUES(?,?)''', (runewordId,c.fetchall()[0][0],))

        for effect in runeword.effects:
            c.execute('''INSERT INTO effect(text, runeword) VALUES(?,?)''', (effect,runewordId,))

    # sample query
    # runeword = "ancient"
    # c.execute('''SELECT rune.name
    #              FROM rune
    #              join runewordRune on runewordRune.rune = rune.id
    #              join runeword on runeword.id = runewordRune.runeword
    #              where runeword.name like ?''', ("%" + runeword + "%",))

    # rows = c.fetchall()
    # for row in rows:
    #     print(row[0])

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
