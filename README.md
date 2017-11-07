# fahda-logfile

A logfile contains information about all data points of every simulation.

## Download

You can download a zip file of the source from [here](https://github.com/sorinlab/fahda-logfile/archive/master.zip). You can also use the `git clone` command to get the files.

```bash
git clone https://github.com/sorinlab/fahda-logfile
cd fahda-logfile
git submodule init
git submodule update
```

## `logfile-make.pl`

An "all-frame" `pdb` file is generated for each simulation using `trjconv`. Parsing the "TITLE" lines in this file gives all the possible frames within a simulation.

```bash
# `echo 1` to select the "protein" group
echo 1 | trjconv -s frame0.tpr -f trj.xtc -o output.pdb

head output.pdb
# output.pdb
REMARK    GENERATED BY TRJCONV
TITLE     41361 t= 10500.00000
REMARK    THIS IS A SIMULATION BOX
CRYST1   75.058   75.058   75.058  90.00  90.00  90.00 P 1           1
MODEL      107
ATOM      1  H5T RG5     1      42.420  55.930  40.590  1.00  0.00
ATOM      2  O5' RG5     1      43.060  55.840  39.880  1.00  0.00
ATOM      3  C5' RG5     1      44.060  56.830  39.900  1.00  0.00
ATOM      4 H5'1 RG5     1      44.170  57.320  40.870  1.00  0.00
ATOM      5 H5'2 RG5     1      43.820  57.610  39.170  1.00  0.00
```

```bash
# USAGE

usegromacs33
./logfile-make.pl PROJ1797 output.log

head output.log
#output.log
1797       0       1         0
1797       0       1       100
1797       0       1       200
1797       0       1       300
1797       0       1       400
...
```

## `logfile_check.py`

`logfile_check.py` looks for the following issues in the logfile.

  1. Missing timestamps (timestamp zero included)
  2. Duplicate timestamps
  3. Last timestamp is not a multiple of 1000

### Usage

`logfile_check.py` is targeted at python3.

```bash
# print help info
./logfile_check.py -h

./logfile_check.py fah.log report.txt
```

### Development

`logfile_check_test.py` contains test cases that try to cover multiple scenarios for the primary methods in `logfile_check.py`. To run the test, you will need to install pytest via pip3.

```bash
sudo pip3 install -U pytest
pytest -v logfile_check_test.py
```