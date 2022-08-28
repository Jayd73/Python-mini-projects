class SudokuCell:
    def __init__(self, topLeft, index, size, order, cvs, bgColor = "white"):
        self.topLeft = topLeft
        self.row = index[0]
        self.colm = index[1]
        self.block = index[2]
        self.order = order
        self.size = size
        self.cvs = cvs
        self.bgColor = bgColor
        self.currColor = self.bgColor
        self.userCandidates = {}
        self.userCandidateNumCopy = []
        self.candidates = []
        self.val = 0
        self.isMutable = True
        self.isFocused = False
        self.valID = None
        self.bgSqrID = None
        self.focusSqrID = None
        self.center = (self.topLeft[0] + self.size/2, self.topLeft[1] + self.size/2)
        self.createSquares()

    def createSquares(self):
        sizeOffset = 2
        tl = self.topLeft
        size = self.size
        self.bgSqrID = self.cvs.create_rectangle(tl[0], tl[1], tl[0] + size, tl[1] + size)
        self.focusSqrID = self.cvs.create_rectangle(tl[0] + sizeOffset, tl[1] + sizeOffset, tl[0] + size - sizeOffset, tl[1] + size - sizeOffset, outline = self.bgColor, fill = self.bgColor)

    def setFocusIn(self, color = "blue"):
        if self.isMutable:
            self.cvs.itemconfig(self.focusSqrID, outline = color, fill = self.currColor, width = 3)
            self.isFocused = True

    def setFocusOut(self):
        if self.isFocused:
            self.cvs.itemconfig(self.focusSqrID, outline = self.currColor, width = 1)
            self.isFocused = False

    def drawValNum(self):
        self.cvs.delete(self.valID)
        self.valID = self.cvs.create_text(self.center[0], self.center[1], font="Cambria "+str(int(10*self.size/20)), text = str(self.val))

    def insertVal(self, valStr, callbackForValChange = lambda : None):
        val = int(str(self.val) + valStr)
        sideLen = self.order * self.order
        if val > sideLen:
            val %= 10

        if self.val != val and val > 0 and val <= sideLen:  # 3rd condition for sideLen < 10
            self.val = val
            if self.userCandidates:
                self.userCandidateNumCopy = list(self.userCandidates.keys())
                self.removeCandidate(removeAll= True)
            self.drawValNum()
            callbackForValChange()

    def insertCandidate(self, numStr):
        self.removeValue()
        num = int(numStr)
        if num not in self.userCandidates and num > 0 and num <= (self.order * self.order):
            offset = self.size / (self.order*2)
            x = self.topLeft[0] + offset * (2 * ((num - 1) % self.order) + 1)
            y = self.topLeft[1] + offset * (2 * ((num - 1) // self.order) + 1)
            self.userCandidates[num] = self.cvs.create_text(x,y,font="FiraCode "+str(int(self.size/(self.order*1.6))) + " bold",text = str(num), fill = "grey34")

    def removeValue(self):
        self.val = 0
        self.cvs.delete(self.valID)

    def removeLSDFromVal(self, delete = False):
        valStr = str(self.val)
        valStr = valStr[:len(valStr)-1]
        if delete or valStr == '':
            self.removeValue()
            for num in self.userCandidateNumCopy:
                self.insertCandidate(num)
        else:
            self.val = int(valStr)
            self.drawValNum()

    def removeCandidate(self, removeAll = False):
        if self.userCandidates:
            num = max(self.userCandidates)
            self.cvs.delete(self.userCandidates[num])
            del self.userCandidates[num]
            if removeAll:
                for textID in self.userCandidates.values():
                    self.cvs.delete(textID)
                self.userCandidates.clear()

    def makeImmutable(self):
        self.changeColor("light grey")
        self.isMutable = False

    def changeNumColor(self, color):
        self.cvs.itemconfig(self.valID, fill = color)

    def changeColor(self, color):
        self.currColor = color
        self.cvs.itemconfig(self.bgSqrID, fill = color)
        self.cvs.itemconfig(self.focusSqrID, fill = color, outline = color)

    def __str__(self):
        return "(row: {}, column: {}, block: {})".format(self.row, self.colm, self.block)