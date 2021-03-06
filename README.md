# StarTool

## Table of contents
* <a href="#concept">Concept</a>
* <a href="#quick-reference">Quick reference</a>
* <a href="#setup">Setup</a>
  * <a href="#unix-based-systems-including-the-partially-eaten-fruit">Unix based systems</a>
  * <a href="#windows">Windows</a>
* <a href="#syntax">Syntax</a>
  * <a href="#general-usage-and-input">General usage and input</a>
  * <a href="#information">Information</a>
  * <a href="#data-display">Data display</a>
  * <a href="#selecting-subsets-of-data">Selecting subsets of data</a>
  * <a href="#global-editors">Global editors</a>
  * <a href="#local-editors">Local editors</a>
  * <a href="#split-and-merge-operations">Split and merge operations</a>
  * <a href="#output">Output</a>
  * <a href="#special">Special</a>
* <a href="#usage-examples">Usage examples</a>

## Concept
The StarTool executes commands for selecting and editing data in a Relion STAR file. The given order of commands defines the order of execution meaning that editing commands work on previously made selections (except when changing global properties as tablenames, column names etc.). Such edited STAR files can be written out as a new starfile and subsets (selections) can be exported as well.

Behind the scenes, the STAR file is loaded into an in-memory SQLite3 database. Selections and edits are executed in that database and only when writing back into a file, the data will be retrieved from the database. Therefore, the StarTool could be easily extended as an interface for solutions where STAR files are stored in an SQLite database.

## Quick reference

These commands (ordered alphabetically) are available.

| Command | Description |
|---|---|
| <a href="#add_col">`--add_col`</a> | Adds a new column |
| <a href="#delete">`--delete`</a> | Deletes selected data |
| <a href="#delete_col">`--delete_col`</a> | Deletes a column |
| <a href="#delete_table">`--delete_table`</a> | Deletes a data table |
| <a href="#deselect">`--deselect`</a> | Unsets all seleections |
| <a href="#info">`--info`</a> | Prints information about STAR file |
| <a href="#math">`--math`</a> | Basic math operations with values and columns |
| <a href="#merge">`--merge`</a> | Merge two or more files |
| <a href="#query">`--query`</a> | Submit a user defined SQLite query |
| <a href="#release">`--release`</a> | Unsets the current table in use (for multi table files) |
| <a href="#rename_col">`--rename_col`</a> | Renames a colum |
| <a href="#rename_table">`--rename_table`</a> | Renames a data table |
| <a href="#replace">`--replace`</a> | Replaces values by a user defined value |
| <a href="#replace_regex">`--replace_regex`</a> | Regular expression base replacing |
| <a href="#replace_star">`--replace_star`</a> | Replace values with values from other STAR file |
| <a href="#select">`--select`</a> | Select data by operator based conditions |
| <a href="#select_regex">`--select_regex`</a> | Select data based on regular expressions |
| <a href="#select_star">`--select_star`</a> | Select data based on matches with reference STAR file |
| <a href="#silent">`--silent`</a> | Mutes program output |
| <a href="#show">`--show`</a> | Prints currently selected data |
| <a href="#sort">`--sort`</a> | Sorts selected data (ascending) |
| <a href="#split_by">`--split_by`</a> | Splits data into batches |
| <a href="#subset">`--subset`</a> | Selects defined data subsets |
| <a href="#tros">`--tros`</a> | Sorts selected data (descending) |
| <a href="#use">`--use`</a> | Defines a table to use (only for multi table STAR files) |
| <a href="#write">`--write`</a> | Writes STAR file |
| <a href="#write_selection">`--write_selection`</a> | Writes current selection to STAR file |
| <a href="#writef">`--writef`</a> | Writes STAR file (force override) |
| <a href="#writef_selection">`--writef_selection`</a> | Writes current selection to STAR file (force override) |



## Setup

StarTool requires Python 2.7.

### Unix based systems (including the partially eaten fruit)

