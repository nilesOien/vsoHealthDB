
# Reading Health Report CSV files into a database

These scripts read into an sqlite database, but would need only minor
modification to read to Postgres or MySQL databases instead.

Assuming you are working in the directory $HOME/vsoHealthDB/ you
can set up by making a python virtual environment like so :

```
python3 -m venv $HOME/vsoHealthDB/pyEnv
```

Assuming the system you are on uses python3 (if not, then just use "python"
in the above command).

Then enter the virtual environment by sourcing the activation file :

```
noien@noienlaptop vsoHealthDB % source $HOME/vsoHealthDB/pyEnv/bin/activate
(pyEnv) noien@noienlaptop vsoHealthDB % 
```

The command prompt should change, as shown above. *You need this so that
any modules installed are only installed in the virtual environment.*

Then upgrade pip and install the utilities needed in the environment :
```
pip install --upgrade pip
pip install sqlalchemy sqlalchemy-utils ruff
```

Then run the python script to set up a database with an empty table in it :

```
./createDB.py
```

A file named report.db will be written. That is the sqlite database.

Optionally, if the sqlite3 client is installed, then you can see the empty
table by running sqlite3 on the file report.db and issuing the .schema
command, as shown below. Use CNTRL-D to exit the sqlite3 client.

```
(pyEnv) noien@noienlaptop vsoHealthDB % sqlite3 report.db 
SQLite version 3.39.5 2022-10-14 20:58:05
Enter ".help" for usage hints.
sqlite> .schema
CREATE TABLE reports (
	"Timestring" VARCHAR NOT NULL, 
	"Provider" VARCHAR NOT NULL, 
	"Source" VARCHAR NOT NULL, 
	"Instrument" VARCHAR NOT NULL, 
	"Status" INTEGER NOT NULL, 
	PRIMARY KEY ("Timestring", "Provider", "Source", "Instrument", "Status"), 
	CONSTRAINT unique_constraint UNIQUE ("Timestring", "Provider", "Source", "Instrument", "Status")
);
sqlite> ^D
```

After the database has been created, a CSV file can be read into the database in verbose mode, like so :
```
./fileToDB.py --inFile vso_health_check_20260521_134851.csv --verbose
```
Subsequent attempts to read the same file will fail due to the
unique constraint placed on the database table.

Optionally, if sqlite3 is installed, we can see how many entries there are in
the database, and print the HAO ones as shown below :
```
(pyEnv) noien@noienlaptop vsoHealthDB % sqlite3 report.db
SQLite version 3.39.5 2022-10-14 20:58:05
Enter ".help" for usage hints.
sqlite> select count(*) from reports;
125
sqlite> select Timestring, Source, Instrument,Status from reports where Provider='HAO';
20260521_134851|MLSO|K-Cor|9
20260521_134851|MLSO|chp|0
20260521_134851|MLSO|dpm|1
20260521_134851|MLSO|mk4|1
20260521_134851|SMM|cp|0
sqlite> ^D
```

The printDB python script can then read from the database and filter the results.
Examples are shown below :
```
 ./printDB.py --minTime 20260521_134850 --maxTime 20260521_134852
 ./printDB.py --sources=STEREO_B,PUNCH
 ./printDB.py --instruments SECCHI,SWAVES
 ./printDB.py --providers=HAO,NSO
```
Filters like the ones above can be combined to operate in conjunction.

The printDB.py script has the --help option that comes automatically with the arg parse module :
```
./printDB.py --help
usage: printDB.py [-h] [--minTime MINTIME] [--maxTime MAXTIME]
                  [--instruments INSTRUMENTS] [--providers PROVIDERS]
                  [--sources SOURCES] [--verbose]

Print a selection from the database.

optional arguments:
  -h, --help            show this help message and exit
  --minTime MINTIME, -b MINTIME
                        Minimum time in YYYYMMDD_HHMMSS format
  --maxTime MAXTIME, -e MAXTIME
                        Maximum time in YYYYMMDD_HHMMSS format
  --instruments INSTRUMENTS, -i INSTRUMENTS
                        Comma separated list of instruments
  --providers PROVIDERS, -p PROVIDERS
                        Comma separated list of providers
  --sources SOURCES, -s SOURCES
                        Comma separated list of sources
  --verbose, -v         Activate verbose messaging.
```

Also, because ruff is installed, one can run
```
ruff check
```
in the virtual environment to check the python code.

# Example

Below is a command to find the problematic responses (non-zero status) from
the JSOC provider for the first five days in May, 2026.
```
./printDB.py --minTime 20260501_000000 --maxTime 20260505_235959 --providers JSOC --minStatus 1
[{'Instrument': 'AIA',
  'Provider': 'JSOC',
  'Source': 'SDO',
  'Status': 8,
  'Timestring': '20260503_130016'},
 {'Instrument': 'AIA',
  'Provider': 'JSOC',
  'Source': 'SDO',
  'Status': 8,
  'Timestring': '20260504_130044'}]
2 results found.
```
Obviously this is reliant on the database having been loaded.

