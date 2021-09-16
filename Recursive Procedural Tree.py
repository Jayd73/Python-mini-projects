from tkinter import *
from CustomVectorModule import *
import random
import copy

class Branch:
	def __init__(self, basePos, branchVect, branchWidth, timesBent = 0):
		self.basePos = basePos
		self.branchVect = branchVect			#tells the length and direc of the branch
		self.branchWidth = branchWidth
		self.timesBent = timesBent

	def drawOn(self, cvs, color = "brown"):
		connectingPts = self.getBentPoints()
		for p1, p2 in zip(connectingPts[:len(connectingPts)-1], connectingPts[1:]):
			cvs.create_line(p1.getX(), p1.getY(), p2.getX(), p2.getY(), width = self.branchWidth, fill = color, capstyle = ROUND, smooth=True)

	def getTipPos(self):
		return self.basePos.getAdd(self.branchVect)

	def getBentPoints(self):
		points = [self.basePos, self.getTipPos()]
		endPt2 = points[-1]
		shiftVect = self.branchVect.getPerpendicularVect2D()
		minShift = 5
		maxShift = 10
		for i in range(self.timesBent):
			endPt1 = points[-2]
			u = random.uniform(0, 1)
			randomPt = endPt1.getScaled((1 - u))
			randomPt.add(endPt2.getScaled(u))
			shiftAmount = random.uniform(minShift, maxShift)
			shiftVect.scale(random.choice([-1, 1]))
			shiftVect.setMagnitude(shiftAmount)
			randomPt.add(shiftVect)
			points.insert(-1, randomPt)
		return points


class Tree:
	def __init__(self, trunk):
		self.branches = [trunk]
		self.terminalBranches = [trunk]

	def grow(self, maxBranchFactor = 4, maxGrowthAng = 45):
		while self.terminalBranches[0].branchWidth >= 0.7:
			for i in range(len(self.terminalBranches)-1, -1, -1):
				termBranch = self.terminalBranches.pop(i)
				newBasePos = termBranch.getTipPos()
				termBranchVect = termBranch.branchVect
				termBranchLen = termBranchVect.getMagnitude()
				for _ in range(random.randint(2, maxBranchFactor)):
					ang = random.uniform(-maxGrowthAng, maxGrowthAng + 1)
					newBranchVect = termBranchVect.getRotatedBy2D(ang)
					newBranchVect.setMagnitude(termBranchLen * random.uniform(0.3, 0.8))
					newBranch = Branch(newBasePos, newBranchVect, termBranch.branchWidth * 0.7, timesBent = 0)#int(newBranchVect.getMagnitude()//70))
					self.branches.append(newBranch)
					self.terminalBranches.append(newBranch)

	def drawOn(self, cvs, leafColor = "green"):
		for branch in self.branches:
			branch.drawOn(cvs)
		self.drawLeaves(cvs, leafColor)

	def drawAndAnimate(self, cvs, rootWin, leafColor = "green"):
		for branch in self.branches:
			branch.drawOn(cvs)
			rootWin.update()
		self.drawLeaves(cvs, leafColor)

	def drawLeaves(self, cvs, leafColor):
		rad = 2
		for branch in self.terminalBranches:
			tipPos = branch.getTipPos()
			cvs.create_oval(tipPos.getX() - rad, tipPos.getY() - rad, tipPos.getX() + rad, tipPos.getY() + rad, fill = leafColor, outline = leafColor)

if __name__ == "__main__":
	rootWin = Tk()
	rootWin.title("Procedural Tree - Fractal tree")

	WIDTH = 800
	HEIGHT = 650

	canvas = Canvas(rootWin, bg="white",height = HEIGHT, width = WIDTH)
	canvas.pack(side=LEFT)

	treeTrunk = Branch (Vector([WIDTH/2, HEIGHT - 10]), Vector([0,-200]), 15, timesBent = 0)
	tree = Tree(treeTrunk)
	tree.grow()
	tree.drawOn(canvas)
	rootWin.update()
	#tree.drawAndAnimate(canvas, rootWin)

	# treeTrunk = Branch (Vector([WIDTH/1.2, HEIGHT - 10]), Vector([0,-200]), 15, timesBent = 0)
	# tree = Tree(treeTrunk)
	# tree.grow()
	# tree.drawOn(canvas, leafColor = "magenta")
	# rootWin.update()

	# treeTrunk = Branch (Vector([WIDTH/4, HEIGHT - 10]), Vector([0,-200]), 15, timesBent = 0)
	# tree = Tree(treeTrunk)
	# tree.grow()
	# tree.drawOn(canvas, leafColor = "orange")
	# rootWin.update()

	rootWin.mainloop()

