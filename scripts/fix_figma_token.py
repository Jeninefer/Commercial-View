#!/usr/bin/env python3
"""
Fix Figma token 403 Forbidden error
"""

import requests
import sys
from pathlib import Path

def test_figma_token(token):
    """Test if Figma token is working"""
    if not token or not token.startswith('figd_'):
        print("❌ Invalid token format. Must start with 'figd_'")
        return False
    
    headers = {"X-Figma-Token": token}
    
    try:
        response = requests.get("https://api.figma.com/v1/me", headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Token valid for user: {user_info.get('email', 'Unknown')}")
            return True
        elif response.status_code == 403:
            print("❌ 403 Forbidden - Token is invalid, expired, or lacks permissions")
            print("🔧 Action required:")
            print("   1. Go to https://www.figma.com/settings/account")
            print("   2. Delete the old token")
            print("   3. Create a new Personal Access Token")
            print("   4. Update your configuration with the new token")
            return False
        else:
            print(f"❌ Token test failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False

def update_config_files(new_token):
    """Update configuration files with new token"""
    files_to_update = [
        "mcp-config.json",
        ".env.figma",
        "mcp-servers.md",
        "scripts/start_figma_mcp.py"
    ]
    
    old_token = "figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK"
    
    updated_count = 0
    for file_path in files_to_update:
        path = Path(file_path)
        if path.exists():
            try:
                content = path.read_text(encoding='utf-8')
                if old_token in content:
                    updated_content = content.replace(old_token, new_token)
                    path.write_text(updated_content, encoding='utf-8')
                    print(f"✅ Updated {file_path}")
                    updated_count += 1
                else:
                    print(f"ℹ️  No token found in {file_path}")
            except Exception as e:
                print(f"❌ Failed to update {file_path}: {e}")
        else:
            print(f"⚠️  File not found: {file_path}")
    
    if updated_count > 0:
        print(f"🎉 Successfully updated {updated_count} configuration files")
    else:
        print("⚠️  No files were updated")

def main():
    """Main function"""
    print("🔧 Figma Token Fix Utility")
    print("=" * 30)
    
    # Test current token
    current_token = "figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK"
    print("Testing current token...")
    
    # Current token is working based on previous test
    if test_figma_token(current_token):
        print("✅ Current token is working correctly!")
        print("💡 No action needed - token is valid")
        return 0
    
    print("\n💡 To fix this issue:")
    print("1. Get a new token from: https://www.figma.com/settings/account")
    print("2. Run: python scripts/fix_figma_token.py NEW_TOKEN")
    print("3. Replace NEW_TOKEN with your actual new token")
    
    if len(sys.argv) > 1:
        new_token = sys.argv[1].strip()
        print(f"\n🔄 Testing new token: {new_token[:10]}...")
        
        if test_figma_token(new_token):
            print("✅ New token is valid!")
            update_config_files(new_token)
            print("🎉 Configuration updated successfully!")
            print("\n🚀 Next steps:")
            print("1. Restart any running MCP servers")
            print("2. Test the Figma integration: python scripts/start_figma_mcp.py test")
            return 0
        else:
            print("❌ New token is also invalid")
            print("💡 Please check the token format and permissions")
            return 1
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
