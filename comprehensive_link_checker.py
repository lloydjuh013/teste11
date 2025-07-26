#!/usr/bin/env python3
"""
Comprehensive Link Checker for mybird.app
Tests both live website and local HTML file
"""

import urllib.request
import urllib.error
import re
import json
import time
from datetime import datetime
from html.parser import HTMLParser
import os

class ComprehensiveLinkChecker:
    def __init__(self):
        self.results = {
            "test_start_time": datetime.now().isoformat(),
            "live_website": {},
            "local_file": {},
            "comparison": {},
            "link_checks": [],
            "summary": {}
        }
        
    def test_url(self, url, timeout=10):
        """Test a single URL and return status"""
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Link Checker Bot)'}
            )
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return {
                    "status": "success",
                    "status_code": response.getcode(),
                    "content_type": response.headers.get('content-type', ''),
                    "accessible": True
                }
                
        except urllib.error.HTTPError as e:
            return {
                "status": "http_error",
                "status_code": e.code,
                "error": str(e.reason),
                "accessible": False
            }
            
        except urllib.error.URLError as e:
            return {
                "status": "url_error",
                "error": str(e.reason),
                "accessible": False
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "accessible": False
            }
            
    def extract_links_from_html(self, html_content):
        """Extract all types of links from HTML content"""
        links = {
            "external_links": [],
            "internal_links": [],
            "onclick_handlers": [],
            "form_actions": [],
            "image_sources": [],
            "script_sources": [],
            "css_links": []
        }
        
        # External HTTP/HTTPS links
        external_pattern = r'href=["\']https?://([^"\']+)["\']'
        for match in re.finditer(external_pattern, html_content):
            full_url = match.group(0)[6:-1]  # Remove href=" and "
            links["external_links"].append(full_url)
            
        # Internal links
        internal_pattern = r'href=["\'](?!https?://)([^"\']+)["\']'
        for match in re.finditer(internal_pattern, html_content):
            link = match.group(1)
            if link and not link.startswith('mailto:') and not link.startswith('tel:'):
                links["internal_links"].append(link)
                
        # Onclick handlers
        onclick_pattern = r'onclick=["\']([^"\']+)["\']'
        for match in re.finditer(onclick_pattern, html_content):
            links["onclick_handlers"].append(match.group(1))
            
        # Form actions
        form_pattern = r'<form[^>]*action=["\']([^"\']+)["\']'
        for match in re.finditer(form_pattern, html_content):
            links["form_actions"].append(match.group(1))
            
        # Image sources
        img_pattern = r'src=["\']([^"\']+\.(jpg|jpeg|png|gif|svg|webp))["\']'
        for match in re.finditer(img_pattern, html_content, re.IGNORECASE):
            links["image_sources"].append(match.group(1))
            
        # Script sources
        script_pattern = r'<script[^>]*src=["\']([^"\']+)["\']'
        for match in re.finditer(script_pattern, html_content):
            links["script_sources"].append(match.group(1))
            
        # CSS links
        css_pattern = r'<link[^>]*href=["\']([^"\']+\.css)["\']'
        for match in re.finditer(css_pattern, html_content):
            links["css_links"].append(match.group(1))
            
        return links
        
    def test_live_website(self):
        """Test the live mybird.app website"""
        print("🌐 Testing live website: https://mybird.app")
        
        url = "https://mybird.app"
        result = self.test_url(url)
        
        if result["accessible"]:
            print(f"✅ Live website accessible (Status: {result['status_code']})")
            
            # Get content for link analysis
            try:
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'Mozilla/5.0 (Link Checker Bot)'}
                )
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    content = response.read().decode('utf-8', errors='ignore')
                    
                # Extract links
                links = self.extract_links_from_html(content)
                
                self.results["live_website"] = {
                    "accessible": True,
                    "status_code": result["status_code"],
                    "content_size": len(content),
                    "links": links,
                    "total_links": sum(len(v) for v in links.values())
                }
                
                print(f"   Content size: {len(content)} bytes")
                print(f"   Total links found: {self.results['live_website']['total_links']}")
                
                return content
                
            except Exception as e:
                print(f"❌ Failed to get content: {e}")
                self.results["live_website"]["error"] = str(e)
                return None
                
        else:
            print(f"❌ Live website not accessible: {result.get('error', 'Unknown error')}")
            self.results["live_website"] = {
                "accessible": False,
                "error": result.get("error", "Unknown error"),
                "status_code": result.get("status_code")
            }
            return None
            
    def test_local_file(self):
        """Test the local HTML file"""
        print("\n📁 Testing local HTML file: index.html")
        
        if not os.path.exists("index.html"):
            print("❌ Local index.html file not found")
            self.results["local_file"] = {"accessible": False, "error": "File not found"}
            return None
            
        try:
            with open("index.html", "r", encoding="utf-8") as f:
                content = f.read()
                
            print(f"✅ Local file accessible")
            print(f"   File size: {len(content)} bytes")
            
            # Extract links
            links = self.extract_links_from_html(content)
            
            self.results["local_file"] = {
                "accessible": True,
                "file_size": len(content),
                "links": links,
                "total_links": sum(len(v) for v in links.values())
            }
            
            print(f"   Total links found: {self.results['local_file']['total_links']}")
            
            return content
            
        except Exception as e:
            print(f"❌ Failed to read local file: {e}")
            self.results["local_file"] = {"accessible": False, "error": str(e)}
            return None
            
    def test_external_links(self, links_dict, source_name):
        """Test external links for accessibility"""
        print(f"\n🔗 Testing external links from {source_name}...")
        
        external_links = links_dict.get("external_links", [])
        if not external_links:
            print("   No external links found")
            return
            
        link_results = []
        
        for i, link in enumerate(external_links[:10]):  # Test first 10 to avoid being rate limited
            print(f"   Testing link {i+1}/{min(len(external_links), 10)}: {link[:50]}...")
            
            result = self.test_url(link, timeout=5)
            link_results.append({
                "url": link,
                "result": result
            })
            
            if result["accessible"]:
                print(f"     ✅ Working (Status: {result['status_code']})")
            else:
                print(f"     ❌ Broken: {result.get('error', 'Unknown error')}")
                
            time.sleep(0.5)  # Be nice to servers
            
        self.results["link_checks"].append({
            "source": source_name,
            "external_links_tested": len(link_results),
            "external_links_total": len(external_links),
            "results": link_results
        })
        
    def analyze_javascript_functionality(self, html_content, source_name):
        """Analyze JavaScript functionality"""
        print(f"\n⚡ Analyzing JavaScript functionality in {source_name}...")
        
        # Extract onclick handlers
        onclick_pattern = r'onclick=["\']([^"\']+)["\']'
        onclick_handlers = re.findall(onclick_pattern, html_content)
        
        # Extract function names
        function_names = set()
        for handler in onclick_handlers:
            match = re.match(r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(', handler)
            if match:
                function_names.add(match.group(1))
                
        # Look for function definitions
        function_def_pattern = r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\('
        defined_functions = set(re.findall(function_def_pattern, html_content))
        
        print(f"   Onclick handlers: {len(onclick_handlers)}")
        print(f"   Unique functions called: {len(function_names)}")
        print(f"   Function definitions found: {len(defined_functions)}")
        
        # Check for missing function definitions
        missing_functions = function_names - defined_functions
        if missing_functions:
            print(f"   ⚠️  Functions called but not defined: {len(missing_functions)}")
            for func in list(missing_functions)[:5]:  # Show first 5
                print(f"      - {func}")
        else:
            print(f"   ✅ All called functions are defined")
            
        return {
            "onclick_handlers": len(onclick_handlers),
            "function_names": list(function_names),
            "defined_functions": list(defined_functions),
            "missing_functions": list(missing_functions)
        }
        
    def compare_versions(self):
        """Compare live website vs local file"""
        print("\n🔄 Comparing live website vs local file...")
        
        if not self.results["live_website"].get("accessible") or not self.results["local_file"].get("accessible"):
            print("   Cannot compare - one or both sources not accessible")
            return
            
        live_total = self.results["live_website"]["total_links"]
        local_total = self.results["local_file"]["total_links"]
        
        print(f"   Live website links: {live_total}")
        print(f"   Local file links: {local_total}")
        
        if live_total == local_total:
            print("   ✅ Same number of links")
        elif live_total > local_total:
            print(f"   ⚠️  Live website has {live_total - local_total} more links")
        else:
            print(f"   ⚠️  Local file has {local_total - live_total} more links")
            
        self.results["comparison"] = {
            "live_links": live_total,
            "local_links": local_total,
            "difference": live_total - local_total
        }
        
    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        print("\n📊 Generating summary report...")
        
        # Calculate statistics
        total_external_tested = sum(
            check.get("external_links_tested", 0) 
            for check in self.results["link_checks"]
        )
        
        working_links = sum(
            sum(1 for link in check.get("results", []) if link["result"]["accessible"])
            for check in self.results["link_checks"]
        )
        
        self.results["summary"] = {
            "live_website_accessible": self.results["live_website"].get("accessible", False),
            "local_file_accessible": self.results["local_file"].get("accessible", False),
            "total_external_links_tested": total_external_tested,
            "working_external_links": working_links,
            "broken_external_links": total_external_tested - working_links,
            "success_rate": (working_links / total_external_tested * 100) if total_external_tested > 0 else 0
        }
        
        # Save detailed report
        self.results["test_end_time"] = datetime.now().isoformat()
        
        with open("mybird_app_comprehensive_report.json", "w") as f:
            json.dump(self.results, f, indent=2)
            
        # Create readable report
        readable_report = self.create_readable_summary()
        with open("mybird_app_comprehensive_report.txt", "w") as f:
            f.write(readable_report)
            
        print("   Reports saved:")
        print("     - mybird_app_comprehensive_report.json")
        print("     - mybird_app_comprehensive_report.txt")
        
    def create_readable_summary(self):
        """Create a human-readable summary"""
        lines = []
        lines.append("="*70)
        lines.append("MYBIRD.APP COMPREHENSIVE LINK TEST REPORT")
        lines.append("="*70)
        lines.append(f"Test Date: {self.results['test_start_time']}")
        lines.append("")
        
        # Live Website Section
        lines.append("LIVE WEBSITE (https://mybird.app)")
        lines.append("-" * 40)
        if self.results["live_website"].get("accessible"):
            lines.append("✅ Status: ACCESSIBLE")
            lines.append(f"   Status Code: {self.results['live_website']['status_code']}")
            lines.append(f"   Content Size: {self.results['live_website']['content_size']:,} bytes")
            lines.append(f"   Total Links: {self.results['live_website']['total_links']}")
        else:
            lines.append("❌ Status: NOT ACCESSIBLE")
            lines.append(f"   Error: {self.results['live_website'].get('error', 'Unknown')}")
        lines.append("")
        
        # Local File Section
        lines.append("LOCAL FILE (index.html)")
        lines.append("-" * 40)
        if self.results["local_file"].get("accessible"):
            lines.append("✅ Status: ACCESSIBLE")
            lines.append(f"   File Size: {self.results['local_file']['file_size']:,} bytes")
            lines.append(f"   Total Links: {self.results['local_file']['total_links']}")
        else:
            lines.append("❌ Status: NOT ACCESSIBLE")
            lines.append(f"   Error: {self.results['local_file'].get('error', 'Unknown')}")
        lines.append("")
        
        # External Link Testing
        lines.append("EXTERNAL LINK TESTING")
        lines.append("-" * 40)
        summary = self.results["summary"]
        lines.append(f"Total external links tested: {summary['total_external_links_tested']}")
        lines.append(f"Working links: {summary['working_external_links']}")
        lines.append(f"Broken links: {summary['broken_external_links']}")
        lines.append(f"Success rate: {summary['success_rate']:.1f}%")
        lines.append("")
        
        # Broken Links Details
        if summary["broken_external_links"] > 0:
            lines.append("BROKEN LINKS DETAILS")
            lines.append("-" * 40)
            for check in self.results["link_checks"]:
                broken_links = [
                    link for link in check.get("results", [])
                    if not link["result"]["accessible"]
                ]
                if broken_links:
                    lines.append(f"From {check['source']}:")
                    for link in broken_links[:3]:  # Show first 3
                        lines.append(f"  ❌ {link['url']}")
                        lines.append(f"     Error: {link['result'].get('error', 'Unknown')}")
            lines.append("")
        
        # Overall Assessment
        lines.append("OVERALL ASSESSMENT")
        lines.append("-" * 40)
        if summary["live_website_accessible"]:
            lines.append("✅ Live website is functional")
        else:
            lines.append("❌ Live website has issues")
            
        if summary["local_file_accessible"]:
            lines.append("✅ Local file is accessible")
        else:
            lines.append("❌ Local file has issues")
            
        if summary["success_rate"] >= 90:
            lines.append("✅ Excellent link quality (90%+ working)")
        elif summary["success_rate"] >= 75:
            lines.append("⚠️  Good link quality (75-90% working)")
        elif summary["success_rate"] >= 50:
            lines.append("⚠️  Poor link quality (50-75% working)")
        else:
            lines.append("❌ Very poor link quality (<50% working)")
            
        lines.append("")
        lines.append(f"Test completed: {self.results.get('test_end_time', '')}")
        
        return "\n".join(lines)
        
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 Starting comprehensive link testing for mybird.app")
        print("="*60)
        
        # Test live website
        live_content = self.test_live_website()
        
        # Test local file
        local_content = self.test_local_file()
        
        # Test external links from live website
        if live_content and self.results["live_website"].get("accessible"):
            self.test_external_links(
                self.results["live_website"]["links"], 
                "live website"
            )
            self.analyze_javascript_functionality(live_content, "live website")
            
        # Test external links from local file
        if local_content and self.results["local_file"].get("accessible"):
            self.test_external_links(
                self.results["local_file"]["links"], 
                "local file"
            )
            self.analyze_javascript_functionality(local_content, "local file")
            
        # Compare versions
        self.compare_versions()
        
        # Generate final report
        self.generate_summary_report()
        
        print("\n✅ Comprehensive testing completed!")
        self.print_final_summary()
        
    def print_final_summary(self):
        """Print final summary"""
        summary = self.results["summary"]
        
        print("\n" + "="*60)
        print("FINAL SUMMARY")
        print("="*60)
        
        if summary["live_website_accessible"]:
            print("✅ Live Website: ACCESSIBLE")
        else:
            print("❌ Live Website: NOT ACCESSIBLE")
            
        if summary["local_file_accessible"]:
            print("✅ Local File: ACCESSIBLE")
        else:
            print("❌ Local File: NOT ACCESSIBLE")
            
        if summary["total_external_links_tested"] > 0:
            print(f"🔗 External Links: {summary['working_external_links']}/{summary['total_external_links_tested']} working ({summary['success_rate']:.1f}%)")
        else:
            print("🔗 External Links: None tested")
            
        print(f"\n📋 Full report: mybird_app_comprehensive_report.txt")

if __name__ == "__main__":
    checker = ComprehensiveLinkChecker()
    checker.run_comprehensive_test()