Extract the two files `startool.py` and `STLib.py` to your location of choice.
Run the Program as `python /path/toStarTool/startool.py`.

In case you want to have the tool available system wide, use a shell alias like `alias stool="python /path/to/StarTool/startool.py $@"`.

### Windows

Coming soon...

## Syntax
### General usage and input
`python startool.py [inputfiles] [selectors/editors] [output]`

Example: `python startool.py a_file.star --select _rlnVoltage=300 --write_selection selection.star`

Multiple files can be loaded by comma separation. The program internally will create tables with the scheme ‘starfilename_tablename’.

In order to make use of faster data handling, one can also use

`python startool.py example.star:example.db`

to load the STAR file into a local data base file. Changes made by editors will be directly affect that database file.
Remember to remove that database file if you want to start over with the original data from your STAR file.

### Information
<a name="info"><pre><b>--info</b></pre></a>

Prints the current starfiles/tables loaded and their labels and record numbers. This should always be
used at the beginning to get an overview what data you actually have loaded.

### Data display
<a name="show"><pre><b>--show</b></pre></a>

Prints the current content of the table in use. Selectors are applied.

### Selecting subsets of data
These methods can be used to select certain subsets of your data. This is useful if you want to edit or extract only a certain part of the data.

<a name="select"><pre><b>--select _rlnLabel operator value</b></pre></a>

Selects a subset of the current table based on an operator comparison. Allowed are 
<table>
 <tr>
  <td>=</td>
  <td>equal</td>
 </tr>
<tr>
  <td>!=</td>
  <td>not equal </td>
 </tr>
<tr>
  <td>\< </td>
  <td>smaller than (needs to be escaped)</td>
 </tr>
<tr>
  <td>\></td>
  <td>greater than (needs to be escaped) </td>
 </tr>
<tr>
  <td>\<= </td>
  <td>smaller or equal than (needs to be escaped) </td>
 </tr>
<tr>
  <td>\>=</td>
  <td>greater or equal than (needs to be escaped) </td>
 </tr>
</table> 

Example: `--select _rlnDefocusU\>=10000` will select all entries with defocus greater or equal to 1 um.

<a name="select_regex"><pre><b>--select_regex _rlnLabel=”regex”</b></pre></a>

Selects a subset of the current table based on a regular expression match. Allowed are regular ex-
pressions.

Example: `--select _rlnMicrographName=”.*\.mrcs$”` will select all entries where _rlnMicrographName end with '.mrcs'.

<a name="select_star"><pre><b>--select_star reference.star:rlnA[variationA],_rlnB[variationB]</b></pre></a>

Selects a subset of the current table based on entries in reference.star. reference.star should only have one data table. The variation value '`[x]`' is optional and will only be interpreted for numerical columns (like coordinates, defocus etc.). Reference STAR files will be loaded temporarily and do not have to be loaded at the program start up. 

Example: `--select_star reference.star:_rlnImageName,_rlnCoordinateX[10],_rlnCoordinateY[10]` will select all entries that match by _rlnMicrographName with reference.star and where _rlnCoordinateX/Y also matches allowing 10 px variation.

<a name="subset"><pre><b>--subset start:end</b></pre></a>

Selects a subset of records including the records given as numbers. For splitting Data into regular batches see also <a href="#split_by">`--split_by`</a>.

Example: `--subset 3:244` will select data entries 3-244 (including 3 and 244).

<a name="deselect"><pre><b>--deselect</b></pre></a>

Unsets all selections.

<a name="use"><pre><b>--use tablename</b></pre></a>

By default, the program uses the table that was read in if there is only one. `--use` must be called, if multiple data tables are read from one or more starfiles (you may check by using `--info`). Calling `--use` will clear all other previously made selections.

<a name="release"><pre><b>--release</b></pre></a>

Releases the current table by unsetting the `--use` and `--select*` statements (changes made by editors will remain).

### Global Editors
Global editors ignore selections made before since they only change global properties of data tables like tablename or column labels.

<a name="add_col"><pre><b>--add_col _rlnNewLabel</b></pre></a>

