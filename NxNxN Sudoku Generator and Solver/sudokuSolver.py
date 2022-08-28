from tkinter import *
from collections import defaultdict

class SudokuSolver:
    def __init__(self):
        self.cellMatrix = None
        self.order = 0
        self.mtCells = []
        self.regionwiseMTCells = [defaultdict(set), defaultdict(set), defaultdict(set)]      #0 - Row, 1 - Colm, 2 - Block

    def setPuzzle(self, cellMatrix):
        self.mtCells = []
        for region in self.regionwiseMTCells:
            region.clear()
        self.cellMatrix = cellMatrix
        self.order = self.cellMatrix[0][0].order
        self.findMTCells()

    def findMTCells(self):
        for eachRow in self.cellMatrix:
            for eachCell in eachRow:
                if eachCell.isMutable:
                    self.mtCells.append(eachCell)
                    self.regionwiseMTCells[0][eachCell.row].add(eachCell)
                    self.regionwiseMTCells[1][eachCell.colm].add(eachCell)
                    self.regionwiseMTCells[2][eachCell.block].add(eachCell)

    def findCandidatesForMTCells(self):
        for mtCell in self.mtCells:
            mtCell.val = 0
        for mtCell in self.mtCells:
            mtCell.candidates.clear()
            for i in range(1, self.order * self.order + 1):
                if self.isValid(i, mtCell):
                    mtCell.candidates.append(i)

    def hasMatchingCellInRow(self, val, cell):
        for eachCell in self.cellMatrix[cell.row]:
            if eachCell.val == val and eachCell is not cell:
                return True
        return False

    def hasMatchingCellInColm(self, val, cell):
        indices = list(range (self.order * self.order))
        indices.remove(cell.row)
        for rowInd in indices:
            otherCell = self.cellMatrix[rowInd][cell.colm]
            if otherCell.val == val:
                return True
        return False

    def hasMatchingCellInBlock(self, val, cell):
        startRowInd = (cell.block // self.order) * self.order
        startColmInd = (cell.block % self.order) * self.order
        for r in range(startRowInd, startRowInd + self.order):
            for c in range(startColmInd, startColmInd + self.order):
                otherCell = self.cellMatrix[r][c]
                if otherCell.val == val and otherCell is not cell:
                    return True
        return False

    def isValid(self, val, cell):
        for hasMatchMethod in [self.hasMatchingCellInRow, self.hasMatchingCellInColm, self.hasMatchingCellInBlock]:
            if hasMatchMethod(val, cell):
                return False
        return True

    def removeFromMTCells(self, cell):
        cellRegionIndices = [cell.row, cell.colm, cell.block]
        for mtCellRegion, cellRegionInd in zip(self.regionwiseMTCells, cellRegionIndices):
            for mtCell in mtCellRegion[cellRegionInd]:
                if cell.val in mtCell.candidates:
                    mtCell.candidates.remove(cell.val)
            mtCellRegion[cellRegionInd].discard(cell)
        self.mtCells.remove(cell)

    def solveSingleCandidateCells(self, callbackForValInsertion):
        i = len(self.mtCells)-1
        while i >= 0:
            mtCell = self.mtCells[i]
            if len(mtCell.candidates) == 1:
                mtCell.val = mtCell.candidates[0]
                callbackForValInsertion(mtCell)
                self.removeFromMTCells(mtCell)
                i = len(self.mtCells) - 1
            else:
                i-=1

    def solveHiddenSingleCandidateCells(self, callbackForValInsertion):
        '''holds count of the candidate in that complete row/colm/block and the last cell that has that candidate.'''
        foundOne = False
        regionRecord = defaultdict(lambda : [0, None])

        for mtCellRegion in self.regionwiseMTCells:
            i = 0
            cellCollections = list(mtCellRegion.values())
            while i < len(cellCollections):
                cellCollection = cellCollections[i]
                for eachCell in cellCollection:
                    for candidate in eachCell.candidates:
                        regionRecord[candidate][0] += 1
                        regionRecord[candidate][1] = eachCell

                for candidate, countRec in regionRecord.items():
                    candidateCount, cell = countRec
                    if candidateCount == 1:
                        foundOne = True
                        i = -1
                        cell.val = candidate
                        callbackForValInsertion(cell)
                        self.removeFromMTCells(cell)
                i+=1
                regionRecord.clear()
        return foundOne

    def solveUsingBacktracking(self, callbackForValInsertion = lambda cell : None):
        if self.mtCells:
            mtCell = self.mtCells.pop(0)
        else:
            return True
        for candidate in mtCell.candidates:
            if self.isValid(candidate, mtCell):
                mtCell.val = candidate
                callbackForValInsertion(mtCell)
                if self.solveUsingBacktracking(callbackForValInsertion):
                    return True
        mtCell.removeValue()
        self.mtCells.insert(0, mtCell)
        return False

    def solve(self, callbackForValInsertion = lambda cell: None):
        self.findCandidatesForMTCells()
        cellSolnFound = True
        while cellSolnFound:
            self.solveSingleCandidateCells(callbackForValInsertion)
            cellSolnFound = self.solveHiddenSingleCandidateCells(callbackForValInsertion)
        self.solveUsingBacktracking(callbackForValInsertion)

    def isValidSolution(self):
        for eachRow in self.cellMatrix:
            for eachCell in eachRow:
                if eachCell.isMutable and not self.isValid(eachCell.val, eachCell):
                    return False
        return True
