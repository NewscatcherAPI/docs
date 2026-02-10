#!/usr/bin/env python3
"""
Redirect Map Validator

Validates redirect-map.json against schema and checks for:
- Duplicate sources
- Circular redirects
- Broken redirect chains
- Invalid paths
- Schema compliance

Usage:
    python validate_redirects.py redirect-map.json [--schema redirect-map.schema.json]

Author: Documentation Team
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class RedirectValidator:
    def __init__(self, redirect_map: dict):
        self.data = redirect_map
        self.redirects = redirect_map.get('redirects', [])
        self.errors = []
        self.warnings = []
        
    def validate_schema_basics(self) -> bool:
        """Validate basic schema requirements."""
        print("Validating basic schema...")
        
        # Check required fields
        if 'version' not in self.data:
            self.errors.append("Missing required field: 'version'")
        elif not isinstance(self.data['version'], str):
            self.errors.append("Field 'version' must be a string")
            
        if 'redirects' not in self.data:
            self.errors.append("Missing required field: 'redirects'")
            return False
            
        if not isinstance(self.redirects, list):
            self.errors.append("Field 'redirects' must be an array")
            return False
            
        if len(self.redirects) == 0:
            self.warnings.append("No redirects defined")
            
        return len(self.errors) == 0
    
    def validate_redirect_objects(self) -> bool:
        """Validate individual redirect objects."""
        print(f"Validating {len(self.redirects)} redirect rules...")
        
        valid = True
        
        for i, redirect in enumerate(self.redirects):
            if not isinstance(redirect, dict):
                self.errors.append(f"Redirect #{i+1}: Must be an object")
                valid = False
                continue
            
            # Check required fields
            for field in ['source', 'destination', 'type', 'status_code']:
                if field not in redirect:
                    self.errors.append(f"Redirect #{i+1}: Missing required field '{field}'")
                    valid = False
            
            # Validate source
            source = redirect.get('source', '')
            if not source.startswith('/'):
                self.errors.append(f"Redirect #{i+1}: Source path must start with '/' - got: {source}")
                valid = False
            
            # Validate destination
            destination = redirect.get('destination', '')
            if not destination.startswith('/'):
                self.errors.append(f"Redirect #{i+1}: Destination path must start with '/' - got: {destination}")
                valid = False
            
            # Validate type
            redirect_type = redirect.get('type')
            if redirect_type not in ['permanent', 'temporary']:
                self.errors.append(f"Redirect #{i+1}: Type must be 'permanent' or 'temporary' - got: {redirect_type}")
                valid = False
            
            # Validate status_code
            status_code = redirect.get('status_code')
            if status_code not in [301, 302, 307, 308]:
                self.errors.append(f"Redirect #{i+1}: Status code must be 301, 302, 307, or 308 - got: {status_code}")
                valid = False
            
            # Type and status_code should match
            if redirect_type == 'permanent' and status_code not in [301, 308]:
                self.warnings.append(f"Redirect #{i+1}: Type is 'permanent' but status code is {status_code} (expected 301 or 308)")
            if redirect_type == 'temporary' and status_code not in [302, 307]:
                self.warnings.append(f"Redirect #{i+1}: Type is 'temporary' but status code is {status_code} (expected 302 or 307)")
        
        return valid
    
    def check_duplicate_sources(self) -> bool:
        """Check for duplicate source paths."""
        print("Checking for duplicate sources...")
        
        sources = {}
        duplicates = []
        
        for i, redirect in enumerate(self.redirects):
            source = redirect.get('source')
            if source in sources:
                duplicates.append(f"Source '{source}' appears in redirects #{sources[source]+1} and #{i+1}")
            else:
                sources[source] = i
        
        if duplicates:
            self.errors.extend(duplicates)
            return False
        
        print(f"  ✓ No duplicates found")
        return True
    
    def check_circular_redirects(self) -> bool:
        """Check for circular redirect chains."""
        print("Checking for circular redirects...")
        
        # Build redirect graph
        graph = {}
        for redirect in self.redirects:
            source = redirect.get('source')
            destination = redirect.get('destination')
            graph[source] = destination
        
        # Check for cycles
        def has_cycle(start: str, visited: Set[str], path: List[str]) -> Tuple[bool, List[str]]:
            if start in visited:
                # Found cycle - return the cycle path
                cycle_start = path.index(start)
                return True, path[cycle_start:] + [start]
            
            if start not in graph:
                return False, []
            
            visited.add(start)
            path.append(start)
            
            cycle, cycle_path = has_cycle(graph[start], visited, path)
            if cycle:
                return True, cycle_path
            
            path.pop()
            visited.remove(start)
            return False, []
        
        circular = []
        for source in graph:
            has_cycle_result, cycle_path = has_cycle(source, set(), [])
            if has_cycle_result:
                cycle_str = ' -> '.join(cycle_path)
                circular.append(f"Circular redirect: {cycle_str}")
        
        if circular:
            self.errors.extend(circular)
            return False
        
        print(f"  ✓ No circular redirects found")
        return True
    
    def check_redirect_chains(self) -> bool:
        """Check for long redirect chains."""
        print("Checking redirect chain lengths...")
        
        # Build redirect graph
        graph = {}
        for redirect in self.redirects:
            source = redirect.get('source')
            destination = redirect.get('destination')
            graph[source] = destination
        
        # Find chain lengths
        long_chains = []
        
        for source in graph:
            chain = [source]
            current = source
            visited = {source}
            
            while current in graph:
                next_hop = graph[current]
                if next_hop in visited:
                    break  # Circular - already caught
                chain.append(next_hop)
                visited.add(next_hop)
                current = next_hop
            
            if len(chain) > 3:
                chain_str = ' -> '.join(chain)
                long_chains.append(f"Long chain ({len(chain)} hops): {chain_str}")
        
        if long_chains:
            self.warnings.extend(long_chains)
            print(f"  ⚠ Found {len(long_chains)} redirect chains longer than 3 hops")
        else:
            print(f"  ✓ No long redirect chains found")
        
        return True
    
    def check_self_redirects(self) -> bool:
        """Check for redirects that point to themselves."""
        print("Checking for self-redirects...")
        
        self_redirects = []
        
        for i, redirect in enumerate(self.redirects):
            source = redirect.get('source')
            destination = redirect.get('destination')
            
            if source == destination:
                self_redirects.append(f"Redirect #{i+1}: Source and destination are identical: {source}")
        
        if self_redirects:
            self.errors.extend(self_redirects)
            return False
        
        print(f"  ✓ No self-redirects found")
        return True
    
    def validate_all(self) -> bool:
        """Run all validations."""
        print("=" * 70)
        print("Redirect Map Validation")
        print("=" * 70)
        print()
        
        valid = True
        
        # Run validations
        valid &= self.validate_schema_basics()
        valid &= self.validate_redirect_objects()
        valid &= self.check_duplicate_sources()
        valid &= self.check_self_redirects()
        valid &= self.check_circular_redirects()
        valid &= self.check_redirect_chains()
        
        return valid
    
    def print_summary(self):
        """Print validation summary."""
        print()
        print("=" * 70)
        print("Validation Summary")
        print("=" * 70)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All validations passed!")
        elif not self.errors:
            print(f"\n✅ No errors (but {len(self.warnings)} warnings)")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} error(s)")
        
        print()


def validate_with_jsonschema(data: dict, schema_file: str) -> bool:
    """Validate using JSON Schema (if jsonschema is installed)."""
    try:
        import jsonschema
        
        print("Validating against JSON Schema...")
        
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        
        jsonschema.validate(instance=data, schema=schema)
        print("  ✓ JSON Schema validation passed")
        return True
        
    except ImportError:
        print("  ℹ️  jsonschema library not installed - skipping schema validation")
        print("     Install with: pip install jsonschema")
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"  ❌ JSON Schema validation failed:")
        print(f"     {e.message}")
        return False
    except Exception as e:
        print(f"  ⚠️  Could not validate schema: {e}")
        return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_redirects.py redirect-map.json [--schema redirect-map.schema.json]")
        sys.exit(1)
    
    json_file = sys.argv[1]
    schema_file = None
    
    # Check for --schema argument
    if '--schema' in sys.argv:
        schema_idx = sys.argv.index('--schema')
        if schema_idx + 1 < len(sys.argv):
            schema_file = sys.argv[schema_idx + 1]
    
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
    
    # Validate with JSON Schema if provided
    schema_valid = True
    if schema_file:
        if not Path(schema_file).exists():
            print(f"Warning: Schema file not found: {schema_file}")
        else:
            schema_valid = validate_with_jsonschema(data, schema_file)
            print()
    
    # Run custom validations
    validator = RedirectValidator(data)
    custom_valid = validator.validate_all()
    validator.print_summary()
    
    # Exit with error code if validation failed
    if not (schema_valid and custom_valid):
        sys.exit(1)


if __name__ == "__main__":
    main()
