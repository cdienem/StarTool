# StarTool

## Table of contents

## Concept
The StarTool executes commands for selecting and editing data in a Relion STAR file. The given order of commands defines the order of execution meaning that editing commands work on previously made selections (except when changing global properties as tablenames, column names etc.). Such edited STAR files can be written out as a new starfile and subsets (selections) can be exported as well.

Behind the scenes, the STAR file is loaded into an in-memory SQLite3 database. Selections and edits are executed in that database and only when writing back into a file, the data will be retrieved from the database. Therefore, the StarTool could be easily extended as an interface for solutions where STAR files are stored in an SQLite database.

## Available commands
feature list here

## Setup

StarTool requires Python 2.7.

### Unix based systems (including the partially eaten fruit)

Extract the two files `startool.py` and `STLib.py` to your location of choice.
Run the Program as `python /path/toStarTool/startool.py`.

In case you want to have the tool available system wide, use a shell alias like `alias stool="python /path/to/StarTool/startool.py $@"`.

### Windows

Coming soon...

## Known Issues

If you encounter any issues, feel free to contact me.

## Syntax
### General usage/Input
`python startool.py [inputfiles] [selectors/editors] [output]`

Example: `python startool.py a_file.star --select _rlnVoltage=300 --write_selection selection.star`

Multiple files can be loaded by comma separation. The program internally will create tables with the scheme ‘starfilename_tablename’.

In order to make use of faster data handling, one can also use

`python startool.py example.star:example.db`

to load the STAR file into a local data base file. Changes made by editors will be directly affect that data base file.
Remember to remove that database file if you want to start over with the original data from your .STAR file.

### Information
<a name="info"><pre><b>--info</b></pre></a>

Prints the current starfiles/tables loaded and their labels and record numbers. This should always be
used at the beginning to get an overview what data you actually have loaded.

### Data display
<a name="show"><pre><b>--show</b></pre></a>

Prints the current content of the table in use. Selectors are applied.

### Selecting subsets of your data

<a name="use"><pre><b>--use tablename</b></pre></a>

Defines, which table is used for subsequent operations. This must be used, if multiple data tables are read from one or more starfiles (you may check by using  `--info` ). Otherwise, the program uses the one table that was read in.
Calling `--use` will clear all other previously made selections.

<a name="select"><pre><b>--select _rlnLabel operator value</b></pre></a>

Selects a subset of the current table based on an operator comparison. Allowed are '=, !=, \<, \>, \<=,
\>= '.

Example: `--select _rlnWhatEver\>=1.3092`

<a name="select_regex"><pre><b>--select_regex _rlnLabel=”regex”</b></pre></a>

Selects a subset of the current table based on a regular expression match. Allowed are regular ex-
pressions.

Example: `--select _rlnWhatEver=”.*\.star$”`

<a name="select_star"><pre><b>--select_star starfile.star:rlnA[variationA],_rlnB[variationB]</b></pre></a>

Selects a subset of the current table based on entries in starfile.star. starfile.star should only have one data table.

Example: `--select_star reference.star:_rlnImageName,_rlnCoordinateX[10],_rlnCoordinateY[10]`

Example: `--select _rlnMicrographName=* --select_fancy _rlnX,_rlnY=reference.star[10,10]`

<a name="release"><pre><b>--release</b></pre></a>

Releases the current table by unsetting the `--use` and `--select*` statements (changes made by editors will remain).

<a name="deselect"><pre><b>--deselect</b></pre></a>

Unsets all selections except for `--use`.

<a name="subset"><pre><b>--subset start:end</b></pre></a>

Selects a subset of records including the records given as numbers.

Example: `--subset 3:244` will select data entries 3-244 (including 3 and 244).

### Global Editors (ignore --select*, --sort, --tros, --subset statements)

<a name="add_col"><pre><b>--add_col _rlnNewLabel</b></pre></a>

Adds a new column named label to the current data table in use.

<a name="rename_col"><pre><b>--rename_col _rlnLabelOld=_rlnLabelNew</b></pre></a>

Renames _rlnLabelOld to _rlnLabelNew in the current table in use.

