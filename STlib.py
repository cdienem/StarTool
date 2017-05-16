#!/bin/python
import sqlite3, re, sys, time

class StarTool:
	# This stores the subqueries from all called select statements
	QUERY = []

	# This holds the current table in use
	CURRENT = ""

	# This holds the starfile-table associations
	# dict = { "starfilename" : ["table1", ...] }
	STARTABLES =  {}

	# if set to 1 no terminal output will be produced
	SILENT = 0

	# this holds the DB cursor
	CURSOR = None
	
	def __init__(self, silent):
		self.SILENT=silent
		

	def createDB(self, obj, fi=""):
		#this is a dummy method that will take over some functionality of __init__ 
		# Creates a DB (either memory or as a file)
		if obj == "mem":
			self.db = sqlite3.connect(':memory:')
			self.CURSOR = self.db.cursor()
		else:			
			self.db = sqlite3.connect(obj)
			self.CURSOR = seld.db.cursor()
			# Create STARTABLES if there is a file already
			self.CURSOR.execute("SELECT name FROM sqlite_master WHERE type='table';")
			tables = self.CURSOR.fetchall()
			ret = []
			self.STARTABLES[fi] = []
			for t in tables:
				self.STARTABLES[fi].append(t[0])
		self.db.create_function("REGEXP", 2, self.regexp)
		self.db.create_function('replace',3,self.preg_replace)

	def star2db(self, starfilename):
	# Reads the star file and saves it as a table in the DB
		self.STARTABLES[starfilename] =  []
		with open(starfilename) as f:
			# Walk through line by line
			name = ""
			labels = []
			data = []
			mode = ""
			# Get the data
			rr = f.read().splitlines()
			p = 1.0
			l = len(rr)
			for line in rr:
				if line[0:5] == "data_":
					# gets the table name
					name = line
				elif line[0:5] == "loop_":
					# gets into a loop thing and tells the program to expect just labels
					mode = "labels"
				elif line[0:4] == "_rln":
					if mode == "labels": # get normal labels here
						params = line.split()
						labels.append(params[0])
					else:
					# labels also hava data just behind
						params = line.split()
						labels.append(params[0])
						if len(data) == 0:
							data.append([])
						data[0].append(params[1])
						# since data came, set the mode
						mode = "data"
				elif line == "":
					# emtpy row, closes table if data was read before
					if mode == "data":
						self.makeTable(starfilename, name, labels, tuple(data))
						# Unset all the vars
						name = ""
						labels = []
						data = []
						mode = ""
				else:
					# mode has to be labels or data before
					if mode == "labels" or mode == "data":

						d = line.split()
						if len(d) != 0:
							# If there is empty fields, they will be filled with NULL
							if len(d) < len(labels):
								for i in range(len(labels)-len(d)):
									d.append("NULL")
							data.append(d)
							mode = "data"
				p = p+1
				self.updateProgress(p/l)
			# Check if reched end of file after a chunk of data
			if mode == "data":
				self.makeTable(starfilename, name, labels, tuple(data))



	# update_progress() : Displays or updates a console progress bar
	## Accepts a float between 0 and 1. Any int will be converted to a float.
	## A value under 0 represents a 'halt'.
	## A value at 1 or bigger represents 100%
	## Credit goes to Brian Khuu (StackOverflow)
	def updateProgress(self, progress):
		if self.SILENT == 0: # switchable output
		    barLength = 20 # Modify this to change the length of the progress bar
		    status = ""
		    if isinstance(progress, int):
		        progress = float(progress)
		    if not isinstance(progress, float):
		        progress = 0
		        status = "error: progress var must be float\r\n"
		    if progress < 0:
		        progress = 0
		        status = "Halt...\r\n"
		    if progress >= 1:
		        progress = 1
		        status = "Done...\r\n"
		    block = int(round(barLength*progress))
		    text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), round(progress*100,2), status)
		    sys.stdout.write(text)
		    sys.stdout.flush()


	def makeTable(self, starfilename, name, labels, data):
	# Creates the given table and fills it with data (overrides existing ones)
		fname = starfilename.split("/")[-1]
		fname = fname.split(".")
		tname = fname[0]+"_"+name
		self.STARTABLES[starfilename].append(tname)
		# go through first row and determine data types
		# removed performance bug here
		for i, field in enumerate(data[0]):
			if self.isReal(field):
				labels[i] += " REAL"
			else:
				labels[i] += " TEXT"
		
		# Join the labels and datatypes
		head = ",".join(labels)
		self.CURSOR.execute("CREATE TABLE IF NOT EXISTS \""+tname+"\"("+head+")")
		number = len(labels)*"?,"
		number = number.strip(",")
		for row in data:
			self.CURSOR.execute("INSERT INTO \""+tname+"\" VALUES ("+number+")",row)
		self.db.commit()

	def isReal(self, value):
	# Checks if the string read from a star file is actually a float value
		try:
			float(value)
			return True
		except ValueError:
			return False

	def showTable(self):
	# Simple debugging method to dump the content of a table
	# TODO: Implement a nicer printing
		l = ""
		for label in self.getLabels():
			l = l+str(label)+"  "
		self.out(l)
		for row in self.CURSOR.execute("SELECT * FROM ("+self.assembleSelector()+")"):
			# this excludes the first field which is the ROWID
			o = ""
			for field in row[1:]:
				o = o+str(field)+"  "
			self.out(o)

	def query(self, q):
	# This method allows experienced users to send SQL querys
	# SELECT querys will print the content
		if q[0:3] == "SEL" or q[0:3] == "sel":
			for row in self.db.execute(q):
				out = ""
				for field in row:
					out += "  "+str(field)
				print out

		else:
			self.CURSOR.execute(q)
			self.db.commit()

	def regexp(self, expr, item):
	# Python regex implementation for SQLite
		reg = re.compile(expr)
		return reg.search(str(item)) is not None

	def preg_replace(self, string, pattern, replace):
	# Python preg_replace implementation for SQLite
		return re.sub(pattern, replace, string)

	def getTables(self):
		self.CURSOR.execute("SELECT name FROM sqlite_master WHERE type='table';")
		tables = self.CURSOR.fetchall()
		ret = []
		for t in tables:
			ret.append(t[0])
		return ret

	def getLabels(self, table="current"):
		if table == "current":
			table = self.CURRENT
		self.CURSOR.execute("SELECT * FROM \""+table+"\"")
		labels = [t[0] for t in self.CURSOR.description]
		return labels

	def getCurrent(self):
		return self.CURRENT

	def debug(self):
		print "CURRENT: "+self.CURRENT
		#print self.QUERY
		print "Query: "+self.assembleSelector()
		print "STARTABLES: "
		print self.STARTABLES
		#for row in c.execute("SELECT rowid, oid, _rowid_ FROM ("+self.assembleSelector()+")"):
	#		print row