Adds a new column to the current data table in use.

<a name="rename_col"><pre><b>--rename_col _rlnLabelOld=_rlnLabelNew</b></pre></a>

Renames _rlnLabelOld to _rlnLabelNew in the current table in use.

<a name="delete_col"><pre><b>--delete_col _rlnUnwantedLabel</b></pre></a>

Removes _rlnUnwantedLabel (including data!) from the current data table in use.

<a name="delete_table"><pre><b>--delete_table tablename</b></pre></a>

Removes the whole table from the starfile (including data!). If the current table is removed, all selec-
tors are reset.

<a name="rename_table"><pre><b>--rename_table tablenameNew</b></pre></a>

Renames the current table in use to tablenameNew. Be aware that renaming tables may screw up compatibility with Relion.

### Local Editors
Loval editors directly affect the data that is currently selected (see <a href="#selecting-subsets-of-data">Selecting subsets of data</a>)
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

Example: `--replace_regex _rlnLabel='\.star$'%'\.sun'` will change all _rlnLabel that end on '.star' to an ending of '.sun'.

Please note that regular expression replacement only works in text based columns.

<a name="replace_star"><pre><b>--replace_star _rlnLabel=reference.star:_rlnReferenceA[variationA],_rlnReferenceB</b></pre></a>

Replaces a subset of date with values from reference.star based on matching conditions with reference.star. reference.star should only have one data table. The variation value '`[x]`' is optional and will only be interpreted for numerical columns (like coordinates, defocus etc.). Reference STAR files will be loaded temporarily and do not have to be loaded at the program start up.

Please note that this operation can take a while when used on large datasets and multiple matching criteria.

Example: `--replace_star _rlnImagename=reference.star:_rlnMicrographName,_rlnCoordinateX[10],_rlnCoordinateY[10]` will replace _rlnImageName of the current data by the values from reference.star where _rlnMicrographName match and where _rlnCoordinateX/Y also match within 10 px variation.

<a name="math"><pre><b>--math _rlnLabel=k operator n</b></pre></a>

Very basic math implementation. Operations can be like 
<table>
 <tr>
  <td>k+n</td>
  <td>addition</td>
 </tr>
 <tr>
  <td>k-n</td>
  <td>subtraction</td>
 </tr>
 <tr>
  <td>k*n</td>
  <td>mutliplication</td>
 </tr>
 <tr>
  <td>k/n</td>
  <td>division</td>
 </tr>
 <tr>
  <td>k**n</td>
  <td>n-th power of k</td>
 </tr>
 <tr>
  <td>n//k</td>
  <td>n-th root of k</td>
 </tr>
</table>

`n` and `k` as used above can be either column names or numbers.

Example: `--math _rlnCoordinateX=_rlnCoordinateX-_rlnOriginX` 

### Split and merge operations

<a name="merge"><pre><b>--merge outputfile.star</b></pre></a>

Merges all currently loaded starfiles into outputfile.star. Only merges STAR files that contain one data table. Columns that do not overlap between all merged STAR files will be dropped (including data!). For more details see <a href="#usage">Usage examples</a>.

<a name="split_by"><pre><b>--split_by _rlnLabel:noOfBatches</b></pre></a>

Splits the dataset into a specific number of batches. If no number of bathches is given, the data will be split into subbatches for each unique value of the given label. 

Example 1: `--split_by _rlnDefocusU:2` will split the STAR file into two subfiles that contain one half of the defocus range each.

Example 2: `--split_by _rlnMicrographName` will split the STAR file into separate files for each micrograph. Note that this can create a large number of files if used with columns as defocus or coordinates!

### Output

<a name="write_selection"><pre><b>--write_selection outputfilename.star</b></pre></a>

Writes the current selection to a STAR file. This is useful if one wants to extract a subset of data. In silent mode (<a href="#silent">´--silent´</a>), this will be forced into `--writef_selection`.

<a name="writef_selection"><pre><b>--writef_selection outputstarfile.star</b></pre></a>

