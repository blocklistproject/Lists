#!/usr/bin/env python3
"""
Random Domain Generator for Pi-hole
Generates random domain combinations from provided keywords
for use in Pi-hole adult content blocking lists.
"""

import random
import argparse
import sys
from typing import List, Set
from itertools import combinations

class DomainGenerator:
    def __init__(self):
        # Common TLDs used by adult content sites
        self.adult_tlds = [
            '.com', '.net', '.org', '.xxx', '.adult', '.sex', '.porn',
            '.tube', '.live', '.tv', '.cam', '.me', '.co', '.io',
            '.biz', '.info', '.online', '.site', '.website', '.fun'
        ]
        
        # Common prefixes and suffixes
        self.prefixes = [
            'www.', 'm.', 'mobile.', 'free.', 'live.', 'cam.',
            'hot.', 'teen.', 'mature.', 'real.', 'amateur.',
            'hd.', 'premium.', 'vip.', 'members.', 'secure.'
        ]
        
        self.suffixes = [
            'hd', 'live', 'cam', 'tube', 'hub', 'videos', 'pics',
            'movies', 'streaming', 'premium', 'free', 'online',
            'mobile', 'tv', 'channel', 'site', 'zone', 'world'
        ]
        
        # Common separators
        self.separators = ['-', '_', '']
        
        # Numbers often used
        self.numbers = ['18', '21', '69', '2024', '2025', 'hd', 'x']

    def generate_domain_variations(self, keywords: List[str], count: int = 100) -> List[str]:
        """Generate domain variations from keywords."""
        domains = set()
        keywords = [kw.lower().strip() for kw in keywords if kw.strip()]
        
        if not keywords:
            print("Error: No valid keywords provided!")
            return []
        
        print(f"Generating {count} domains from keywords: {', '.join(keywords)}")
        
        while len(domains) < count:
            # Choose generation method randomly
            method = random.choice([
                'simple_combination',
                'with_prefix',
                'with_suffix',
                'with_numbers',
                'keyword_pairs',
                'subdomain_style'
            ])
            
            domain = self._generate_by_method(method, keywords)
            if domain and self._is_valid_domain(domain):
                domains.add(domain)
        
        return sorted(list(domains))

    def _generate_by_method(self, method: str, keywords: List[str]) -> str:
        """Generate a domain using specific method."""
        
        if method == 'simple_combination':
            keyword = random.choice(keywords)
            tld = random.choice(self.adult_tlds)
            return f"{keyword}{tld}"
        
        elif method == 'with_prefix':
            prefix = random.choice(self.prefixes)
            keyword = random.choice(keywords)
            tld = random.choice(self.adult_tlds)
            return f"{prefix}{keyword}{tld}"
        
        elif method == 'with_suffix':
            keyword = random.choice(keywords)
            suffix = random.choice(self.suffixes)
            sep = random.choice(self.separators)
            tld = random.choice(self.adult_tlds)
            return f"{keyword}{sep}{suffix}{tld}"
        
        elif method == 'with_numbers':
            keyword = random.choice(keywords)
            number = random.choice(self.numbers)
            sep = random.choice(self.separators)
            tld = random.choice(self.adult_tlds)
            
            if random.choice([True, False]):
                return f"{keyword}{sep}{number}{tld}"
            else:
                return f"{number}{sep}{keyword}{tld}"
        
        elif method == 'keyword_pairs':
            if len(keywords) >= 2:
                kw1, kw2 = random.sample(keywords, 2)
                sep = random.choice(self.separators)
                tld = random.choice(self.adult_tlds)
                return f"{kw1}{sep}{kw2}{tld}"
            else:
                # Fallback to simple combination
                return f"{random.choice(keywords)}{random.choice(self.adult_tlds)}"
        
        elif method == 'subdomain_style':
            subdomain = random.choice(keywords)
            main_domain = random.choice(keywords + self.suffixes)
            tld = random.choice(self.adult_tlds)
            return f"{subdomain}.{main_domain}{tld}"
        
        return ""

    def _is_valid_domain(self, domain: str) -> bool:
        """Basic domain validation."""
        if not domain or len(domain) < 4:
            return False
        
        # Remove protocol if present
        domain = domain.replace('http://', '').replace('https://', '')
        
        # Check for valid characters
        allowed_chars = set('abcdefghijklmnopqrstuvwxyz0123456789.-')
        if not all(c in allowed_chars for c in domain.lower()):
            return False
        
        # Must contain a dot
        if '.' not in domain:
            return False
        
        # Cannot start or end with dash/dot
        if domain.startswith('-') or domain.endswith('-'):
            return False
        
        return True

    def save_to_file(self, domains: List[str], filename: str, format_type: str = 'pihole'):
        """Save domains to file in specified format."""
        try:
            with open(filename, 'w') as f:
                if format_type.lower() == 'pihole':
                    # Pi-hole format
                    f.write("# Generated adult content domains for Pi-hole\n")
                    f.write("# Generated using custom domain generator\n\n")
                    for domain in domains:
                        f.write(f"0.0.0.0 {domain}\n")
                elif format_type.lower() == 'hosts':
                    # Standard hosts file format
                    f.write("# Generated adult content domains\n\n")
                    for domain in domains:
                        f.write(f"127.0.0.1 {domain}\n")
                elif format_type.lower() == 'dnsmasq':
                    # DNSMasq format
                    for domain in domains:
                        f.write(f"address=/{domain}/0.0.0.0\n")
                else:
                    # Plain list
                    for domain in domains:
                        f.write(f"{domain}\n")
            
            print(f"Successfully saved {len(domains)} domains to {filename}")
            
        except Exception as e:
            print(f"Error saving to file: {e}")

    def load_keywords_from_file(self, filename: str) -> List[str]:
        """Load keywords from a text file."""
        try:
            with open(filename, 'r') as f:
                keywords = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            print(f"Loaded {len(keywords)} keywords from {filename}")
            return keywords
        except Exception as e:
            print(f"Error loading keywords from file: {e}")
            return []

