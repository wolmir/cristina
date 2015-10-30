import pygame
import random

class Grid():
	SPACING_X = 65#50
	SPACING_Y = 100 #60
	START_X = 35#SPACING_X
	START_Y = 200 #175
	END_X = 640
	END_Y = 550

	def __init__(self):
		#self.num_rows = 0
		#self.num_columns = 0
		self.rows = list()

		self.num_rows = 10 #(self.END_X - self.START_X) / self.SPACING_X 
		self.num_columns = 4 #(self.END_Y - self.START_Y) / self.SPACING_Y 

		for x in range( self.num_rows ):
			row = list()
			pos_x = self.START_X + ( x * self.SPACING_X)

			for y in range ( self.num_columns ):
				pos_y = self.START_Y + ( y * self.SPACING_Y)
				node = Node(x,y)
				node.pos = ( pos_x, pos_y) 
				row.append( node )
			
			self.rows.append( row )

		print "Rows: " + str(self.num_rows) + "  Columns: " + str(self.num_columns)

	def getNode(self, row, column):
		if row > self.num_rows or row < 0:
			return None
		if column > self.num_columns or column < 0:
			return None
		return self.rows[row][column]

	def setNode(self, row, column, flower):
		if row >= self.num_rows or row < 0:
			return False
		if column >= self.num_columns or column < 0:
			return False
		if self.rows[row][column].isFilled():
			return False
		#print "Row: " + str(row) + "  Column: " + str(column)
		flower.setPosition( row, column, self.rows[row][column].pos )
		self.rows[row][column].flower = flower
		return True

	def isThereVacantNode(self):
		for row in self.rows:
			for node in row:
				if not node.isFilled():
					return True
		return False

	def draw(self, surface):
		for row in self.rows:
			for node in row:
				pygame.draw.circle( surface, 
									(255,255,255), 
									node.pos,
									2 )

	def getSurroundingNodes(self, row, column ):
		surroundingNodes = []
		if row+1 < self.num_rows:
			surroundingNodes.append( self.rows[row+1][column] )
			if column+1 < self.num_columns:
				surroundingNodes.append( self.rows[row+1][column+1] )
			if column-1 >= 0:
				surroundingNodes.append( self.rows[row+1][column-1] )
		if row-1 >= 0:
			surroundingNodes.append( self.rows[row-1][column] )
			if column+1 < self.num_columns:
				surroundingNodes.append( self.rows[row-1][column+1] )
			if column-1 >= 0:
				surroundingNodes.append( self.rows[row-1][column-1] )
		if column+1 < self.num_columns:
			surroundingNodes.append( self.rows[row][column+1] )
		if column-1 >= 0:
			surroundingNodes.append( self.rows[row][column-1] )
		return surroundingNodes

	def findRandomEmptySurroundingNode( self, row, column ):
		surroundingNodes = self.getSurroundingNodes( row, column )
		emptySurroundingNodes = []
		for node in surroundingNodes:
			if not node.isFilled():
				emptySurroundingNodes.append(node)
		if emptySurroundingNodes:
			chooseNode = random.randrange(len(emptySurroundingNodes))
			return emptySurroundingNodes[chooseNode]
		else:
			return None

	def findNodeWithEmpty( self, row, column ):
		surroundingNodes = self.getSurroundingNodes( row, column )
		emptySurroundingNodes = []
		for node in surroundingNodes:
			if not node.isFilled():
				emptySurroundingNodes.append(node)
		if emptySurroundingNodes:
			return self.rows[row][column]
		else:
			return None

class Node():
	def __init__(self, rowIndex, columnIndex, flower=None):
		self.flower = flower
		self.pos = (0,0)
		self.rowIndex = rowIndex
		self.columnIndex = columnIndex

	def isFilled(self):
		if self.flower != None:
			return True
		else:
			return False