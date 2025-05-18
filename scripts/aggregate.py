#!/usr/bin/env python3
import os
import glob
import re

def load_domains(path):
    domains = set()
    with open(path, encoding='utf-8') as f:
        for line in f:
            # Remove comments
            line = line.split('#',1)[0].strip()
            
            # Skip empty lines or comment lines
            if not line or line.startswith('!') or line.startswith('['):
                continue
                
            # Extract domain from "0.0.0.0 domain.com" format
            if line.startswith('0.0.0.0 '):
                domain = line[8:].strip()
                # Ensure it's a valid domain
                if domain and ' ' not in domain:
                    domains.add(domain)
            else:
                # Try to extract domain if it's just a raw domain
                if re.match(r'^[a-zA-Z0-9][-a-zA-Z0-9.]*\.[a-zA-Z]{2,}$', line):
                    domains.add(line)
    return domains

def write_hosts(domains, out_path):
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('# Generated hosts file\n')
        for d in sorted(domains):
            f.write(f'0.0.0.0 {d}\n')

def write_dnsmasq(domains, out_path):
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('# Generated dnsmasq config\n')
        for d in sorted(domains):
            f.write(f'address=/{d}/0.0.0.0\n')

def write_adblock(domains, out_path):
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('! Generated Adblock rules\n')
        for d in sorted(domains):
            f.write(f'||{d}^$important\n')

if __name__ == '__main__':
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # The list files are in the repository root, not in a 'Lists' subdirectory
    lists_dir = base_dir
    out_dir   = os.path.join(base_dir, 'releases')
    os.makedirs(out_dir, exist_ok=True)

    domains = set()
    for txt in glob.glob(os.path.join(lists_dir, '*.txt')):
        # Skip everything.txt to avoid duplicates
        if not os.path.basename(txt) == 'everything.txt':
            print(f'Processing {os.path.basename(txt)}...')
            file_domains = load_domains(txt)
            domains.update(file_domains)
            print(f'  Added {len(file_domains)} domains')

    write_hosts(domains,     os.path.join(out_dir, 'aggregated-hosts.txt'))
    write_dnsmasq(domains,   os.path.join(out_dir, 'aggregated-dnsmasq.conf'))
    write_adblock(domains,   os.path.join(out_dir, 'aggregated-adblock.txt'))

    print(f'➜ Wrote {len(domains)} unique domains into {out_dir}')
