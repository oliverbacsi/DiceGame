#!/usr/bin/env python3

import random, re, os, time

NUMPLAYERS :int
WISHINDEX :int
NUMDICEPERPLAYER :int
NAMELIST :list = ["Abigail","Brandon","Cynthia","Dylan","Emily","Fidel","Gemma","Harold","Indira","Jackson","Kylie",
                  "Leslie","Mona","Nolan","Olivia","Patrick","Rosamund","Sam","Tracy","Vincent","Wendy","Zed",
                  "Ashton","Belle","Chuck","Daisy","Elmer","Francine","Gordon","Hailey","Ian","Jennifer","Karl",
                  "Linda","Mike","Nina","Oscar","Priscilla","Robert","Sally","Thomas","Veronica","Will","Zelmira"]
PLAYERNAME :str


#################### CLASS PART ####################


class Game :

    def __init__(self) :
        global NUMPLAYERS, NUMDICEPERPLAYER, NAMELIST, WISHINDEX, PLAYERNAME
        # This is to keep the main loop running. False when Game Over condition is met (1 player left)
        self.StayInGame  :bool =True
        # List of Player objects in game. All players are always in this list.
        # Players with empty Dice list are out.
        self.PlayerList  :list =list(())
        # Counts the total number of game turns passed (for statistical reasons)
        # Also it helps to display the "fading" effect to display how old a bet is.
        self.GameTurns   :int =1
        # The "previous" bet value and qty to remember (to beat)
        self.LastBetVal  :int =-1
        self.LastBetQty  :int =-1
        # The current bet value and qty that is being placed right now in this turn.
        self.CurrBetVal  :int =-1
        self.CurrBetQty  :int =-1
        # Pointer to the last player object who placed the last bet.
        self.PrevPlayer  =None

        # Create all the player objects, trying to place the human player at the desired index in the queue
        for i in range(0,WISHINDEX) :
            self.PlayerList.append(Player(NAMELIST.pop(random.randrange(len(NAMELIST))),i,False))
            if self.PrevPlayer : self.PrevPlayer.NextPlayer = self.PlayerList[-1]
            self.PrevPlayer = self.PlayerList[-1]
        self.PlayerList.append(Player(PLAYERNAME,WISHINDEX,True))
        if self.PrevPlayer : self.PrevPlayer.NextPlayer = self.PlayerList[-1]
        self.PrevPlayer = self.PlayerList[-1]
        for i in range(WISHINDEX+1,NUMPLAYERS) :
            self.PlayerList.append(Player(NAMELIST.pop(random.randrange(len(NAMELIST))),i,False))
            if self.PrevPlayer : self.PrevPlayer.NextPlayer = self.PlayerList[-1]
            self.PrevPlayer = self.PlayerList[-1]
        self.PlayerList[-1].NextPlayer = self.PlayerList[0]
        self.CurrPlayer = self.PlayerList[0]
        self.PrevPlayer = None


    def checkBlock(self) -> None :
        """Current player announced a block, so check who won and who lost"""
        countedNum :int =0
        popupWindow(["","","BLOCK !!!".center(30),"",""])
        for pl in self.PlayerList :
            for di in pl.DiceList :
                di.reveal()
                countedNum += di.valueAs(g.LastBetVal)
        time.sleep(1)
        pl1 :str = "pc" if self.LastBetQty == 1 else "pcs"
        pl2 :str = "pc" if countedNum == 1 else "pcs"
        if self.LastBetQty > countedNum :
            # Block successful, current player won, prev player lost
            popupWindow([f"{self.PrevPlayer.Name} : at least {self.LastBetQty} {pl1} of {self.LastBetVal}'s",
                         f"Counted: {countedNum} {pl2} of {self.LastBetVal}'s and 1's",
                         "","",
                         f"{self.CurrPlayer.Name} made a successful block, {self.PrevPlayer.Name} loses a dice."])
            self.PrevPlayer.duelLost()
        else :
            # Block unsuccessful, current player lost, prev player won
            popupWindow([f"{self.PrevPlayer.Name} : at least {self.LastBetQty} {pl1} of {self.LastBetVal}'s",
                         f"Counted: {countedNum} {pl2} of {self.LastBetVal}'s and 1's",
                         "","",
                         f"{self.CurrPlayer.Name} made an unsuccessful block and loses a dice."])
            self.CurrPlayer.duelLost()
        if self.getNumActivePlayers() == 1 :
            self.StayInGame = False
            return
        self.LastBetVal =-1
        self.LastBetQty =-1
        self.CurrBetVal =-1
        self.CurrBetQty =-1
        self.rollAll()
        self.forwardTurn()


    def rollAll(self) -> None :
        """Roll all player's dice"""
        for i in range(0,3) :
            for pl in self.PlayerList :
                pl.rollAllDice(False)
        for pl in self.PlayerList :
            pl.rollAllDice(True)


    def getRemainingDiceNum(self) -> int :
        """Count the number of dice still in game and return as int"""
        ret :int =0
        for pl in self.PlayerList : ret += len(pl.DiceList)
        return ret


    def getNumActivePlayers(self) -> int :
        """Count the number of players still in game"""
        ret :int =0
        for pl in self.PlayerList :
            if len(pl.DiceList) : ret+=1
        return ret


    def forwardTurn(self) -> None :
        """Let the game step forward one turn"""
        self.LastBetVal = self.CurrBetVal
        self.LastBetQty = self.CurrBetQty
        self.CurrBetVal = -1
        self.CurrBetQty = -1
        self.PrevPlayer = self.CurrPlayer
        self.CurrPlayer = self.CurrPlayer.NextPlayer
        self.GameTurns += 1
        self.redrawScreen()


    def redrawScreen(self) -> None :
        """Refresh everything on the screen"""
        print("\x1b[0m\x1b[2J\x1b[H",end="")
        print("#"*30+" GAME OF DICE "+"#"*30+" ["+str(self.getRemainingDiceNum())+"]")
        print("#   "+"Player".center(30)+" ."+"Dice".center(NUMDICEPERPLAYER*2+1)+". Last bet")
        print("# - "+"-"*30+" | "+"-"*NUMDICEPERPLAYER*2+"| ----- ---- --- -- - - -")
        for pl in self.PlayerList : pl.prettyPrint()



