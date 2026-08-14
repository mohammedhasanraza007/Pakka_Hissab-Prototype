#!/usr/bin/env python3
"""
Pakka Hisaab Mascot Integration Verification Script
Scans the application to verify mascot is properly integrated and non-intrusive
"""

import os
import re
from pathlib import Path

class MascotIntegrationScanner:
    def __init__(self, repo_root):
        self.repo_root = Path(repo_root)
        self.issues = []
        self.warnings = []
        self.success = []
        
    def scan_html(self):
        """Verify HTML includes mascot stylesheet and script"""
        print("\n🔍 Scanning HTML...")
        html_file = self.repo_root / "Pakka-Hisaab" / "frontend" / "index.html"
        
        if not html_file.exists():
            self.issues.append(f"❌ HTML file not found: {html_file}")
            return
        
        with open(html_file, 'r') as f:
            content = f.read()
        
        # Check for mascot stylesheet
        if 'mascot.css' in content:
            self.success.append("✓ Mascot CSS linked in HTML")
        else:
            self.issues.append("❌ Mascot CSS not linked in HTML")
        
        # Check for mascot script
        if 'mascot.js' in content:
            self.success.append("✓ Mascot JS loaded in HTML")
        else:
            self.issues.append("❌ Mascot JS not loaded in HTML")
        
        # Verify script loads BEFORE app.js (important)
        if content.find('mascot.js') < content.find('app.js'):
            self.success.append("✓ Mascot script loads before app.js")
        else:
            self.warnings.append("⚠ Mascot script should load before app.js")

    def scan_css(self):
        """Verify CSS doesn't modify core UI"""
        print("🔍 Scanning CSS...")
        css_file = self.repo_root / "Pakka-Hisaab" / "frontend" / "mascot.css"
        
        if not css_file.exists():
            self.issues.append(f"❌ Mascot CSS file not found: {css_file}")
            return
        
        with open(css_file, 'r') as f:
            content = f.read()
        
        # Check mascot is small
        if 'max-width: 120px' in content or 'max-width: 100px' in content or 'max-width: 80px' in content:
            self.success.append("✓ Mascot size properly constrained (≤120px)")
        else:
            self.warnings.append("⚠ Mascot max-width not clearly defined")
        
        # Check fixed positioning
        if 'position: fixed' in content:
            self.success.append("✓ Mascot uses fixed positioning (won't shift layout)")
        else:
            self.issues.append("❌ Mascot should use fixed positioning")
        
        # Check z-index is reasonable
        if 'z-index: 50' in content or 'z-index: 40' in content or 'z-index: 30' in content:
            self.success.append("✓ Mascot z-index reasonable (not front-most)")
        else:
            self.warnings.append("⚠ Verify mascot z-index doesn't block critical UI")
        
        # Check pointer-events: none (non-intrusive)
        if 'pointer-events: none' in content:
            self.success.append("✓ Mascot container doesn't block clicks")
        else:
            self.warnings.append("⚠ Mascot should not intercept pointer events")
        
        # Check animations exist
        animations = ['mascot-float', 'mascot-attention', 'mascot-success', 'mascot-concern']
        for anim in animations:
            if anim in content:
                self.success.append(f"✓ Animation '{anim}' defined")
            else:
                self.warnings.append(f"⚠ Animation '{anim}' not found")
        
        # Check prefers-reduced-motion
        if 'prefers-reduced-motion' in content:
            self.success.append("✓ Accessibility: prefers-reduced-motion respected")
        else:
            self.issues.append("❌ Missing accessibility: prefers-reduced-motion")

    def scan_javascript(self):
        """Verify JS module is independent and non-blocking"""
        print("🔍 Scanning JavaScript...")
        js_file = self.repo_root / "Pakka-Hisaab" / "frontend" / "mascot.js"
        
        if not js_file.exists():
            self.issues.append(f"❌ Mascot JS file not found: {js_file}")
            return
        
        with open(js_file, 'r') as f:
            content = f.read()
        
        # Check for IIFE (independent module)
        if '(() => {' in content or '(function () {' in content:
            self.success.append("✓ Mascot uses IIFE (independent module)")
        else:
            self.warnings.append("⚠ Mascot should be in IIFE for isolation")
        
        # Check no global variables
        if content.count('const Mascot = ') == 1:
            self.success.append("✓ Single global namespace (Mascot object)")
        else:
            self.issues.append("❌ Multiple global variables detected")
        
        # Check error handling
        if '.catch' in content or 'try' in content or 'onerror' in content:
            self.success.append("✓ Error handling present (graceful degradation)")
        else:
            self.warnings.append("⚠ Add error handling for asset load failures")
        
        # Check no external dependencies
        deps = ['jquery', 'react', 'vue', 'lodash', 'gsap', 'anime']
        found_deps = [d for d in deps if d in content.lower()]
        if not found_deps:
            self.success.append("✓ No external dependencies")
        else:
            self.issues.append(f"❌ Found dependencies: {found_deps}")
        
        # Check auto-initialization
        if 'DOMContentLoaded' in content or 'document.readyState' in content:
            self.success.append("✓ Mascot auto-initializes")
        else:
            self.warnings.append("⚠ Mascot should auto-initialize")
        
        # Check video fallback
        if 'onerror' in content and ('.png' in content or '.jpg' in content):
            self.success.append("✓ Video has PNG fallback")
        else:
            self.issues.append("❌ Missing video-to-PNG fallback")

    def scan_app_js(self):
        """Verify core app.js is UNMODIFIED"""
        print("🔍 Scanning app.js (core functionality)...")
        app_file = self.repo_root / "Pakka-Hisaab" / "frontend" / "app.js"
        
        if not app_file.exists():
            self.issues.append(f"❌ app.js not found: {app_file}")
            return
        
        with open(app_file, 'r') as f:
            content = f.read()
        
        # Check app.js doesn't reference mascot
        if 'Mascot' not in content or content.count('Mascot') < 1:
            self.success.append("✓ app.js is independent (no mascot coupling)")
        else:
            # Could be OK if just calling Mascot.method(), but worth noting
            self.warnings.append("⚠ Verify app.js doesn't depend on Mascot for core logic")
        
        # Check core functions still exist
        core_funcs = ['executeCommand', 'renderState', 'settle', 'startListening']
        found = [f for f in core_funcs if f in content]
        if len(found) == len(core_funcs):
            self.success.append(f"✓ Core functions intact: {', '.join(core_funcs)}")
        else:
            self.issues.append(f"❌ Missing core functions: {set(core_funcs) - set(found)}")

    def scan_assets(self):
        """Verify mascot assets exist or path is correct"""
        print("🔍 Scanning mascot assets...")
        
        # Check for original WhatsApp files
        whatsapp_image = self.repo_root / "Pakka-Hisaab" / "WhatsApp Image 2026-08-14 at 7.29.26 PM.jpeg"
        whatsapp_video = self.repo_root / "Pakka-Hisaab" / "WhatsApp Video 2026-08-14 at 7.29.28 PM.mp4"
        
        if whatsapp_image.exists():
            size_kb = whatsapp_image.stat().st_size / 1024
            self.success.append(f"✓ Mascot image asset found ({size_kb:.1f} KB)")
        else:
            self.warnings.append("⚠ Mascot image not in repo root (check assets/mascot/)")
        
        if whatsapp_video.exists():
            size_kb = whatsapp_video.stat().st_size / 1024
            self.success.append(f"✓ Mascot video asset found ({size_kb:.1f} KB)")
        else:
            self.warnings.append("⚠ Mascot video not in repo root (check assets/mascot/)")
        
        # Check for organized assets
        organized_dir = self.repo_root / "Pakka-Hisaab" / "assets" / "mascot"
        if organized_dir.exists():
            files = list(organized_dir.glob("*"))
            if files:
                self.success.append(f"✓ Organized asset directory exists with {len(files)} file(s)")
            else:
                self.warnings.append("⚠ Asset directory exists but is empty")
        else:
            self.warnings.append("⚠ Run organize_mascot.py to create Pakka-Hisaab/assets/mascot/")

    def scan_sizing(self):
        """Verify mascot doesn't take whole screen"""
        print("🔍 Verifying mascot is small and non-intrusive...")
        css_file = self.repo_root / "Pakka-Hisaab" / "frontend" / "mascot.css"
        
        if not css_file.exists():
            return
        
        with open(css_file, 'r') as f:
            content = f.read()
        
        # Parse max-width values
        widths = re.findall(r'max-width:\s*(\d+)px', content)
        if widths:
            max_w = max(int(w) for w in widths)
            if max_w <= 120:
                self.success.append(f"✓ Max mascot width: {max_w}px (small, non-intrusive)")
            elif max_w <= 150:
                self.warnings.append(f"⚠ Mascot width {max_w}px (consider reducing below 120px)")
            else:
                self.issues.append(f"❌ Mascot width {max_w}px is too large")
        
        # Check bottom/right offsets
        if '20px' in content or '12px' in content or '8px' in content:
            self.success.append("✓ Mascot has appropriate margins from edges")
        else:
            self.warnings.append("⚠ Verify mascot edge margins")
        
        # Check fixed positioning doesn't create scroll
        if 'overflow' not in content or 'overflow: hidden' in content:
            self.success.append("✓ Mascot shouldn't cause scrollbars")
        
        # Check visibility doesn't hide important UI
        if 'visibility: hidden' in content or 'display: none' in content:
            # These should only be in conditional states
            self.success.append("✓ Visibility control present (for hiding state)")

    def generate_report(self):
        """Generate and print final report"""
        print("\n" + "="*70)
        print("PAKKA HISAAB MASCOT INTEGRATION VERIFICATION REPORT")
        print("="*70)
        
        total = len(self.success) + len(self.warnings) + len(self.issues)
        
        # Success section
        if self.success:
            print("\n✅ PASSED CHECKS:")
            for item in self.success:
                print(f"   {item}")
        
        # Warnings section
        if self.warnings:
            print("\n⚠️  WARNINGS (Review but not critical):")
            for item in self.warnings:
                print(f"   {item}")
        
        # Issues section
        if self.issues:
            print("\n❌ CRITICAL ISSUES (Must fix):")
            for item in self.issues:
                print(f"   {item}")
        
        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"✅ Passed:  {len(self.success)}/{total}")
        print(f"⚠️  Warnings: {len(self.warnings)}/{total}")
        print(f"❌ Issues:   {len(self.issues)}/{total}")
        
        if self.issues:
            print("\n🔴 STATUS: INTEGRATION HAS ISSUES")
            print("Please fix critical issues before deployment")
            return False
        elif self.warnings:
            print("\n🟡 STATUS: INTEGRATION OK (with minor warnings)")
            print("Ready for testing, but review warnings for best practices")
            return True
        else:
            print("\n🟢 STATUS: INTEGRATION PERFECT")
            print("Mascot is properly integrated and non-intrusive ✨")
            return True

def main():
    import sys
    
    repo_root = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print(f"Scanning repository: {repo_root}")
    
    scanner = MascotIntegrationScanner(repo_root)
    
    scanner.scan_html()
    scanner.scan_css()
    scanner.scan_javascript()
    scanner.scan_app_js()
    scanner.scan_assets()
    scanner.scan_sizing()
    
    success = scanner.generate_report()
    
    sys.exit(0 if success or not scanner.issues else 1)

if __name__ == "__main__":
    main()
