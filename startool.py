#!/bin/python
import argparse, sys, os.path, re
import STlib

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

parser.add_argument('i', action='store')

parser.add_argument('--info', action=store_ordered, nargs='?')
parser.add_argument('--show', action=store_ordered, nargs='?')
parser.add_argument('--debug', action=store_ordered, nargs='?')

#Selectors
parser.add_argument('--use', action=store_ordered)
parser.add_argument('--select', action=store_ordered)
parser.add_argument('--select_regex', action=store_ordered)
parser.add_argument('--select_star', action=store_ordered)
parser.add_argument('--select_fancy', action=store_ordered)
parser.add_argument('--release', action=store_ordered, nargs='?')
parser.add_argument('--deselect', action=store_ordered, nargs='?')
parser.add_argument('--sort', action=store_ordered)
parser.add_argument('--tros', action=store_ordered)
parser.add_argument('--subset', action=store_ordered)

#Global Editors
parser.add_argument('--add_col', action=store_ordered)
parser.add_argument('--delete_col', action=store_ordered)
parser.add_argument('--rename_col', action=store_ordered)

parser.add_argument('--delete_table', action=store_ordered)
parser.add_argument('--rename_table', action=store_ordered)

#Local Editors
parser.add_argument('--replace', action=store_ordered)
parser.add_argument('--replace_regex', action=store_ordered)
parser.add_argument('--replace_star', action=store_ordered)
# Deletes stuff from the local selection
parser.add_argument('--delete', action=store_ordered, nargs='?')

parser.add_argument('--merge', action=store_ordered)

#Special
parser.add_argument('--query', action=store_ordered)
parser.add_argument('--math', action=store_ordered) # still experimental

# Output
parser.add_argument('--split_by', action=store_ordered)

parser.add_argument('--write_selection', action=store_ordered)
parser.add_argument('--write', action=store_ordered)
parser.add_argument('--writef', action=store_ordered)

# parse the arguments
args = parser.parse_args()


# Load the input file(s) and store in memory if not specified otherwise
# If there is the location specified, split it

print "### StarTool 1.1 (by Chris) ###"

if ":" in args.i:
	part = args.i.split(":")
	if part[1] == "mem":
		print "Starting StarTool in memory\n"
		stardb = STlib.StarTool("mem")
		# Get filenames to load
		for fil in part[0].split(","):
			print "Loading "+fil+"..."
			if os.path.isfile(fil):
				stardb.star2db(fil)
			else:
				print "File "+fil+" does not exist.\n"
	else:
		print "Starting StarTool with local DB ("+part[1]+")\n"
		make="no"
		if not os.path.isfile(part[1]) or os.stat(part[1]).st_size == 0:
			make = "yes"
		stardb = STlib.StarTool(part[1], part[0])
		if make == "yes":
			for fil in part[0].split(","):
				print "Loading "+fil+"..."
				if os.path.isfile(fil):
					stardb.star2db(fil)
				else:
					print "File "+fil+" does not exist.\n"
			
else:
	print "Starting StarTool in memory\n"
	stardb = STlib.StarTool("mem")
	part = []
	part.append(args.i)
	# Get filenames to load
	for fil in part[0].split(","):
		print "Loading "+fil+"..."
		if os.path.isfile(fil):
			stardb.star2db(fil)
		else:
			print "File "+fil+" does not exist.\n"



# Check if there is only one table and use it
if len(stardb.getTables()) == 1:
	stardb.useTable(stardb.getTables()[0])
	print "\nOnly one input table read, using "+stardb.getTables()[0]

# Check if optional ordered commands were given
if hasattr(args, "ordered_args"):
# Walk through commands and do 
	for cmd in args.ordered_args:
