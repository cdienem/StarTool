#!/bin/bash

# this will be a test routine script to test basal functionality of the startool
# it only tests for certain expected outputs

echo "Starting StarTool unit test..."

# load std file and test --debug first

if $(python startool.py testfiles/2test_startup.star --debug | grep -q "Query"); then
	echo "CHECK OK --debug"
else
	echo "CHECK FAILED --debug"
	exit
fi

# check different types of files to load



#--info
if $(python startool.py testfiles/2test_startup.star --info | grep -q "_rlnAngleRot"); then
	echo "CHECK OK --info"
else
	echo "CHECK FAILED --info"
	exit
fi

#--show
if $(python startool.py testfiles/2test_startup.star --show | grep -q "ref_projections.mrcs"); then
	echo "CHECK OK --show"
else
	echo "CHECK FAILED --show"
	exit
fi

#--select
if $(python startool.py testfiles/2test_startup.star --select _rlnAngleRot=45 --show | grep -q "45.0"); then
	echo "CHECK OK --select"
else
	echo "CHECK FAILED --select"
	exit
fi

#--write_selection
if [ -f testfiles/tmp.star ]; then
	rm -f testfiles/tmp.star
fi
python startool.py testfiles/2test_startup.star --select _rlnAngleRot=45 --write_selection testfiles/tmp.star > /dev/null
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
python startool.py testfiles/2test_startup.star --write testfiles/tmp.star > /dev/null
if [ -f testfiles/tmp.star ]; then
	echo "CHECK OK --write"
	rm -f testfiles/tmp.star
else
	echo "CHECK FAILED --write"
fi


#--use USE
if $(python startool.py testfiles/2test_twotable.star --use 2test_twotable_data_two --debug | grep -q "CURRENT: 2test_twotable_data_two"); then
	echo "CHECK OK --use"
else
	echo "CHECK FAILED --use"
fi

#--select_regex

if $(python startool.py testfiles/2test_startup.star --select_regex _rlnImageName='1\d{1}@r' --show | grep -q "11@ref"); then
	echo "CHECK OK --select_regex"
else
	echo "CHECK FAILED --select_regex"
fi

#--select_star
if $(python startool.py testfiles/2test_startup.star --select_star testfiles/2test_reference.star:_rlnAngleRot --show | grep -q "45.0"); then
	echo "CHECK OK --select_star (no variation)"
else
	echo "CHECK FAILED --select_star (no variation)"
fi

if $(python startool.py testfiles/2test_startup.star --select_star testfiles/2test_reference.star:_rlnAngleRot[2] --show | grep -q "47.0"); then
	echo "CHECK OK --select_star (variation)"
else
	echo "CHECK FAILED --select_star (variation)"
fi


#--release -> check output of debug

if $(python startool.py testfiles/2test_startup.star --release --debug | grep -q "CURRENT: NONE"); then
	echo "CHECK OK --release"
else
	echo "CHECK FAILED --release"
fi


#--deselect -> check output of debug

if $(python startool.py testfiles/2test_startup.star --select _rlnAngleRot=* --deselect --debug | grep -q "Query: SELECT ROWID,\* FROM \""); then
	echo "CHECK OK --deselect"
else
	echo "CHECK FAILED --deselect"
fi

#--subset

#--sort -> check with subset

#--tros -> check with subset

#--add_col -> check info

#--delete_col -> check info

#--rename_col -> check info

#--delete_table -> check info

#--rename_table -> check info



#--replace

#--replace_regex

#--replace_star

#--delete

#--merge

#--math
