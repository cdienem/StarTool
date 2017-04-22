#!/bin/bash

# this will be a test routine script to test basal functionality of the startool
# it only tests for certain expected outputs

echo "Starting StarTool test..."

# load std file and test --debug first

if $(python startool.py testfiles/test_startup.star --debug | grep -q "Query"); then
	echo "CHECK OK --debug"
else
	echo "CHECK FAILED --debug"
	exit
fi

# check different types of files to load



#--info
if $(python startool.py testfiles/test_startup.star --info | grep -q "_rlnAngleRot"); then
	echo "CHECK OK --info"
else
	echo "CHECK FAILED --info"
	exit
fi

#--show
if $(python startool.py testfiles/test_startup.star --show | grep -q "ref_projections.mrcs"); then
	echo "CHECK OK --show"
else
	echo "CHECK FAILED --show"
	exit
fi

#--select
if $(python startool.py testfiles/test_startup.star --select _rlnAngleRot=45 --show | grep -q "45.0"); then
	echo "CHECK OK --select"
else
	echo "CHECK FAILED --select"
	exit
fi

#--write_selection
if [ -f testfiles/tmp.star ]; then
	rm -f testfiles/tmp.star
fi
python startool.py testfiles/test_startup.star --select _rlnAngleRot=45 --write_selection testfiles/tmp.star > /dev/null
if [ -f testfiles/tmp.star ]; then
	echo "CHECK OK --write_selection"
	rm -f testfiles/tmp.star
else
	echo "CHECK FAILED --write_selection"
fi 

#--write WRITE
if [ -f testfiles/tmp.star ]; then
	rm -f testfiles/tmp.star
fi
python startool.py testfiles/test_startup.star --write testfiles/tmp.star > /dev/null
if [ -f testfiles/tmp.star ]; then
	echo "CHECK OK --write"
	rm -f testfiles/tmp.star
else
	echo "CHECK FAILED --write"
fi


#--use USE
if $(python startool.py testfiles/test_twotable.star --use test_twotable_data_two --debug | grep -q "CURRENT: test_twotable_data_two"); then
	echo "CHECK OK --use"
else
	echo "CHECK FAILED --use"
fi


#--select_regex

#--select_star

#--select_fancy

#--release -> check output of debug

#--deselect -> check output of debug

#--sort

#--tros

#--subset

#--add_col

#--delete_col

#--rename_col

#--delete_table

#--rename_table

#--replace

#--replace_regex

#--replace_star

#--delete

#--merge

#--query
