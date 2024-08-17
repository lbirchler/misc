#!/usr/bin/env python3
'''
stig-util.py

REQUIREMENTS
  # yum install openscap-scanner
  # yum install scap-security-guide

USAGE
  stig-util.py [-h] {scan,fails,fix}

  positional arguments:
    scan
    fails SUMMARY_FILE
    fix REMEDIATION_FILE OUTPUT_FILE RULE_PATTERNS

WORKFLOW
  Run scan
  # ./stig-util.py scan  

  List failed rules 
  # ./stig-util.py fails stig-202408171708-summary.txt  

  Generate script for specific failed rules (e.g any rule with kernel in rule name)
  # ./stig-util.py fix stig-202408171645-remediation.sh stig-fix-kernel.sh kernel

  Run fix script
  # ./stig-fix-kernel.sh

  Rinse and repeat
'''
import argparse
import os
import subprocess
import sys
from datetime import datetime


SCAP_SOURCE = "/usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml"

DATE = datetime.now().strftime('%Y%m%d%H%M')

RESULTS_FILE     = f"stig-{DATE}-results.xml"
REPORT_FILE      = f"stig-{DATE}-report.html"
REMEDIATION_FILE = f"stig-{DATE}-remediation.sh"
SUMMARY_FILE     = f"stig-{DATE}-summary.txt"


def run_scan():
  '''Run a scan and generate results and html report files.'''
  print('+ Running scan...')
  subprocess.call(f'''\
    oscap xccdf eval \
    --profile stig \
    --results {RESULTS_FILE} \
    --report {REPORT_FILE} \
    {SCAP_SOURCE} \
    | tee {SUMMARY_FILE}''',
    shell=True,
    stdout=sys.stdout,
    stderr=sys.stderr
  )
  print(f'+ Created {RESULTS_FILE}')
  print(f'+ Created {REPORT_FILE}')
  print(f'+ Created {SUMMARY_FILE}')

  print('+ Scan results')
  subprocess.call(
    f'grep Result {SUMMARY_FILE} | cut -f2 | sort | uniq -c',
    shell=True,
    stdout=sys.stdout
  )

  # generate remediation script based on the scan results
  subprocess.call(f'''\
    oscap xccdf generate fix \
    --fix-type bash \
    --output {REMEDIATION_FILE} \
    --result-id "$(oscap info {RESULTS_FILE} | grep "Result ID:" | cut -d ':' -f2 | tr -d ' ')" \
    {RESULTS_FILE}''',
    shell=True,
    stdout=sys.stdout,
    stderr=sys.stderr
  )
  print(f'+ Created {REMEDIATION_FILE}')


def list_fails(summary_file):
  subprocess.call(
    f'grep -B3 -P "Result.+fail" {summary_file} | grep Rule | cut -f2',
    shell=True,
    stdout=sys.stdout
  )


def gen_fix_script(remediation_file, output_file, rule_patterns):
  rules = {}
  with open(remediation_file, 'r') as f:
    copy = False
    rule = ''
    code = ''
    for line in f:
      if line.startswith(') # END'):
        code += line
        code += '\n\n'
        rules[rule] = code
        rule = ''
        code = ''
        copy = False
      if line.startswith('# BEGIN'):
        rule = line.split(' ')[-1].rstrip()[1:-1]
        copy = True
      if copy:
        code += line

  fixes = ''
  for k,v in rules.items():
    for pat in rule_patterns:
      if pat in k:
        fixes += v

  with open(output_file, 'w') as f:
    f.write(f'#!/usr/bin/env bash\n\n{fixes}')
  os.chmod(output_file, 0o700)
  print(f'+ Created {output_file}')


def main():
  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers(dest='cmd')

  scan = subparsers.add_parser('scan', help='run new scan')

  fails = subparsers.add_parser('fails', help='list fails')
  fails.add_argument('SUMMARY_FILE')

  fix = subparsers.add_parser('fix', help='create remediation script for specific rules')
  fix.add_argument('REMEDIATION_FILE')
  fix.add_argument('OUTPUT_FILE')
  fix.add_argument('RULE_PATTERNS', nargs='+')

  args = parser.parse_args()

  if args.cmd == 'scan':
    run_scan()
  elif args.cmd == 'fails':
    list_fails(args.SUMMARY_FILE)
  elif args.cmd == 'fix':
    gen_fix_script(args.REMEDIATION_FILE, args.OUTPUT_FILE, args.RULE_PATTERNS)


if __name__ == '__main__':
  main()
