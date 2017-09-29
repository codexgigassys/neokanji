import argparse
import sys
import urllib2
import json
import datetime
import getopt
import time
from IPython import embed
"""the dates will be displayed in UTC-0"""

# TODO: REFACTOR


def get_hashes_from(file):
    text_file = open(file, "r")
    hashes = text_file.read().splitlines()
    text_file.close()
    return hashes


def get_page(url):
    response = None
    attempts = 0
    request = urllib2.Request(url)
    while attempts < 3:
        try:
            response = urllib2.urlopen(request).read()
            break
        except Exception:
            attempts += 1
            time.sleep(1)
    if not response:
        return None

    try:
        response_dict = json.loads(response)
    except ValueError:
        return None

    return response_dict


def get_metadata(file_hash):
    metadata = get_page(
        "http://CODEX_HOST:4500/api/v1/metadata?file_hash=%s" % file_hash)
    return metadata


def get_office_data(metadata):
    macros = metadata.get('office', {}).get('macros', {}).get('macros', [])
    names = []
    for macro in macros:
        names.append(macro.get('macro_name'))
    return names


def get_office_last_saved_time(metadata):
    last_saved_time = metadata.get('office', {}).get(
        'metadata', {}).get('last_saved_time')
    if not last_saved_time:
        last_saved_time = "-"
    return str(last_saved_time)


def codex_timestamp_to_datetime(hex_str_str):
    hex_str = hex_str_str.replace("'", "")
    int_val = int(hex_str, 0)
    return datetime.datetime.utcfromtimestamp(int_val)


def get_filename_from_metadata(metadata):
    return (metadata
            .get('particular_header', {})
            .get('version', {})
            .get('string_file_info', {})
            .get('OriginalFilename', "-"))


def get_parsed_pdb_from_metadata(metadata):
    strings = (metadata.get('particular_header', {}).get('strings', {})
               .get('interesting', []))
    pdbs = []
    for st in strings:
        if ".pdb" in st.lower():
            pdbs.append(st.replace("'", "").split(".pdb", 1)[0] + ".pdb")
    return pdbs


def get_interesting_strings(metadata):
    interesting = (metadata.get('particular_header', {}).get('strings', {})
                   .get('interesting', []))
    for st in interesting:
        if ".pdb" in st.lower():
            interesting.remove(st)
    return interesting


def get_compilation_timestr_from_metadata(metadata):
    compilation_time = (metadata
                        .get('particular_header', {})
                        .get('headers', {})
                        .get('file_header', {})
                        .get('TimeDateStamp'))
    if not compilation_time:
        compilation_timestr = "-"
    else:
        compilation_timestamp = codex_timestamp_to_datetime(compilation_time)
        compilation_timestr = compilation_timestamp.strftime(
            '%Y-%m-%d %H:%M:%S')
    return compilation_timestr


def get_size_from_metadata(metadata):
    return str(metadata.get('size', "-"))


def get_signatures_from(metadata):
    signatures = (metadata.get('dynamic', {}).get('signatures', []))
    return signatures


def get_description_from_metadata(metadata):
    description = metadata.get('description', "-")
    return description.replace(",", "")


def process_hash(file_hash):
    metadata = get_metadata(file_hash)
    if not metadata:
        return None

    sha1 = metadata.get('hash', {}).get('sha1')
    sha256 = metadata.get('hash', {}).get('sha2')
    md5 = metadata.get('hash', {}).get('md5')

    if not sha1:
        return {}

    print file_hash
    print "\n"

    file_name = get_filename_from_metadata(metadata)

    pdb = []
    pdb = get_parsed_pdb_from_metadata(metadata)

    compilation_timestr = get_compilation_timestr_from_metadata(metadata)

    size = get_size_from_metadata(metadata)

    description = get_description_from_metadata(metadata)

    signatures = []
    signatures = get_signatures_from(metadata)

    interesting = get_interesting_strings(metadata)

    office = get_office_data(metadata)
    last_saved_time = get_office_last_saved_time(metadata)
    data = {'SHA1': sha1,
            'SHA256': sha256,
            'MD5': md5,
            'File_Name': file_name,
            'PDB': pdb,
            'Compilation_Time': compilation_timestr,
            'Size': size,
            'Description': description,
            'Signatures': signatures,
            'Interesting': interesting,
            'Last_Saved': last_saved_time,
            'Office': office
            }

    return data


def save_json_to_file(data, outputfile):
    f = open(outputfile.replace(".txt", ""), 'w')
    json.dump(data, f)
    f.close()


def main(argv):

    inputfile = argv
    hashes = get_hashes_from(inputfile)
    processed_hashes = []

    for file_hash in hashes:
        data = process_hash(file_hash)
        if data is not None:
            processed_hashes.append(data)
    outputfile = inputfile.replace(".txt", ".json")
    save_json_to_file(processed_hashes, outputfile)


if __name__ == "__main__":
    main(sys.argv[1:])
