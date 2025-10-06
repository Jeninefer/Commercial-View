#!/usr/bin/env python3
"""
Enhanced Figma token management for Commercial-View commercial lending platform
"""

import requests
import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

def test_figma_token(token: str) -> Tuple[bool, Dict]:
    """Enhanced Figma token testing with detailed validation"""
    if not token or not token.startswith('figd_'):
        print("❌ Invalid token format. Must start with 'figd_'")
        return False, {}
    
    headers = {"X-Figma-Token": token}
    
    try:
        # Test basic authentication
        response = requests.get("https://api.figma.com/v1/me", headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Token valid for user: {user_info.get('email', 'Unknown')}")
            print(f"   User ID: {user_info.get('id', 'Unknown')}")
            print(f"   Handle: {user_info.get('handle', 'Unknown')}")
            
            # Test file access permissions for Commercial-View
            return test_commercial_view_access(token, headers, user_info)
        elif response.status_code == 403:
            print("❌ 403 Forbidden - Token is invalid, expired, or lacks permissions")
            print("🔧 Action required:")
            print("   1. Go to https://www.figma.com/settings/account")
            print("   2. Delete the old token")
            print("   3. Create a new Personal Access Token")
            print("   4. Ensure token has 'File content' read permission")
            print("   5. Update your configuration with the new token")
            return False, {}
        else:
            print(f"❌ Token test failed: {response.status_code} - {response.text}")
            return False, {}
            
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False, {}

def test_commercial_view_access(token: str, headers: Dict, user_info: Dict) -> Tuple[bool, Dict]:
    """Test Commercial-View specific Figma file access"""
    print("🏦 Testing Commercial-View Figma integration...")
    
    # Commercial-View dashboard file ID (example)
    dashboard_file_id = "Zli1oqL-_I1usmRAkOZtRTXdTWeHF6E-OTKKhgJwKPE"
    
    try:
        # Test file access
        file_url = f"https://api.figma.com/v1/files/{dashboard_file_id}"
        response = requests.get(file_url, headers=headers)
        
        if response.status_code == 200:
            file_info = response.json()
            print(f"✅ Commercial-View dashboard access: OK")
            print(f"   File name: {file_info.get('name', 'Unknown')}")
            print(f"   Last modified: {file_info.get('lastModified', 'Unknown')}")
            
            # Test specific components access
            return test_dashboard_components(token, headers, dashboard_file_id)
        elif response.status_code == 403:
            print("❌ Cannot access Commercial-View dashboard file")
            print("💡 Ensure the token has access to the Commercial-View Figma file")
            return False, user_info
        else:
            print(f"⚠️  Dashboard file test: {response.status_code}")
            return True, user_info  # Token works but file access limited
            
    except Exception as e:
        print(f"⚠️  Dashboard access test failed: {e}")
        return True, user_info  # Token works but file access uncertain

def test_dashboard_components(token: str, headers: Dict, file_id: str) -> Tuple[bool, Dict]:
    """Test access to specific Commercial-View dashboard components"""
    print("📊 Testing dashboard components access...")
    
    try:
        # Get file components
        components_url = f"https://api.figma.com/v1/files/{file_id}/components"
        response = requests.get(components_url, headers=headers)
        
        if response.status_code == 200:
            components = response.json()
            component_count = len(components.get('meta', {}).get('components', []))
            print(f"✅ Dashboard components: {component_count} components accessible")
            
            # Look for Commercial-View specific components
            cv_components = []
            for comp_id, comp_info in components.get('meta', {}).get('components', {}).items():
                if any(keyword in comp_info.get('name', '').lower() 
                      for keyword in ['kpi', 'dashboard', 'metric', 'commercial', 'lending']):
                    cv_components.append(comp_info.get('name', comp_id))
            
            if cv_components:
                print(f"🏦 Commercial-View components found: {len(cv_components)}")
                for comp in cv_components[:3]:  # Show first 3
                    print(f"   - {comp}")
            
            return True, {'component_count': component_count, 'cv_components': cv_components}
        else:
            print(f"⚠️  Components access: {response.status_code}")
            return True, {}
            
    except Exception as e:
        print(f"⚠️  Components test failed: {e}")
        return True, {}

def find_token_references() -> List[Path]:
    """Find all files that might contain Figma tokens"""
    search_patterns = [
        "**/*.json",
        "**/*.py",
        "**/*.md",
        "**/.env*",
        "**/config*"
    ]
    
    project_root = Path(".")
    found_files = []
    
    for pattern in search_patterns:
        found_files.extend(project_root.glob(pattern))
    
    # Filter files that likely contain tokens
    token_files = []
    for file_path in found_files:
        if file_path.is_file() and file_path.stat().st_size < 1024 * 1024:  # < 1MB
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                if 'figd_' in content or 'figma' in content.lower():
                    token_files.append(file_path)
            except:
                pass
    
    return token_files

def update_config_files(new_token: str, old_token: Optional[str] = None) -> int:
    """Enhanced configuration file updating with backup"""
    if not old_token:
        old_token = "figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK"
    
    # Standard configuration files
    standard_files = [
        "mcp-config.json",
        ".env.figma",
        "mcp-servers.md", 
        "scripts/start_figma_mcp.py"
    ]
    
    # Find additional files with token references
    additional_files = find_token_references()
    
    all_files = list(set(standard_files + [str(f) for f in additional_files]))
    
    print(f"🔍 Found {len(all_files)} files to check for token updates")
    
    updated_count = 0
    backup_dir = Path("backups/figma_tokens")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    for file_path_str in all_files:
        file_path = Path(file_path_str)
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Check for old token
                if old_token in content:
                    # Create backup
                    backup_path = backup_dir / f"{file_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                    backup_path.write_text(content)
                    
                    # Update content
                    updated_content = content.replace(old_token, new_token)
                    file_path.write_text(updated_content, encoding='utf-8')
                    
                    print(f"✅ Updated {file_path} (backup: {backup_path.name})")
                    updated_count += 1
                elif 'figd_' in content:
                    print(f"ℹ️  {file_path} contains other Figma tokens (not updated)")
                
            except Exception as e:
                print(f"❌ Failed to update {file_path}: {e}")
        else:
            print(f"⚠️  File not found: {file_path}")
    
    if updated_count > 0:
        print(f"🎉 Successfully updated {updated_count} configuration files")
        print(f"💾 Backups saved to: {backup_dir}")
    else:
        print("⚠️  No files were updated")
    
    return updated_count

def create_figma_config() -> None:
    """Create comprehensive Figma configuration for Commercial-View"""
    config = {
        "figma": {
            "api_base_url": "https://api.figma.com/v1",
            "commercial_view": {
                "dashboard_file_id": "Zli1oqL-_I1usmRAkOZtRTXdTWeHF6E-OTKKhgJwKPE",
                "components": {
                    "kpi_tiles": True,
                    "charts": True,
                    "tables": True,
                    "navigation": True
                }
            },
            "rate_limits": {
                "requests_per_minute": 60,
                "burst_limit": 10
            },
            "cache": {
                "enabled": True,
                "ttl_seconds": 300
            }
        }
    }
    
    config_file = Path("configs/figma_config.json")
    config_file.parent.mkdir(exist_ok=True)
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"📄 Created Figma configuration: {config_file}")

