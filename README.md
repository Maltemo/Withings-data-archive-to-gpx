# Withings-data-archive-to-gpx

Withings archive GPS data from your connected watch, extracts data of a specific timelapse and generate a GPX file compatible with Strava

Sometimes, while using a Withings watch, if you pause an activity for too long and you unpause the activity, you will loose the second part of your session on the withings interface and on Strava.
The data was recorded, but Withings seem to have a bug detecting the start and the end of an activity with a pause.

This tool is there to help recover this missing data.

Disclaimer : I didn’t manage the heart rate data because I didn’t take the time to understand how to calculate it based on the raw data.

## Download withings GPS archive

Request data archive from your withings account using this link : https://account.withings.com/export/user_select

Check your emails, you’ll have to wait a bit for the archive to be generated.

Once you got the mail, download the archive.

Place it in the folder of this project.

## Using the tool

### Install

This tool doesn’t need dependencies

Python 3 will be enough, I only tested it on Python 3.9, but it should be compatible with python 3.7

So you got nothing to do :D

Side note : `sys` standard library is only used to properly exit the program on specific errors. 
[Python documentation on sys.exit](https://docs.python.org/3.9/library/sys.html#sys.exit)

### Usage 

#### Help

```commandline
python3 withings_data_extract.py -h
```

Output of the help manual :
```commandline
usage: Withings data archive to gpx [-h] [-o OUTPUT_FILE] [-d FILTER_DATE]
                                    [-s FILTER_STARTING_DATETIME]
                                    [-e FILTER_ENDING_DATETIME]
                                    archive_file_name

Withings archive GPS data from your connected watch, extracts data of a
specific timelapse and generate a GPX file compatible with Strava

positional arguments:
  archive_file_name     Name of the archive downloaded from Withings website

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Name of gpx file you want to generate, without
                        extension
  -d FILTER_DATE, --filter-date FILTER_DATE
                        Filtering data to extract all the coordinates of a
                        specific day. Date must be in ISO format
  -s FILTER_STARTING_DATETIME, --filter-starting-datetime FILTER_STARTING_DATETIME
                        Filtering data to extract based on an interval.
                        Starting date must be in ISO format
  -e FILTER_ENDING_DATETIME, --filter-ending-datetime FILTER_ENDING_DATETIME
                        Filtering data to extract based on an interval. Ending
                        date must be in ISO format
```

Dates MUST be in format [ISO_8601](https://en.wikipedia.org/wiki/ISO_8601), otherwise it won’t work.

#### Example of usage

Extracting from the withings zip archive every data recorded on the 2nd of April 2023:

```commandline
python3 withings_data_extract.py data_Tournesol_164556747.zip -d "2023-04-02T00:00:00+02:00" -o paris_marathon
```

The GPX file will be named `paris_marathon.gpx`.

Extracting from the withings zip a bicycle ride on the 6th of July 2023, from 14h30 (2:30 PM) to 17h45 (5:45 PM):
```commandline
python3 withings_data_extract.py data_Haddock_168956734.zip -s "2023-07-06T14:30:00+02:00" -e "2023-07-06T17:45:00+02:00"
```

As the option `-o` isn’t provided, the output GPX file is named `out.gpx`.

### Import GPX file to Strava

You can just follow this link : https://www.strava.com/upload/select (why over complicating things)

And upload the GPX file. Tadaa