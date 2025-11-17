#!/usr/bin/env python3
"""
Batch download images from Dropbox shared folders using Excel file input.
"""

import argparse
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from datetime import datetime
import shutil
from tqdm import tqdm
from download_dropbox import download_first_file


class DownloadStats:
    """Track download statistics and failures"""
    def __init__(self):
        self.total = 0
        self.completed = 0
        self.skipped = 0
        self.failed = []
        
    def add_completed(self):
        self.completed += 1
        
    def add_skipped(self):
        self.skipped += 1
        
    def add_failed(self, upc, url, error):
        self.failed.append({
            'upc': upc,
            'url': url,
            'error': str(error)
        })
        
    def print_summary(self):
        print("\n" + "="*60)
        print("DOWNLOAD SUMMARY")
        print("="*60)
        print(f"Total items:     {self.total}")
        print(f"Downloaded:      {self.completed}")
        print(f"Skipped:         {self.skipped}")
        print(f"Failed:          {len(self.failed)}")
        print("="*60)
        
        if self.failed:
            print("\nFAILED DOWNLOADS:")
            for item in self.failed:
                print(f"  UPC: {item['upc']}")
                print(f"  URL: {item['url']}")
                print(f"  Error: {item['error']}")
                print()


def check_existing_file(output_dir, upc):
    """
    Check if a file with the given UPC already exists in the output directory.
    Returns the file path if found, None otherwise.
    """
    output_path = Path(output_dir)
    if not output_path.exists():
        return None
    
    # Check for files starting with the UPC
    for file in output_path.iterdir():
        if file.is_file() and file.stem == str(upc):
            return file
    
    return None


