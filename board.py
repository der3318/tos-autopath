import random
import copy
import queue
from PIL import Image
from basic import Move, StoneType, Runestone
import utils

class TosBoard():

    def __init__(self):
        self.numOfRows = 5
        self.numOfCols = 6
        self.runestones = [ [None] * self.numOfCols for row in range(self.numOfRows) ]
        self.currentPosition = [0, 0]
        self.previousPosition = self.currentPosition

    def __repr__(self):
        output = ""
        for row in range(self.numOfRows):
            for col in range(self.numOfCols):
                stone = self.runestones[row][col]
                output = output + str(stone)
            output = output + "\n"
        return output

    def _swap(self, _pos1, _pos2):
        swapTmp = self.runestones[ _pos1[0] ][ _pos1[1] ]
        self.runestones[ _pos1[0] ][ _pos1[1] ] = self.runestones[ _pos2[0] ][ _pos2[1] ]
        self.runestones[ _pos2[0] ][ _pos2[1] ] = swapTmp

    def randomInitialized(self):
        for rowIdx in range(self.numOfRows):
            for colIdx in range(self.numOfCols):
                stone = Runestone( random.choice( list(StoneType) ) )
                self.runestones[rowIdx][colIdx] = stone
        self.currentPosition = [random.randrange(self.numOfRows), random.randrange(self.numOfCols)]
        self.previousPosition = self.currentPosition
        self.runestones[ self.currentPosition[0] ][ self.currentPosition[1] ].status = "*"

    def initFromFile(self, _filePath):
        with open(_filePath, "r") as fin:
            for lineIdx, line in enumerate(fin):
                tokenList = line.strip().split()
                if len(tokenList) != 6:
                    continue
                for tokenIdx, token in enumerate(tokenList):
                    stone = None
                    if token == "D":    stone = Runestone(StoneType.DARK)
                    if token == "L":    stone = Runestone(StoneType.LIGHT)
                    if token == "W":    stone = Runestone(StoneType.WATER)
                    if token == "F":    stone = Runestone(StoneType.FIRE)
                    if token == "E":    stone = Runestone(StoneType.EARTH)
                    if token == "H":    stone = Runestone(StoneType.HEALTH)
                    self.runestones[lineIdx][tokenIdx] = stone

    def initFromScreenshot(self, _filePath):
        types = utils.screenshotToTypes(_filePath, self.numOfRows, self.numOfCols)
        for rowIdx in range(self.numOfRows):
            for colIdx in range(self.numOfCols):
                self.runestones[rowIdx][colIdx] = Runestone(types[rowIdx][colIdx])

    def setCurrentPosition(self, _pos):
        self.runestones[ self.currentPosition[0] ][ self.currentPosition[1] ].status = " "
        self.currentPosition = _pos
        self.previousPosition = self.currentPosition
        self.runestones[ self.currentPosition[0] ][ self.currentPosition[1] ].status = "*"

    def getSuccessorList(self):
        successorList = list()
        for move in list(Move):
            newPosition = [sum(z) for z in zip(list(move.value), self.currentPosition)]
            if newPosition == self.previousPosition:
                continue
            if 0 <= newPosition[0] < self.numOfRows and 0 <= newPosition[1] < self.numOfCols:
                newBoard = TosBoard()
                newBoard.runestones = [copy.copy(row) for row in self.runestones]
                newBoard.currentPosition = newPosition
                newBoard.previousPosition = self.currentPosition
                newBoard._swap(newPosition, self.currentPosition)
                successorList.append( (newBoard, move) )
        return successorList

    def evaluate(self):
        # determine if the stone would be removed
        removed = [ [None] * self.numOfCols for row in range(self.numOfRows) ]
        for rowIdx in range(self.numOfRows):
            for colIdx in range(self.numOfCols - 2):
                stone1 = self.runestones[rowIdx][colIdx];
                stone2 = self.runestones[rowIdx][colIdx + 1]
                stone3 = self.runestones[rowIdx][colIdx + 2]
                if stone1.type == stone2.type and stone2.type == stone3.type:
                    for delta in range(3):
                        removed[rowIdx][colIdx + delta] = stone1.type
        for colIdx in range(self.numOfCols):
            for rowIdx in range(self.numOfRows - 2):
                stone1 = self.runestones[rowIdx][colIdx];
                stone2 = self.runestones[rowIdx + 1][colIdx]
                stone3 = self.runestones[rowIdx + 2][colIdx]
                if stone1.type == stone2.type and stone2.type == stone3.type:
                    for delta in range(3):
                        removed[rowIdx + delta][colIdx] = stone1.type
        # check if the stone you take at first will be removed or not
        end = False
        if removed[ self.currentPosition[0] ][ self.currentPosition[1] ]:
            end = True
        # calculate the number of stones removed and change their status for printing
        stones = 0
        for rowIdx in range(self.numOfRows):
            for colIdx in range(self.numOfCols):
                self.runestones[rowIdx][colIdx].status = " "
                if removed[rowIdx][colIdx] != None:
                    stones = stones + 1
                    self.runestones[rowIdx][colIdx].status = "+"
        self.runestones[ self.currentPosition[0] ][ self.currentPosition[1] ].status = "*"
        # check if four boundaries are removed or not
        boundary = 0
        if removed[0][0] != None:
            boundary = boundary + 1
        if removed[0][-1] != None:
            boundary = boundary + 1
        if removed[-1][0] != None:
            boundary = boundary + 1
        if removed[-1][-1] != None:
            boundary = boundary + 1
        # calculate combo
        combo = 0
        for rowIdx in range(self.numOfRows):
            for colIdx in range(self.numOfCols):
                if removed[rowIdx][colIdx] != None:
                    combo = combo + 1
                    t = removed[rowIdx][colIdx]
                    q = queue.Queue()
                    q.put( (rowIdx, colIdx) )
                    while not q.empty():
                        (r, c) = q.get()
                        removed[r][c] = None
                        if r + 1 < self.numOfRows and removed[r + 1][c] == t:
                            q.put( (r + 1, c) )
                        if c + 1 < self.numOfCols and removed[r][c + 1] == t:
                            q.put( (r, c + 1) )
                        if r - 1 >= 0 and removed[r - 1][c] == t:
                            q.put( (r - 1, c) )
                        if c - 1 >= 0 and removed[r][c - 1] == t:
                            q.put( (r, c - 1) )
        # return results
        return stones, boundary, combo, end

