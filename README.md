# StarTool
## Setup

StarTool requires Python 2.7.

### Unix based systems (including the partially eaten fruit)

Extract the two files `startool.py` and `STLib.py` to your location of choice.
Run the Program as `python /path/toStarTool/startool.py`.

In case you want to have the tool available system wide, use a shell alias like `alias stool="python /path/to/StarTool/startool.py $@"`.

### Windows

Coming soon...

## Known Issues

- STAR files that start with a number in the filename will make the program crash (e.g 3drefine_resilt.star). Will be fixed soon.

## Syntax
### General usage/Input
`python startool.py [inputfiles] [selectors/editors] [output]`

Example: `python startool.py a_file.star --select _rlnVoltage=300 --write_selection selection.star`

Multiple files can be loaded by comma separation. The program internally will create tables with the
scheme ‘starfilename_tablename’.

In order to make use of faster data handling, one can also use

`python startool.py example.star:example.db`

to load the STAR file into a local data base file. Changes made by editors will be directly affect that data base file.
Remember to remove that database file if you want to start over with the original data from your .STAR file.

### Information
`--info`

Prints the current starfiles/tables loaded and their labels and record numbers. This should always be
used at the beginning to get an overview what data you actually have loaded.

`--show`

Prints the current content of the table in use. Selectors are applied.
### Selectors
`--use [ tablename ]`

Defines, which table is used for subsequent operations. This must be used, if multiple data tables are
read from one or more starfiles (see also `--info` ). Otherwise, the program uses the table read in.
Calling --use will clear all other previously made selector.

`--select [ _rlnLabel operator value ]`

Selects a subset of the current table based on an operator comparison. Allowed are '=, !=, \<, \>, \<=,
\>= '.

Example: `--select _rlnWhatEver\>=1.3092`

`--select _rlnLabel=*` sets a dummy selection for a column that is used as reference for some
editors (see `--replace_star` , `--select_fancy` ).

`--select_regex [ _rlnLabel=”regex” ]`

Selects a subset of the current table based on a regular expression match. Allowed are regular ex-
pressions.

Example: `--select _rlnWhatEver=”.*\.star$”`

`--select_star [ rlnLabel=starfile.star ]`

Selects a subset of the current table based on entries in starfile.star. starfile.star should only have
one data table.

Example: `--select_star _rlnWhatEver=other_file.star`

`--select_fancy rlnA,rlnLB=reference.star[variationA,variationB]`

Selects the records from the current table where values for the given labels are matching records in
the reference.star file within the given variation (+/-). Only selects values that also match by the most
recent label used in a selector (consider the use of `--select _rlnLabel=*` to avoid unexpected behavior). Number of labels and variation values must match.

Example: `--select _rlnMicrographName=* --select_fancy _rlnX,_rlnY=reference.star[10,10]`

`--release`

Releases the current table by unsetting the --use and --selector statements (changes made by editors
will remain).

`--deselect`

Unsets all made selectors except for the table in use.

`--sort [ _rlnlabel ]`

Sorts the data by the given label (ascending).

`--tros [ _rlnlabel ]`

Sorts the data by the given label (descending).

`--subset 1:200`

Selects a subset of records including the records given as numbers.

Example: `--subset 3:244`

Will select data entries 3-244 (including 3 and 244).

### Global Editors (ignore --select*, --sort, --tros, --subset statements)

`--add_col [ _rlnNewLabel ]`

Adds a new column named label to the current data table in use.

`--rename_col _rlnLabelOld=_rlnLabelNew`

Renames _rlnLabelOld to _rlnLabelNew in the current table in use.

`--delete_col [ _rlnUnwantedLabel ]`

Removes _rlnUnwantedLabel (including data!) from the current data table in use.

`--delete_table [ tablename ]`

Removes the whole table from the starfile (including data!). If the current table is removed, all selec-
tors are reset.

`--rename_table tablenameNew`

Renames the current table in use to tablenameNew.

### Local Editors (work on current selection)

`--delete`

Deletes the current selection from the data table in use.

`--replace _rlnWhatEver=3.1415`

Replaces all values of fields with the given value. The label needs to exist in the current data table.
This can also be used to fill empty columns with zeros.

`--replace_regex _rlnWhatEver=search%replace`

Replaces all values of the specified column matching the 'search' pattern with 'replace'. Regular ex-
pressions are allowed for search and replace (as in `sed` for example).

Example: `--replace_regex _rlnLabel=\.star$%\.sun`

`--replace_star _rlnWhatEver=reference.star`

Replaces the values of the specified column with the values from reference.star. Only copies values
that match by the most recently selected column (consider the use of `--select _rlnLabel=*` to
avoid unexpected behavior). The reference star-file should only contain one data table.

### Merging operations

`--merge [outputfile.star]`

Merges all currently loaded starfiles into outputfile.star. Only merges STAR-files that contain one
data table. Columns that do not overlap between all merged STAR-files will be dropped (including
data!).

### Output

`--write_selection [ outputfilename.star ]`

Writes the current selection to a STAR-file. This is useful if one wants to extract a subset of a single
data table.

If the a whole STAR-file shall be reconstructed with changes applied, see `--write` . If only specific
tables should be written, remove unwanted tables using the `--delete_table` method.

`--write [ outputstarfile.star ]`

Writes all tables belonging to the STAR-file which the current table is part of. Changes made to the
individual tables by editor methods will be written (selection will be released before writing). If only
specific tables or subsets should be written, you may use `--use` and write it as a selection with `--write_selection`.

### Special

`--query [ SQLite-query ]`

This option is for experienced users that want to send their own SQLite queries. It will ignore any
previously called selector methods. A SELECT statement will trigger a print of the called data.
