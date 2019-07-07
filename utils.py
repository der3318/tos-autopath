import sys
import copy
import queue
from PIL import Image, ImageDraw
import os
from basic import StoneType
import config as cfg

def analyze(_initBoard):
    # determine where to start
    q = queue.PriorityQueue()
    minCost, bestRowIdx, bestColIdx = 10e9, 0, 0
    # try every possible stone
    for rowIdx in range(_initBoard.numOfRows):
        for colIdx in range(_initBoard.numOfCols):
            _initBoard.setCurrentPosition([rowIdx, colIdx])
            cost, count, moveList = 10e9, 0, []
            q.put( (cost, count, moveList, _initBoard) )
            while not q.empty():
                (cost, _, moveList, board) = q.get()
                if cost < minCost:
                    minCost, bestRowIdx, bestColIdx = (cost, rowIdx, colIdx)
                if len(moveList) >= 5:
                    continue
                for successorIdx, successor in enumerate( board.getSuccessorList() ):
                    count = count + 1
                    (newBoard, move) = successor
                    stones, boundary, combo, end = newBoard.evaluate()
                    newCost = -(combo * 100 + boundary * 50 + stones) + len(moveList) * 0.001
                    newCost = newCost + 100 if end else newCost
                    newMoveList = copy.copy(moveList)
                    newMoveList.append(move)
                    q.put( (newCost, count, newMoveList, newBoard) )
    # search end - set current position to the best position
    _initBoard.setCurrentPosition([bestRowIdx, bestColIdx])
    stones, boundary, combo, end = _initBoard.evaluate()
    sys.stderr.write(str(_initBoard) + "\n")
    # search best result
    q = queue.PriorityQueue()
    cost, count, moveList = 10e9, 0, []
    minCost, bestMoveList, bestBoard = (cost, moveList, _initBoard)
    numOfPhases, finalMoveList = 5, []
    # break the search mechanism into several phases
    for it in range(1, numOfPhases + 1):
        q.put( (minCost, count, bestMoveList, bestBoard) )
        # bfs with evaluation as reward
        while not q.empty():
            (cost, _, moveList, board) = q.get()
            if cost < minCost:
                minCost, bestMoveList, bestBoard = (cost, moveList, board)
            if len(moveList) >= 10:
                continue
            for successorIdx, successor in enumerate( board.getSuccessorList() ):
                count = count + 1
                (newBoard, move) = successor
                stones, boundary, combo, end = newBoard.evaluate()
                newCost = -(combo * 100 + boundary * 10 * (numOfPhases - it) + stones) + len(moveList) * 0.001
                newCost = newCost + 100 if end and it != numOfPhases else newCost
                newMoveList = copy.copy(moveList)
                newMoveList.append(move)
                q.put( (newCost, count, newMoveList, newBoard) )
        # end search - concatenate the move list and evaluate again
        stones, boundary, combo, end = bestBoard.evaluate()
        minCost = -(combo * 100 + boundary * 10 * (numOfPhases - 1 - it) + stones)
        minCost = minCost + 100 if end and it != (numOfPhases - 1) else minCost
        finalMoveList = finalMoveList + bestMoveList
        bestMoveList = []
        sys.stderr.write( "phase {}/{}\n".format(it, numOfPhases) )
        sys.stderr.write( "stones={}, boundary={}, combo={}, end={}, steps={}, count={}\n".format(stones, boundary, combo, end, len(finalMoveList), count) )
        sys.stderr.write(str(bestBoard) + "\n")
    # return final result
    return bestBoard, finalMoveList

def visualizePath(_initBoard, _bestBoard, _finalMoveList):
    # create directory
    if not os.path.exists(cfg.outputDir):
        os.makedirs(cfg.outputDir)
    # setup image objecdts
    hand = Image.open(cfg.imagePath["hand"]).convert("RGBA")
    flag = Image.open(cfg.imagePath["flag"]).convert("RGBA")
    type2Foreground = {
        StoneType.DARK: Image.open(cfg.imagePath["dark"]).convert("RGBA"),
        StoneType.LIGHT: Image.open(cfg.imagePath["light"]).convert("RGBA"),
        StoneType.WATER: Image.open(cfg.imagePath["water"]).convert("RGBA"),
        StoneType.FIRE: Image.open(cfg.imagePath["fire"]).convert("RGBA"),
        StoneType.EARTH: Image.open(cfg.imagePath["earth"]).convert("RGBA"),
        StoneType.HEALTH: Image.open(cfg.imagePath["health"]).convert("RGBA")
    }
    # init draw settings
    pixels = cfg.settings["pixels"]
    lineWidth = cfg.settings["lineWidth"]
    lineColor = cfg.settings["lineColor"]
    # draw init board
    background = Image.open(cfg.imagePath["background"]).convert("RGBA")
    for rowIdx in range(_initBoard.numOfRows):
        for colIdx in range(_initBoard.numOfCols):
            stone = _initBoard.runestones[rowIdx][colIdx]
            foreground = type2Foreground[stone.type]
            location = (colIdx * pixels, rowIdx * pixels)
            background.paste(foreground, location, foreground)
    background.save( os.path.join(cfg.outputDir, "initBoard.png") )
    # draw path images
    board = _initBoard
    path = Image.open( os.path.join(cfg.outputDir, "initBoard.png") ).convert("RGBA")
    d = ImageDraw.Draw(path)
    pathIdx, visited = 1, [board.previousPosition]
    for finalMoveIdx, finalMove in enumerate(_finalMoveList):
        for successorIdx, successor in enumerate( board.getSuccessorList() ):
            (newBoard, move) = successor
            board = newBoard if finalMove == move else board
        if board.currentPosition in visited:
            location = (visited[0][1] * pixels, visited[0][0] * pixels)
            path.paste(hand, location, hand)
            location = (board.previousPosition[1] * pixels, board.previousPosition[0] * pixels)
            path.paste(flag, location, flag)
            path.save( os.path.join( cfg.outputDir, "path{:0>2d}.png".format(pathIdx) ) )
            path = Image.open( os.path.join(cfg.outputDir, "initBoard.png") ).convert("RGBA")
            d = ImageDraw.Draw(path)
            pathIdx, visited = pathIdx + 1, [board.previousPosition]
        delta = pixels // 2
        src = (board.previousPosition[1] * pixels + delta, board.previousPosition[0] * pixels + delta)
        des = (board.currentPosition[1] * pixels + delta, board.currentPosition[0] * pixels + delta)
        d.line([src, des], fill = lineColor, width = lineWidth)
        visited.append(board.currentPosition)
    location = (visited[0][1] * pixels, visited[0][0] * pixels)
    path.paste(hand, location, hand)
    location = (board.currentPosition[1] * pixels, board.currentPosition[0] * pixels)
    path.paste(flag, location, flag)
    path.save( os.path.join( cfg.outputDir, "path{:0>2d}.png".format(pathIdx) ) )
    # draw best board
    background = Image.open(cfg.imagePath["background"]).convert("RGBA")
    for rowIdx in range(_bestBoard.numOfRows):
        for colIdx in range(_bestBoard.numOfCols):
            stone = _bestBoard.runestones[rowIdx][colIdx]
            foreground = type2Foreground[stone.type]
            location = (colIdx * pixels, rowIdx * pixels)
            background.paste(foreground, location, foreground)
    background.save( os.path.join(cfg.outputDir, "bestBoard.png") )

