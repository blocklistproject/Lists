#!/usr/bin/env python3
import os
import glob

def load_domains(path):
    domains = set()
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.split('#',1)[0].strip()
            if not line or line.startswith('!') or line.startswith('['):
                continue
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
    lists_dir = os.path.join(base_dir, 'Lists')
    out_dir   = os.path.join(base_dir, 'releases')
    os.makedirs(out_dir, exist_ok=True)

    domains = set()
    for txt in glob.glob(os.path.join(lists_dir, '*.txt')):
        domains |= load_domains(txt)

    write_hosts(domains,     os.path.join(out_dir, 'aggregated-hosts.txt'))
    write_dnsmasq(domains,   os.path.join(out_dir, 'aggregated-dnsmasq.conf'))
    write_adblock(domains,   os.path.join(out_dir, 'aggregated-adblock.txt'))

    print(f'➜ Wrote {len(domains)} unique domains into {out_dir}')