def main():
    parser = argparse.ArgumentParser(description='Generate random domains for Pi-hole adult content blocking')
    parser.add_argument('-k', '--keywords', nargs='+', help='Keywords to use for generation')
    parser.add_argument('-f', '--keyword-file', help='File containing keywords (one per line)')
    parser.add_argument('-c', '--count', type=int, default=100, help='Number of domains to generate (default: 100)')
    parser.add_argument('-o', '--output', help='Output filename')
    parser.add_argument('--format', choices=['pihole', 'hosts', 'dnsmasq', 'plain'], 
                       default='pihole', help='Output format (default: pihole)')
    parser.add_argument('--preview', action='store_true', help='Preview first 10 generated domains')
    
    args = parser.parse_args()
    
    generator = DomainGenerator()
    keywords = []
    
    # Load keywords from file or command line
    if args.keyword_file:
        keywords.extend(generator.load_keywords_from_file(args.keyword_file))
    
    if args.keywords:
        keywords.extend(args.keywords)
    
    if not keywords:
        print("Error: No keywords provided. Use -k for command line keywords or -f for keyword file.")
        print("\nExample usage:")
        print("  python domain_generator.py -k adult content keywords -c 50 -o blocklist.txt")
        print("  python domain_generator.py -f keywords.txt -c 200 --format pihole -o pihole_blocklist.txt")
        sys.exit(1)
    
    # Generate domains
    domains = generator.generate_domain_variations(keywords, args.count)
    
    if not domains:
        print("No domains were generated!")
        sys.exit(1)
    
    # Preview if requested
    if args.preview:
        print(f"\nPreview (first 10 of {len(domains)} generated domains):")
        for domain in domains[:10]:
            print(f"  {domain}")
        print("...")
    
    # Save to file if output specified
    if args.output:
        generator.save_to_file(domains, args.output, args.format)
    else:
        # Print to stdout
        print(f"\nGenerated {len(domains)} domains:\n")
        for domain in domains:
            if args.format == 'pihole':
                print(f"0.0.0.0 {domain}")
            elif args.format == 'hosts':
                print(f"127.0.0.1 {domain}")
            elif args.format == 'dnsmasq':
                print(f"address=/{domain}/0.0.0.0")
            else:
                print(domain)

if __name__ == "__main__":
    main()
