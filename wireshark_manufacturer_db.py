import argparse
import csv
import os
import re
import sys

import requests

URL = "https://gitlab.com/wireshark/wireshark/-/raw/master/manuf"

RE_VENDOR_CODE = re.compile(r'^\b[0-9A-F]+\b') # select lines that start with a vendor code
RE_OCTET = re.compile(r'(\:|\-|\.)')           # ":", "-", or "." can be used to separate octets
RE_SUBNET = re.compile(r'\/(\d+)')             # well-known MAC addresses may not have a full 6 
                                               # octets and insted have a netmask following them

def download_file():
    """Download raw text file."""
    r = requests.get(URL, stream=True)
    if r.status_code != 200:
        print("[!] Error downloading raw text file: %s" % r.reason) 
        sys.exit(1)
    data = r.content.decode().splitlines()
    return data
    
def load_file(fp: str): 
    """Read in raw text file from disk."""
    try:
        with open(fp, 'r') as f:
            data = [l.rstrip() for l in f.readlines()]
            return data            
    except Exception as e:            
        print("[!] Error importing raw text file: %s" % e)
        sys.exit(1)

    
def process(data: list):
    """Parse vendor codes, subnets, and vendor names from raw text file."""
    records = []
    for content in data: 
        if not RE_VENDOR_CODE.search(content):
            continue
        line = content.rsplit('\t')            
        try:
            vendor_code_hex = line[0]
            vendor_code = RE_OCTET.sub('', vendor_code_hex)
            if RE_SUBNET.search(vendor_code_hex):
                subnet = RE_SUBNET.search(vendor_code_hex).group(1) 
                vendor_code_hex = RE_SUBNET.sub('', vendor_code_hex)
                vendor_code = RE_SUBNET.sub('', vendor_code)
            else:        
                subnet = ''
            vendor_name = line[1]
            vendor_fullname = line[2] if len(line) == 3 else ''
            records.append([vendor_code, vendor_code_hex, subnet, vendor_name, vendor_fullname])
        except Exception as e:            
            print("[!] Error processing %s: %s"  % (line, e))
    return records
    
    
def main(args):
    headers = ['vendor_code', 'vendor_code_hex', 'subnet', 'vendor_name', 'vendor_fullname']
    
    with open(args.output_file, "w") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        if args.input_file:
           data = load_file(args.input_file)
        else:           
           data = download_file()
        writer.writerows(process(data))
            
    print("[+] File saved to: %s" % os.path.abspath(args.output_file))
    
if __name__ == "__main__":    
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument("-i", "--input_file", help="Path of Wireshark Manufacturer Databases text file")
    parser.add_argument("-o", "--output_file", default="wireshark_manufacturer_database.csv", help="Output path of processed Wireshark Manufacturer Database text file")
    args = parser.parse_args()
    
    main(args)