####### SELECTORS:

	def useTable(self, table):
		# Sets the current table
		self.CURRENT = table
		# Sets an initial selector
		self.QUERY.append("SELECT * FROM ?")

	def sortCol(self, col):
	# Sets ASC sorting for a column
		self.QUERY.append("SELECT * FROM ? ORDER BY \""+col+"\" ASC")

	def trosCol(self, col):
	# Sets DESC sorting for a column
		self.QUERY.append("SELECT * FROM ? ORDER BY \""+col+"\" DESC")

	def subset(self, ran):
	# Adds a LIMIT n OFFSET k statement to the queries
		self.QUERY.append("SELECT * FROM ? LIMIT "+str(ran[1]-ran[0]+1)+" OFFSET "+str(ran[0]-1))

	def select(self, col , mod, pattern):
		if pattern == "*":
			# Sets a dummy selection to a specific column
			self.QUERY.append("SELECT * FROM ? WHERE \""+col+"\" != ''")
		else:
			# Escape strings with 
			if type(pattern) == str or type(pattern) == unicode:
				pattern = "\""+pattern+"\"" # necessary for string patterns to be quoted in the query
			self.QUERY.append("SELECT * FROM ? WHERE \""+col+"\" "+mod+" "+str(pattern))

	def select_regex(self, col, pattern):
		self.QUERY.append("SELECT * FROM ? WHERE \""+col+"\" REGEXP '"+pattern+"'")

	def select_star(self, starfile, opts):
		# Starfile should be pre-loaded with star2db()
		# Retrieve the tablename of the reference star file
		reftable = self.STARTABLES[starfile][0]
		# Prepare query
		q = "SELECT * FROM ? AS t1 WHERE EXISTS (SELECT * FROM "+reftable+" AS t2 WHERE 1"
		# Go through the options
		for option in opts:
			# Exclude the ignored ones
			if option != None:
				if option[1] != 0:
					#Testing existensce of such parameters in the other table
					q += " AND t2."+option[0]+" BETWEEN t1."+option[0]+"-"+str(option[1])+" AND t1."+option[0]+"+"+str(option[1])+"" 
				else:
					q += " AND t2."+option[0]+"=t1."+option[0]+""
		# Add closing bracket
		q+=")"
		# Append to selector
		self.QUERY.append(q)

	def getTableNum(self, starfile):
		return len(self.STARTABLES[starfile])
			
	def assembleSelector(self):
		# this assembles a nested query for the selections that have been made
		# replaces "?" by the current table (for the first entry) or by the 
		for i in range(len(self.QUERY)):
			if i == 0:
				select = self.QUERY[i].replace("FROM ?", "FROM \""+self.CURRENT+"\"")
				# introduces the ROWID in selection statement to make it available at the very end
				select = select.replace("SELECT ", "SELECT ROWID,")
			else:
				select = self.QUERY[i].replace("FROM ?","FROM ("+select+")")
		return select

	def releaseTable(self):
	# Unsets current table, selectors and sorters
		self.CURRENT = ""
		self.QUERY = ["SELECT * FROM ?"]

	def deselect(self):
	# Unsets current selections
		self.QUERY = ["SELECT * FROM ?"]