# Methods without restrictions
		print "\nEXECUTE: --"+str(cmd[0])+" "+str(cmd[1]).replace("None","")
		if cmd[0] == "info":
			# None
			stardb.info()

		elif cmd[0] == "use":
			# Tablename
			if cmd[1] in stardb.getTables():
				stardb.useTable(cmd[1])
			else:
				print cmd[1]+" does not exist..."
		elif cmd[0] == "deselect":
			# none
			stardb.deselect()

		elif cmd[0] == "merge":
			# starfilename.star
			if os.path.isfile(cmd[1]):
				print "The file '"+str(cmd[1])+"' already exists."
				ans = raw_input("Do you want to override (y/n)?")
				if ans == "y":
					print "Overriding the file."
					stardb.mergeStar(cmd[1])
				else:
					print "Not overriding."
			else:
				stardb.mergeStar(cmd[1])

		elif cmd[0] == "query":
			# just accept it here
			stardb.query(cmd[1])
			print "Executing custom query ('"+cmd[1]+"')..."

		elif cmd[0] == "delete_table":
			# None
			# No restriction
			if cmd[1] in stardb.getTables():
				stardb.removeTable(cmd[1])
			else:
				print "Cannot delete '"+cmd[1]+"' because it does not exist."

		elif cmd[0] == "debug":
			# prints some debug information
			stardb.debug()

		elif cmd[0] == "split_by":
			if cmd[1] in stardb.getLabels():
				stardb.splitBy(cmd[1])
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
						print "Column '"+cmd[1]+"' already exists."

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
							print "Cannot rename '"+old+"' to '"+new+"' because it either does not exist or the new name is already taken.\n"
					else:
						print "The input is malformed (--rename).\n"

				
				elif cmd[0] == "sort":
					# _rlnLabel
					if cmd[1] in stardb.getLabels():
						stardb.sortCol(cmd[1])
					else:
						print "Column "+cmd[1]+" does not exist."

				elif cmd[0] == "tros":
					# _rlnLabel
					if cmd[1] in stardb.getLabels():
						stardb.trosCol(cmd[1])
					else:
						print "Column "+cmd[1]+" does not exist."
					
				elif cmd[0] == "subset":
					# 1:100
					res = re.search("^([0-9]+):([0-9]+)$",str(cmd[1]))
					if res != None:
						stardb.subset([int(res.group(1)),int(res.group(2))])
					else:
						print "Your input is malformed (--subset)."

				elif cmd[0] == "rename_table":
					# TablenameNew
					if cmd[1] not in stardb.getTables():					
						stardb.renameTable(cmd[1])
					else:
						print "Cannot rename '"+stardb.getCurrent()+"' to '"+cmd[1]+"' because the new name is already taken.\n"

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
								print "Column "+col+" does not exist."
						else:
							print "Your input is malformed. Please add a valid operator (--select)."

				elif cmd[0] == "select_regex":
					# _rlnLabel='regex'
					# _rlnLabel=regexp
					if cmd[1] != None and cmd[1].split("=")[0] in stardb.getLabels() and cmd[1].split("=")[1] != "":
						com = cmd[1].split("=")
						stardb.select_regex(com[0], com[1])
					else:
						print "Your input is malformed (--select_regex)"

				elif cmd[0] == "select_star":
					# _rlnLabel=ref.star
					if cmd[1] != None and cmd[1].split("=")[0] in stardb.getLabels() and os.path.isfile(cmd[1].split("=")[1]):
						com = cmd[1].split("=")
						stardb.select_star(com[1],com[0])
					else:
						print "Your input is malformed (--select_star)"

				elif cmd[0] == "select_fancy":
					# _rlnLabelA,_rlnLabelB=ref.star[variationA,variationB]
					# ^((,?_rln\w+)+)=(\w+\.star)\[?((,? *[0-9.]+ *)+)\]$
					# group 1: lanbels
					# group 3: starfile
					# group 4: variations
					pat = "^((,?_rln\w+)+)=(\w+\.star)\[?((,? *[0-9.]+ *)+)\]$"
					match = re.search(pat,cmd[1])
					if match != None and os.path.isfile(match.group(3)):
						lab = match.group(1).split(",")
						star = match.group(3)
						varia = match.group(4).split(",")
						stardb.select_fancy(star,lab,varia)
					else:
						print "Your input is malformed (--select_fancy)"

				elif cmd[0] == "replace":
					# _rlnLabel=valueABC
					com = cmd[1].split("=")
					if com[0] in stardb.getLabels():
						stardb.replace(com[0],com[1])
					else:
						print "Column "+com[0]+" does not exist (--replace)"

				elif cmd[0] == "replace_regex":
					# _rlnLabel=search%replace
					com = cmd[1].split("=")
					if com[0] in stardb.getLabels():
						pat = com[1].split("%")
						stardb.replace_regex(com[0],pat[0],pat[1])
					else:
						print "Column "+com[0]+" does not exist (--replace_regex)"
					pass

				elif cmd[0] == "replace_star":
					# _rlnLabel=ref.star
					com = cmd[1].split("=")
					if com[0] in stardb.getLabels() and os.path.isfile(com[1]):
						stardb.replace_star(com[0],com[1])
					else:
						print "Column "+stardb.getCurrent()+"."+com[0]+" does not exist (--replace_star)"

				elif cmd[0] == "delete":#
					# None, calls release after execution
					# removel of current selection
					stardb.deleteSelection()
					pass
				
				elif cmd[0] == "write_selection":
					# outputstar.star
					# Needs a table selected
					if os.path.isfile(cmd[1]):
						print "The file '"+str(cmd[1])+"' already exists."
						ans = raw_input("Do you want to override (y/n)?")
						if ans == "y":
							print "Overriding the file."
							stardb.writeSelection(cmd[1])
						else:
							print "Not overriding."
					else:
						stardb.writeSelection(cmd[1])
				elif cmd[0] == "write":#
					if os.path.isfile(cmd[1]):
						print "The file '"+str(cmd[1])+"' already exists."
						ans = raw_input("Do you want to override (y/n)?")
						if ans == "y":
							print "Overriding the file."
							stardb.writeStar(cmd[1])
						else:
							print "Not overriding."
					else:
						stardb.writeStar(cmd[1])
				
				elif cmd[0] == "writef":#
					stardb.writeStar(cmd[1])

				elif cmd[0] == "math":
					# rlnLabel=(number|rlnLabel)(operator)(number|rlnLabel)
					pat = "^\_rln(.*?)=(.+?)(\/\/|\*\*|\+|\-|\*|\/)(.+)$"
					match = re.search(pat,cmd[1])
					stardb.doMath("_rln"+match.group(1), match.group(2), match.group(3), match.group(4))

			else:
				print "You must select a table with --use before you can proceed."


			



			
# Bugs:


# Todo:
# - improve the show screen -> only columns!
# - implement merge_clean function (checks for duplicates before insert into tmp)
# - implement math functions (simple operations with columns like **, / + -, use compilation of expressions by python compiler.parse)
# - refactor program startup
# - rewrite the editors that work on selection to use the4 ROWID for better identification of entries (UPDATE table SET x = y WHERE ROWID...
#		-> for this change the usage of db cursors in a way that there is only a single cursor created (otherwise rowid is not visible)

# Notes: 
# > replace functions in context of selectors -> is fine but a bit weird becaue the replace does not release the selector. If one changes the value of the previous selector, it will be an emptsy selectionb afterwards
# > all writer methods need a table selected by --use the corresponding star file will be written
# > replace_regex: the stupid case of someone replacing a string into a float field?