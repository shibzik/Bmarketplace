#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Moldovan Business Marketplace
Tests all API endpoints with various scenarios and filters
"""

import requests
import json
import sys
from typing import Dict, List, Any
import time

# Backend URL from environment
BACKEND_URL = "https://d2d8bc66-4ba6-4364-9176-ddd5853aaddc.preview.emergentagent.com/api"

class BusinessMarketplaceAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = []
        self.sample_business_ids = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} - {test_name}"
        if details:
            result += f": {details}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> tuple:
        """Make HTTP request and return response and success status"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, timeout=30)
            else:
                return None, False, f"Unsupported method: {method}"
                
            return response, True, ""
        except requests.exceptions.RequestException as e:
            return None, False, str(e)
    
    def test_root_endpoint(self):
        """Test the root API endpoint"""
        print("\n=== Testing Root Endpoint ===")
        response, success, error = self.make_request("GET", "/")
        
        if not success:
            self.log_test("Root Endpoint", False, f"Request failed: {error}")
            return
            
        if response.status_code == 200:
            try:
                data = response.json()
                if "message" in data:
                    self.log_test("Root Endpoint", True, f"Message: {data['message']}")
                else:
                    self.log_test("Root Endpoint", False, "No message in response")
            except json.JSONDecodeError:
                self.log_test("Root Endpoint", False, "Invalid JSON response")
        else:
            self.log_test("Root Endpoint", False, f"Status code: {response.status_code}")
    
    def test_business_listings_basic(self):
        """Test basic business listings endpoint"""
        print("\n=== Testing Business Listings API ===")
        response, success, error = self.make_request("GET", "/businesses")
        
        if not success:
            self.log_test("Business Listings Basic", False, f"Request failed: {error}")
            return
            
        if response.status_code == 200:
            try:
                businesses = response.json()
                if isinstance(businesses, list):
                    count = len(businesses)
                    self.log_test("Business Listings Basic", True, f"Retrieved {count} businesses")
                    
                    # Store business IDs for detail testing
                    self.sample_business_ids = [b.get('id') for b in businesses if b.get('id')]
                    
                    # Verify sample data structure
                    if count >= 5:
                        self.log_test("Sample Data Count", True, f"Found {count} businesses (expected ≥5)")
                        
                        # Check first business structure
                        first_business = businesses[0]
                        required_fields = ['id', 'title', 'industry', 'region', 'annual_revenue', 
                                         'ebitda', 'asking_price', 'risk_grade', 'status']
                        missing_fields = [field for field in required_fields if field not in first_business]
                        
                        if not missing_fields:
                            self.log_test("Business Data Structure", True, "All required fields present")
                        else:
                            self.log_test("Business Data Structure", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_test("Sample Data Count", False, f"Only {count} businesses found (expected ≥5)")
                else:
                    self.log_test("Business Listings Basic", False, "Response is not a list")
            except json.JSONDecodeError:
                self.log_test("Business Listings Basic", False, "Invalid JSON response")
        else:
            self.log_test("Business Listings Basic", False, f"Status code: {response.status_code}")
    
    def test_business_detail(self):
        """Test business detail endpoint"""
        print("\n=== Testing Business Detail API ===")
        
        if not self.sample_business_ids:
            self.log_test("Business Detail", False, "No business IDs available for testing")
            return
            
        # Test with first business ID
        business_id = self.sample_business_ids[0]
        response, success, error = self.make_request("GET", f"/businesses/{business_id}")
        
        if not success:
            self.log_test("Business Detail", False, f"Request failed: {error}")
            return
            
        if response.status_code == 200:
            try:
                business = response.json()
                required_fields = ['id', 'title', 'description', 'industry', 'region', 
                                 'annual_revenue', 'ebitda', 'asking_price', 'risk_grade',
                                 'financial_data', 'key_metrics', 'seller_name']
                missing_fields = [field for field in required_fields if field not in business]
                
                if not missing_fields:
                    self.log_test("Business Detail", True, f"Retrieved detailed business: {business.get('title', 'Unknown')}")
                    
                    # Test financial data structure
                    financial_data = business.get('financial_data', [])
                    if isinstance(financial_data, list) and len(financial_data) > 0:
                        first_year = financial_data[0]
                        financial_fields = ['year', 'revenue', 'profit_loss', 'ebitda', 'assets', 'liabilities', 'cash_flow']
                        missing_financial = [field for field in financial_fields if field not in first_year]
                        
                        if not missing_financial:
                            self.log_test("Financial Data Structure", True, f"Complete financial data for {len(financial_data)} years")
                        else:
                            self.log_test("Financial Data Structure", False, f"Missing financial fields: {missing_financial}")
                    else:
                        self.log_test("Financial Data Structure", False, "No financial data found")
                        
                    # Test view increment (make another request and check if views increased)
                    time.sleep(1)  # Small delay
                    response2, success2, _ = self.make_request("GET", f"/businesses/{business_id}")
                    if success2 and response2.status_code == 200:
                        business2 = response2.json()
                        views1 = business.get('views', 0)
                        views2 = business2.get('views', 0)
                        if views2 > views1:
                            self.log_test("View Increment", True, f"Views increased from {views1} to {views2}")
                        else:
                            self.log_test("View Increment", False, f"Views did not increment: {views1} -> {views2}")
                else:
                    self.log_test("Business Detail", False, f"Missing fields: {missing_fields}")
            except json.JSONDecodeError:
                self.log_test("Business Detail", False, "Invalid JSON response")
        elif response.status_code == 404:
            self.log_test("Business Detail", False, f"Business not found: {business_id}")
        else:
            self.log_test("Business Detail", False, f"Status code: {response.status_code}")
    
    def test_industry_filtering(self):
        """Test filtering by industry"""
        print("\n=== Testing Industry Filtering ===")
        
        industries_to_test = ["manufacturing", "retail", "food_service", "technology", "agriculture"]
        
        for industry in industries_to_test:
            response, success, error = self.make_request("GET", "/businesses", {"industry": industry})
            
            if not success:
                self.log_test(f"Industry Filter ({industry})", False, f"Request failed: {error}")
                continue
                
            if response.status_code == 200:
                try:
                    businesses = response.json()
                    if isinstance(businesses, list):
                        # Check if all businesses have the correct industry
                        correct_industry = all(b.get('industry') == industry for b in businesses)
                        if correct_industry:
                            self.log_test(f"Industry Filter ({industry})", True, f"Found {len(businesses)} businesses")
                        else:
                            wrong_industries = [b.get('industry') for b in businesses if b.get('industry') != industry]
                            self.log_test(f"Industry Filter ({industry})", False, f"Wrong industries found: {wrong_industries}")
                    else:
                        self.log_test(f"Industry Filter ({industry})", False, "Response is not a list")
                except json.JSONDecodeError:
                    self.log_test(f"Industry Filter ({industry})", False, "Invalid JSON response")
            else:
                self.log_test(f"Industry Filter ({industry})", False, f"Status code: {response.status_code}")
    
    def test_region_filtering(self):
        """Test filtering by region"""
        print("\n=== Testing Region Filtering ===")
        
        regions_to_test = ["chisinau", "balti", "cahul"]
        
        for region in regions_to_test:
            response, success, error = self.make_request("GET", "/businesses", {"region": region})
            
            if not success:
                self.log_test(f"Region Filter ({region})", False, f"Request failed: {error}")
                continue
                
            if response.status_code == 200:
                try:
                    businesses = response.json()
                    if isinstance(businesses, list):
                        # Check if all businesses have the correct region
                        correct_region = all(b.get('region') == region for b in businesses)
                        if correct_region:
                            self.log_test(f"Region Filter ({region})", True, f"Found {len(businesses)} businesses")
                        else:
                            wrong_regions = [b.get('region') for b in businesses if b.get('region') != region]
                            self.log_test(f"Region Filter ({region})", False, f"Wrong regions found: {wrong_regions}")
                    else:
                        self.log_test(f"Region Filter ({region})", False, "Response is not a list")
                except json.JSONDecodeError:
                    self.log_test(f"Region Filter ({region})", False, "Invalid JSON response")
            else:
                self.log_test(f"Region Filter ({region})", False, f"Status code: {response.status_code}")
    
    def test_revenue_filtering(self):
        """Test filtering by revenue range"""
        print("\n=== Testing Revenue Range Filtering ===")
        
        # Test minimum revenue filter
        response, success, error = self.make_request("GET", "/businesses", {"min_revenue": 1000000})
        
        if success and response.status_code == 200:
            try:
                businesses = response.json()
                if isinstance(businesses, list):
                    valid_revenue = all(b.get('annual_revenue', 0) >= 1000000 for b in businesses)
                    if valid_revenue:
                        self.log_test("Min Revenue Filter", True, f"Found {len(businesses)} businesses with revenue ≥ 1M")
                    else:
                        invalid = [b.get('annual_revenue') for b in businesses if b.get('annual_revenue', 0) < 1000000]
                        self.log_test("Min Revenue Filter", False, f"Found businesses below threshold: {invalid}")
                else:
                    self.log_test("Min Revenue Filter", False, "Response is not a list")
            except json.JSONDecodeError:
                self.log_test("Min Revenue Filter", False, "Invalid JSON response")
        else:
            self.log_test("Min Revenue Filter", False, f"Request failed: {error if not success else response.status_code}")
        
        # Test maximum revenue filter
        response, success, error = self.make_request("GET", "/businesses", {"max_revenue": 2000000})
        
        if success and response.status_code == 200:
            try:
                businesses = response.json()
                if isinstance(businesses, list):
                    valid_revenue = all(b.get('annual_revenue', 0) <= 2000000 for b in businesses)
                    if valid_revenue:
                        self.log_test("Max Revenue Filter", True, f"Found {len(businesses)} businesses with revenue ≤ 2M")
                    else:
                        invalid = [b.get('annual_revenue') for b in businesses if b.get('annual_revenue', 0) > 2000000]
                        self.log_test("Max Revenue Filter", False, f"Found businesses above threshold: {invalid}")
                else:
                    self.log_test("Max Revenue Filter", False, "Response is not a list")
            except json.JSONDecodeError:
                self.log_test("Max Revenue Filter", False, "Invalid JSON response")
        else:
            self.log_test("Max Revenue Filter", False, f"Request failed: {error if not success else response.status_code}")
    
    def test_risk_grade_filtering(self):
        """Test filtering by risk grade"""
        print("\n=== Testing Risk Grade Filtering ===")
        
        risk_grades = ["A", "B", "C", "D", "E"]
        
        for grade in risk_grades:
            response, success, error = self.make_request("GET", "/businesses", {"risk_grade": grade})
            
            if not success:
                self.log_test(f"Risk Grade Filter ({grade})", False, f"Request failed: {error}")
                continue
                
            if response.status_code == 200:
                try:
                    businesses = response.json()
                    if isinstance(businesses, list):
                        correct_grade = all(b.get('risk_grade') == grade for b in businesses)
                        if correct_grade:
                            self.log_test(f"Risk Grade Filter ({grade})", True, f"Found {len(businesses)} businesses")
                        else:
                            wrong_grades = [b.get('risk_grade') for b in businesses if b.get('risk_grade') != grade]
                            self.log_test(f"Risk Grade Filter ({grade})", False, f"Wrong grades found: {wrong_grades}")
                    else:
                        self.log_test(f"Risk Grade Filter ({grade})", False, "Response is not a list")
                except json.JSONDecodeError:
                    self.log_test(f"Risk Grade Filter ({grade})", False, "Invalid JSON response")
            else:
                self.log_test(f"Risk Grade Filter ({grade})", False, f"Status code: {response.status_code}")
    
    def test_sorting(self):
        """Test sorting functionality"""
        print("\n=== Testing Sorting ===")
        
        sort_tests = [
            ("asking_price", "asc"),
            ("asking_price", "desc"),
            ("annual_revenue", "asc"),
            ("annual_revenue", "desc"),
            ("created_at", "desc"),
            ("views", "desc")
        ]
        
        for sort_by, sort_order in sort_tests:
            # Test with featured_first=False to get pure sorting
            params = {"sort_by": sort_by, "sort_order": sort_order, "featured_first": False}
            response, success, error = self.make_request("GET", "/businesses", params)
            
            if not success:
                self.log_test(f"Sort by {sort_by} {sort_order}", False, f"Request failed: {error}")
                continue
                
            if response.status_code == 200:
                try:
                    businesses = response.json()
                    if isinstance(businesses, list) and len(businesses) > 1:
                        # Check if sorting is correct
                        values = [b.get(sort_by) for b in businesses if b.get(sort_by) is not None]
                        if len(values) > 1:
                            is_sorted = True
                            for i in range(1, len(values)):
                                if sort_order == "asc" and values[i] < values[i-1]:
                                    is_sorted = False
                                    break
                                elif sort_order == "desc" and values[i] > values[i-1]:
                                    is_sorted = False
                                    break
                            
                            if is_sorted:
                                self.log_test(f"Sort by {sort_by} {sort_order}", True, f"Correctly sorted {len(businesses)} businesses")
                            else:
                                self.log_test(f"Sort by {sort_by} {sort_order}", False, "Incorrect sorting order")
                        else:
                            self.log_test(f"Sort by {sort_by} {sort_order}", True, "Insufficient data to verify sorting")
                    else:
                        self.log_test(f"Sort by {sort_by} {sort_order}", True, "Response received (insufficient data for sort verification)")
                except json.JSONDecodeError:
                    self.log_test(f"Sort by {sort_by} {sort_order}", False, "Invalid JSON response")
            else:
                self.log_test(f"Sort by {sort_by} {sort_order}", False, f"Status code: {response.status_code}")
        
        # Test sorting with featured_first=True (default behavior)
        print("\n=== Testing Sorting with Featured First ===")
        params = {"sort_by": "asking_price", "sort_order": "asc", "featured_first": True}
        response, success, error = self.make_request("GET", "/businesses", params)
        
        if success and response.status_code == 200:
            try:
                businesses = response.json()
                if isinstance(businesses, list) and len(businesses) > 0:
                    # Separate featured and non-featured businesses
                    featured = [b for b in businesses if b.get('featured', False)]
                    non_featured = [b for b in businesses if not b.get('featured', False)]
                    
                    # Check if featured businesses come first
                    featured_first_correct = True
                    if featured and non_featured:
                        # Find the last featured business index and first non-featured business index
                        last_featured_idx = -1
                        first_non_featured_idx = len(businesses)
                        
                        for i, b in enumerate(businesses):
                            if b.get('featured', False):
                                last_featured_idx = i
                            elif first_non_featured_idx == len(businesses):
                                first_non_featured_idx = i
                        
                        if last_featured_idx >= first_non_featured_idx:
                            featured_first_correct = False
                    
                    # Check sorting within each group
                    featured_sorted = True
                    non_featured_sorted = True
                    
                    if len(featured) > 1:
                        featured_prices = [b.get('asking_price') for b in featured]
                        for i in range(1, len(featured_prices)):
                            if featured_prices[i] < featured_prices[i-1]:
                                featured_sorted = False
                                break
                    
                    if len(non_featured) > 1:
                        non_featured_prices = [b.get('asking_price') for b in non_featured]
                        for i in range(1, len(non_featured_prices)):
                            if non_featured_prices[i] < non_featured_prices[i-1]:
                                non_featured_sorted = False
                                break
                    
                    if featured_first_correct and featured_sorted and non_featured_sorted:
                        self.log_test("Featured First + Sorting", True, f"Featured businesses first, then sorted within groups")
                    else:
                        issues = []
                        if not featured_first_correct:
                            issues.append("featured not first")
                        if not featured_sorted:
                            issues.append("featured group not sorted")
                        if not non_featured_sorted:
                            issues.append("non-featured group not sorted")
                        self.log_test("Featured First + Sorting", False, f"Issues: {', '.join(issues)}")
                else:
                    self.log_test("Featured First + Sorting", False, "No businesses returned")
            except json.JSONDecodeError:
                self.log_test("Featured First + Sorting", False, "Invalid JSON response")
        else:
            self.log_test("Featured First + Sorting", False, f"Request failed: {error if not success else response.status_code}")
    
    def test_featured_prioritization(self):
        """Test featured business prioritization"""
        print("\n=== Testing Featured Business Prioritization ===")
        
        response, success, error = self.make_request("GET", "/businesses", {"featured_first": True})
        
        if not success:
            self.log_test("Featured Prioritization", False, f"Request failed: {error}")
            return
            
        if response.status_code == 200:
            try:
                businesses = response.json()
                if isinstance(businesses, list) and len(businesses) > 0:
                    # Check if featured businesses come first
                    featured_found = False
                    non_featured_found = False
                    featured_after_non_featured = False
                    
                    for business in businesses:
                        is_featured = business.get('featured', False)
                        if is_featured:
                            if non_featured_found:
                                featured_after_non_featured = True
                                break
                            featured_found = True
                        else:
                            non_featured_found = True
                    
                    if featured_found and not featured_after_non_featured:
                        self.log_test("Featured Prioritization", True, "Featured businesses appear first")
                    elif not featured_found:
                        self.log_test("Featured Prioritization", True, "No featured businesses to test prioritization")
                    else:
                        self.log_test("Featured Prioritization", False, "Featured businesses not properly prioritized")
                else:
                    self.log_test("Featured Prioritization", False, "No businesses returned")
            except json.JSONDecodeError:
                self.log_test("Featured Prioritization", False, "Invalid JSON response")
        else:
            self.log_test("Featured Prioritization", False, f"Status code: {response.status_code}")
    
    def test_filter_options_endpoints(self):
        """Test filter options endpoints"""
        print("\n=== Testing Filter Options APIs ===")
        
        # Test industries endpoint
        response, success, error = self.make_request("GET", "/industries")
        if success and response.status_code == 200:
            try:
                industries = response.json()
                if isinstance(industries, list) and len(industries) > 0:
                    # Check structure
                    first_industry = industries[0]
                    if 'value' in first_industry and 'label' in first_industry:
                        self.log_test("Industries Endpoint", True, f"Retrieved {len(industries)} industries")
                    else:
                        self.log_test("Industries Endpoint", False, "Invalid industry structure")
                else:
                    self.log_test("Industries Endpoint", False, "No industries returned")
            except json.JSONDecodeError:
                self.log_test("Industries Endpoint", False, "Invalid JSON response")
        else:
            self.log_test("Industries Endpoint", False, f"Request failed: {error if not success else response.status_code}")
        
        # Test regions endpoint
        response, success, error = self.make_request("GET", "/regions")
        if success and response.status_code == 200:
            try:
                regions = response.json()
                if isinstance(regions, list) and len(regions) > 0:
                    first_region = regions[0]
                    if 'value' in first_region and 'label' in first_region:
                        self.log_test("Regions Endpoint", True, f"Retrieved {len(regions)} regions")
                    else:
                        self.log_test("Regions Endpoint", False, "Invalid region structure")
                else:
                    self.log_test("Regions Endpoint", False, "No regions returned")
            except json.JSONDecodeError:
                self.log_test("Regions Endpoint", False, "Invalid JSON response")
        else:
            self.log_test("Regions Endpoint", False, f"Request failed: {error if not success else response.status_code}")
        
        # Test risk grades endpoint
        response, success, error = self.make_request("GET", "/risk-grades")
        if success and response.status_code == 200:
            try:
                risk_grades = response.json()
                if isinstance(risk_grades, list) and len(risk_grades) > 0:
                    first_grade = risk_grades[0]
                    if 'value' in first_grade and 'label' in first_grade:
                        self.log_test("Risk Grades Endpoint", True, f"Retrieved {len(risk_grades)} risk grades")
                    else:
                        self.log_test("Risk Grades Endpoint", False, "Invalid risk grade structure")
                else:
                    self.log_test("Risk Grades Endpoint", False, "No risk grades returned")
            except json.JSONDecodeError:
                self.log_test("Risk Grades Endpoint", False, "Invalid JSON response")
        else:
            self.log_test("Risk Grades Endpoint", False, f"Request failed: {error if not success else response.status_code}")
    
    def test_combined_filters(self):
        """Test multiple filters combined"""
        print("\n=== Testing Combined Filters ===")
        
        # Test industry + region combination
        params = {"industry": "manufacturing", "region": "chisinau"}
        response, success, error = self.make_request("GET", "/businesses", params)
        
        if success and response.status_code == 200:
            try:
                businesses = response.json()
                if isinstance(businesses, list):
                    valid_combination = all(
                        b.get('industry') == 'manufacturing' and b.get('region') == 'chisinau'
                        for b in businesses
                    )
                    if valid_combination:
                        self.log_test("Combined Filters (Industry + Region)", True, f"Found {len(businesses)} matching businesses")
                    else:
                        self.log_test("Combined Filters (Industry + Region)", False, "Some businesses don't match both filters")
                else:
                    self.log_test("Combined Filters (Industry + Region)", False, "Response is not a list")
            except json.JSONDecodeError:
                self.log_test("Combined Filters (Industry + Region)", False, "Invalid JSON response")
        else:
            self.log_test("Combined Filters (Industry + Region)", False, f"Request failed: {error if not success else response.status_code}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Moldovan Business Marketplace Backend API Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 80)
        
        # Run all test methods
        self.test_root_endpoint()
        self.test_business_listings_basic()
        self.test_business_detail()
        self.test_industry_filtering()
        self.test_region_filtering()
        self.test_revenue_filtering()
        self.test_risk_grade_filtering()
        self.test_sorting()
        self.test_featured_prioritization()
        self.test_filter_options_endpoints()
        self.test_combined_filters()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        return passed == total

if __name__ == "__main__":
    tester = BusinessMarketplaceAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)