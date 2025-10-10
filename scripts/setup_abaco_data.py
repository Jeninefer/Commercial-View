"""
Setup script to locate and copy Abaco CSV files to the data directory
"""

import os
import shutil
from pathlib import Path
import logging

def find_abaco_files():
    """Find Abaco CSV files in common locations."""
    
    # Common locations where files might be
    search_locations = [
        Path.home() / "Downloads",
        Path.home() / "Desktop", 
        Path.home() / "Documents",
        Path("/mnt/data"),  # Based on schema file
        Path.cwd(),  # Current directory
        Path.cwd() / "data"  # Project data directory
    ]
    
    # Files we're looking for
    abaco_files = {
        "Abaco - Loan Tape_Loan Data_Table.csv": "loan_data",
        "Abaco - Loan Tape_Historic Real Payment_Table.csv": "payment_history", 
        "Abaco - Loan Tape_Payment Schedule_Table.csv": "payment_schedule"
    }
    
    found_files = {}
    
    print("🔍 Searching for Abaco CSV files...")
    
    for location in search_locations:
        if not location.exists():
            continue
            
        print(f"   📂 Checking: {location}")
        
        for filename, file_type in abaco_files.items():
            if file_type in found_files:
                continue  # Already found this file
                
            file_path = location / filename
            if file_path.exists():
                found_files[file_type] = str(file_path)
                print(f"   ✅ Found {file_type}: {file_path}")
    
    return found_files, abaco_files

def setup_abaco_data():
    """Setup Abaco data files in the project data directory."""
    
    print("📊 Abaco Data Setup")
    print("=" * 50)
    
    # Ensure data directory exists
    data_dir = Path.cwd() / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Find files
    found_files, target_files = find_abaco_files()
    
    if not found_files:
        print("❌ No Abaco CSV files found!")
        print("\n💡 Please ensure the following files are available:")
        for filename in target_files.keys():
            print(f"   • {filename}")
        print("\n📥 Try placing them in one of these locations:")
        print("   • ~/Downloads/")
        print("   • ~/Desktop/") 
        print("   • Current directory")
        return False
    
    # Copy files to data directory
    copied_files = []
    
    for file_type, source_path in found_files.items():
        # Get target filename
        target_filename = None
        for filename, ftype in target_files.items():
            if ftype == file_type:
                target_filename = filename
                break
        
        if target_filename:
            target_path = data_dir / target_filename
            
            try:
                shutil.copy2(source_path, target_path)
                copied_files.append(target_filename)
                
                # Check file size
                file_size = target_path.stat().st_size / (1024 * 1024)  # MB
                print(f"✅ Copied {file_type}: {file_size:.1f} MB")
                
            except Exception as e:
                print(f"❌ Error copying {file_type}: {e}")
    
    # Summary
    print(f"\n📋 Setup Summary:")
    print(f"   • Files copied: {len(copied_files)}")
    print(f"   • Target directory: {data_dir}")
    
    if len(copied_files) == 3:
        print("🎉 All Abaco files ready!")
        
        # Verify file contents
        print("\n🔍 Verifying file contents...")
        
        for filename in copied_files:
            file_path = data_dir / filename
            try:
                import pandas as pd
                df = pd.read_csv(file_path, nrows=5)  # Just read first 5 rows
                print(f"   ✅ {filename}: {df.shape[1]} columns detected")
            except Exception as e:
                print(f"   ⚠️  {filename}: Could not read - {e}")
        
        return True
    else:
        print("⚠️  Some files may be missing. Check locations above.")
        return False

if __name__ == '__main__':
    success = setup_abaco_data()
    
    if success:
        print("\n🚀 Ready to run Abaco integration!")
        print("   Next: python portfolio.py --abaco-only")
    else:
        print("\n🔧 Please locate the Abaco CSV files and try again")
