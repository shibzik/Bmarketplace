import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Helper function to format currency
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

// Helper function to format industry names
const formatIndustryName = (industry) => {
  return industry.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

// Helper function to format region names
const formatRegionName = (region) => {
  return region.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

// Helper function to get risk grade color
const getRiskGradeColor = (grade) => {
  switch (grade) {
    case 'A': return 'bg-green-100 text-green-800';
    case 'B': return 'bg-blue-100 text-blue-800';
    case 'C': return 'bg-yellow-100 text-yellow-800';
    case 'D': return 'bg-orange-100 text-orange-800';
    case 'E': return 'bg-red-100 text-red-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

// Business Card Component
const BusinessCard = ({ business, onClick }) => {
  return (
    <div 
      className={`bg-white rounded-lg shadow-md border hover:shadow-lg transition-shadow cursor-pointer ${
        business.featured ? 'border-blue-500 border-2' : 'border-gray-200'
      }`}
      onClick={() => onClick(business.id)}
    >
      {business.featured && (
        <div className="bg-blue-500 text-white text-xs px-2 py-1 rounded-t-lg">
          FEATURED
        </div>
      )}
      
      <div className="p-6">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-xl font-semibold text-gray-900 line-clamp-2">{business.title}</h3>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskGradeColor(business.risk_grade)}`}>
            Risk: {business.risk_grade}
          </span>
        </div>
        
        <div className="space-y-2 mb-4">
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Industry:</span>
            <span className="text-sm font-medium">{formatIndustryName(business.industry)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Region:</span>
            <span className="text-sm font-medium">{formatRegionName(business.region)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Annual Revenue:</span>
            <span className="text-sm font-medium text-green-600">{formatCurrency(business.annual_revenue)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">EBITDA:</span>
            <span className="text-sm font-medium text-green-600">{formatCurrency(business.ebitda)}</span>
          </div>
        </div>
        
        <div className="border-t pt-4 mb-4">
          <div className="flex justify-between items-center">
            <span className="text-lg font-bold text-gray-900">Asking Price:</span>
            <span className="text-lg font-bold text-blue-600">{formatCurrency(business.asking_price)}</span>
          </div>
        </div>
        
        <div className="flex justify-between text-xs text-gray-500">
          <span>{business.views} views</span>
          <span>{business.inquiries} inquiries</span>
        </div>
      </div>
    </div>
  );
};

// Business Detail Modal
const BusinessDetailModal = ({ business, onClose }) => {
  if (!business) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-start mb-6">
            <h2 className="text-2xl font-bold text-gray-900">{business.title}</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-3">Business Overview</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Industry:</span>
                  <span className="font-medium">{formatIndustryName(business.industry)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Region:</span>
                  <span className="font-medium">{formatRegionName(business.region)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Risk Grade:</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskGradeColor(business.risk_grade)}`}>
                    {business.risk_grade}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Seller:</span>
                  <span className="font-medium">{business.seller_name}</span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-3">Financial Summary</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Annual Revenue:</span>
                  <span className="font-medium text-green-600">{formatCurrency(business.annual_revenue)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">EBITDA:</span>
                  <span className="font-medium text-green-600">{formatCurrency(business.ebitda)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Asking Price:</span>
                  <span className="font-medium text-blue-600 text-lg">{formatCurrency(business.asking_price)}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-3">Description</h3>
            <p className="text-gray-700">{business.description}</p>
          </div>
          
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-3">Reason for Sale</h3>
            <p className="text-gray-700">{business.reason_for_sale}</p>
          </div>
          
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-3">Growth Opportunities</h3>
            <p className="text-gray-700">{business.growth_opportunities}</p>
          </div>
          
          {business.key_metrics && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-3">Key Metrics</h3>
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(business.key_metrics).map(([key, value]) => (
                  <div key={key} className="flex justify-between">
                    <span className="text-gray-600">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span>
                    <span className="font-medium">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {business.financial_data && business.financial_data.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-3">3-Year Financial Data</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="text-left p-2">Year</th>
                      <th className="text-right p-2">Revenue</th>
                      <th className="text-right p-2">Profit/Loss</th>
                      <th className="text-right p-2">EBITDA</th>
                      <th className="text-right p-2">Cash Flow</th>
                    </tr>
                  </thead>
                  <tbody>
                    {business.financial_data.map((data, index) => (
                      <tr key={index} className="border-t">
                        <td className="p-2 font-medium">{data.year}</td>
                        <td className="text-right p-2">{formatCurrency(data.revenue)}</td>
                        <td className="text-right p-2">{formatCurrency(data.profit_loss)}</td>
                        <td className="text-right p-2">{formatCurrency(data.ebitda)}</td>
                        <td className="text-right p-2">{formatCurrency(data.cash_flow)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          
          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">Interested in this business?</h3>
            <p className="text-blue-800 text-sm mb-4">
              Subscribe to access seller contact information and detailed due diligence documents.
            </p>
            <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
              Subscribe to Contact Seller
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Filter Component
const BusinessFilters = ({ filters, onFilterChange, industries, regions, riskGrades }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md mb-6">
      <h3 className="text-lg font-semibold mb-4">Filter Businesses</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Industry</label>
          <select
            value={filters.industry || ""}
            onChange={(e) => onFilterChange("industry", e.target.value || null)}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Industries</option>
            {industries.map(industry => (
              <option key={industry.value} value={industry.value}>{industry.label}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Region</label>
          <select
            value={filters.region || ""}
            onChange={(e) => onFilterChange("region", e.target.value || null)}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Regions</option>
            {regions.map(region => (
              <option key={region.value} value={region.value}>{region.label}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Risk Grade</label>
          <select
            value={filters.risk_grade || ""}
            onChange={(e) => onFilterChange("risk_grade", e.target.value || null)}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Risk Grades</option>
            {riskGrades.map(grade => (
              <option key={grade.value} value={grade.value}>{grade.label}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
          <select
            value={filters.sort_by || "created_at"}
            onChange={(e) => onFilterChange("sort_by", e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="created_at">Date Listed</option>
            <option value="asking_price">Price</option>
            <option value="annual_revenue">Revenue</option>
            <option value="views">Views</option>
          </select>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Min Revenue</label>
          <input
            type="number"
            value={filters.min_revenue || ""}
            onChange={(e) => onFilterChange("min_revenue", e.target.value ? parseFloat(e.target.value) : null)}
            placeholder="0"
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Max Revenue</label>
          <input
            type="number"
            value={filters.max_revenue || ""}
            onChange={(e) => onFilterChange("max_revenue", e.target.value ? parseFloat(e.target.value) : null)}
            placeholder="No limit"
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [businesses, setBusinesses] = useState([]);
  const [selectedBusiness, setSelectedBusiness] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    industry: null,
    region: null,
    min_revenue: null,
    max_revenue: null,
    risk_grade: null,
    sort_by: "created_at"
  });
  const [industries, setIndustries] = useState([]);
  const [regions, setRegions] = useState([]);
  const [riskGrades, setRiskGrades] = useState([]);

  useEffect(() => {
    fetchBusinesses();
    fetchFilterOptions();
  }, [filters]);

  const fetchBusinesses = async () => {
    try {
      setLoading(true);
      const queryParams = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== "") {
          queryParams.append(key, value);
        }
      });
      
      const response = await axios.get(`${API}/businesses?${queryParams}`);
      setBusinesses(response.data);
    } catch (error) {
      console.error("Error fetching businesses:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFilterOptions = async () => {
    try {
      const [industriesRes, regionsRes, riskGradesRes] = await Promise.all([
        axios.get(`${API}/industries`),
        axios.get(`${API}/regions`),
        axios.get(`${API}/risk-grades`)
      ]);
      
      setIndustries(industriesRes.data);
      setRegions(regionsRes.data);
      setRiskGrades(riskGradesRes.data);
    } catch (error) {
      console.error("Error fetching filter options:", error);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleBusinessClick = async (businessId) => {
    try {
      const response = await axios.get(`${API}/businesses/${businessId}`);
      setSelectedBusiness(response.data);
    } catch (error) {
      console.error("Error fetching business details:", error);
    }
  };

  const handleCloseModal = () => {
    setSelectedBusiness(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">MoldovaBiz</h1>
              <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                Marketplace
              </span>
            </div>
            <nav className="flex space-x-6">
              <a href="#" className="text-gray-700 hover:text-blue-600">Browse Businesses</a>
              <a href="#" className="text-gray-700 hover:text-blue-600">List Your Business</a>
              <a href="#" className="text-gray-700 hover:text-blue-600">Subscribe</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section 
        className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-20"
        style={{
          backgroundImage: `linear-gradient(rgba(37, 99, 235, 0.8), rgba(29, 78, 216, 0.8)), url('https://images.unsplash.com/photo-1521791136064-7986c2920216')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Moldova's Premier Business Marketplace
          </h2>
          <p className="text-xl md:text-2xl mb-8 opacity-90">
            Discover profitable businesses for sale with transparent financial data and professional due diligence
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
              Browse Businesses
            </button>
            <button className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors">
              List Your Business
            </button>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <BusinessFilters
          filters={filters}
          onFilterChange={handleFilterChange}
          industries={industries}
          regions={regions}
          riskGrades={riskGrades}
        />

        {/* Business Grid */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-900">
              Available Businesses ({businesses.length})
            </h2>
            <div className="text-sm text-gray-600">
              Showing {businesses.length} businesses
            </div>
          </div>
          
          {loading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {businesses.map(business => (
                <BusinessCard
                  key={business.id}
                  business={business}
                  onClick={handleBusinessClick}
                />
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">MoldovaBiz</h3>
              <p className="text-gray-400">
                Professional marketplace for buying and selling Moldovan businesses with transparent financial data.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">For Buyers</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Browse Businesses</a></li>
                <li><a href="#" className="hover:text-white">Subscription Plans</a></li>
                <li><a href="#" className="hover:text-white">Due Diligence Guide</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">For Sellers</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">List Your Business</a></li>
                <li><a href="#" className="hover:text-white">Pricing</a></li>
                <li><a href="#" className="hover:text-white">Seller Guide</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Terms of Service</a></li>
                <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white">Moldovan Compliance</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 MoldovaBiz. All rights reserved. Compliant with Moldovan Law 133/2011.</p>
          </div>
        </div>
      </footer>

      {/* Business Detail Modal */}
      {selectedBusiness && (
        <BusinessDetailModal
          business={selectedBusiness}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
}

export default App;