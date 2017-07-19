#!/bin/python
import argparse, sys, os.path, re
import STlib

version="1.3"



# Extends the argparse module to store ordered args in a separate namespace
class store_ordered(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not 'ordered_args' in namespace:
            setattr(namespace, 'ordered_args', [])
        previous = namespace.ordered_args
        previous.append((self.dest, values))
        setattr(namespace, 'ordered_args', previous)

parser = argparse.ArgumentParser(prog="startool", 
								description="Swiss army knife for editing star files",
								epilog="t")

parser.add_argument('inputfile', action='store')

parser.add_argument('--info', action=store_ordered, nargs='?', metavar="None")
parser.add_argument('--show', action=store_ordered, nargs='?', metavar="None")
parser.add_argument('--debug', action=store_ordered, nargs='?', metavar="None")
parser.add_argument('--silent', action=store_ordered, nargs='?', metavar="None")

#Selectors
parser.add_argument('--use', action=store_ordered, metavar="tablename")


parser.add_argument('--select', action=store_ordered, metavar="_rlnLabel\><=value")

parser.add_argument('--select_regex', action=store_ordered, metavar="_rlnlabel='regular expression'")

parser.add_argument('--select_star', action=store_ordered, metavar="starfile.star:_rlnLabelA"+u"\u27e6"+"variationA"+u"\u27e7"+",_rlnLabelB")

parser.add_argument('--subset', action=store_ordered, metavar="start:end")

parser.add_argument('--release', action=store_ordered, nargs='?', metavar="None")

parser.add_argument('--deselect', action=store_ordered, nargs='?', metavar="None")

#Sorters
parser.add_argument('--sort', action=store_ordered, metavar="_rlnLabel")
parser.add_argument('--tros', action=store_ordered, metavar="_rlnLabel")



#Global Editors
parser.add_argument('--add_col', action=store_ordered, metavar="_rlnNewLabel")
parser.add_argument('--delete_col', action=store_ordered, metavar="_rlnLabel")
parser.add_argument('--rename_col', action=store_ordered, metavar="_rlnOldLabel=_rlnNewLabel")

parser.add_argument('--delete_table', action=store_ordered, metavar="tablename")
parser.add_argument('--rename_table', action=store_ordered, metavar="new_tablename")

#Local Editors
parser.add_argument('--replace', action=store_ordered, metavar="_rlnLabel=value")
parser.add_argument('--replace_regex', action=store_ordered, metavar="_rlnLabel='search'%'replace'")
parser.add_argument('--replace_star', action=store_ordered, metavar="_rlnLabel=starfile.star:_rlnRefLabelA"+u"\u27e6"+"variationA"+u"\u27e7"+",_rlnRefLabelB"+u"\u27e6"+"variationB"+u"\u27e7"+"")

# Deletes stuff from the local selection
parser.add_argument('--delete', action=store_ordered, nargs='?', metavar="None")



#Special
parser.add_argument('--query', action=store_ordered, metavar="SQLite query")
parser.add_argument('--math', action=store_ordered, metavar="_rlnLabel=A operator B") # still experimental

# Output
parser.add_argument('--split_by', action=store_ordered, metavar="_rlnLabel:number of batches")
parser.add_argument('--merge', action=store_ordered, metavar="starfilename.star")
parser.add_argument('--writef', action=store_ordered, metavar="starfilename.star")
parser.add_argument('--writef_selection', action=store_ordered, metavar="starfilename.star")
parser.add_argument('--write', action=store_ordered, metavar="starfilename.star")
parser.add_argument('--write_selection', action=store_ordered, metavar="starfilename.star")

# parse the arguments
args = parser.parse_args()


# Start the instance in verbose or silent mode
if hasattr(args, "ordered_args") and ('silent',None) in args.ordered_args:
	stardb = STlib.StarTool(1)
else:
	stardb = STlib.StarTool(0)

# Load the input file(s) and store in memory if not specified otherwise
# If there is the location specified, split it

stardb.out( "### StarTool "+version+" (by Chris) ###")
if ":" in args.inputfile:
	part = args.inputfile.split(":")
	if part[1] == "mem":
		stardb.out( "Starting StarTool in memory\n")
		stardb.createDB("mem")
		# Get filenames to load
		for fil in part[0].split(","):
			stardb.out( "Loading "+fil+"...")
			if os.path.isfile(fil):
				stardb.star2db(fil)
			else:
				stardb.out( "File "+fil+" does not exist.\n")
	else:
		stardb.out( "Starting StarTool with local DB ("+part[1]+")\n")
		make="no"
		if not os.path.isfile(part[1]) or os.stat(part[1]).st_size == 0:
			make = "yes"
		stardb.createDB(part[1], part[0])
		if make == "yes":
			for fil in part[0].split(","):
				stardb.out( "Loading "+fil+"...")
				if os.path.isfile(fil):
					stardb.star2db(fil)
				else:
					stardb.out( "File "+fil+" does not exist.\n")
			
else:
	stardb.out( "Starting StarTool in memory\n")
	stardb.createDB("mem")
	part = []
	part.append(args.inputfile)
	# Get filenames to load
	for fil in part[0].split(","):
		stardb.out( "Loading "+fil+"...")
		if os.path.isfile(fil):
			stardb.star2db(fil)
		else:
			stardb.out( "File "+fil+" does not exist.\n")



# Check if there is only one table and use it
if len(stardb.getTables()) == 1:
	stardb.useTable(stardb.getTables()[0])
	stardb.out( "\nOnly one input table read, using "+stardb.getTables()[0])

# Check if optional ordered commands were given
if hasattr(args, "ordered_args"):
# Walk through commands and do 
	for cmd in args.ordered_args:
# Methods without restrictions
		stardb.out( "\nEXECUTE: --"+str(cmd[0])+" "+str(cmd[1]).replace("None",""))
		if cmd[0] == "info":
			# None
			stardb.info()

		elif cmd[0] == "use":
			# Tablename
			if cmd[1] in stardb.getTables():
				stardb.useTable(cmd[1])
			else:
				stardb.out( cmd[1]+" does not exist...")
		elif cmd[0] == "deselect":
			# none
			stardb.deselect()

		elif cmd[0] == "merge":
			# starfilename.star
			if os.path.isfile(cmd[1]):
				if stardb.isSilent() != True:
					stardb.out( "The file '"+str(cmd[1])+"' already exists.")
					ans = raw_input("Do you want to override (y/n)?")
					if ans == "y":
						stardb.out( "Overriding the file.")
						stardb.mergeStar(cmd[1])
					else:
						stardb.out( "Not overriding.")
				else:
					stardb.mergeStar(cmd[1])
			else:
				stardb.mergeStar(cmd[1])

		elif cmd[0] == "query":
			# just accept it here
			stardb.query(cmd[1])
			stardb.out( "Executing custom query ('"+cmd[1]+"')...")

		elif cmd[0] == "delete_table":
			# None
			# No restriction
			if cmd[1] in stardb.getTables():
				stardb.removeTable(cmd[1])
			else:
				stardb.out( "Cannot delete '"+cmd[1]+"' because it does not exist.")

		elif cmd[0] == "debug":
			# prints some debug information
			stardb.debug()

		elif cmd[0] == "split_by":
			# _rlnLabel:10 || _rlnlabel
			c = cmd[1].split(":")
			if len(c) == 1:
				batch = -1;
			else:
				batch = int(c[1])

			if c[0] in stardb.getLabels():
				stardb.splitBy(cmd[1],batch)
			else:
				stardb.out("Please provide a column name that exists.")

		else:
			# go here with comands that have restrictions
			# Methods that need a table selected
			if stardb.getCurrent() != "":
				if cmd[0] == "show":
					# None
					stardb.showTable()

				elif cmd[0] == "release":
					# None
					stardb.releaseTable()

				elif cmd[0] == "add_col":
					# _rlnLabel
					if cmd[1] not in stardb.getLabels():
						stardb.addCol(cmd[1])
					else:
						stardb.out( "Column '"+cmd[1]+"' already exists.")

				elif cmd[0] == "delete_col":
					# _rlnLabel
					cols = cmd[1].split(",")
					for col in cols:
						if col in stardb.getLabels():
							stardb.deleteCol(col)
						else:
							print "Cannot delete column '"+col+"' because it does not exist.\n"

				elif cmd[0] == "rename_col":
					#_rlnLabelOld=_rlnLabelNew			
					if True: # here will be the pattern matching
						old = cmd[1].split("=")[0]
						new = cmd[1].split("=")[1]
						if old in stardb.getLabels() and new not in stardb.getLabels():
							stardb.renameCol(old, new)
						else:
							stardb.out( "Cannot rename '"+old+"' to '"+new+"' because it either does not exist or the new name is already taken.\n")
					else:
						stardb.out( "The input is malformed (--rename).\n")

				
				elif cmd[0] == "sort":
					# _rlnLabel
					if cmd[1] in stardb.getLabels():
						stardb.sortCol(cmd[1])
					else:
						stardb.out( "Column "+cmd[1]+" does not exist.")

				elif cmd[0] == "tros":
					# _rlnLabel
					if cmd[1] in stardb.getLabels():
						stardb.trosCol(cmd[1])
					else:
						stardb.out( "Column "+cmd[1]+" does not exist.")
					
				elif cmd[0] == "subset":
					# 1:100
					res = re.search("^([0-9]+):([0-9]+)$",str(cmd[1]))
					if res != None:
						stardb.subset([int(res.group(1)),int(res.group(2))])
					else:
						stardb.out( "Your input is malformed (--subset).")

				elif cmd[0] == "rename_table":
					# TablenameNew
					if cmd[1] not in stardb.getTables():					
						stardb.renameTable(cmd[1])
					else:
						stardb.out( "Cannot rename '"+stardb.getCurrent()+"' to '"+cmd[1]+"' because the new name is already taken.\n")

				elif cmd[0] == "select":
					# _rlnLabel <=|>=|<|>|!=|= value
					# Split the command here and get all three parts of it
					# ^\_rln(.*?)(>=|<=|!=|>|<|=){1}(.*)$	
					if cmd[1] != None:
						pat = "^\_rln(.*?)(>=|<=|!=|>|<|=){1}(.*)$"
						match = re.search(pat,cmd[1])
						if match != None:
							col = "_rln"+match.group(1)
							if col in stardb.getLabels():
								op = match.group(2)
								val = match.group(3)
								stardb.select(col, op, val)
							else:
								stardb.out( "Column "+col+" does not exist.")
						else:
							stardb.out( "Your input is malformed. Please add a valid operator (--select).")

				elif cmd[0] == "select_regex":
					# _rlnLabel='regex'
					# _rlnLabel=regexp
					if cmd[1] != None and cmd[1].split("=")[0] in stardb.getLabels() and cmd[1].split("=")[1] != "":
						com = cmd[1].split("=")
						stardb.select_regex(com[0], com[1])
					else:
						stardb.out( "Your input is malformed (--select_regex).")

				elif cmd[0] == "select_star":
					# ref.star:_rlnA[var],_rlnB[var]
					file = cmd[1].split(":")[0]
					options = cmd[1].split(":")[1].split(",")
					if os.path.isfile(file):
						# Load the reference STAR file
						stardb.star2db(file)
						# check if there is a single table
						if stardb.getTableNum(file) == 1:
							# extract variations (if present)
							for i in range(len(options)):
								o = options[i].split("[")
								if len(o) == 1:
									options[i] = [o[0],0]
								else:
									try:
										num = float(o[1].replace("]",""))
										options[i] = [o[0],num]
									except ValueError:
										stardb.out("The variation value must be a number.")
										options[i] = None
							stardb.select_star(file, options)
						else:
							stardb.out("The reference STAR file should only contain a single table.")			
					else:
						stardb.out("The reference file "+str(file)+" does not exist.")

				elif cmd[0] == "replace":
					# _rlnLabel=valueABC
					com = cmd[1].split("=")
					if com[0] in stardb.getLabels():
						stardb.replace(com[0],com[1])
					else:
						stardb.out( "Column "+com[0]+" does not exist (--replace).")

				elif cmd[0] == "replace_regex":
					# _rlnLabel=search%replace
					com = cmd[1].split("=")
					if com[0] in stardb.getLabels():
						pat = com[1].split("%")
						stardb.replace_regex(com[0],pat[0],pat[1])
					else:
						stardb.out( "Column "+com[0]+" does not exist (--replace_regex).")

				elif cmd[0] == "replace_star":
					# _rlnLabel=ref.star:_rlnA[var],_rlnB[var]
					label = cmd[1].split("=")[0] 
					file = cmd[1].split("=")[1].split(":")[0]
					options = cmd[1].split(":")[1].split(",")
					if label in stardb.getLabels(): 
						if os.path.isfile(file):
							# Load the reference STAR file
							# EXCEPTION HANDLING!
							stardb.star2db(file)
							if stardb.getTableNum(file) == 1:
								
								# extract variations (if present)
								for i in range(len(options)):
									o = options[i].split("[")
									if len(o) == 1:
										options[i] = [o[0],0]
									else:
										try:
											num = float(o[1].replace("]",""))
											options[i] = [o[0],num]
										except ValueError:
											stardb.out("The variation value must be a number.")
											options[i] = None
								stardb.replace_star(label, file, options)
							else:
								stardb.out("The reference file "+str(file)+" does not exist.")

						else:
							stardb.out("The reference STAR file should only contain a single table.")								
					else:
						stardb.out("Column "+str(label)+" does not exist.")

				elif cmd[0] == "delete":#
					# None, calls release after execution
					# removel of current selection
					stardb.deleteSelection()
				
				elif cmd[0] == "write_selection":
					# outputstar.star
					# Needs a table selected
					if stardb.isSilent():
						stardb.writeSeleection(cmd[1])
					else:
						if os.path.isfile(cmd[1]):
							stardb.out( "The file '"+str(cmd[1])+"' already exists.")
							ans = raw_input("Do you want to override (y/n)?")
							if ans == "y":
								stardb.out( "Overriding the file.")
								stardb.writeSelection(cmd[1])
							else:
								stardb.out( "Not overriding.")
						else:
							stardb.writeSelection(cmd[1])
				elif cmd[0] == "write":#
					if stardb.isSilent():
						stardb.writeStar(cmd[1])
					else:
						if os.path.isfile(cmd[1]):
							stardb.out( "The file '"+str(cmd[1])+"' already exists.")
							ans = raw_input("Do you want to override (y/n)?")
							if ans == "y":
								stardb.out( "Overriding the file.")
								stardb.writeStar(cmd[1])
							else:
								stardb.out( "Not overriding.")
						else:
							stardb.writeStar(cmd[1])				
				elif cmd[0] == "writef":#
					stardb.writeStar(cmd[1])

				elif cmd[0] == "math":
					# rlnLabel=(number|rlnLabel)(operator)(number|rlnLabel)
					pat = "^(_rln.*?)=(.+?)(\/\/|\*\*|\+|\-|\*|\/)(.+)$"
					match = re.search(pat,cmd[1])
					if match != None:
						# check column existence
						error = ""
						for item in match.groups():
							if item[0:4] == "_rln" and item not in stardb.getLabels():
								error += str(item)+" does not exist.\n"
						if error == "":
							stardb.doMath(match.group(1), match.group(2), match.group(3), match.group(4))
						else:
							stardb.out(error)
					else:
						stardb.out("Your input is malformed (--math).")
			else:
				stardb.out( "You must select a table with --use before you can proceed.")