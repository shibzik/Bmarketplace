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
import base64
import io

# Backend URL from environment
BACKEND_URL = "https://d2d8bc66-4ba6-4364-9176-ddd5853aaddc.preview.emergentagent.com/api"

class BusinessMarketplaceAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = []
        self.sample_business_ids = []
        self.created_business_ids = []  # Track businesses created during testing
        
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
    
    def test_business_creation(self):
        """Test business creation API"""
        print("\n=== Testing Business Creation API ===")
        
        # Test 1: Create business with full data
        full_business_data = {
            "title": "Test Moldovan Bakery Chain",
            "description": "Traditional bakery chain with 3 locations in Chisinau serving fresh bread and pastries daily",
            "industry": "food_service",
            "region": "chisinau",
            "annual_revenue": 450000.0,
            "ebitda": 67500.0,
            "asking_price": 650000.0,
            "risk_grade": "B",
            "seller_name": "Ion Popescu",
            "seller_email": "ion.popescu@example.com",
            "reason_for_sale": "Retirement after 20 years",
            "growth_opportunities": "Expand to other cities, add online ordering, catering services",
            "financial_data": [
                {
                    "year": 2023,
                    "revenue": 450000,
                    "profit_loss": 54000,
                    "ebitda": 67500,
                    "assets": 580000,
                    "liabilities": 280000,
                    "cash_flow": 62000
                },
                {
                    "year": 2022,
                    "revenue": 420000,
                    "profit_loss": 50400,
                    "ebitda": 63000,
                    "assets": 550000,
                    "liabilities": 300000,
                    "cash_flow": 58000
                }
            ],
            "key_metrics": {
                "employees": 15,
                "years_in_business": 20,
                "locations": 3,
                "daily_customers": 200
            },
            "status": "draft"
        }
        
        response, success, error = self.make_request("POST", "/businesses", data=full_business_data)
        
        if not success:
            self.log_test("Business Creation (Full Data)", False, f"Request failed: {error}")
        elif response.status_code == 200:
            try:
                created_business = response.json()
                
                # Verify required fields are present (based on actual API response)
                required_fields = ['id', 'title', 'description', 'industry', 'region', 'annual_revenue', 
                                 'ebitda', 'asking_price', 'risk_grade', 'status', 'seller_name', 
                                 'created_at', 'views', 'inquiries']
                missing_fields = [field for field in required_fields if field not in created_business]
                
                if not missing_fields:
                    # Verify status is draft
                    if created_business.get('status') == 'draft':
                        # Verify auto-generated fields
                        if (created_business.get('views') == 0 and 
                            created_business.get('inquiries') == 0 and
                            created_business.get('id') and
                            created_business.get('created_at')):
                            
                            self.created_business_ids.append(created_business['id'])
                            self.log_test("Business Creation (Full Data)", True, 
                                        f"Created business with ID: {created_business['id']}, Status: {created_business['status']}")
                        else:
                            self.log_test("Business Creation (Full Data)", False, "Auto-generated fields not properly set")
                    else:
                        self.log_test("Business Creation (Full Data)", False, f"Expected status 'draft', got '{created_business.get('status')}'")
                else:
                    self.log_test("Business Creation (Full Data)", False, f"Missing fields: {missing_fields}")
                    
            except json.JSONDecodeError:
                self.log_test("Business Creation (Full Data)", False, "Invalid JSON response")
        else:
            self.log_test("Business Creation (Full Data)", False, f"Status code: {response.status_code}")
        
        # Test 2: Create business with minimal required data
        minimal_business_data = {
            "title": "Test Tech Startup",
            "description": "Innovative software development company",
            "industry": "technology",
            "region": "balti",
            "annual_revenue": 150000.0,
            "ebitda": 45000.0,
            "asking_price": 300000.0,
            "risk_grade": "A",
            "seller_name": "Maria Ionescu",
            "seller_email": "maria.ionescu@example.com",
            "reason_for_sale": "New opportunity abroad",
            "growth_opportunities": "Scale internationally",
            "financial_data": [
                {
                    "year": 2023,
                    "revenue": 150000,
                    "profit_loss": 36000,
                    "ebitda": 45000,
                    "assets": 200000,
                    "liabilities": 80000,
                    "cash_flow": 42000
                }
            ],
            "key_metrics": {
                "employees": 8,
                "years_in_business": 3
            }
        }
        
        response, success, error = self.make_request("POST", "/businesses", data=minimal_business_data)
        
        if success and response.status_code == 200:
            try:
                created_business = response.json()
                if created_business.get('status') == 'draft' and created_business.get('id'):
                    self.created_business_ids.append(created_business['id'])
                    self.log_test("Business Creation (Minimal Data)", True, 
                                f"Created business with minimal data, ID: {created_business['id']}")
                else:
                    self.log_test("Business Creation (Minimal Data)", False, "Business not created properly")
            except json.JSONDecodeError:
                self.log_test("Business Creation (Minimal Data)", False, "Invalid JSON response")
        else:
            self.log_test("Business Creation (Minimal Data)", False, f"Request failed: {error if not success else response.status_code}")
        
        # Test 3: Test validation for required fields (missing title)
        invalid_business_data = {
            "description": "Test business without title",
            "industry": "retail",
            "region": "chisinau",
            "annual_revenue": 100000.0,
            "ebitda": 15000.0,
            "asking_price": 200000.0,
            "risk_grade": "C",
            "seller_name": "Test Seller",
            "seller_email": "test@example.com",
            "reason_for_sale": "Test",
            "growth_opportunities": "Test",
            "financial_data": [],
            "key_metrics": {}
        }
        
        response, success, error = self.make_request("POST", "/businesses", data=invalid_business_data)
        
        if success and response.status_code == 422:  # Validation error expected
            self.log_test("Business Creation Validation", True, "Properly rejected business without required title field")
        elif success and response.status_code == 200:
            self.log_test("Business Creation Validation", False, "Should have rejected business without title")
        else:
            self.log_test("Business Creation Validation", False, f"Unexpected response: {error if not success else response.status_code}")
    
    def test_business_update(self):
        """Test business update API"""
        print("\n=== Testing Business Update API ===")
        
        if not self.created_business_ids:
            self.log_test("Business Update", False, "No created businesses available for testing")
            return
        
        business_id = self.created_business_ids[0]
        
        # Test 1: Update business with partial data
        update_data = {
            "title": "Updated Moldovan Bakery Chain - Premium",
            "asking_price": 750000.0,
            "growth_opportunities": "Expand to other cities, add online ordering, catering services, franchise opportunities",
            "status": "pending_payment"
        }
        
        response, success, error = self.make_request("PUT", f"/businesses/{business_id}", data=update_data)
        
        if not success:
            self.log_test("Business Update (Partial Data)", False, f"Request failed: {error}")
        elif response.status_code == 200:
            try:
                updated_business = response.json()
                
                # Verify updates were applied
                if (updated_business.get('title') == update_data['title'] and
                    updated_business.get('asking_price') == update_data['asking_price'] and
                    updated_business.get('status') == update_data['status']):
                    
                    # Verify updated_at was changed (check if created_at exists as proxy)
                    if updated_business.get('created_at'):
                        self.log_test("Business Update (Partial Data)", True, 
                                    f"Successfully updated business, new status: {updated_business['status']}")
                    else:
                        self.log_test("Business Update (Partial Data)", False, "Business response incomplete")
                else:
                    self.log_test("Business Update (Partial Data)", False, "Updates not properly applied")
                    
            except json.JSONDecodeError:
                self.log_test("Business Update (Partial Data)", False, "Invalid JSON response")
        else:
            self.log_test("Business Update (Partial Data)", False, f"Status code: {response.status_code}")
        
        # Test 2: Update financial data and key metrics
        financial_update = {
            "financial_data": [
                {
                    "year": 2023,
                    "revenue": 480000,
                    "profit_loss": 57600,
                    "ebitda": 72000,
                    "assets": 620000,
                    "liabilities": 260000,
                    "cash_flow": 66000
                }
            ],
            "key_metrics": {
                "employees": 18,
                "years_in_business": 20,
                "locations": 4,
                "daily_customers": 250,
                "new_metric": "premium_products"
            }
        }
        
        response, success, error = self.make_request("PUT", f"/businesses/{business_id}", data=financial_update)
        
        if success and response.status_code == 200:
            try:
                updated_business = response.json()
                financial_data = updated_business.get('financial_data', [])
                key_metrics = updated_business.get('key_metrics', {})
                
                if (len(financial_data) > 0 and 
                    financial_data[0].get('revenue') == 480000 and
                    key_metrics.get('employees') == 18 and
                    key_metrics.get('new_metric') == 'premium_products'):
                    
                    self.log_test("Business Update (Financial Data)", True, "Successfully updated financial data and metrics")
                else:
                    self.log_test("Business Update (Financial Data)", False, "Financial data or metrics not updated properly")
            except json.JSONDecodeError:
                self.log_test("Business Update (Financial Data)", False, "Invalid JSON response")
        else:
            self.log_test("Business Update (Financial Data)", False, f"Request failed: {error if not success else response.status_code}")
        
        # Test 3: Test 404 for non-existent business
        fake_id = "non-existent-business-id"
        response, success, error = self.make_request("PUT", f"/businesses/{fake_id}", data={"title": "Test"})
        
        if success and response.status_code == 404:
            self.log_test("Business Update (404 Test)", True, "Properly returned 404 for non-existent business")
        else:
            self.log_test("Business Update (404 Test)", False, f"Expected 404, got: {response.status_code if success else error}")
    
    def test_seller_businesses(self):
        """Test get seller's businesses API"""
        print("\n=== Testing Seller Businesses API ===")
        
        # Since seller_id is not returned in API responses, we'll get it from database
        try:
            import asyncio
            from motor.motor_asyncio import AsyncIOMotorClient
            import os
            from dotenv import load_dotenv
            
            load_dotenv('/app/backend/.env')
            
            async def get_seller_id():
                client = AsyncIOMotorClient(os.environ['MONGO_URL'])
                db = client[os.environ['DB_NAME']]
                business = await db.business_listings.find_one()
                seller_id = business.get('seller_id') if business else None
                client.close()
                return seller_id
            
            seller_id = asyncio.run(get_seller_id())
            
            if not seller_id:
                self.log_test("Seller Businesses", False, "Could not get seller_id from database")
                return
            
            # Test getting seller's businesses
            response, success, error = self.make_request("GET", f"/businesses/seller/{seller_id}")
            
            if not success:
                self.log_test("Seller Businesses", False, f"Request failed: {error}")
            elif response.status_code == 200:
                try:
                    seller_businesses = response.json()
                    
                    if isinstance(seller_businesses, list):
                        if len(seller_businesses) > 0:
                            self.log_test("Seller Businesses", True, 
                                        f"Retrieved {len(seller_businesses)} businesses for seller")
                        else:
                            self.log_test("Seller Businesses", True, "No businesses found for seller (valid response)")
                    else:
                        self.log_test("Seller Businesses", False, "Response is not a list")
                        
                except json.JSONDecodeError:
                    self.log_test("Seller Businesses", False, "Invalid JSON response")
            else:
                self.log_test("Seller Businesses", False, f"Status code: {response.status_code}")
                
        except ImportError:
            self.log_test("Seller Businesses", False, "Could not import required modules for database access")
    
    def test_payment_processing(self):
        """Test payment processing API"""
        print("\n=== Testing Payment Processing API ===")
        
        if not self.created_business_ids:
            self.log_test("Payment Processing", False, "No created businesses available for testing")
            return
        
        business_id = self.created_business_ids[0]
        
        # Test 1: Process payment for valid business
        payment_data = {
            "business_id": business_id,
            "payment_type": "listing_fee",
            "amount": 99.0
        }
        
        # Try payment multiple times to test the 90% success rate
        payment_attempts = []
        for attempt in range(5):
            response, success, error = self.make_request("POST", f"/businesses/{business_id}/payment", data=payment_data)
            
            if success and response.status_code == 200:
                try:
                    payment_result = response.json()
                    payment_attempts.append(payment_result.get('status'))
                    
                    # Verify payment response structure
                    required_fields = ['payment_id', 'status', 'business_id', 'amount', 'message']
                    missing_fields = [field for field in required_fields if field not in payment_result]
                    
                    if not missing_fields:
                        if payment_result.get('status') == 'success':
                            # Verify business status changed to active
                            business_response, business_success, _ = self.make_request("GET", f"/businesses/{business_id}")
                            if business_success and business_response.status_code == 200:
                                business = business_response.json()
                                if business.get('status') == 'active':
                                    self.log_test(f"Payment Processing (Attempt {attempt + 1})", True, 
                                                f"Payment successful, business status changed to active")
                                    break
                                else:
                                    self.log_test(f"Payment Processing (Attempt {attempt + 1})", False, 
                                                f"Payment successful but business status is {business.get('status')}")
                            else:
                                self.log_test(f"Payment Processing (Attempt {attempt + 1})", False, 
                                            "Could not verify business status after payment")
                        else:
                            self.log_test(f"Payment Processing (Attempt {attempt + 1})", True, 
                                        f"Payment failed as expected (simulated failure): {payment_result.get('message')}")
                    else:
                        self.log_test(f"Payment Processing (Attempt {attempt + 1})", False, 
                                    f"Missing payment response fields: {missing_fields}")
                        
                except json.JSONDecodeError:
                    self.log_test(f"Payment Processing (Attempt {attempt + 1})", False, "Invalid JSON response")
            else:
                self.log_test(f"Payment Processing (Attempt {attempt + 1})", False, 
                            f"Request failed: {error if not success else response.status_code}")
        
        # Analyze success rate
        successful_payments = payment_attempts.count('success')
        total_attempts = len(payment_attempts)
        
        if total_attempts > 0:
            success_rate = (successful_payments / total_attempts) * 100
            if 70 <= success_rate <= 100:  # Allow some variance in the 90% simulation
                self.log_test("Payment Success Rate Simulation", True, 
                            f"Success rate: {success_rate:.1f}% ({successful_payments}/{total_attempts})")
            else:
                self.log_test("Payment Success Rate Simulation", False, 
                            f"Unexpected success rate: {success_rate:.1f}% (expected ~90%)")
        
        # Test 2: Test payment for non-existent business
        fake_business_id = "non-existent-business-id"
        response, success, error = self.make_request("POST", f"/businesses/{fake_business_id}/payment", data=payment_data)
        
        if success and response.status_code == 404:
            self.log_test("Payment Processing (404 Test)", True, "Properly returned 404 for non-existent business")
        else:
            self.log_test("Payment Processing (404 Test)", False, 
                        f"Expected 404, got: {response.status_code if success else error}")
    
    def test_integration_workflow(self):
        """Test complete integration workflow: create → update → pay → verify active"""
        print("\n=== Testing Integration Workflow ===")
        
        # Step 1: Create a new business
        workflow_business_data = {
            "title": "Integration Test Restaurant",
            "description": "Test restaurant for integration workflow",
            "industry": "food_service",
            "region": "chisinau",
            "annual_revenue": 300000.0,
            "ebitda": 45000.0,
            "asking_price": 450000.0,
            "risk_grade": "B",
            "seller_name": "Test Workflow Seller",
            "seller_email": "workflow@example.com",
            "reason_for_sale": "Integration testing",
            "growth_opportunities": "Test expansion",
            "financial_data": [
                {
                    "year": 2023,
                    "revenue": 300000,
                    "profit_loss": 36000,
                    "ebitda": 45000,
                    "assets": 400000,
                    "liabilities": 200000,
                    "cash_flow": 42000
                }
            ],
            "key_metrics": {
                "employees": 12,
                "years_in_business": 5
            }
        }
        
        response, success, error = self.make_request("POST", "/businesses", data=workflow_business_data)
        
        if not success or response.status_code != 200:
            self.log_test("Integration Workflow", False, f"Step 1 (Create) failed: {error if not success else response.status_code}")
            return
        
        try:
            created_business = response.json()
            workflow_business_id = created_business['id']
            
            if created_business.get('status') != 'draft':
                self.log_test("Integration Workflow", False, f"Step 1: Expected draft status, got {created_business.get('status')}")
                return
            
            # Step 2: Update the business
            update_data = {
                "title": "Integration Test Restaurant - Updated",
                "status": "pending_payment"
            }
            
            response, success, error = self.make_request("PUT", f"/businesses/{workflow_business_id}", data=update_data)
            
            if not success or response.status_code != 200:
                self.log_test("Integration Workflow", False, f"Step 2 (Update) failed: {error if not success else response.status_code}")
                return
            
            updated_business = response.json()
            if updated_business.get('status') != 'pending_payment':
                self.log_test("Integration Workflow", False, f"Step 2: Expected pending_payment status, got {updated_business.get('status')}")
                return
            
            # Step 3: Process payment (try multiple times until success)
            payment_data = {
                "business_id": workflow_business_id,
                "payment_type": "listing_fee",
                "amount": 99.0
            }
            
            payment_successful = False
            for attempt in range(10):  # Try up to 10 times to get a successful payment
                response, success, error = self.make_request("POST", f"/businesses/{workflow_business_id}/payment", data=payment_data)
                
                if success and response.status_code == 200:
                    payment_result = response.json()
                    if payment_result.get('status') == 'success':
                        payment_successful = True
                        break
                else:
                    self.log_test("Integration Workflow", False, f"Step 3 (Payment) failed: {error if not success else response.status_code}")
                    return
            
            if not payment_successful:
                self.log_test("Integration Workflow", False, "Step 3: Could not achieve successful payment after 10 attempts")
                return
            
            # Step 4: Verify business is now active and appears in public listings
            response, success, error = self.make_request("GET", f"/businesses/{workflow_business_id}")
            
            if not success or response.status_code != 200:
                self.log_test("Integration Workflow", False, f"Step 4 (Verify) failed: {error if not success else response.status_code}")
                return
            
            final_business = response.json()
            if final_business.get('status') != 'active':
                self.log_test("Integration Workflow", False, f"Step 4: Expected active status, got {final_business.get('status')}")
                return
            
            # Step 5: Verify business appears in public listings
            response, success, error = self.make_request("GET", "/businesses")
            
            if success and response.status_code == 200:
                public_businesses = response.json()
                found_in_public = any(b.get('id') == workflow_business_id for b in public_businesses)
                
                if found_in_public:
                    self.log_test("Integration Workflow", True, 
                                "Complete workflow successful: create → update → pay → active → public listing")
                else:
                    self.log_test("Integration Workflow", False, "Business not found in public listings after payment")
            else:
                self.log_test("Integration Workflow", False, f"Step 5 (Public listing check) failed: {error if not success else response.status_code}")
                
        except (json.JSONDecodeError, KeyError) as e:
            self.log_test("Integration Workflow", False, f"JSON parsing error: {str(e)}")
    
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Moldovan Business Marketplace Backend API Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 80)
        
        # Run existing tests first
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
        
        # Run new Business Creation/Update and Payment Processing tests
        self.test_business_creation()
        self.test_business_update()
        self.test_seller_businesses()
        self.test_payment_processing()
        self.test_integration_workflow()
        
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