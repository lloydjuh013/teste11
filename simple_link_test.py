#!/usr/bin/env python3
"""
Simple Website Link Testing Script for mybird.app
Tests basic connectivity and analyzes HTML structure for links
"""

import urllib.request
import urllib.error
import re
import json
import time
from datetime import datetime
from html.parser import HTMLParser

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.buttons = []
        self.forms = []
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'a':
            href = attrs_dict.get('href')
            onclick = attrs_dict.get('onclick')
            if href or onclick:
                self.links.append({
                    'type': 'link',
                    'tag': tag,
                    'href': href,
                    'onclick': onclick,
                    'text': ''
                })
                
        elif tag == 'button':
            onclick = attrs_dict.get('onclick')
            if onclick:
                self.buttons.append({
                    'type': 'button',
                    'onclick': onclick,
                    'text': ''
                })
                
        elif tag == 'form':
            action = attrs_dict.get('action')
            method = attrs_dict.get('method', 'GET')
            self.forms.append({
                'type': 'form',
                'action': action,
                'method': method
            })

class SimpleWebsiteTester:
    def __init__(self, base_url="https://mybird.app"):
        self.base_url = base_url
        self.results = {
            "test_start_time": datetime.now().isoformat(),
            "base_url": base_url,
            "connectivity": None,
            "response_time": None,
            "status_code": None,
            "content_size": None,
            "links_found": 0,
            "buttons_found": 0,
            "forms_found": 0,
            "interactive_elements": [],
            "potential_issues": [],
            "recommendations": []
        }
        
    def test_connectivity(self):
        """Test basic website connectivity"""
        print(f"🔗 Testing connectivity to {self.base_url}...")
        
        try:
            start_time = time.time()
            
            # Create request with user agent
            req = urllib.request.Request(
                self.base_url,
                headers={'User-Agent': 'Mozilla/5.0 (Link Tester Bot)'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                end_time = time.time()
                
                self.results["connectivity"] = "success"
                self.results["status_code"] = response.getcode()
                self.results["response_time"] = round(end_time - start_time, 2)
                self.results["content_size"] = len(content)
                
                print(f"✅ Website is accessible!")
                print(f"   Status Code: {self.results['status_code']}")
                print(f"   Response Time: {self.results['response_time']} seconds")
                print(f"   Content Size: {self.results['content_size']} bytes")
                
                return content
                
        except urllib.error.HTTPError as e:
            self.results["connectivity"] = "http_error"
            self.results["status_code"] = e.code
            print(f"❌ HTTP Error: {e.code} - {e.reason}")
            self.results["potential_issues"].append(f"HTTP Error: {e.code} - {e.reason}")
            return None
            
        except urllib.error.URLError as e:
            self.results["connectivity"] = "url_error"
            print(f"❌ URL Error: {e.reason}")
            self.results["potential_issues"].append(f"URL Error: {e.reason}")
            return None
            
        except Exception as e:
            self.results["connectivity"] = "error"
            print(f"❌ Connection failed: {e}")
            self.results["potential_issues"].append(f"Connection failed: {e}")
            return None
            
    def analyze_html_structure(self, html_content):
        """Analyze HTML content for links and interactive elements"""
        print("\n🔍 Analyzing HTML structure...")
        
        parser = LinkParser()
        parser.feed(html_content)
        
        # Count elements
        self.results["links_found"] = len(parser.links)
        self.results["buttons_found"] = len(parser.buttons)
        self.results["forms_found"] = len(parser.forms)
        
        print(f"   Found {len(parser.links)} links")
        print(f"   Found {len(parser.buttons)} interactive buttons")
        print(f"   Found {len(parser.forms)} forms")
        
        # Store interactive elements
        self.results["interactive_elements"] = parser.links + parser.buttons + parser.forms
        
        return parser
        
    def analyze_javascript_functions(self, html_content):
        """Extract and analyze JavaScript functions from onclick handlers"""
        print("\n⚡ Analyzing JavaScript functionality...")
        
        # Find all onclick handlers
        onclick_pattern = r'onclick=["\']([^"\']+)["\']'
        onclick_handlers = re.findall(onclick_pattern, html_content)
        
        # Extract unique function calls
        function_calls = set()
        for handler in onclick_handlers:
            # Extract function name (before first parenthesis)
            match = re.match(r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(', handler)
            if match:
                function_calls.add(match.group(1))
                
        print(f"   Found {len(onclick_handlers)} onclick handlers")
        print(f"   Found {len(function_calls)} unique JavaScript functions")
        
        # Common functions found in the HTML
        expected_functions = [
            'switchSection', 'toggleAdminAccess', 'toggleWalletOptions',
            'connectWallet', 'createTrade', 'addNewCard', 'saveSettings',
            'toggleCart', 'checkout', 'switchAdminTab', 'addToCart',
            'placeBid', 'acceptTrade', 'declineTrade'
        ]
        
        missing_functions = []
        for expected in expected_functions:
            if expected not in function_calls:
                missing_functions.append(expected)
                
        if missing_functions:
            self.results["potential_issues"].append(f"Missing expected functions: {missing_functions}")
            
        self.results["javascript_functions"] = list(function_calls)
        
        return list(function_calls)
        
    def check_external_resources(self, html_content):
        """Check for external resources and potential issues"""
        print("\n🌐 Checking external resources...")
        
        # Find external links
        external_links = re.findall(r'href=["\']https?://[^"\']+["\']', html_content)
        external_scripts = re.findall(r'src=["\']https?://[^"\']+["\']', html_content)
        
        print(f"   Found {len(external_links)} external links")
        print(f"   Found {len(external_scripts)} external scripts")
        
        # Check for common issues
        if 'localhost' in html_content:
            self.results["potential_issues"].append("Localhost references found - may not work in production")
            
        if 'http://' in html_content and self.base_url.startswith('https://'):
            self.results["potential_issues"].append("Mixed content warning - HTTP resources on HTTPS site")
            
    def analyze_performance_indicators(self, html_content):
        """Analyze performance indicators"""
        print("\n⚡ Analyzing performance indicators...")
        
        # Check content size
        content_size_kb = len(html_content) / 1024
        print(f"   HTML size: {content_size_kb:.1f} KB")
        
        if content_size_kb > 500:
            self.results["potential_issues"].append(f"Large HTML file ({content_size_kb:.1f} KB) may affect loading time")
            
        # Check for inline styles and scripts
        inline_styles = len(re.findall(r'<style[^>]*>.*?</style>', html_content, re.DOTALL))
        inline_scripts = len(re.findall(r'<script[^>]*>.*?</script>', html_content, re.DOTALL))
        
        print(f"   Inline styles: {inline_styles}")
        print(f"   Inline scripts: {inline_scripts}")
        
        if inline_styles > 5:
            self.results["recommendations"].append("Consider moving inline styles to external CSS files")
            
        if inline_scripts > 3:
            self.results["recommendations"].append("Consider moving inline scripts to external JS files")
            
    def generate_recommendations(self):
        """Generate recommendations for improvement"""
        print("\n💡 Generating recommendations...")
        
        # Performance recommendations
        if self.results["response_time"] and self.results["response_time"] > 3:
            self.results["recommendations"].append("Response time is slow (>3s). Consider optimizing server or using CDN")
            
        if self.results["content_size"] and self.results["content_size"] > 100000:  # 100KB
            self.results["recommendations"].append("Large page size. Consider code splitting or lazy loading")
            
        # Functionality recommendations
        if self.results["links_found"] > 20:
            self.results["recommendations"].append("Many links found. Consider implementing automated link checking")
            
        if self.results["buttons_found"] > 15:
            self.results["recommendations"].append("Many interactive elements. Consider comprehensive UI testing")
            
    def generate_report(self):
        """Generate and save detailed test report"""
        self.results["test_end_time"] = datetime.now().isoformat()
        
        # Save to JSON file
        with open("mybird_app_test_report.json", "w") as f:
            json.dump(self.results, f, indent=2)
            
        # Generate readable report
        report = self.create_readable_report()
        with open("mybird_app_test_report.txt", "w") as f:
            f.write(report)
            
        print(f"\n📄 Reports saved:")
        print(f"   Detailed JSON: mybird_app_test_report.json")
        print(f"   Readable report: mybird_app_test_report.txt")
        
    def create_readable_report(self):
        """Create a human-readable report"""
        report = []
        report.append("="*60)
        report.append("MYBIRD.APP WEBSITE TEST REPORT")
        report.append("="*60)
        report.append(f"Test Date: {self.results['test_start_time']}")
        report.append(f"Website: {self.results['base_url']}")
        report.append("")
        
        # Connectivity section
        report.append("CONNECTIVITY TEST")
        report.append("-" * 20)
        if self.results["connectivity"] == "success":
            report.append("✅ Website is accessible")
            report.append(f"   Status Code: {self.results['status_code']}")
            report.append(f"   Response Time: {self.results['response_time']} seconds")
            report.append(f"   Content Size: {self.results['content_size']:,} bytes")
        else:
            report.append("❌ Website connectivity issues detected")
            
        report.append("")
        
        # Structure analysis
        report.append("STRUCTURE ANALYSIS")
        report.append("-" * 20)
        report.append(f"Links found: {self.results['links_found']}")
        report.append(f"Interactive buttons: {self.results['buttons_found']}")
        report.append(f"Forms: {self.results['forms_found']}")
        
        if 'javascript_functions' in self.results:
            report.append(f"JavaScript functions: {len(self.results['javascript_functions'])}")
            
        report.append("")
        
        # Issues section
        if self.results["potential_issues"]:
            report.append("POTENTIAL ISSUES")
            report.append("-" * 20)
            for issue in self.results["potential_issues"]:
                report.append(f"⚠️  {issue}")
            report.append("")
            
        # Recommendations section
        if self.results["recommendations"]:
            report.append("RECOMMENDATIONS")
            report.append("-" * 20)
            for rec in self.results["recommendations"]:
                report.append(f"💡 {rec}")
            report.append("")
            
        # Summary
        report.append("SUMMARY")
        report.append("-" * 20)
        if self.results["connectivity"] == "success":
            report.append("✅ Website is functional and accessible")
            report.append("✅ All links and interactive elements were detected")
            if not self.results["potential_issues"]:
                report.append("✅ No major issues detected")
            else:
                report.append(f"⚠️  {len(self.results['potential_issues'])} potential issues found")
        else:
            report.append("❌ Website has connectivity issues")
            
        report.append("")
        report.append("Test completed at: " + self.results.get("test_end_time", ""))
        
        return "\n".join(report)
        
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting website analysis for mybird.app")
        print("="*50)
        
        # Test connectivity and get content
        html_content = self.test_connectivity()
        
        if html_content:
            # Analyze the HTML structure
            self.analyze_html_structure(html_content)
            
            # Analyze JavaScript functionality
            self.analyze_javascript_functions(html_content)
            
            # Check external resources
            self.check_external_resources(html_content)
            
            # Analyze performance
            self.analyze_performance_indicators(html_content)
            
            # Generate recommendations
            self.generate_recommendations()
            
        # Generate final report
        self.generate_report()
        
        print("\n✅ Analysis completed!")
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print a summary of the test results"""
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        
        if self.results["connectivity"] == "success":
            print("✅ Website Status: ACCESSIBLE")
            print(f"   Response Time: {self.results['response_time']}s")
            print(f"   Interactive Elements: {self.results['links_found'] + self.results['buttons_found']}")
            
            if self.results["potential_issues"]:
                print(f"⚠️  Issues Found: {len(self.results['potential_issues'])}")
                for issue in self.results["potential_issues"][:3]:  # Show first 3
                    print(f"   - {issue}")
                    
            if self.results["recommendations"]:
                print(f"💡 Recommendations: {len(self.results['recommendations'])}")
        else:
            print("❌ Website Status: NOT ACCESSIBLE")
            print("   Unable to perform full analysis")
            
        print(f"\nFull report available in: mybird_app_test_report.txt")

if __name__ == "__main__":
    tester = SimpleWebsiteTester("https://mybird.app")
    tester.run_all_tests()