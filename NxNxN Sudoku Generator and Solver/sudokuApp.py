from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import random

from sudokuCell import SudokuCell
from sudokuSolver import SudokuSolver

class SudokuApp:
    INSERTING_GIVENS = 0
    INSERTING_VALUES = 1
    INSERTING_CANDIDATES = 2

    def __init__(self, root, boardSize, order = 3, bgColor = "white"):
        self.root = root
        self.boardSize = boardSize
        self.bgColor = bgColor
        self.order = order
        self.state = SudokuApp.INSERTING_VALUES
        self.cells = []
        self.borderLineWidth = 2       #no odd numbers here
        self.currFocusedCell = None
        self.multiDigitCand = ''
        self.blockSize = (self.boardSize - self.borderLineWidth * (self.order+1)) / self.order
        self.invalidEntryCells = set()
        self.cellsToImmute = set()
        self.setUpWindow()
        self.setUpBoard()
        self.solver = SudokuSolver()
        self.solver.setPuzzle(self.cells)

    def setUpWindow(self):
        self.board = Canvas(self.root, bg = self.bgColor, height = self.boardSize, width = self.boardSize)
        self.board.pack (side = LEFT)
        self.board.focus_set()

        self.insertValAndSubmissionBtn = Button(self.root, text = "Insert\nVal", font = ("Fira Code", 10, "bold") ,command = lambda : self.switchState(SudokuApp.INSERTING_VALUES), height = 2, width = 10)
        self.insertValAndSubmissionBtn.pack(fill = X)

        self.pencilMarkAndCancelBtn = Button(self.root, text="Pencil\nMark", font = ("Fira Code", 10, "bold") ,command = lambda: self.switchState(SudokuApp.INSERTING_CANDIDATES), height = 2, width = 10)
        self.pencilMarkAndCancelBtn.pack(fill = X)

        self.board.bind('<1>', self.handleFocusing)
        self.board.bind('<3>', self.deselectCurrFocused)
        self.board.bind('<Key>', self.insertNums)
        self.board.bind('<BackSpace>', self.removeNums)
        self.board.bind('<Delete>', self.removeNums)

        #for debugging
        #self.board.bind('<Return>', self.changeOrder)

        self.board.bind('<KeyPress-Alt_L>', self.startTakingMultiDigitCand)
        self.board.bind('<KeyRelease-Alt_L>', self.insertMultiDigitCandidates)
        self.board.bind('<KeyPress-Alt_R>', self.startTakingMultiDigitCand)
        self.board.bind('<KeyRelease-Alt_R>', self.insertMultiDigitCandidates)

        self.board.bind('<Control-n>', lambda e : self.clearBoard(alsoClearGivens = True))
        self.board.bind('<Control-i>', lambda e : self.switchState(SudokuApp.INSERTING_GIVENS))
        self.board.bind('<Control-g>', lambda e : self.handleChangingOrder())
        self.board.bind('<Control-r>', lambda e : self.generateRandomPuzzle())
        self.board.bind('<Control-z>', lambda e : self.clearBoard())
        self.board.bind('<space>', lambda e : self.solveBoard())
        self.board.bind('p', lambda e : self.switchState(SudokuApp.INSERTING_CANDIDATES))
        self.board.bind('v', lambda e : self.switchState(SudokuApp.INSERTING_VALUES))

        menuBar = Menu(self.root)
        fileMenu=Menu(menuBar, tearoff = 0)
        fileMenu.add_command(label="New                  Ctrl+N", command = lambda : self.clearBoard(alsoClearGivens = True))
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit",command = self.root.destroy)

        editMenu = Menu(menuBar, tearoff = 0)
        editMenu.add_command(label="Insert Givens                  Ctrl+I", command = lambda : self.switchState(SudokuApp.INSERTING_GIVENS))
        editMenu.add_command(label="Change Order                Ctrl+G", command = self.handleChangingOrder)
        editMenu.add_command(label="Clear                               Ctrl+Z", command = self.clearBoard)

        commandMenu = Menu(menuBar, tearoff = 0)
        commandMenu.add_command(label = "Solve                                  Space", command = self.solveBoard)
        commandMenu.add_command(label = "Generate Random           Ctrl+R", command = self.generateRandomPuzzle)

        menuBar.add_cascade(label="File",menu = fileMenu)
        menuBar.add_cascade(label="Edit",menu = editMenu)
        menuBar.add_cascade(label="Commands", menu = commandMenu)
        self.root.config(menu = menuBar)

        #editMenu.entryconfig("Insert Givens                  Ctrl+I", state = "disabled")

    def setUpBoard(self):
        #drawing lines
        cvs_err = 2
        startPoint = self.borderLineWidth/2 + cvs_err
        endPoint = self.boardSize - self.borderLineWidth/2 + cvs_err

        for i in range(self.order + 1):
            newVal = i * (self.blockSize + self.borderLineWidth) + self.borderLineWidth/2 + cvs_err
            self.board.create_line(startPoint, newVal, endPoint, newVal, width = self.borderLineWidth)
            self.board.create_line(newVal, startPoint, newVal, endPoint, width = self.borderLineWidth)

        #creating cells
        self.cells = []
        cellSize = self.blockSize/self.order
        tx = self.borderLineWidth + cvs_err
        ty = self.borderLineWidth + cvs_err
        for r in range (self.order * self.order):
            lst=[]
            for c in range (self.order * self.order):
                x = tx + c * cellSize + (c//self.order) * self.borderLineWidth
                y = ty + r * cellSize + (r//self.order) * self.borderLineWidth
                b = c // self.order + r - r % self.order
                cell = SudokuCell( (x, y), (r, c, b), cellSize, self.order, self.board)
                lst.append(cell)
            self.cells.append(lst)

        self.currFocusedCell = self.cells[0][0]
        self.root.update()

    def getCellFromPoint(self,x,y):
        if x <= self.boardSize and y <= self.boardSize:
            cellSize = self.cells[0][0].size
            blockAndLineWidth = self.blockSize + self.borderLineWidth

            xRem = int(x % blockAndLineWidth)
            yRem = int(y % blockAndLineWidth)

            if xRem > self.borderLineWidth and yRem > self.borderLineWidth:
                xBlocks = x // blockAndLineWidth
                yBlocks = y // blockAndLineWidth
                x -= (xBlocks + 1) * self.borderLineWidth
                y -= (yBlocks + 1) * self.borderLineWidth
                colm = int(x / cellSize)
                row = int(y / cellSize)
                return self.cells[row][colm]

    def handleFocusing(self, event):
        self.deselectCurrFocused()
        cell = self.getCellFromPoint(event.x, event.y)
        if cell and cell.isMutable:
            if self.state == SudokuApp.INSERTING_GIVENS:
                cell.changeColor("grey70")
                self.cellsToImmute.add(cell)
            cell.setFocusIn("blue")
            self.currFocusedCell = cell
        self.root.update()

    def deselectCurrFocused(self, event = None):
        if self.currFocusedCell.isFocused and self.state == SudokuApp.INSERTING_GIVENS and not self.currFocusedCell.val:
            self.currFocusedCell.changeColor(self.currFocusedCell.bgColor)
            self.cellsToImmute.discard(self.currFocusedCell)
        self.currFocusedCell.setFocusOut()

    def insertNums (self, event):
        if self.currFocusedCell.isFocused and event.char.isdigit():
            if self.state == SudokuApp.INSERTING_CANDIDATES:
                self.currFocusedCell.insertCandidate(event.char)
            elif self.state == SudokuApp.INSERTING_VALUES or self.state == SudokuApp.INSERTING_GIVENS:
                self.currFocusedCell.insertVal(event.char, callbackForValChange = self.checkValidity)

    def checkValidity(self):
        listCopy = list(self.invalidEntryCells)
        for cell in reversed(listCopy):
            if self.solver.isValid(cell.val, cell):
                cell.changeNumColor("black")
                listCopy.remove(cell)
        self.invalidEntryCells = set(listCopy)

        if not self.solver.isValid(self.currFocusedCell.val, self.currFocusedCell):
            self.currFocusedCell.changeNumColor("red")
            self.invalidEntryCells.add(self.currFocusedCell)

    def removeNums (self, event):
        if self.currFocusedCell.isFocused:
            delete = False
            if event.keysym == "Delete":
                delete = True
            if self.currFocusedCell.val:
                self.currFocusedCell.removeLSDFromVal(delete)
                if self.currFocusedCell.val == 0:
                    self.invalidEntryCells.discard(self.currFocusedCell)
            else:
                self.currFocusedCell.removeCandidate(delete)

    def startTakingMultiDigitCand(self, event):
        if self.state == SudokuApp.INSERTING_CANDIDATES and self.currFocusedCell.isFocused:
            self.board.unbind('<KeyPress-Alt_L>')
            self.board.unbind('<KeyPress-Alt_R>')
            self.board.bind('<Key>', self.concatForMultiDigit)

    def concatForMultiDigit(self, event):
        if event.char.isdigit():
            self.multiDigitCand += event.char

    def insertMultiDigitCandidates(self, event):
        if self.multiDigitCand:
            self.currFocusedCell.insertCandidate(self.multiDigitCand)
            self.multiDigitCand = ''
            self.board.bind('<Key>', self.insertNums)
            self.board.bind('<KeyPress-Alt_L>', self.startTakingMultiDigitCand)
            self.board.bind('<KeyPress-Alt_R>', self.startTakingMultiDigitCand)

    #for debugging
    def setBoard(self, valStr = '0'*81):
        sideLen = self.order * self.order
        for r, eachRow in enumerate(self.cells):
            for eachCell, i in zip(eachRow, range(sideLen * r, sideLen * r + sideLen)):
                if valStr[i] != '0':
                    eachCell.insertVal(valStr[i])
                    eachCell.isMutable = False
                    eachCell.changeColor("grey70")
        self.root.update()
        self.solver.setPuzzle(self.cells)

    #for debugging
    def countGivens(self):
        count = 0
        for eachRow in self.cells:
            for eachCell in eachRow:
                if eachCell.val != 0:
                    count+=1
        return count

    def clearBoard(self, alsoClearGivens = False):
        for eachRow in self.cells:
            for eachCell in eachRow:
                eachCell.removeCandidate(removeAll = True)
                if eachCell.isMutable or alsoClearGivens:
                    eachCell.removeValue()
                    eachCell.changeColor(eachCell.bgColor)
                    eachCell.isMutable = True
        self.cellsToImmute.clear()
        self.invalidEntryCells.clear()
        self.currFocusedCell = self.cells[0][0]

    def generateRandomPuzzle(self):
        self.cellsToImmute.clear()
        self.invalidEntryCells.clear()
        puzzleMatrix = []
        sideLen = self.order * self.order
        availableNums = list(range(1, sideLen + 1))
        random.shuffle(availableNums)
        for i in range(sideLen):
            if i % self.order == 0:
                availableNums = availableNums[1:] + availableNums[:1]
            else:
                availableNums = availableNums[self.order:] + availableNums[:self.order]
            puzzleMatrix.append(availableNums[:])

        orderMultipleIndices = [i*self.order for i in range(self.order)]
        #shuffling rows
        for _ in range(random.randrange(1,5)):
            ind = random.choice(orderMultipleIndices)
            r1 = random.randrange(ind, ind + self.order)
            r2 = random.randrange(ind, ind + self.order)

            temp = puzzleMatrix[r1]
            puzzleMatrix[r1] = puzzleMatrix[r2]
            puzzleMatrix[r2] = temp

        #shuffling columns
        for _ in range(random.randrange(1,5)):
            ind = random.choice(orderMultipleIndices)
            c1 = random.randrange(ind, ind + self.order)
            c2 = random.randrange(ind, ind + self.order)
            for rowInd in range(sideLen):
                temp = puzzleMatrix[rowInd][c1]
                puzzleMatrix[rowInd][c1] = puzzleMatrix[rowInd][c2]
                puzzleMatrix[rowInd][c2] = temp

        self.clearBoard(alsoClearGivens = True)
        #inserting all the values in the cells
        for eachRow, valRow in zip(self.cells, puzzleMatrix):
            for eachCell, val in zip(eachRow, valRow):
                eachCell.val = val

        self.solver.setPuzzle(self.cells)

        #removing nums from the board
        rowIndices = list(range(sideLen))
        random.shuffle(rowIndices)
        colmIndices = list(range(sideLen))
        random.shuffle(colmIndices)
        for r in rowIndices:
            for c in colmIndices:
                cell = self.cells[r][c]
                hasOnlyOneCandidate = True
                nums = list(range(1, sideLen + 1))
                nums.remove(cell.val)
                for num in nums:
                    if self.solver.isValid(num, cell):
                        hasOnlyOneCandidate = False
                        break
                if hasOnlyOneCandidate:
                    cell.val = 0
                else:
                    self.cellsToImmute.add(cell)

        #finalizing the givens
        for cell in self.cellsToImmute:
            cell.drawValNum()
            cell.changeColor("grey70")
            self.root.update()
        self.immuteCells()

    def solveBoard(self):
        if self.immuteCells():
            def drawNumOnBoard(cell):
                self.currFocusedCell.setFocusOut()
                self.currFocusedCell = cell
                self.currFocusedCell.setFocusIn()
                cell.drawValNum()
                cell.removeCandidate(removeAll=True)
                self.root.update()
            self.solver.solve(drawNumOnBoard)

    def setForSolving(self):
        self.insertValAndSubmissionBtn.config(text = "Insert\nVal", command = lambda : self.switchState(SudokuApp.INSERTING_VALUES))
        self.pencilMarkAndCancelBtn.config(text = "Pencil\nMark", command = lambda: self.switchState(SudokuApp.INSERTING_CANDIDATES))
        self.switchState(SudokuApp.INSERTING_VALUES)

    def handleChangingOrder(self):
        num = simpledialog.askinteger("New Order","Order:", minvalue = 1)
        if type(num) is int:
            self.changeOrder(num)
        '''once the dialog appears, the focus is set out of the canvas and not returned back. Hence the following'''
        self.board.focus_set()

    def changeOrder(self, num):
        self.board.delete("all")
        self.order = int(num)
        self.blockSize = (self.boardSize - self.borderLineWidth * (self.order+1)) / self.order
        self.setUpBoard()
        self.setForSolving()
        self.solver.setPuzzle(self.cells)

    def clearInsertedGivens(self):
        for cell in self.cellsToImmute:
            cell.changeColor(cell.bgColor)
            cell.removeValue()
        self.cellsToImmute.clear()

    def cancelGivensInsertion(self):
        self.clearInsertedGivens()
        self.setForSolving()

    def immuteCells(self):
        self.root.update()
        for invalidCell in self.invalidEntryCells:
            if invalidCell in self.cellsToImmute:
                messagebox.showerror("Invalid Entry", "Not a valid Sudoku Puzzle")
                return False
        for cell in self.cellsToImmute:
            if cell.val != 0:
                cell.isMutable = False
        self.deselectCurrFocused()
        self.cellsToImmute.clear()
        self.solver.setPuzzle(self.cells)
        self.setForSolving()
        return True

    def switchState(self, state):
        if state == SudokuApp.INSERTING_GIVENS:
            self.currFocusedCell.setFocusOut()
            self.insertValAndSubmissionBtn.config(text = "Done", command = self.immuteCells)
            self.pencilMarkAndCancelBtn.config(text = "Cancel", command = self.cancelGivensInsertion)
            self.state = SudokuApp.INSERTING_GIVENS
        elif state == SudokuApp.INSERTING_VALUES or state == SudokuApp.INSERTING_CANDIDATES:
            self.state = state