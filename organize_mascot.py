#!/usr/bin/env python3
"""
Mascot Asset Organization Script
Organizes WhatsApp-named mascot files into proper asset directory structure
Run this after cloning to organize mascot assets.
"""

import os
import shutil
from pathlib import Path

def organize_mascot_assets():
    """Move mascot assets from root to proper asset directory."""
    
    repo_root = Path(__file__).parent
    pakka_hisaab = repo_root / "Pakka-Hisaab"
    
    # Asset directories
    asset_dir = pakka_hisaab / "assets" / "mascot"
    asset_dir.mkdir(parents=True, exist_ok=True)
    
    # Expected source files (WhatsApp filenames)
    mascot_image_src = pakka_hisaab / "WhatsApp Image 2026-08-14 at 7.29.26 PM.jpeg"
    mascot_video_src = pakka_hisaab / "WhatsApp Video 2026-08-14 at 7.29.28 PM.mp4"
    
    # Target filenames (clean names)
    mascot_image_dst = asset_dir / "mascot.png"
    mascot_video_dst = asset_dir / "mascot.mp4"
    
    # Copy image
    if mascot_image_src.exists() and not mascot_image_dst.exists():
        print(f"Copying mascot image: {mascot_image_src.name} → {mascot_image_dst.name}")
        shutil.copy2(mascot_image_src, mascot_image_dst)
        print(f"✓ Image copied to {mascot_image_dst}")
    elif mascot_image_dst.exists():
        print(f"✓ Mascot image already exists at {mascot_image_dst}")
    else:
        print(f"⚠ Mascot image not found at {mascot_image_src}")
    
    # Copy video
    if mascot_video_src.exists() and not mascot_video_dst.exists():
        print(f"Copying mascot video: {mascot_video_src.name} → {mascot_video_dst.name}")
        shutil.copy2(mascot_video_src, mascot_video_dst)
        print(f"✓ Video copied to {mascot_video_dst}")
    elif mascot_video_dst.exists():
        print(f"✓ Mascot video already exists at {mascot_video_dst}")
    else:
        print(f"⚠ Mascot video not found at {mascot_video_src}")
    
    print("\n✓ Mascot assets organized successfully!")
    print(f"Assets location: {asset_dir}")

if __name__ == "__main__":
    organize_mascot_assets()