def download_and_rename(upc, image_url, output_dir, debug=False, thread_id=0, progress_bar=None):
    """
    Download the first image from a Dropbox folder and rename it with the UPC.
    
    Args:
        upc: UPC code to use as filename
        image_url: Dropbox shared folder URL
        output_dir: Directory to save the file
        debug: Enable debug output
        thread_id: Thread identifier for unique Chrome profiles
        progress_bar: Optional tqdm progress bar instance
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Check if file already exists
        existing = check_existing_file(output_dir, upc)
        if existing:
            return (True, f"Skipped (already exists: {existing.name})")
        
        # Create a unique temp directory for this download
        temp_dir = Path(output_dir) / f".tmp_{thread_id}_{upc}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Use a unique Chrome profile per thread
        user_data_dir = f"/tmp/chrome-download-{thread_id}"
        
        try:
            # Download the file
            downloaded_file = download_first_file(
                url=image_url,
                output_dir=str(temp_dir),
                debug=debug,
                use_alt_method=False,
                user_data_dir=user_data_dir,
                progress_bar=progress_bar,
                file_label=str(upc)
            )
            
            if not downloaded_file or not downloaded_file.exists():
                return (False, "Download failed - no file returned")
            
            # Get the file extension
            extension = downloaded_file.suffix
            
            # Rename and move to output directory
            final_path = Path(output_dir) / f"{upc}{extension}"
            shutil.move(str(downloaded_file), str(final_path))
            
            # Clean up temp directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            
            return (True, f"Downloaded as {final_path.name}")
            
        finally:
            # Clean up temp directory even if download failed
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
        
    except Exception as e:
        return (False, f"Error: {str(e)}")


def process_excel(excel_file, output_dir, threads=1, debug=False):
    """
    Process Excel file and download images.
    
    Args:
        excel_file: Path to Excel file with UPC and "IMAGES_LINK" columns
        output_dir: Directory to save downloaded files
        threads: Number of parallel download threads
        debug: Enable debug output
    """
    # Read Excel file
    print(f"Reading Excel file: {excel_file}")
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        print(f"✗ Error reading Excel file: {e}")
        sys.exit(1)
    
    # Validate columns
    if 'UPC' not in df.columns or 'IMAGES_LINK' not in df.columns:
        print("✗ Error: Excel file must contain 'UPC' and 'IMAGES_LINK' columns")
        print(f"  Found columns: {', '.join(df.columns)}")
        sys.exit(1)
    
    # Filter out rows with missing data
    df = df.dropna(subset=['UPC', 'IMAGES_LINK'])
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    stats = DownloadStats()
    stats.total = len(df)
    
    print(f"Found {stats.total} items to process")
    print(f"Output directory: {output_path.resolve()}")
    print(f"Threads: {threads}")
    print()
    
    # Process downloads
    if threads == 1:
        # Single-threaded processing with progress bar
        with tqdm(total=stats.total, desc="Processing", unit="file", position=0) as pbar:
            for idx, row in df.iterrows():
                upc = str(row['UPC']).strip()
                url = str(row['IMAGES_LINK']).strip()
                
                pbar.set_description(f"Processing {upc}")
                
                success, message = download_and_rename(upc, url, output_dir, debug, thread_id=0, progress_bar=pbar)
                
                if success:
                    if "Skipped" in message:
                        stats.add_skipped()
                        pbar.write(f"⊘ {upc}: {message}")
                    else:
                        stats.add_completed()
                        pbar.write(f"✓ {upc}: {message}")
                else:
                    stats.add_failed(upc, url, message)
                    pbar.write(f"✗ {upc}: {message}")
                
                pbar.update(1)
    else:
        # Multi-threaded processing with progress bars
        # Create a progress bar for each thread plus an overall progress bar
        thread_bars = {}
        
        with tqdm(total=stats.total, desc="Overall Progress", unit="file", position=0) as overall_pbar:
            # Create individual progress bars for each thread
            for i in range(threads):
                thread_bars[i] = tqdm(
                    total=0, 
                    desc=f"Thread {i+1}: Idle", 
                    unit="step",
                    position=i+1,
                    leave=False
                )
            
            with ThreadPoolExecutor(max_workers=threads) as executor:
                # Submit all tasks
                future_to_item = {}
                for idx, row in df.iterrows():
                    upc = str(row['UPC']).strip()
                    url = str(row['IMAGES_LINK']).strip()
                    
                    thread_id = idx % threads
                    pbar = thread_bars[thread_id]
                    
                    future = executor.submit(
                        download_and_rename,
                        upc, url, output_dir, debug, 
                        thread_id=thread_id,
                        progress_bar=pbar
                    )
                    future_to_item[future] = (idx, upc, url, pbar)
                
                # Process completed tasks
                for future in as_completed(future_to_item):
                    idx, upc, url, pbar = future_to_item[future]
                    
                    try:
                        success, message = future.result()
                        
                        if success:
                            if "Skipped" in message:
                                stats.add_skipped()
                                overall_pbar.write(f"⊘ {upc}: {message}")
                            else:
                                stats.add_completed()
                                overall_pbar.write(f"✓ {upc}: {message}")
                        else:
                            stats.add_failed(upc, url, message)
                            overall_pbar.write(f"✗ {upc}: {message}")
                            
                    except Exception as e:
                        stats.add_failed(upc, url, str(e))
                        overall_pbar.write(f"✗ {upc}: Exception: {str(e)}")
                    
                    overall_pbar.update(1)
            
            # Close all thread progress bars
            for pbar in thread_bars.values():
                pbar.close()
    
    # Print summary
    stats.print_summary()
    
    # Write failed items to a file if any
    if stats.failed:
        failed_file = output_path / f"failed_downloads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(failed_file, 'w') as f:
            f.write("FAILED DOWNLOADS\n")
            f.write("="*60 + "\n\n")
            for item in stats.failed:
                f.write(f"UPC: {item['upc']}\n")
                f.write(f"URL: {item['url']}\n")
                f.write(f"Error: {item['error']}\n\n")
        print(f"\nFailed downloads logged to: {failed_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Batch download images from Dropbox using Excel file input',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python main.py ./data/Book1.xlsx output
  python main.py ./data/Book1.xlsx output --threads 4
  python main.py ./data/Book1.xlsx output --threads 4 --debug

Excel file format:
  Column 1: UPC (product code)
  Column 2: IMAGES_LINK (Dropbox shared folder URL)
        """
    )
    
    parser.add_argument('excel_file', help='Path to Excel file (.xlsx)')
    parser.add_argument('output_dir', help='Output directory for downloaded files')
    parser.add_argument('--threads', type=int, default=1,
                       help='Number of parallel download threads (default: 1)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable verbose debug output')
    
    args = parser.parse_args()
    
    # Validate inputs
    excel_path = Path(args.excel_file)
    if not excel_path.exists():
        print(f"✗ Error: Excel file not found: {excel_path}")
        sys.exit(1)
    
    if not excel_path.suffix.lower() in ['.xlsx', '.xls']:
        print(f"✗ Error: File must be an Excel file (.xlsx or .xls)")
        sys.exit(1)
    
    if args.threads < 1:
        print(f"✗ Error: Threads must be at least 1")
        sys.exit(1)
    
    # Process the Excel file
    process_excel(
        excel_file=str(excel_path),
        output_dir=args.output_dir,
        threads=args.threads,
        debug=args.debug
    )


if __name__ == "__main__":
    main()
