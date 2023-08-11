import argparse
import sys

from csv import DictReader
from datetime import datetime
from zipfile import ZipFile


ANALYZED_FILES = [
        "raw_location_longitude.csv",
        "raw_location_latitude.csv",
        "raw_location_altitude.csv"
    ]


def extract_data_from_archive(path_to_archive_file):
    """
    Extract specific files from Withings data archive. If they don’t exist, stops the program
    :param path_to_archive_file: path to Withings data archive
    """
    zip_file = ZipFile(path_to_archive_file)

    if not all(file_name in zip_file.namelist() for file_name in ANALYZED_FILES):
        print(f"[!] Missing at least one of those file in the provided archive : {', '.join(ANALYZED_FILES)}")
        sys.exit(1)
    else:
        for csv_file in ANALYZED_FILES:
            zip_file.extract(csv_file)
        print("[+] Extraction completed")


def filter_by_date(data, _date):
    """Filter a given array on a specific date"""
    return [
        (_datetime, value)
        for _datetime, value in data
        if _datetime.date() == _date
    ]


def filter_by_interval(data, starting_datetime, ending_datetime):
    """Filter a given array based on a date interval"""
    return [
        (_datetime, value)
        for _datetime, value in data
        if starting_datetime <= _datetime <= ending_datetime
    ]


def generate_gpx_xml(activity_name, data):
    """
    Generates an XML string with Strava GPX format based on given data
    :param activity_name: Name of the activity that will display in Strava by default
    :param data: Array containing other arrays of date, longitude, latitude and altitude in the following order
    :return: String containing GPX formatted data
    """
    head = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        "<gpx creator=\"StravaGPX\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd\" version=\"1.1\" xmlns=\"http://www.topografix.com/GPX/1/1\" xmlns:gpxtpx=\"http://www.garmin.com/xmlschemas/TrackPointExtension/v1\" xmlns:gpxx=\"http://www.garmin.com/xmlschemas/GpxExtensions/v3\">"
        f"<metadata><time>{data[0][0].strftime('%Y-%m-%dT%H:%M:%SZ')}</time></metadata>"
        f"<trk><name>{activity_name}</name><type>1</type>"
    )

    tracking_data = "<trkseg>"
    for _date, _long, _lat, _alt in data:
        tracking_data += (
            f"<trkpt lat=\"{_lat}\" lon=\"{_long}\"><ele>{_alt}</ele>"
            f"<time>{_date.strftime('%Y-%m-%dT%H:%M:%SZ')}</time>"
            "</trkpt>"
        )
    tracking_data += "</trkseg>"

    footer = "</trk></gpx>"

    return head + tracking_data + footer


def extract_data_from_csv_file(file_path):
    """
    From a specific CSV file, extract the date and the given value. Works only for data with value containing only one element.
    :param file_path: Path to a given CSV file, previously extracted from Withings archive
    :return: Returns an array of
    """
    with open(file_path, "r") as data_file:
        csv_data = DictReader(data_file)
        return [
            (datetime.fromisoformat(data['start']), data['value'].strip('[]'))
            for data in csv_data
        ]
    
    
def get_parsed_args():
    """ Parsing given arguments and returning them """
    parser = argparse.ArgumentParser(
        prog="Withings data archive to gpx",
        description=(
            "Withings archive GPS data from your connected watch, extracts data of a specific timelapse and "
            "generate a GPX file compatible with Strava"
        )
    )
    parser.add_argument("archive_file_name", help="Name of the archive downloaded from Withings website")
    parser.add_argument(
        "-o",
        "--output-file",
        required=False,
        default="out",
        help="Name of gpx file you want to generate, without extension"
    )
    parser.add_argument(
        "-d",
        "--filter-date",
        required=False,
        help="Filtering data to extract all the coordinates of a specific day. Date must be in ISO format"
    )
    parser.add_argument(
        "-s",
        "--filter-starting-datetime",
        required=False,
        help="Filtering data to extract based on an interval. Starting date must be in ISO format"
    )
    parser.add_argument(
        "-e",
        "--filter-ending-datetime",
        required=False,
        help="Filtering data to extract based on an interval. Ending date must be in ISO format"
    )
    args = parser.parse_args()
    return args
    

def main():
    args = get_parsed_args()

    extract_data_from_archive(args.archive_file_name)

    date_longitude_tuples = extract_data_from_csv_file(ANALYZED_FILES[0])
    date_latitude_tuples = extract_data_from_csv_file(ANALYZED_FILES[1])
    date_altitude_tuples = extract_data_from_csv_file(ANALYZED_FILES[2])

    if args.filter_date:
        date_to_extract = datetime.fromisoformat(args.filter_date).date()
        date_longitude_filtered = filter_by_date(date_longitude_tuples, date_to_extract)
        date_latitude_filtered = filter_by_date(date_latitude_tuples, date_to_extract)
        date_altitude_filtered = filter_by_date(date_altitude_tuples, date_to_extract)
    elif args.filter_starting_datetime and args.filter_ending_datetime:
        starting_datetime = datetime.fromisoformat(args.filter_starting_datetime)
        ending_datetime = datetime.fromisoformat(args.filter_ending_datetime)
        date_longitude_filtered = filter_by_interval(date_longitude_tuples, starting_datetime, ending_datetime)
        date_latitude_filtered = filter_by_interval(date_latitude_tuples, starting_datetime, ending_datetime)
        date_altitude_filtered = filter_by_interval(date_altitude_tuples, starting_datetime, ending_datetime)
    else:
        print(
            "[!] At least one filter must be used : a filter by date or a filter on a timelapse" +
            " with a starting and ending date"
        )
        print("[-] Program exiting")
        sys.exit(1)
    print("[+] Filtering completed")

    # There is certainly a way to merge this data in an elegant way but im lazy today
    merged_long_lat_alt = []

    for _date, long in date_longitude_filtered:
        merged_long_lat_alt.append([_date, long])

    for _date, lat in date_latitude_filtered:
        for count, data in enumerate(merged_long_lat_alt):
            final_data_date = data[0]
            if _date == final_data_date:
                merged_long_lat_alt[count].append(lat)

    for _date, alt in date_altitude_filtered:
        for count, data in enumerate(merged_long_lat_alt):
            final_data_date = data[0]
            if _date == final_data_date:
                merged_long_lat_alt[count].append(alt)
    print("[+] Data merged")

    gpx_xml = generate_gpx_xml("withings archive extractor", merged_long_lat_alt)
    print("[+] GPX text generated")

    output_file_name = args.output_file + ".gpx"
    with open(output_file_name, "w") as f:
        f.write(gpx_xml)
    print("[+] GPX file generated")


if __name__ == "__main__":
    main()