def validate_environment() -> bool:
    """Validate Commercial-View environment for Figma integration"""
    print("🔍 Validating Commercial-View environment...")
    
    required_dirs = ["configs", "scripts", "src"]
    missing_dirs = [d for d in required_dirs if not Path(d).exists()]
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    print("✅ Environment validation passed")
    return True

def main():
    """Enhanced main function with comprehensive Commercial-View integration"""
    print("🏦 Commercial-View Figma Token Management")
    print("=" * 50)
    
    # Validate environment
    if not validate_environment():
        return 1
    
    # Test current token
    current_token = "figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK"
    print("🔍 Testing current token...")
    
    is_valid, token_info = test_figma_token(current_token)
    
    if is_valid:
        print("✅ Current token is working correctly!")
        print("💡 No action needed - token is valid for Commercial-View")
        
        # Create/update configuration
        create_figma_config()
        
        print("\n🚀 Integration ready! Available endpoints:")
        print("   - Dashboard components sync")
        print("   - KPI visualization updates")
        print("   - Commercial lending metrics display")
        return 0
    
    print("\n💡 To fix this issue:")
    print("1. Get a new token from: https://www.figma.com/settings/account")
    print("2. Ensure token has 'File content' read permission")
    print("3. Run: python scripts/fix_figma_token.py NEW_TOKEN")
    print("4. Replace NEW_TOKEN with your actual new token")
    
    if len(sys.argv) > 1:
        new_token = sys.argv[1].strip()
        print(f"\n🔄 Testing new token: {new_token[:10]}...")
        
        is_valid, token_info = test_figma_token(new_token)
        
        if is_valid:
            print("✅ New token is valid!")
            updated_count = update_config_files(new_token, current_token)
            
            if updated_count > 0:
                create_figma_config()
                print("🎉 Configuration updated successfully!")
                print("\n🚀 Next steps:")
                print("1. Restart any running MCP servers")
                print("2. Test the integration: python scripts/start_figma_mcp.py test")
                print("3. Verify Commercial-View dashboard sync")
                return 0
            else:
                print("⚠️  Token is valid but no files were updated")
                return 1
        else:
            print("❌ New token is also invalid")
            print("💡 Please check the token format and permissions")
            print("💡 Ensure token has access to Commercial-View Figma files")
            return 1
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