class Dice :

    def __init__(self, PlayerID :int, DiceID :int) :
        """Initialize a Dice object.
        Parameters:
        :param PlayerID: Which player the dice belong to (ID of PlayerList)
        :param DiceID: Which of the player's dice it is
        """
        # This is the screen Y --- TODO: Correct
        self.Y :int =PlayerID+4
        # This is the screen X --- TODO: Correct
        self.X :int =DiceID*2+38
        # Actual dynamic value of the dice (the face up)
        self.Value :int =0
        self.Color :str ="\x1b[0m"


    def roll(self, Show :bool =False) -> None :
        """Generate a random value for the dice.
        If Show is true, show the real value of the dice, otherwise hide it
        """
        self.Value = random.randint(1,6)
        if Show :
            self.Color = "\x1b[1;48;5;"+["238","201","209","220","154","84","105"][self.Value]+"m\x1b[1;38;5;232m"
            self.displayNumber()
        else :
            self.Color = "\x1b[1;48;5;"+str(random.randrange(17,231))+"m\x1b[1;38;5;232m"
            self.displayColor()


    def displayColor(self) -> None :
        """Show a colored square only."""
        print("\x1b["+str(self.Y)+";"+str(self.X)+"H"+self.Color+" ",end="\x1b[0m")

    def displayNumber(self) -> None :
        """Show the value of the dice."""
        print("\x1b["+str(self.Y)+";"+str(self.X)+"H"+self.Color+str(self.Value),end="\x1b[0m")

    def reveal(self) -> None :
        """Reveal the value if block is made and it's the moment of truth"""
        print("\x1b["+str(self.Y)+";"+str(self.X)+"H\x1b[1;48;5;"+
              ["238","201","209","220","154","84","105"][self.Value]+"m\x1b[1;38;5;232m"+str(self.Value),end="\x1b[0m")


    def valueAs(self, Which :int) -> int :
        """Return the number what is the value of the current dice status if considering as 'Which'.
        Parameters:
        :param Which : The value the dice value is checked against.
        :returns: 1 if counts, 0 if does not count.
        """
        return 1 if self.Value in [Which, 1] else 0