Same as `--write_selection`, however overrides files without asking.

<a name="write"><pre><b>--write outputstarfile.star</b></pre></a>

Writes all tables belonging to the STAR file which the current table is part of. Changes made to the
individual tables by editor methods will be written (selection will be released before writing). If only
specific tables or subsets should be written, you may use `--use` and write it as a selection with `--write_selection`.

<a name="writef"><pre><b>--writef outputstarfile.star</b></pre></a>

Same as `--write`, however overrides files without asking.

### Special

<a name="silent"><pre><b>--silent</b></pre></a>
This mutes the program (useful for automated procedures). Be aware that muting the program will force files to be overwritten (`--writef` and `--writef_selection` will be called instead of `--write` and `--write_selection`).

<a name="query"><pre><b>--query SQLite-query</b></pre></a>

This option is for experienced users that want to send their own SQLite queries. It will ignore any previously called selector methods. A SELECT statement will trigger a print of the called data.

## Usage Examples

Most tasks can be achieved by usage of very simple command. However, to demonstrate the flexibility of the StarTool, they are covered as well in the usage examples.

### Split particles by class after classification
*Scenario:* After running a 3D classification with 4 classes, a 3D refinement of all classes shall be performed automatically. In order to do so, one needs to split the data STAR file of the last iteration (lets assume iteration 25 here) into STAR files for the individual classes.

*Solution:* Write a shell script that looks like this
```bash
#!/bin/bash

# Run your Relion here:
relion_refine ... (run the 3d classification here)

python startool.py path/to/classification/3dclass_it025_data.star --select _rlnClassNumber=1 --write_selection path/to/classification/3dclass_it025_data_class001.star --deselect --select _rlnClassNumber=2 --write_selection path/to/classification/3dclass_it025_data_class002.star --deselect --select _rlnClassNumber=3 --write_selection path/to/classification/3dclass_it025_data_class003.star --deselect --select _rlnClassNumber=4 --write_selection path/to/classification/3dclass_it025_data_class004.star 

# Run the refinements here using the new inputs:
relion_refine ...
```

The only disadvantage here is that particles might need to be regrouped prior to 3D refinement if the number of particles is rather low. Unfortunately I did not come across a way of regrouping particles with Relion on the command line. 

### Split data by defocus

*Scenario:* For automated particle picking it might be required to use different defocus ranges in order to optimize the picking thresholds. For this example I want to split my data at a defocus of 1.7 um.

*Solution:*
```bash
python startool.py micrographs_ctf.star --select _rlnDefocusU\<=17000 --write_selection micrographs_ctf_df1.star --deselect --select _rlnDefocusU\>17000 --write_selection micrographs_ctf_df2.star
```

### Replace defocus values by values from reference

*Scenario:* You have redone CTF estimation using a program that performs better thatn your initial method and you want to replace the defocus values in your particle STAR file with the new ones.

*Solution:*
```bash
python startool.py data.star --replace_star _rlnDefocusU=better_ctf.star:_rlnMicrographName,_rlnCoordinateX,_rlnCoordinateY --replace_star _rlnDefocusV=better_ctf.star:_rlnMicrographName,_rlnCoordinateX,_rlnCoordinateY --write data_better_ctf.star
```
This will copy defocus values from better_ctf.star based on exactly matching micrograph name and particle coordinates.

### Recenter particles for re-extraction
*Scenario:* You still work with a version of Relion that cannot re-center particles automatically for re-extraction and you want to re-center refined particles according to their new origin values.

*Solution:*
```bash
python startool.py data.star --math _rlnCoordinateX=_rlnCoordinateX-_rlnOriginX --math _rlnCoordinateY=_rlnCoordinateY-_rlnOriginY --write data_recenter.star
```

### Split data files into batches per micrograph


*Scenario:* You want to split your particle STAR file into micrograph batches.

*Solution:*
```bash
python startool.py data.star --split_by _rlnMicrographName
```
This will create a lot of files containing particles per micrographs.