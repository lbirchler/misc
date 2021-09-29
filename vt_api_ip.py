from rich import color
from config import API_KEY
from datetime import datetime
import argparse
import pandas as pd
import requests
import time
import sys
from rich.console import Console
from rich.table import Table 
from rich.style import Style

console = Console()
danger_style = Style(color='red', bold=True)
warning_style = Style(color='yellow', bold=True)

def get_ip_report(ip, API_KEY):
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    header = {"x-apikey": API_KEY}
    try:
        r = requests.get(url, headers=header).json()
    except requests.ConnectionError as e:
        print(f"ConnectionError: {e}")
        sys.exit()
    console.print(f'[+] Results for ip: [bold cyan]{ip}[/bold cyan]')
    return r["data"]

def ip_attributes(rpt):
    table = Table(title='Attributes', show_header=False) 
    table.add_column("attr")
    table.add_column("value")

    data = rpt["attributes"]
    for key, value in data.items():
        if key in [
            "network",
            "country",
            "continent",
            "asn",
            "as_owner",
            "regional_internet_registry",
        ]:
            table.add_row(str(key), str(value))
    console.print(table)
    return

def analysis_stats(rpt):
    table = Table(title='Analysis Stats', show_header=False) 
    table.add_column("attr")
    table.add_column("value")

    data = rpt['attributes']['last_analysis_stats']
    for key, value in data.items():
        if key in ['malicious']:
            table.add_row(str(key), str(value), style=danger_style)
        elif key in ['suspicious']:
            table.add_row(str(key), str(value), style=warning_style)
        else:
            table.add_row(str(key), str(value))
    console.print(table)
    return

def analysis_results(rpt):
    table = Table(title='Analysis Results') 
    table.add_column("Vendor")
    table.add_column("Category")
    table.add_column("Result")
    table.add_column("Method")

    data = rpt['attributes']['last_analysis_results']
    for vendor, result in data.items():
        r = [vendor]
        for key, value in result.items():
            if value != 'engine_name':
                r.append(str(value))
        if r[1] == 'malicious':
            table.add_row(r[0], f'[red]{r[1]}[/red]', r[2], r[3])
        if r[1] == 'suspicious':
            table.add_row(r[0], f'[yellow]{r[1]}[/yellow]', r[2], r[3])
    console.print(table)
    return

def main(input_file):
    with open(input_file, "r") as f:
        ip_list = f.read().split()

    # separate list of ips into groups of 4
    ip_sublists = [ip_list[x : x + 4] for x in range(0, len(ip_list), 4)]
    total_sublists = len(ip_sublists)
    for sublist in ip_sublists:
        for ip in sublist:
            print('')
            x = get_ip_report(ip, API_KEY)
            print('')
            f"\n{ip_attributes(x)}"
            f"\n{analysis_stats(x)}"
            f"\n{analysis_results(x)}"
            console.print(f"link: [link={x['links']['self']}]{x['links']['self']}[/link]")
            print('')
        if total_sublists > 1:
            time.sleep(61)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="input file", type=str)
    args = parser.parse_args()

    input = args.input

    main(input_file=input)