class Player :

    def __init__(self, Name :str, ID :int, isHuman :bool =False) :
        """Initialize a Player object.
        Parameters:
        :param Name : The Name of the player as str
        :param ID : The Player's ID in the list
        :param isHuman : Whether this is the human player or not
        """
        global NUMDICEPERPLAYER
        # The display name of the player:
        self.Name         :str  =Name
        # List of Dice objects that are still in game. If none: Player is out.
        self.DiceList     :list =list(())
        # True if bet is asked manually, otherwise bet is put automatically.
        self.isHuman      :bool =isHuman
        # When player is out, this stores the ranking for the final display of all rankings
        self.FinishedRank :int  =0
        # A small integer number to show how much is the (computer) player on the "safe side" when putting bets.
        # This influences the behaviour a little bit, although not too much
        self.SafePlayer   :int  =random.randint(-2,2)
        # Create the dice objects for the player
        for d in range(NUMDICEPERPLAYER) : self.DiceList.append(Dice(ID,d))
        # Remember the last bet as a text string to display beside the player
        self.LastBet      :str  =""
        # The number of turn this above bet was made (to be able to fade based on age)
        self.BetTurn      :int  =0
        # Pointer to the next player object
        self.NextPlayer =None


    def rollAllDice(self, Final :bool =False) :
        """Roll all Dice still in game"""
        for d in self.DiceList : d.roll(Final and self.isHuman)


    def mostDiceVals(self) -> int :
        """Return the highest value of the dice with the most qty"""
        tempList :list = list((-1, 0, 0, 0, 0, 0, 0))
        tempMax  :int  =0
        tempVal  :int
        retList  :list = list(())
        for dc in self.DiceList :
            tempList[dc.Value]+=1
            tempMax = max(tempMax, tempList[dc.Value])
        # The number of ones is counted, too, because we can use them as 6's for example
        for tempVal in range(6,0,-1) :
            if tempList[tempVal] == tempMax :
                retList.append(tempVal)

        # If there is only 1 value with most qty, then return the value itself
        # Except if it is '1' then don't care.
        if len(retList) == 1 :
            if retList[0] == 1 :
                return random.randint(2,6)
            else :
                return retList[0]

        # So we have more possible values with highest qty
        #+++There could be a check here if there is such a value in the list that is higher than the last bet,
        #   because then the qty doesn't need to be raised so the bet is safer.
        #   but as first let's just pick a random of these values to confuse opponents. (excluding the 1)
        if 1 in retList : retList.remove(1)
        return random.choice(retList)


    def duelLost(self) -> None :
        """This player has lost a duel, make all arrangements"""
        if not len(self.DiceList) : return
        self.DiceList.pop()
        if not len(self.DiceList) :
            self.LastBet ="---"
            self.BetTurn = g.GameTurns
            self.FinishedRank = g.getNumActivePlayers()+1
            for pl in g.PlayerList :
                if pl.NextPlayer == self :
                    pl.NextPlayer = self.NextPlayer


    def makeBet(self) -> None :
        """Try to assess a new bet"""

        if self.isHuman :
            aValid :bool =False
            ans = "error"
            while not aValid :
                ans = input(f"\x1b[{len(g.PlayerList)+5};1HPlace Your bet: (either 'X Y' for 'X pcs of Y' or 'block' to block the previous bet) : ")
                m5 = re.match("^([1-9][0-9]?) ([2-6])$", ans)
                if ans.lower() in ["b", "blk", "block"] :
                    if g.LastBetVal == -1 :
                        print("\n\x1b[1m*** Can not block in this step! ***\x1b[0m")
                        input("[PRESS ENTER]")
                        aValid = False
                    else :
                        ans = "block"
                        aValid = True
                elif m5 :
                    if int(m5[1]) < g.LastBetQty or (int(m5[1]) == g.LastBetQty and int(m5[2]) <= g.LastBetVal) :
                        ans = "error"
                        aValid = False
                    else :
                        g.CurrBetQty = int(m5[1]) ; g.CurrBetVal = int(m5[2])
                        aValid = True
                else :
                    aValid = False
        else :
            # Try to make an AI bet
            time.sleep(2)
            ans = self.generateAIBet()

        if ans.lower() in ["b", "blk", "block"]:
            self.LastBet = "--- block ---"
            self.BetTurn = g.GameTurns
            g.checkBlock()
        else :
            pl3 :str = "pc" if g.CurrBetQty == 1 else "pcs"
            self.LastBet = f"{g.CurrBetQty} {pl3} of {g.CurrBetVal}"
            self.BetTurn = g.GameTurns
            g.forwardTurn()


    def generateAIBet(self) -> str :
        """Generate a best possible bet by algorhythm.
        :returns : the bet string"""

        # Check how many dice could be for the previous bet:
        # Mathematical max:
        estNumPMax :int = g.getRemainingDiceNum() - len(self.DiceList)
        # A sane estimation:
        estNumP    :int = (g.getRemainingDiceNum() - len(self.DiceList)) // 3
        for dc in self.DiceList :
            estNumP += dc.valueAs(g.LastBetVal)
            estNumPMax += dc.valueAs(g.LastBetVal)

        # Check if previous bet qty is not possible:
        if g.LastBetQty > estNumPMax : return "block"

        # See which would be my bet and now many there could be of it
        g.CurrBetVal = self.mostDiceVals()
        g.CurrBetQty = (g.getRemainingDiceNum() - len(self.DiceList)) // 3
        betCeiling :int = g.getRemainingDiceNum() - len(self.DiceList)
        for dc in self.DiceList :
            g.CurrBetQty += dc.valueAs(g.CurrBetVal)
            betCeiling   += dc.valueAs(g.CurrBetVal)

        # See if it is rather safe to raise the bet
        betQtyAdder: int = 1 if g.CurrBetVal <= g.LastBetVal else 0
        if g.CurrBetQty >= g.LastBetQty + betQtyAdder + self.SafePlayer:
            g.CurrBetQty = max(g.LastBetQty + betQtyAdder, 1)
            if g.CurrBetQty > betCeiling :
                g.CurrBetQty = -1
                return "block"
            else :
                return str(g.CurrBetQty)+" "+str(g.CurrBetVal)

        # See how safe it is to block
        if estNumP < g.LastBetQty - self.SafePlayer : return "block"

        # Check raise without safety :
        if g.CurrBetQty >= g.LastBetQty + betQtyAdder:
            g.CurrBetQty = max(g.LastBetQty + betQtyAdder, 1)
            if g.CurrBetQty > betCeiling :
                g.CurrBetQty = -1
                return "block"
            else :
                return str(g.CurrBetQty)+" "+str(g.CurrBetVal)

        # Check block without safety :
        if estNumP <= g.LastBetQty : return "block"

        # Give up.... Raise, hoping that next player does not block
        g.CurrBetQty = max(g.LastBetQty + betQtyAdder, 1)
        if g.CurrBetQty > betCeiling:
            g.CurrBetQty = -1
            return "block"
        else:
            return str(g.CurrBetQty) + " " + str(g.CurrBetVal)


    def prettyPrint(self) -> None :
        """Print one row on the screen with current status"""
        if g.CurrPlayer == self :
            DefaultColor = "\x1b[1;33;44m"
            Tagger = " > "
        else :
            DefaultColor = "\x1b[0m"
            Tagger = "   "
        print("#"+DefaultColor+Tagger+self.Name.ljust(31)+"\x1b[0m|"+DefaultColor,end=" ")
        for i in range(0,NUMDICEPERPLAYER) : print(" ",end=" ")
        print("\x1b[0m|"+DefaultColor,end=" ")
        fgColNum = 256-(g.GameTurns-self.BetTurn)
        fgColNum = min(max(fgColNum,235),255)
        print("\x1b[1;38;5;"+str(fgColNum)+"m"+self.LastBet.ljust(32),end="\x1b[0m")
        for di in self.DiceList :
            if self.isHuman :
                di.displayNumber()
            else :
                di.displayColor()
        print("\x1b[0m")



