import sys
import os
from board import TosBoard
import utils
import config as cfg

# get board object
initBoard = TosBoard()
# init
initBoard.randomInitialized()
if cfg.inputFileName != None:
    initBoard.initFromFile(cfg.inputFileName)
# test evaluation
stones, boundary, combo, end = initBoard.evaluate()
# start searching
bestBoard, finalMoveList = utils.analyze(initBoard)
# evaluate and visualization
stones, boundary, combo, end = bestBoard.evaluate()
utils.visualizePath(initBoard, bestBoard, finalMoveList)
# dump result to txt file
with open(os.path.join(cfg.outputDir, "output.txt"), "w") as fout:
    fout.write( "startRowIdx={}\n".format(initBoard.currentPosition[0]) )
    fout.write( "startColIdx={}\n".format(initBoard.currentPosition[1]) )
    for move in finalMoveList:
        fout.write( "{} ".format(move) )
    fout.write( "\nstones={}\ncombo={}\nsteps={}\n".format( stones, combo, len(finalMoveList) ) )

