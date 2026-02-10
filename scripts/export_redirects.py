#!/usr/bin/env python3
"""
Redirect Rules Export Script

Exports redirect-map.json to various platform formats:
- Mintlify (redirects.json)
- Cloudflare Page Rules
- Nginx configuration
- Apache .htaccess
- Vercel (vercel.json)
- Netlify (_redirects)

Usage:
    python export_redirects.py redirect-map.json --format mintlify
    python export_redirects.py redirect-map.json --format cloudflare
    python export_redirects.py redirect-map.json --format nginx
    python export_redirects.py redirect-map.json --format apache
    python export_redirects.py redirect-map.json --format all

Author: Documentation Team
"""

import json
import sys
from pathlib import Path
from typing import List, Dict


def export_mintlify(redirects: List[Dict], output_file: str = "mintlify-redirects.json"):
    """Export to Mintlify redirects.json format."""
    
    mintlify_redirects = []
    
    for redirect in redirects:
        # Mintlify uses simple source/destination format
        mintlify_redirects.append({
            "source": redirect['source'],
            "destination": redirect['destination']
        })
    
    output = {"redirects": mintlify_redirects}
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"✓ Mintlify redirects exported to: {output_file}")
    print(f"  Add this file to your Mintlify project root")


def export_cloudflare(redirects: List[Dict], output_file: str = "cloudflare-rules.txt"):
    """Export to Cloudflare Page Rules format."""
    
    rules = []
    rules.append("# Cloudflare Page Rules Configuration")
    rules.append("# Copy these rules to your Cloudflare dashboard")
    rules.append("# Go to: Websites > [Your Site] > Rules > Page Rules")
    rules.append("")
    
    for i, redirect in enumerate(redirects, 1):
        rules.append(f"# Rule {i}")
        rules.append(f"URL Match: https://www.newscatcherapi.com{redirect['source']}")
        rules.append(f"Setting: Forwarding URL")
        rules.append(f"Status Code: {redirect['status_code']}")
        rules.append(f"Destination: https://www.newscatcherapi.com{redirect['destination']}")
        rules.append("")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rules))
    
    print(f"✓ Cloudflare rules exported to: {output_file}")
    print(f"  Apply these rules in your Cloudflare dashboard")


def export_nginx(redirects: List[Dict], output_file: str = "nginx-redirects.conf"):
    """Export to Nginx configuration format."""
    
    lines = []
    lines.append("# Nginx Redirect Configuration")
    lines.append("# Add this to your nginx.conf or site configuration")
    lines.append("")
    lines.append("server {")
    lines.append("    # ... your existing configuration ...")
    lines.append("")
    
    for redirect in redirects:
        status = redirect['status_code']
        source = redirect['source']
        destination = redirect['destination']
        
        # Nginx redirect syntax
        lines.append(f"    location = {source} {{")
        lines.append(f"        return {status} {destination};")
        lines.append(f"    }}")
        lines.append("")
    
    lines.append("}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Nginx configuration exported to: {output_file}")
    print(f"  Include this file in your nginx configuration")


def export_apache(redirects: List[Dict], output_file: str = "apache-redirects.htaccess"):
    """Export to Apache .htaccess format."""
    
    lines = []
    lines.append("# Apache Redirect Configuration")
    lines.append("# Add this to your .htaccess file")
    lines.append("")
    lines.append("RewriteEngine On")
    lines.append("")
    
    for redirect in redirects:
        status = redirect['status_code']
        source = redirect['source']
        destination = redirect['destination']
        
        # Escape special regex characters
        escaped_source = source.replace('.', r'\.')
        
        # Determine redirect flag
        if status == 301:
            flag = "R=301,L"
        elif status == 302:
            flag = "R=302,L"
        elif status == 307:
            flag = "R=307,L"
        elif status == 308:
            flag = "R=308,L"
        else:
            flag = "R,L"
        
        lines.append(f"RewriteRule ^{escaped_source.lstrip('/')}$ {destination} [{flag}]")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Apache redirects exported to: {output_file}")
    print(f"  Place this file as .htaccess in your document root")


def export_vercel(redirects: List[Dict], output_file: str = "vercel-redirects.json"):
    """Export to Vercel vercel.json format."""
    
    vercel_redirects = []
    
    for redirect in redirects:
        vercel_redirects.append({
            "source": redirect['source'],
            "destination": redirect['destination'],
            "permanent": redirect['type'] == 'permanent'
        })
    
    output = {
        "redirects": vercel_redirects
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"✓ Vercel redirects exported to: {output_file}")
    print(f"  Merge this with your existing vercel.json")


def export_netlify(redirects: List[Dict], output_file: str = "_redirects"):
    """Export to Netlify _redirects format."""
    
    lines = []
    lines.append("# Netlify Redirects Configuration")
    lines.append("# Place this file as _redirects in your publish directory")
    lines.append("")
    
    for redirect in redirects:
        status = redirect['status_code']
        source = redirect['source']
        destination = redirect['destination']
        
        lines.append(f"{source}  {destination}  {status}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Netlify redirects exported to: {output_file}")
    print(f"  Place this file in your publish directory")


def main():
    if len(sys.argv) < 2:
        print("Usage: python export_redirects.py redirect-map.json --format [mintlify|cloudflare|nginx|apache|vercel|netlify|all]")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    # Default format
    export_format = 'all'
    
    # Check for --format argument
    if '--format' in sys.argv:
        format_idx = sys.argv.index('--format')
        if format_idx + 1 < len(sys.argv):
            export_format = sys.argv[format_idx + 1].lower()
    
    # Check if file exists
    if not Path(json_file).exists():
        print(f"Error: File not found: {json_file}")
        sys.exit(1)
    
    # Load JSON
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {json_file}")
        print(f"  {e}")
        sys.exit(1)
    
    redirects = data.get('redirects', [])
    
    if not redirects:
        print("Error: No redirects found in JSON file")
        sys.exit(1)
    
    print("=" * 70)
    print("Redirect Rules Export")
    print("=" * 70)
    print(f"Source: {json_file}")
    print(f"Total redirects: {len(redirects)}")
    print(f"Export format: {export_format}")
    print()
    
    # Export based on format
    formats = {
        'mintlify': export_mintlify,
        'cloudflare': export_cloudflare,
        'nginx': export_nginx,
        'apache': export_apache,
        'vercel': export_vercel,
        'netlify': export_netlify
    }
    
    if export_format == 'all':
        for fmt_name, fmt_func in formats.items():
            fmt_func(redirects)
            print()
    elif export_format in formats:
        formats[export_format](redirects)
        print()
    else:
        print(f"Error: Unknown format '{export_format}'")
        print(f"Available formats: {', '.join(formats.keys())}, all")
        sys.exit(1)
    
    print("=" * 70)
    print("Export Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