#################### PROC PART ####################

def askForInt(Question :str, Min: int, Max: int, Def: int) -> int :
    """Ask to input an integer
    Parameters:
    :param Question : The question to be displayed as input prompt
    :param Min : Smallest value still to accept
    :param Max : Largest value still to accept
    :param Def : The default value if no input is entered
    :returns: The valid integer
    """
    ans :str
    ain :int =-1
    while True:
        ans = input(f"{Question} ({Min}-{Max}) [def:{Def}] :")
        if not len(ans) : ans=str(Def)
        if not ans.isdecimal() : continue
        ain = int(ans)
        if ain < Min or ain > Max : continue
        break
    return ain


def popupWindow(Msg :list) -> None :
    """Display an automatically sized popup window with the message inside, each list element is a row"""
    MaxLen :int =-1
    Wid :int = int(os.environ["COLUMNS"])
    for txt in Msg : MaxLen = max(MaxLen,len(txt))
    MaxLen += 4
    XS :int = (Wid-MaxLen) // 2
    YS :int = 5
    print(f"\x1b[{YS};{XS}H"+"#"*MaxLen,end="") ; YS+=1
    print(f"\x1b[{YS};{XS}H#"+" "*(MaxLen-2),end="#") ; YS+=1
    for txt in Msg :
        print(f"\x1b[{YS};{XS}H#"+txt.center(MaxLen-2)+"#",end="")
        YS+=1
    print(f"\x1b[{YS};{XS}H#"+" "*(MaxLen-2),end="#") ; YS+=1
    print(f"\x1b[{YS};{XS}H"+"#"*(MaxLen-10),end=" [ENTER] #")
    input("")



#################### MAIN PART ####################


NUMPLAYERS = askForInt("How many players including You?",2, len(NAMELIST)+1,15)
WISHINDEX  = askForInt("Which one are You?",1, NUMPLAYERS, 1)-1
PLAYERNAME = input("What is Your name? : ")
NUMDICEPERPLAYER = askForInt("How many initial dice per player?", 1, 4, 2)

try :
    NAMELIST.remove(PLAYERNAME)
except :
    pass

g = Game()
g.redrawScreen()
g.rollAll()

while g.StayInGame :
    g.CurrPlayer.makeBet()

Classification :list =list(())
# When this process is called, the winner player is not classified yet!
for px in g.PlayerList :
    if len(px.DiceList) :
        px.FinishedRank = 1
        break
# This is phukin' stupid but it's OK for now:
for px in g.PlayerList :
    Classification.append(str(px.FinishedRank).zfill(2)+" - "+px.Name)
Classification.sort()
col :int =255
print("\x1b[0m\x1b[2J\x1b[H\n"+"#"*100)
print("#   FINAL CLASSIFICATION OF PLAYERS\n#")
for itm in Classification :
    print("# \x1b[1;38;5;"+str(col)+"m"+itm+"\x1b[0m")
    if col > 232 : col-=1