<a name="delete_col"><pre><b>--delete_col _rlnUnwantedLabel</b></pre></a>

Removes _rlnUnwantedLabel (including data!) from the current data table in use.

<a name="delete_table"><pre><b>--delete_table tablename</b></pre></a>

Removes the whole table from the starfile (including data!). If the current table is removed, all selec-
tors are reset.

<a name="rename_table"><pre><b>--rename_table tablenameNew</b></pre></a>

Renames the current table in use to tablenameNew. Be aware that renaming tables may screw up compatibility with Relion.

### Local Editors (work on current selection)

<a name="sort"><pre><b>--sort _rlnlabel</b></pre></a>

Sorts the selected data by the given label (ascending).

<a name="tros"><pre><b>--tros _rlnlabel</b></pre></a>

Sorts the selected data by the given label (descending).

<a name="delete"><pre><b>--delete</b></pre></a>

Deletes the current selection from the data table in use.

<a name="replace"><pre><b>--replace _rlnWhatEver=3.1415</b></pre></a>

Replaces all values of the specified column with the given value. The column needs to exist in the current data table.
This can also be used to fill empty columns with zeros (because Relion can not handle empty columns).

<a name="replace_regex"><pre><b>--replace_regex _rlnWhatEver='search'%'replace'</b></pre></a>

Replaces all values of the specified column matching the 'search' pattern with 'replace'. Regular expressions are allowed for search and replace (as in `sed` for example).

Example: `--replace_regex _rlnLabel='\.star$'%'\.sun'`

<a name="replace_star"><pre><b>--replace_star _rlnWhatEver=reference.star:_rlnReferenceA[variationA],_rlnReferenceB</b></pre></a>

need update

<a name="math"><pre><b>--math _rlnLabel=a operator b</b></pre></a>

Very basic math implementation. Operators can be `+`, `-`, `*`, `/`, `**` (power; `k**n` is k to the n-th power) and `//` (root; `n//k` is the n-th root of k). `a` and `b` as used above can be either column names or numbers.

Example: `--math _rlnCoordinateX=_rlnCoordinateX-_rlnOriginX` 

### Split and merge operations

<a name="merge">`--merge outputfile.star`</a>

Merges all currently loaded starfiles into outputfile.star. Only merges STAR files that contain one data table. Columns that do not overlap between all merged STAR files will be dropped (including data!). For more details see <a href="#usage">Usage examples</a>.
***
<a name="split_by">`--split_by _rlnLabel:noOfBatches`</a>

This splits the dataset into a specific number of batches. If no number of bathches is given, the data will be split into subbatches for each unique value of the given label. 

Example 1: `--split_by _rlnDefocusU:2` will split the STAR file into two subfiles that contain one half of the defocus range each.

Example 2: `--split_by _rlnMicrographName` will split the STAR file into separate files for each micrograph (e.g particles). Note that this can create a large number of files!2

### Output

<a name="write_selection">`--write_selection outputfilename.star`</a>

Writes the current selection to a STAR-file. This is useful if one wants to extract a subset of data.

If the a whole STAR-file shall be written with changes applied, see `--write`.

<a name="writef_selection"><pre><b>--writef_selection outputstarfile.star</b></pre></a>

Same as `--write_selection`, however overrides files without asking.

<a name="write"><pre><b>--write outputstarfile.star</b></pre></a>

Writes all tables belonging to the STAR-file which the current table is part of. Changes made to the
individual tables by editor methods will be written (selection will be released before writing). If only
specific tables or subsets should be written, you may use `--use` and write it as a selection with `--write_selection`.

<a name="writef"><pre><b>--writef outputstarfile.star</b></pre></a>

Same as `--write`, however overrides files without asking.

### Special

<a name="silent"><pre><b>--silent</b></pre></a>
This mutes the program (useful for automated procedures). Be aware that muting the program will force files to be overwritten (`--writef` will be called instead of `--write`).

<a name="query"><pre><b>--query SQLite-query</b></pre></a>

This option is for experienced users that want to send their own SQLite queries. It will ignore any previously called selector methods. A SELECT statement will trigger a print of the called data.

## Usage Examples
Split by defocus
Batches