######## EDITORS:

	def addCol(self, col):
	# Adds a column to the table
	# Default is type TEXT, upon filling, the 
	# values are checked and type might be changed
		q = "ALTER TABLE \""+self.CURRENT+"\" ADD COLUMN \""+col+"\" TEXT"
		self.CURSOR.execute(q)
		self.db.commit()

	def deleteCol(self, col):
	# This needs a workaround since DROP COLUMN isnt supported by sqlite	
	#BEGIN TRANSACTION;
	#CREATE TEMPORARY TABLE t1_backup(a,b);
	#INSERT INTO t1_backup SELECT a,b FROM t1;
	#DROP TABLE t1;
	#CREATE TABLE t1(a,b);
	#INSERT INTO t1 SELECT a,b FROM t1_backup;
	#DROP TABLE t1_backup;
	#COMMIT;
		self.CURSOR.execute("SELECT * FROM \""+self.CURRENT+"\"")
		labels = self.getLabels()
		labels.remove(col)
		self.CURSOR.execute("CREATE TEMPORARY TABLE tmp("+",".join(labels)+")")
		self.CURSOR.execute("INSERT INTO tmp SELECT "+",".join(labels)+" FROM \""+self.CURRENT+"\"")
		self.CURSOR.execute("DROP TABLE \""+self.CURRENT+"\"")
		self.CURSOR.execute("CREATE TABLE \""+self.CURRENT+"\"("+",".join(labels)+")")
		self.CURSOR.execute("INSERT INTO \""+self.CURRENT+"\" SELECT "+",".join(labels)+" FROM tmp")
		self.CURSOR.execute("DROP TABLE tmp")
		self.db.commit()

	def renameCol(self, col, newcolname):
		# Uses similar workaround as deleteCol
		self.CURSOR.execute("SELECT * FROM \""+self.CURRENT+"\"")
		labels = self.getLabels(self.CURRENT)
		newlabels = list(labels)
		newlabels[newlabels.index(col)] = newcolname
		self.CURSOR.execute("CREATE TEMPORARY TABLE tmp("+",".join(labels)+")")
		self.CURSOR.execute("INSERT INTO tmp SELECT "+",".join(labels)+" FROM \""+self.CURRENT+"\"")
		self.CURSOR.execute("DROP TABLE \""+self.CURRENT+"\"")
		self.CURSOR.execute("CREATE TABLE \""+self.CURRENT+"\"("+",".join(newlabels)+")")
		self.CURSOR.execute("INSERT INTO \""+self.CURRENT+"\" SELECT "+",".join(labels)+" FROM tmp")
		self.CURSOR.execute("DROP TABLE tmp")
		self.db.commit()

	def renameTable(self, newtablename):
		q = "ALTER TABLE \""+self.CURRENT+"\" RENAME TO \""+newtablename+"\""
		self.CURSOR.execute(q)
		self.db.commit()
		# Rename in STARTABLES
		for t in self.STARTABLES.keys():
			if self.CURRENT in self.STARTABLES[t]:
				self.STARTABLES[t][self.STARTABLES[t].index(self.CURRENT)] = newtablename
				break
		self.CURRENT = newtablename


	def removeTable(self, table):
		self.CURSOR.execute("DROP TABLE \""+table+"\"")
		self.db.commit()
		for t in self.STARTABLES.keys():
			if self.CURRENT in self.STARTABLES[t]:
				self.STARTABLES[t].pop(self.STARTABLES[t].index(self.CURRENT))
				break
		if table == self.CURRENT:
			self.releaseTable()

	def getRawTablename(self,table):
		for star in self.STARTABLES:
			if table in self.STARTABLES[star]:
				n = star.replace(".star","")
				if re.search(n,self.CURRENT) != None:
					name = self.CURRENT.replace(n+"_","")
				else:
					name = "data_"+self.CURRENT
		return name

	def mergeStar(self,starfile):
		# merges all starfiles currently read 
		# they should only consist of one table each with the same name
		# implement a merge clean option that check for duplicates
		tables = []
		labels = []
		tab = ""
		# collect tables of mergable starfiles
		for star in self.STARTABLES:
			if len(self.STARTABLES[star]) == 1:
				
				if tab == "":
					tab = self.getRawTablename(self.STARTABLES[star][0])
					tables.append(self.STARTABLES[star][0])
					labels.append(self.getLabels(self.STARTABLES[star][0]))
				else:
					# collect their labels if their raw tables mattch
					if self.getRawTablename(self.STARTABLES[star][0]) == tab:
						tables.append(self.STARTABLES[star][0])
						labels.append(self.getLabels(self.STARTABLES[star][0]))
		# manually calculate the intersection of all lable lists stored in labels
		m = 0
		labels_intersect = []
		for l in labels[0]:
			for labelset in labels:
				if l in labelset:
					m = m+1
			if m == len(labels):
				labels_intersect.append(l)
			m = 0


		# create tmp table, put all data there
		# hijack write_selection to write this table
		self.CURSOR.execute("CREATE TEMPORARY TABLE tmp_"+tab+"("+",".join(labels_intersect)+")")
		self.db.commit()
		for t in tables:
			self.CURSOR.execute("INSERT INTO tmp_"+tab+" SELECT "+",".join(labels_intersect)+" FROM \""+t+"\"")
			self.db.commit()
		bak_cur = self.CURRENT
		bak_que = self.QUERY
		self.CURRENT = "tmp_"+tab
		self.QUERY = ["SELECT * FROM ?"]
		self.STARTABLES["tmp"] = ["tmp_"+tab]
		self.writeSelection(starfile)
		self.CURRENT = bak_cur
		self.QUERY = bak_que
		del(self.STARTABLES["tmp"])
		self.CURSOR.execute("DROP TABLE tmp_"+tab)
		self.db.commit()


	def replace(self, col, val):
		# Check type of val here
		if type(val) == str:
			val = "'"+val+"'"
		else:
			val = str(val)
		# Asseble the query
		q = "UPDATE \""+self.CURRENT+"\" SET \""+col+"\"="+val+" WHERE ROWID IN (SELECT ROWID FROM ("+self.assembleSelector()+"))"
		self.CURSOR.execute(q)
		self.db.commit()

	def replace_star(self, col, starfile, opts):
		# Starfile should be pre-loaded with star2db()
		# Retrieve the tablename of the reference star file
		reftable = self.STARTABLES[starfile][0]
		# Prepare query

		# UPDATE t1.col = (select t2.col FROM t2 AS t2 WHERE t2.col = t1.col)

		q1 = "UPDATE \""+self.CURRENT+"\" SET "+col+" = (SELECT "+reftable+"."+col+" FROM "+reftable+" WHERE 1"
		q2 = " WHERE EXISTS (SELECT * FROM \""+reftable+"\" WHERE 1"
		# Go through the options
		for option in opts:
			# Exclude the ignored ones
			if option != None:
				if option[1] != 0:
					#Testing existensce of such parameters in the other table
					q1 += " AND "+reftable+"."+option[0]+" BETWEEN "+self.CURRENT+"."+option[0]+"-"+str(option[1])+" AND "+self.CURRENT+"."+option[0]+"+"+str(option[1])+"" 
					q2 += " AND "+reftable+"."+option[0]+" BETWEEN "+self.CURRENT+"."+option[0]+"-"+str(option[1])+" AND "+self.CURRENT+"."+option[0]+"+"+str(option[1])+"" 
					pass
				else:
					q1 += " AND "+reftable+"."+option[0]+"="+self.CURRENT+"."+option[0]+""
					q2 += " AND "+reftable+"."+option[0]+"="+self.CURRENT+"."+option[0]+""
					pass
				
		# Append to selector
		q1 += ")"
		q2 += ")"
		
		query = q1+q2
		query += " AND "+self.CURRENT+".ROWID IN (SELECT ROWID FROM ("+self.assembleSelector()+"))"
		print query
		self.CURSOR.execute(query)
		self.db.commit()
		

	def replace_regex(self, col, search, repl):
		self.CURSOR.execute("UPDATE \""+self.CURRENT+"\" SET \""+col+"\"=replace("+col+",?,?) WHERE ROWID IN (SELECT ROWID FROM ("+self.assembleSelector()+"))",(search,repl,))
		self.db.commit()




	def deleteSelection(self):
		q = "DELETE FROM \""+self.CURRENT+"\" WHERE ROWID in (SELECT ROWID FROM ("+self.assembleSelector()+"))"
		self.CURSOR.execute(q)
		self.db.commit()

	def doMath(self, field, a, operator, b):
		# a and b can be values (number) or field names of the current table in use
		# method for doing simple math tasks like
		# add: +
		# subtract: -
		# multiply: *
		# devide: /
		# power: ** 
		# root: will be done as fractional pow
		# math is done on the current selection	
		if operator == "+":
			self.CURSOR.execute("UPDATE "+self.CURRENT+" SET \""+field+"\" = \""+a+"\" + \""+b+"\" WHERE ROWID in (SELECT ROWID FROM ("+self.assembleSelector()+"))")
		elif operator == "-":
			self.CURSOR.execute("UPDATE "+self.CURRENT+" SET \""+field+"\" = \""+a+"\" - \""+b+"\" WHERE ROWID in (SELECT ROWID FROM ("+self.assembleSelector()+"))")
		elif operator == "/":
			self.CURSOR.execute("UPDATE "+self.CURRENT+" SET \""+field+"\" = \""+a+"\" / \""+b+"\" WHERE ROWID in (SELECT ROWID FROM ("+self.assembleSelector()+"))")
		elif operator == "*":
			self.CURSOR.execute("UPDATE "+self.CURRENT+" SET \""+field+"\" = \""+a+"\" * \""+b+"\" WHERE ROWID in (SELECT ROWID FROM ("+self.assembleSelector()+"))")
		elif operator == "**":
			pass
		pass



	def countRows(self, table):
		self.CURSOR.execute("select count(*) from \""+table+"\"")
		return str(self.CURSOR.fetchone()[0])


	def info(self):
		for t in self.STARTABLES.keys():
			print t
			for table in self.STARTABLES[t]:
				print "\t"+table+" ("+self.countRows(table)+" rows)"
				for l in self.getLabels(table):
					print "\t\t"+l
			if len(self.STARTABLES.keys()) > 1:
				print "\n\n"

	def splitBy(self, colname, batch=-1):
