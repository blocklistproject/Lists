import os
import sys

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "pulse360.com"

# Define file patterns and how to match the domain
# Each entry: (relative_path, check_function)
# check_function(line) returns True if line should be removed (i.e., contains the domain as an entry)
def check_plain_line(line):
    # Line is exactly the domain (maybe with whitespace)
    return line.strip() == DOMAIN

def check_hosts_line(line):
    # Line like "0.0.0.0 domain" or "::1 domain"
    parts = line.strip().split()
    return len(parts) >= 2 and parts[1] == DOMAIN

def check_adguard_line(line):
    # Line like "||domain^"
    stripped = line.strip()
    return stripped == f"||{DOMAIN}^"

def check_dnsmasq_line(line):
    # Line like "server=/domain/"
    stripped = line.strip()
    return stripped == f"server=/{DOMAIN}/"

# Mapping of files to check functions
FILES_TO_CHECK = [
    ("abuse.txt", check_hosts_line),
    ("adguard/abuse-ags.txt", check_adguard_line),
    ("adguard/ads-ags.txt", check_adguard_line),
    ("adguard/basic-ags.txt", check_adguard_line),
    ("adguard/everything-ags.txt", check_adguard_line),
    ("adguard/malware-ags.txt", check_adguard_line),
    ("ads.txt", check_hosts_line),
    ("alt-version/abuse-nl.txt", check_hosts_line),
    ("alt-version/ads-nl.txt", check_hosts_line),
    ("alt-version/basic-nl.txt", check_hosts_line),
    ("alt-version/everything-nl.txt", check_hosts_line),
    ("alt-version/malware-nl.txt", check_hosts_line),
    ("basic.txt", check_hosts_line),
    ("dnsmasq-version/abuse-dnsmasq.txt", check_dnsmasq_line),
    ("dnsmasq-version/ads-dnsmasq.txt", check_dnsmasq_line),
    ("dnsmasq-version/everything-dnsmasq.txt", check_dnsmasq_line),
    ("dnsmasq-version/malware-dnsmasq.txt", check_dnsmasq_line),
    ("everything.txt", check_hosts_line),
    ("malware.txt", check_hosts_line),
]

def main():
    changed_files = []
    for rel_path, check_func in FILES_TO_CHECK:
        path = os.path.join(REPO_DIR, rel_path)
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue
        with open(path) as f:
            lines = f.readlines()
        new_lines = []
        removed = 0
        for line in lines:
            if check_func(line):
                removed += 1
                print(f"Removing from {rel_path}: {line.strip()}")
                continue
            new_lines.append(line)
        if removed > 0:
            with open(path, 'w') as f:
                f.writelines(new_lines)
            print(f"Updated {rel_path}: removed {removed} occurrence(s)")
            changed_files.append(rel_path)
        else:
            print(f"No match found in {rel_path}")

    if not changed_files:
        print("No changes made.")
        return 0

    # Run build.py to regenerate derived files
    print("\nRunning build.py...")
    result = os.system("python3 build.py")
    if result != 0:
        print("Build failed!")
        return 1

    # Commit changes
    print("\nCommitting changes...")
    os.system("git add .")
    commit_msg = f"Remove false positive domain {DOMAIN} from blocklists\n\nRemoved from: {', '.join(changed_files)}"
    os.system(f'git commit -m "{commit_msg}"')

    # Push
    print("\nPushing to origin...")
    os.system("git push origin main")

    print("\nDone.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
