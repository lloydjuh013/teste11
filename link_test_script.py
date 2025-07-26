#!/usr/bin/env python3
"""
Website Link Testing Script for mybird.app
Tests all links, buttons, and interactive elements for functionality
"""

import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import json
from datetime import datetime

class WebsiteTester:
    def __init__(self, base_url="https://mybird.app"):
        self.base_url = base_url
        self.results = {
            "test_start_time": datetime.now().isoformat(),
            "base_url": base_url,
            "links_tested": 0,
            "links_working": 0,
            "links_broken": 0,
            "interactive_elements_tested": 0,
            "interactive_elements_working": 0,
            "interactive_elements_broken": 0,
            "detailed_results": [],
            "errors": []
        }
        
        # Setup Chrome driver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            print("Attempting to install required dependencies...")
            self.install_dependencies()
            
    def install_dependencies(self):
        """Install required dependencies"""
        import subprocess
        import sys
        
        packages = [
            "selenium",
            "requests",
            "webdriver-manager"
        ]
        
        for package in packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except subprocess.CalledProcessError:
                print(f"Failed to install {package}")
                
        # Install Chrome and ChromeDriver
        try:
            subprocess.check_call(["apt-get", "update"])
            subprocess.check_call(["apt-get", "install", "-y", "chromium-browser", "chromium-chromedriver"])
        except subprocess.CalledProcessError:
            print("Failed to install Chrome dependencies")
            
    def test_basic_connectivity(self):
        """Test basic website connectivity"""
        print(f"Testing basic connectivity to {self.base_url}...")
        
        try:
            response = requests.get(self.base_url, timeout=10)
            if response.status_code == 200:
                print("✅ Website is accessible")
                self.results["detailed_results"].append({
                    "type": "connectivity",
                    "url": self.base_url,
                    "status": "success",
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                })
                return True
            else:
                print(f"❌ Website returned status code: {response.status_code}")
                self.results["errors"].append(f"Website returned status code: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to website: {e}")
            self.results["errors"].append(f"Failed to connect to website: {e}")
            return False
            
    def load_website(self):
        """Load the website in the browser"""
        print(f"Loading website: {self.base_url}")
        
        try:
            self.driver.get(self.base_url)
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print("✅ Website loaded successfully")
            return True
            
        except TimeoutException:
            print("❌ Website failed to load within timeout")
            self.results["errors"].append("Website failed to load within timeout")
            return False
            
    def test_navigation_links(self):
        """Test navigation menu links"""
        print("\nTesting navigation links...")
        
        nav_items = [
            "switchSection('marketplace')",
            "switchSection('auctions')", 
            "switchSection('trading')",
            "switchSection('admin')"
        ]
        
        for nav_item in nav_items:
            try:
                element = self.driver.find_element(By.XPATH, f"//a[@onclick=\"{nav_item}\"]")
                if element.is_displayed():
                    element.click()
                    time.sleep(1)  # Wait for section to load
                    print(f"✅ Navigation item working: {nav_item}")
                    self.results["interactive_elements_working"] += 1
                else:
                    print(f"⚠️  Navigation item not visible: {nav_item}")
                    
            except Exception as e:
                print(f"❌ Navigation item failed: {nav_item} - {e}")
                self.results["interactive_elements_broken"] += 1
                self.results["errors"].append(f"Navigation item failed: {nav_item} - {e}")
                
            self.results["interactive_elements_tested"] += 1
            
    def test_interactive_buttons(self):
        """Test interactive buttons and onclick handlers"""
        print("\nTesting interactive buttons...")
        
        button_functions = [
            "toggleAdminAccess()",
            "toggleWalletOptions()",
            "connectWallet('Phantom')",
            "connectWallet('MetaMask')",
            "connectWallet('Solflare')",
            "createTrade()",
            "addNewCard()",
            "saveSettings()",
            "toggleCart()",
            "checkout()"
        ]
        
        for func in button_functions:
            try:
                elements = self.driver.find_elements(By.XPATH, f"//button[@onclick=\"{func}\"]")
                if elements:
                    element = elements[0]
                    if element.is_displayed() and element.is_enabled():
                        try:
                            self.driver.execute_script("arguments[0].click();", element)
                            time.sleep(0.5)
                            print(f"✅ Button function working: {func}")
                            self.results["interactive_elements_working"] += 1
                        except ElementClickInterceptedException:
                            print(f"⚠️  Button not clickable: {func}")
                    else:
                        print(f"⚠️  Button not visible/enabled: {func}")
                else:
                    print(f"⚠️  Button not found: {func}")
                    
            except Exception as e:
                print(f"❌ Button function failed: {func} - {e}")
                self.results["interactive_elements_broken"] += 1
                self.results["errors"].append(f"Button function failed: {func} - {e}")
                
            self.results["interactive_elements_tested"] += 1
            
    def test_admin_functionality(self):
        """Test admin panel functionality"""
        print("\nTesting admin functionality...")
        
        try:
            # Try to access admin section
            admin_btn = self.driver.find_element(By.XPATH, "//button[@onclick='toggleAdminAccess()']")
            admin_btn.click()
            time.sleep(1)
            
            # Test admin tabs
            admin_tabs = [
                "switchAdminTab('overview')",
                "switchAdminTab('cards')",
                "switchAdminTab('users')",
                "switchAdminTab('settings')"
            ]
            
            for tab in admin_tabs:
                try:
                    tab_element = self.driver.find_element(By.XPATH, f"//button[@onclick=\"{tab}\"]")
                    if tab_element.is_displayed():
                        tab_element.click()
                        time.sleep(0.5)
                        print(f"✅ Admin tab working: {tab}")
                        self.results["interactive_elements_working"] += 1
                    else:
                        print(f"⚠️  Admin tab not visible: {tab}")
                        
                except Exception as e:
                    print(f"❌ Admin tab failed: {tab} - {e}")
                    self.results["interactive_elements_broken"] += 1
                    
                self.results["interactive_elements_tested"] += 1
                
        except Exception as e:
            print(f"❌ Admin functionality test failed: {e}")
            self.results["errors"].append(f"Admin functionality test failed: {e}")
            
    def test_form_functionality(self):
        """Test forms and input elements"""
        print("\nTesting form functionality...")
        
        try:
            # Test search functionality
            search_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            for i, search_input in enumerate(search_inputs):
                if search_input.is_displayed():
                    search_input.clear()
                    search_input.send_keys("test search")
                    print(f"✅ Search input {i+1} working")
                    self.results["interactive_elements_working"] += 1
                else:
                    print(f"⚠️  Search input {i+1} not visible")
                    
                self.results["interactive_elements_tested"] += 1
                
        except Exception as e:
            print(f"❌ Form functionality test failed: {e}")
            self.results["errors"].append(f"Form functionality test failed: {e}")
            
    def test_responsive_design(self):
        """Test responsive design at different screen sizes"""
        print("\nTesting responsive design...")
        
        screen_sizes = [
            (1920, 1080),  # Desktop
            (768, 1024),   # Tablet
            (375, 667)     # Mobile
        ]
        
        for width, height in screen_sizes:
            try:
                self.driver.set_window_size(width, height)
                time.sleep(1)
                
                # Check if main elements are visible
                body = self.driver.find_element(By.TAG_NAME, "body")
                if body.is_displayed():
                    print(f"✅ Responsive design working at {width}x{height}")
                    self.results["interactive_elements_working"] += 1
                else:
                    print(f"❌ Responsive design issue at {width}x{height}")
                    self.results["interactive_elements_broken"] += 1
                    
            except Exception as e:
                print(f"❌ Responsive test failed at {width}x{height}: {e}")
                self.results["interactive_elements_broken"] += 1
                
            self.results["interactive_elements_tested"] += 1
            
    def test_performance(self):
        """Test website performance"""
        print("\nTesting website performance...")
        
        try:
            start_time = time.time()
            self.driver.get(self.base_url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            load_time = time.time() - start_time
            
            print(f"✅ Page load time: {load_time:.2f} seconds")
            
            if load_time < 3:
                print("✅ Good performance (< 3 seconds)")
                performance_status = "good"
            elif load_time < 5:
                print("⚠️  Acceptable performance (3-5 seconds)")
                performance_status = "acceptable"
            else:
                print("❌ Poor performance (> 5 seconds)")
                performance_status = "poor"
                
            self.results["detailed_results"].append({
                "type": "performance",
                "load_time": load_time,
                "status": performance_status
            })
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            self.results["errors"].append(f"Performance test failed: {e}")
            
    def generate_report(self):
        """Generate and save test results"""
        self.results["test_end_time"] = datetime.now().isoformat()
        
        # Calculate success rates
        total_interactive = self.results["interactive_elements_tested"]
        working_interactive = self.results["interactive_elements_working"]
        
        if total_interactive > 0:
            success_rate = (working_interactive / total_interactive) * 100
        else:
            success_rate = 0
            
        self.results["success_rate"] = success_rate
        
        # Save results to file
        with open("website_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
            
        # Print summary
        print("\n" + "="*50)
        print("WEBSITE TEST SUMMARY")
        print("="*50)
        print(f"Website: {self.base_url}")
        print(f"Interactive elements tested: {total_interactive}")
        print(f"Interactive elements working: {working_interactive}")
        print(f"Interactive elements broken: {total_interactive - working_interactive}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Errors encountered: {len(self.results['errors'])}")
        
        if self.results['errors']:
            print("\nErrors:")
            for error in self.results['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
                
        print(f"\nDetailed results saved to: website_test_results.json")
        
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting comprehensive website test for mybird.app")
        print("="*60)
        
        # Basic connectivity test
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Stopping tests.")
            return
            
        # Load website
        if not self.load_website():
            print("❌ Failed to load website. Stopping tests.")
            return
            
        # Run all tests
        self.test_navigation_links()
        self.test_interactive_buttons()
        self.test_admin_functionality()
        self.test_form_functionality()
        self.test_responsive_design()
        self.test_performance()
        
        # Generate report
        self.generate_report()
        
        # Cleanup
        if hasattr(self, 'driver'):
            self.driver.quit()
            
        print("\n✅ All tests completed!")
        
if __name__ == "__main__":
    tester = WebsiteTester("https://mybird.app")
    tester.run_all_tests()