# Two ways of splitting: by uniques or into batches
		if batch == -1:
			# Works on the current selection
			q = self.CURSOR.execute("SELECT DISTINCT \""+colname+"\" FROM \""+self.CURRENT+"\" WHERE ROWID in (SELECT ROWID FROM ("+self.assembleSelector()+"))" )
			uniques = q.fetchall()
			for entry in uniques:
				# Adds another layer of selection
				self.select(colname , "=", entry[0])
				# In case of filenames in uniques
				if "/" in str(entry[0]):
					name = str(entry[0]).rsplit("/",1)[1]
				else:
					name = str(entry[0])
				self.writeSelection(name+".star")
				# Need to remove the last selection from the QUERY in order to proceed to the next unique
				del(self.QUERY[-1])
		else:
			# count current selection
			self.CURSOR.execute("SELECT COUNT(*) FROM \""+self.CURRENT+"\" WHERE ROWID in (SELECT ROWID FROM ("+self.assembleSelector()+"))")
			num = self.CURSOR.fetchone()[0]
			per_batch = int(num) // int(batch)
			for i in range (0, batch):
				start = i*per_batch+1
				if i != batch-1:
					stop = start+per_batch-1
				else:
					stop = num
				self.subset([start,stop])
				self.writeSelection("batch_"+str(i+1)+".star")
				del(self.QUERY[-1])
		

	def writeSelection(self, starfilename, mode="w+"):
	# writes the current selection
	# std mode is overide (w+)d
	# is also used by writeStar
	# Extract table name for star file
	# account for renamed tables not having the _data_ anymore
	# This is fishy if the filename contains 'data'
		for star in self.STARTABLES:
			if self.CURRENT in self.STARTABLES[star]:
				n = star.replace(".star","")
				if re.search(n,self.CURRENT) != None:
					name = self.CURRENT.replace(n+"_","")
				else:
					name = "data_"+self.CURRENT
		
		labels = self.getLabels()
		# gets the data rows that are in the labels
		fields = ",".join(labels)
		exe = self.CURSOR.execute("SELECT "+fields+" FROM ("+self.assembleSelector()+")")
		data = exe.fetchall()
		if len(data) == 1:
			with open(starfilename,mode) as f:
				f.write("\n")
				f.write(name)
				f.write("\n\n")
				for i in range(len(labels)):
					f.write(labels[i]+"  "+str(data[0][i])+"\n")
			f.close()
			pass
		else:
			with open(starfilename,mode) as f:
				f.write("\n")
				f.write(name)
				f.write("\n\n")
				f.write("loop_\n")
				for i in range(len(labels)):
					f.write(labels[i]+" #"+str(i+1)+"\n")
				# put data there
				for row in data:
					for item in row:
						f.write("  "+str(item))
					f.write("\n")
				f.write("\n")
			f.close()
			
	def writeStar(self, outstar, instar="current"):
		# Hijacks the writeSelection method by setting CURRENT and QUERY
		# restores it afterwards
		bak_cur = self.CURRENT
		bak_que = list(self.QUERY)
		if instar == "current":
			instar = self.CURRENT
		# look where it belongs
		for st in self.STARTABLES.keys():
			if instar in self.STARTABLES[st]:
				star = st
				tables = list(self.STARTABLES[st])
				break
		i = 0
		for table in tables:
			if i == 0:
				mode = "w+"
				i = 1
			else:
				mode = "a+"
			self.CURRENT = table
			self.QUERY = []
			self.QUERY.append("SELECT * FROM ?")
			self.writeSelection(outstar,mode)
		#restore query and current
		self.QUERY = list(bak_que)
		self.CURRENT = list(bak_cur)

	def out(self, content):
		if self.SILENT == 0:
			print content

	def isSilent(self):
		if self.SILENT == 1:
			return True
		else:
			return False