#!/bin/python

"""
This module contains a STAR file parser that returns a STAR file object

A STAR file obj has the following methods:

#I/O methods
starfile.read(filename)
starfile.write(filename)

# Getter methods
starfile.getFilename() -> returns filename
starfile.getTables() -> returns list of tablenames
starfile.getLabels(str tablename) -> returns a list of labels
starfile.getTypes(str tablename) -> returns a list with data types (string, float or integer)
starfile.getType(str labelname) -> returns the type of a label
starfile.getCol(str labelname or int column index)
starfile.getRow(int index)
starfile.getRaw(str table) -> returns a nested row-by-row list of data

# The DATA attribute stores all data in some kind of simple data frame and can be accessed in various ways by the getter methods

starfile.DATA {
	"filename": {
		"tablename" : {
			labels : {
				"labelname" : {
					type : str/int/float
					col_id : column index stores original position
				}
			}
			label : [row 1, row 2, ...]
		}
	}
}

This itself might be broken down into table, label etc. objects in future.

The module can be extended to actually perform simple STAR-file editing functionalities directly on the dictionary stored data.

This module can be implemented in a multi-STAR file framework.
"""

class StarFile(object):

	# Allowed label identifyers
	label_identifyers = ["_rln", "_wrp"]

	def __init__(self):
		# creates a starfile object
		self.DATA = {}

	def read(self, starfilename):
		# Reads the star file and saves it in self.DATA

		# Note for OOP: break down the label and data adding into submethods

		# Create dictionary for the starfile
		self.DATA[starfilename] = {}
		# Open the file
		with open(starfilename) as infile:
			# Get the data as an itaratible
			raw_data = iter(infile.read().splitlines())
			while True:
				try:
					line = raw_data.next()
					
					if line[0:5] == "data_":
						# Extracts the table name
						table = self.addTable(line)

					elif line [0:4] in self.label_identifyers:
						# Put exception here if there is a single entry table!
						labels = line.split()
						if labels[-1][0] == "#":
							# Multi entry table
							self.DATA[starfilename][table]["labels"][labels[0]] = { "type" : "", "col_id" : int(labels[1].replace("#",""))}
							# Create list that will be filled with data fields
							self.DATA[starfilename][table][labels[0]] = []
						else:
							self.DATA[starfilename][table]["labels"][labels[0]] = { "type" : self.whatType(labels[1]), "col_id" : int(len(self.DATA[starfilename][table]["labels"])+1)}
							self.DATA[starfilename][table][labels[0]] = []
							self.DATA[starfilename][table][labels[0]].append(labels[1])
							#Single entry table
					else:
						if line.strip() != "" and line[0:5] != "loop_":
							data_fields = line.split()
							for field_index in  range(len(data_fields)):
								self.DATA[starfilename][table][self.getLabelByIndex(table, field_index+1)].append(data_fields[field_index])
								if self.DATA[starfilename][table]["labels"][self.getLabelByIndex(table, field_index+1)]["type"] == "":
									self.DATA[starfilename][table]["labels"][self.getLabelByIndex(table, field_index+1)]["type"] = self.whatType(data_fields[field_index])
				except StopIteration:
					# Stop the loop when it reached EOF
					break
	
	def whatType(self, value):
		if "." in value:
			try:
				float(value)
				return "FLOAT"
			except ValueError:
				return "STRING"
		# still might be int
		else:
			try:
				int(value)
				return "INTEGER"
			except ValueError:
				return "STRING"

	def addTable(self, tablename):
		self.DATA[self.getFilename()][tablename] = {}
		self.DATA[self.getFilename()][tablename]["labels"] = {}
		return tablename

	def getLabelByIndex(self, tablename, index):
		for label in self.DATA[self.getFilename()][tablename]["labels"]:
			if self.DATA[self.getFilename()][tablename]["labels"][label]["col_id"] == index:
				return label


	def getFilename(self):
		return self.DATA.keys()[0]

	def getTables(self):
		return self.DATA[self.getFilename()].keys()

	def getLabels(self, tablename):
		return self.DATA[self.getFilename()][tablename]["labels"].keys()

	def getTypes(self, tablename):
		types = []
		for label in self.DATA[self.getFilename()][tablename]["labels"].keys():
			types.append(self.DATA[self.getFilename()][tablename]["labels"][label]["type"])
		return types

	def getType(self, tablename, label):
		return self.DATA[self.getFilename()][tablename]["labels"][label]["type"]

	def getColumn(self, tablename, column):
		if type(column) == int:
			return self.DATA[self.getFilename()][tablename][self.getLabelByIndex(tablename, column)]
		else:
			return self.DATA[self.getFilename()][tablename][column]

	def getRow(self, tablename, index):
		row = []
		for column in self.getLabels(tablename):
			row.append(self.getColumn(tablename, column)[index-1])
		return row

	def getRawData(self, tablename):
		# append a list for each label
		# take each column and fill them according to their col id
		
		pass

star = StarFile()
star.read("2test_twotable.star")
#print star.getFilename()
#print star.getTables()
#print star.getLabels(star.getTables()[0])
#print star.getTypes(star.getTables()[1])
#print star.getType(star.getTables()[1], star.getLabels(star.getTables()[1])[0])

#print star.getColumn(star.getTables()[1],2)
print star.getRawData(star.getTables()[0])
print star.getRawData(star.getTables()[1])

#print star.DATA