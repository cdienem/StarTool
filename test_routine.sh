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

if $(python startool.py testfiles/2test_startup.star --subset 1:1 --show | grep -q "000001@references/ref_projections.mrcs") && ! $(python startool.py testfiles/2test_startup.star --subset 1:1 --show | grep -q "000002@references/ref_projections.mrcs"); then
	echo "CHECK OK --subset"
else
	echo "CHECK FAILED --subset"
fi

#--sort -> check with subset

if $(python startool.py testfiles/2test_startup.star --sort _rlnAngleRot --subset 1:1 --show | grep -q "000001@references/ref_projections.mrcs") && $(python startool.py testfiles/2test_startup.star --tros _rlnAngleRot --tros _rlnAngleTilt --subset 1:1 --show | grep -q "000013@references/ref_projections.mrcs"); then
	echo "CHECK OK --sort/--tros"
else
	echo "CHECK FAILED --sort/--tros"
fi


#--add_col -> check info

if $(python startool.py testfiles/2test_startup.star --add_col _rlnTest --info | tail -4 | grep -q "_rlnTest"); then
	echo "CHECK OK --add_col"
else
	echo "CHECK FAILED --add_col"
fi

#--delete_col -> check info

if ! $(python startool.py testfiles/2test_startup.star --delete_col _rlnImageName --info | tail -3 | grep -q "_rlnImageName"); then
	echo "CHECK OK --delete_col"
else
	echo "CHECK FAILED --delete_col"
fi


#--rename_col -> check info

if $(python startool.py testfiles/2test_startup.star --rename_col _rlnImageName=_rlnTest --info | tail -4 | grep -q "_rlnTest"); then
	echo "CHECK OK --rename_col"
else
	echo "CHECK FAILED --rename_col"
fi

#--rename_table -> check info

if $(python startool.py testfiles/2test_startup.star --rename_table new_table_name --info | tail -4 | grep -q "new_table_name"); then
	echo "CHECK OK --rename_table"
else
	echo "CHECK FAILED --rename_table"
fi

#--replace

if $(python startool.py testfiles/2test_startup.star --replace _rlnImageName=Hallo --show | tail -4 | grep -q "Hallo"); then
	echo "CHECK OK --replace"
else
	echo "CHECK FAILED --replace"
fi

#--replace_regex

if $(python startool.py testfiles/2test_startup.star --replace_regex _rlnImageName='\d@'%'ABCabc' --show | tail -4 | grep -q "ABCabc"); then
	echo "CHECK OK --replace_regex"
else
	echo "CHECK FAILED --replace_regex"
fi

#--replace_star

if [ $(python startool.py testfiles/2test_startup.star --replace_star _rlnImageName=testfiles/2test_reference.star:_rlnAngleRot,_rlnAngleTilt --show | grep ".sun" | wc -l) -eq 2 ]; then
	echo "CHECK OK --replace_star (no variation)"
else
	echo "CHECK FAILED --replace_regex (no variation)"
fi

if [ $(python startool.py testfiles/2test_startup.star --replace_star _rlnImageName=testfiles/2test_reference.star:_rlnAngleRot[2],_rlnAngleTilt --show | grep ".sun" | wc -l) -eq 3 ]; then
	echo "CHECK OK --replace_star (with variation)"
else
	echo "CHECK FAILED --replace_regex (with variation)"
fi

#--delete

if ! $(python startool.py testfiles/2test_startup.star --select _rlnImageName="000013@references/ref_projections.mrcs" --delete --show | tail -5 | grep -q "000013@references/ref_projections.mrcs" ); then
	echo "CHECK OK --delete"
else
	echo "CHECK FAILED --delete"
fi


#--math

if ! $(python startool.py testfiles/2test_startup.star --math _rlnAngleTilt=_rlnAngleTilt+1 --show | grep -q "48.0" ); then
	echo "CHECK OK --math"
else
	echo "CHECK FAILED --math"
fi


# --delete_table

#--merge

#--query

#--silent

#--split_by

#--writef

#--writef_selection