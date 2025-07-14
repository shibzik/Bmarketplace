import React, { useState, useEffect, useContext, createContext } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Verify token and get user info
      fetchUserInfo();
    }
  }, [token]);

  const fetchUserInfo = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user info:', error);
      logout();
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token, user } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(user);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      return { success: true, user };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  const register = async (email, password, name, role) => {
    try {
      const response = await axios.post(`${API}/auth/register`, {
        email,
        password,
        name,
        role
      });
      return { success: true, user: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Registration failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, fetchUserInfo }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

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

// Authentication Modal Component
const AuthModal = ({ isOpen, onClose, mode, onSwitchMode }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    role: 'buyer'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const { login, register } = useAuth();

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      if (mode === 'login') {
        const result = await login(formData.email, formData.password);
        if (result.success) {
          onClose();
          setSuccess('Login successful!');
        } else {
          setError(result.error);
        }
      } else {
        const result = await register(formData.email, formData.password, formData.name, formData.role);
        if (result.success) {
          setSuccess('Registration successful! Please check your email for verification.');
          setTimeout(() => onSwitchMode('login'), 2000);
        } else {
          setError(result.error);
        }
      }
    } catch (error) {
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            {mode === 'login' ? 'Login' : 'Sign Up'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => handleInputChange('password', e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          {mode === 'register' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">I am a</label>
              <select
                value={formData.role}
                onChange={(e) => handleInputChange('role', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="buyer">Buyer (looking to buy a business)</option>
                <option value="seller">Seller (looking to sell a business)</option>
              </select>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Please wait...' : (mode === 'login' ? 'Login' : 'Sign Up')}
          </button>
        </form>

        <div className="mt-4 text-center">
          <button
            onClick={() => onSwitchMode(mode === 'login' ? 'register' : 'login')}
            className="text-blue-600 hover:text-blue-800"
          >
            {mode === 'login' 
              ? "Don't have an account? Sign up" 
              : "Already have an account? Login"}
          </button>
        </div>
      </div>
    </div>
  );
};

// Subscription Modal Component
const SubscriptionModal = ({ isOpen, onClose, onSubscriptionSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [planType, setPlanType] = useState('monthly');
  const { user } = useAuth();

  const handleSubscriptionPayment = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await axios.post(`${API}/subscription/payment`, {
        user_id: user.id,
        plan_type: planType,
        amount: planType === 'monthly' ? 29.99 : 299.99
      });
      
      if (response.data.status === 'success') {
        onSubscriptionSuccess(response.data);
      } else {
        setError(response.data.message || 'Payment failed');
      }
    } catch (error) {
      setError('Payment failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Subscribe to Access</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>
        
        <div className="mb-6">
          <p className="text-gray-600 mb-4">
            Subscribe to access seller contact information and detailed business documents.
          </p>
          
          <div className="space-y-4">
            <div className={`border-2 rounded-lg p-4 cursor-pointer ${
              planType === 'monthly' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
            }`} onClick={() => setPlanType('monthly')}>
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-semibold">Monthly Plan</h3>
                  <p className="text-sm text-gray-600">Access to all business listings</p>
                </div>
                <div className="text-right">
                  <span className="text-2xl font-bold">$29.99</span>
                  <span className="text-gray-600">/month</span>
                </div>
              </div>
            </div>
            
            <div className={`border-2 rounded-lg p-4 cursor-pointer ${
              planType === 'annual' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
            }`} onClick={() => setPlanType('annual')}>
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-semibold">Annual Plan</h3>
                  <p className="text-sm text-gray-600">Save 17% with annual billing</p>
                </div>
                <div className="text-right">
                  <span className="text-2xl font-bold">$299.99</span>
                  <span className="text-gray-600">/year</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}
        
        <div className="flex space-x-4">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSubscriptionPayment}
            disabled={loading}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Processing...' : `Subscribe ${planType === 'monthly' ? '$29.99' : '$299.99'}`}
          </button>
        </div>
        
        <div className="mt-4 text-xs text-gray-500 text-center">
          <p>This is a mock payment system for demonstration purposes.</p>
          <p>90% success rate simulation for testing.</p>
        </div>
      </div>
    </div>
  );
};

// File Upload Component
const FileUploadSection = ({ businessId, documents, onDocumentUploaded, onDocumentDeleted }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setError('Only PDF files are allowed');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    if (documents.length >= 10) {
      setError('Maximum 10 documents allowed per listing');
      return;
    }

    try {
      setUploading(true);
      setError('');

      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API}/businesses/${businessId}/documents`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      onDocumentUploaded(response.data);
    } catch (error) {
      setError('Upload failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDocument = async (documentId) => {
    try {
      await axios.delete(`${API}/businesses/${businessId}/documents/${documentId}`);
      onDocumentDeleted(documentId);
    } catch (error) {
      setError('Delete failed: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Business Documents</h3>
        <span className="text-sm text-gray-600">{documents.length}/10 documents</span>
      </div>

      {error && (
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {documents.length < 10 && (
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            disabled={uploading}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className={`cursor-pointer ${uploading ? 'opacity-50' : ''}`}
          >
            {uploading ? (
              <div className="text-gray-600">Uploading...</div>
            ) : (
              <div>
                <div className="text-gray-600 mb-2">
                  Click to upload a PDF document
                </div>
                <div className="text-sm text-gray-500">
                  Maximum 10MB, PDF files only
                </div>
              </div>
            )}
          </label>
        </div>
      )}

      {documents.length > 0 && (
        <div className="space-y-2">
          {documents.map((doc) => (
            <div key={doc.id} className="flex justify-between items-center p-3 border rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="text-red-600">📄</div>
                <div>
                  <div className="font-medium">{doc.filename}</div>
                  <div className="text-sm text-gray-500">
                    {(doc.file_size / 1024 / 1024).toFixed(2)} MB
                  </div>
                </div>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleDeleteDocument(doc.id)}
                  className="text-red-600 hover:text-red-800"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Business Listing Form Component
const BusinessListingForm = ({ onClose, onSuccess }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    industry: '',
    region: '',
    annual_revenue: '',
    ebitda: '',
    asking_price: '',
    risk_grade: '',
    seller_name: '',
    seller_email: '',
    reason_for_sale: '',
    growth_opportunities: '',
    financial_data: [
      { year: new Date().getFullYear(), revenue: '', profit_loss: '', ebitda: '', assets: '', liabilities: '', cash_flow: '' },
      { year: new Date().getFullYear() - 1, revenue: '', profit_loss: '', ebitda: '', assets: '', liabilities: '', cash_flow: '' },
      { year: new Date().getFullYear() - 2, revenue: '', profit_loss: '', ebitda: '', assets: '', liabilities: '', cash_flow: '' }
    ],
    key_metrics: {}
  });
  const [industries, setIndustries] = useState([]);
  const [regions, setRegions] = useState([]);
  const [riskGrades, setRiskGrades] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchFilterOptions();
  }, []);

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

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleFinancialDataChange = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      financial_data: prev.financial_data.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  const handleKeyMetricChange = (key, value) => {
    setFormData(prev => ({
      ...prev,
      key_metrics: {
        ...prev.key_metrics,
        [key]: value
      }
    }));
  };

  const validateStep = (step) => {
    switch (step) {
      case 1:
        return formData.title && formData.description && formData.industry && formData.region;
      case 2:
        return formData.annual_revenue && formData.ebitda && formData.asking_price && formData.risk_grade;
      case 3:
        return formData.seller_name && formData.seller_email && formData.reason_for_sale;
      case 4:
        return formData.financial_data.every(item => item.revenue && item.profit_loss && item.ebitda);
      default:
        return true;
    }
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => prev + 1);
      setError('');
    } else {
      setError('Please fill in all required fields');
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => prev - 1);
    setError('');
  };

  const handleSaveDraft = async () => {
    try {
      setLoading(true);
      setError('');
      
      const payload = {
        ...formData,
        annual_revenue: parseFloat(formData.annual_revenue),
        ebitda: parseFloat(formData.ebitda),
        asking_price: parseFloat(formData.asking_price),
        financial_data: formData.financial_data.map(item => ({
          ...item,
          revenue: parseFloat(item.revenue) || 0,
          profit_loss: parseFloat(item.profit_loss) || 0,
          ebitda: parseFloat(item.ebitda) || 0,
          assets: parseFloat(item.assets) || 0,
          liabilities: parseFloat(item.liabilities) || 0,
          cash_flow: parseFloat(item.cash_flow) || 0
        })),
        status: 'draft'
      };

      const response = await axios.post(`${API}/businesses`, payload);
      onSuccess(response.data, 'draft');
    } catch (error) {
      setError('Error saving draft: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async () => {
    try {
      setLoading(true);
      setError('');
      
      const payload = {
        ...formData,
        annual_revenue: parseFloat(formData.annual_revenue),
        ebitda: parseFloat(formData.ebitda),
        asking_price: parseFloat(formData.asking_price),
        financial_data: formData.financial_data.map(item => ({
          ...item,
          revenue: parseFloat(item.revenue) || 0,
          profit_loss: parseFloat(item.profit_loss) || 0,
          ebitda: parseFloat(item.ebitda) || 0,
          assets: parseFloat(item.assets) || 0,
          liabilities: parseFloat(item.liabilities) || 0,
          cash_flow: parseFloat(item.cash_flow) || 0
        })),
        status: 'pending_payment'
      };

      const response = await axios.post(`${API}/businesses`, payload);
      onSuccess(response.data, 'publish');
    } catch (error) {
      setError('Error creating listing: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Business Information</h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Business Title *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your business title"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
              <textarea
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                rows="4"
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Describe your business..."
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Industry *</label>
                <select
                  value={formData.industry}
                  onChange={(e) => handleInputChange('industry', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select Industry</option>
                  {industries.map(industry => (
                    <option key={industry.value} value={industry.value}>{industry.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Region *</label>
                <select
                  value={formData.region}
                  onChange={(e) => handleInputChange('region', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select Region</option>
                  {regions.map(region => (
                    <option key={region.value} value={region.value}>{region.label}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        );
      case 2:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Financial Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Annual Revenue (USD) *</label>
                <input
                  type="number"
                  value={formData.annual_revenue}
                  onChange={(e) => handleInputChange('annual_revenue', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="1000000"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">EBITDA (USD) *</label>
                <input
                  type="number"
                  value={formData.ebitda}
                  onChange={(e) => handleInputChange('ebitda', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="200000"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Asking Price (USD) *</label>
                <input
                  type="number"
                  value={formData.asking_price}
                  onChange={(e) => handleInputChange('asking_price', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="1500000"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Risk Grade *</label>
                <select
                  value={formData.risk_grade}
                  onChange={(e) => handleInputChange('risk_grade', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select Risk Grade</option>
                  {riskGrades.map(grade => (
                    <option key={grade.value} value={grade.value}>{grade.label}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        );
      case 3:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Seller Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Your Name *</label>
                <input
                  type="text"
                  value={formData.seller_name}
                  onChange={(e) => handleInputChange('seller_name', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="John Doe"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email Address *</label>
                <input
                  type="email"
                  value={formData.seller_email}
                  onChange={(e) => handleInputChange('seller_email', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="john@example.com"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Reason for Sale *</label>
              <textarea
                value={formData.reason_for_sale}
                onChange={(e) => handleInputChange('reason_for_sale', e.target.value)}
                rows="3"
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Why are you selling this business?"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Growth Opportunities</label>
              <textarea
                value={formData.growth_opportunities}
                onChange={(e) => handleInputChange('growth_opportunities', e.target.value)}
                rows="3"
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="What are the potential growth opportunities?"
              />
            </div>
          </div>
        );
      case 4:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">3-Year Financial Data</h3>
            {formData.financial_data.map((yearData, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <h4 className="font-semibold mb-3">Year {yearData.year}</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Revenue *</label>
                    <input
                      type="number"
                      value={yearData.revenue}
                      onChange={(e) => handleFinancialDataChange(index, 'revenue', e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Profit/Loss *</label>
                    <input
                      type="number"
                      value={yearData.profit_loss}
                      onChange={(e) => handleFinancialDataChange(index, 'profit_loss', e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">EBITDA *</label>
                    <input
                      type="number"
                      value={yearData.ebitda}
                      onChange={(e) => handleFinancialDataChange(index, 'ebitda', e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Cash Flow</label>
                    <input
                      type="number"
                      value={yearData.cash_flow}
                      onChange={(e) => handleFinancialDataChange(index, 'cash_flow', e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        );
      case 5:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Key Metrics</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Number of Employees</label>
                <input
                  type="number"
                  value={formData.key_metrics.employees || ''}
                  onChange={(e) => handleKeyMetricChange('employees', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Years in Business</label>
                <input
                  type="number"
                  value={formData.key_metrics.years_in_business || ''}
                  onChange={(e) => handleKeyMetricChange('years_in_business', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Locations</label>
                <input
                  type="number"
                  value={formData.key_metrics.locations || ''}
                  onChange={(e) => handleKeyMetricChange('locations', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Additional Info</label>
                <input
                  type="text"
                  value={formData.key_metrics.additional_info || ''}
                  onChange={(e) => handleKeyMetricChange('additional_info', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Any additional key metrics"
                />
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">List Your Business</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
          </div>
          
          {/* Progress Bar */}
          <div className="mb-6">
            <div className="flex justify-between mb-2">
              {[1, 2, 3, 4, 5].map((step) => (
                <div
                  key={step}
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    step <= currentStep
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {step}
                </div>
              ))}
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(currentStep / 5) * 100}%` }}
              ></div>
            </div>
          </div>
          
          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}
          
          {renderStep()}
          
          <div className="flex justify-between mt-8">
            <button
              onClick={handlePrevious}
              disabled={currentStep === 1}
              className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            <div className="flex space-x-4">
              {currentStep === 5 ? (
                <>
                  <button
                    onClick={handleSaveDraft}
                    disabled={loading}
                    className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                  >
                    {loading ? 'Saving...' : 'Save Draft'}
                  </button>
                  <button
                    onClick={handlePublish}
                    disabled={loading}
                    className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {loading ? 'Publishing...' : 'Publish Listing'}
                  </button>
                </>
              ) : (
                <button
                  onClick={handleNext}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Next
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Payment Modal Component
const PaymentModal = ({ business, onClose, onPaymentSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('card');

  const handlePayment = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await axios.post(`${API}/businesses/${business.id}/payment`, {
        business_id: business.id,
        payment_type: 'listing_fee',
        amount: 99.0
      });
      
      if (response.data.status === 'success') {
        onPaymentSuccess(response.data);
      } else {
        setError(response.data.message || 'Payment failed');
      }
    } catch (error) {
      setError('Payment failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-900">Complete Payment</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-xl"
            >
              ×
            </button>
          </div>
          
          <div className="mb-6">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Listing Fee</h3>
              <p className="text-sm text-gray-600 mb-2">
                Business: {business.title}
              </p>
              <div className="flex justify-between items-center">
                <span className="text-lg font-semibold">Total:</span>
                <span className="text-lg font-bold text-blue-600">$99.00</span>
              </div>
            </div>
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Payment Method</label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="card"
                  checked={paymentMethod === 'card'}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                  className="mr-2"
                />
                Credit/Debit Card
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="bank"
                  checked={paymentMethod === 'bank'}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                  className="mr-2"
                />
                Bank Transfer
              </label>
            </div>
          </div>
          
          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}
          
          <div className="flex space-x-4">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handlePayment}
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Processing...' : 'Pay $99.00'}
            </button>
          </div>
          
          <div className="mt-4 text-xs text-gray-500 text-center">
            <p>This is a mock payment system for demonstration purposes.</p>
            <p>90% success rate simulation for testing.</p>
          </div>
        </div>
      </div>
    </div>
  );
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
  const { user } = useAuth();
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  
  if (!business) return null;

  const isSubscribed = user?.role === 'buyer' && 
                      user?.subscription_status === 'active' && 
                      user?.subscription_expires_at && 
                      new Date(user.subscription_expires_at) > new Date();

  const canViewSellerInfo = user?.role === 'seller' && business.seller_id === user.id || isSubscribed;

  const handleContactSeller = () => {
    if (!user) {
      setShowAuthModal(true);
      return;
    }
    
    if (user.role !== 'buyer') {
      alert('Only buyers can contact sellers');
      return;
    }
    
    if (!isSubscribed) {
      setShowSubscriptionModal(true);
      return;
    }
  };

  const handleSubscriptionSuccess = () => {
    setShowSubscriptionModal(false);
    // Refresh user info to get updated subscription status
    window.location.reload();
  };

  const handleDocumentDownload = async (documentId) => {
    try {
      const response = await axios.get(`${API}/businesses/${business.id}/documents/${documentId}`);
      const { filename, content_type, file_data } = response.data;
      
      // Convert base64 to blob and download
      const byteCharacters = atob(file_data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: content_type });
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download document');
    }
  };

  return (
    <>
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
                  {canViewSellerInfo && business.seller_email && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Email:</span>
                      <span className="font-medium">{business.seller_email}</span>
                    </div>
                  )}
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
            
            {business.documents && business.documents.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-3">Business Documents</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {business.documents.map((doc, index) => (
                    <div key={index} className="flex items-center p-3 border rounded-lg">
                      <div className="text-red-600 mr-3">📄</div>
                      <div className="flex-1">
                        <div className="font-medium">{doc.filename}</div>
                        <div className="text-sm text-gray-500">
                          {(doc.file_size / 1024 / 1024).toFixed(2)} MB
                        </div>
                      </div>
                      {canViewSellerInfo ? (
                        <button
                          onClick={() => handleDocumentDownload(doc.id)}
                          className="text-blue-600 hover:text-blue-800 text-sm"
                        >
                          Download
                        </button>
                      ) : (
                        <span className="text-gray-400 text-sm">Subscription Required</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div className="mt-8 p-4 bg-blue-50 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">Interested in this business?</h3>
              {canViewSellerInfo ? (
                <div>
                  <p className="text-blue-800 text-sm mb-4">
                    You have access to seller contact information and can download all documents.
                  </p>
                  <div className="bg-green-50 p-3 rounded">
                    <p className="text-green-800 font-medium">Contact Information:</p>
                    <p className="text-green-700">Email: {business.seller_email}</p>
                  </div>
                </div>
              ) : (
                <div>
                  <p className="text-blue-800 text-sm mb-4">
                    Subscribe to access seller contact information and detailed due diligence documents.
                  </p>
                  <button 
                    onClick={handleContactSeller}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Subscribe to Contact Seller
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Subscription Modal */}
      {showSubscriptionModal && (
        <SubscriptionModal
          isOpen={showSubscriptionModal}
          onClose={() => setShowSubscriptionModal(false)}
          onSubscriptionSuccess={handleSubscriptionSuccess}
        />
      )}

      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          mode={authMode}
          onSwitchMode={setAuthMode}
        />
      )}
    </>
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
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

// App Content Component
function AppContent() {
  const [businesses, setBusinesses] = useState([]);
  const [selectedBusiness, setSelectedBusiness] = useState(null);
  const [showListingForm, setShowListingForm] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [pendingBusiness, setPendingBusiness] = useState(null);
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
  const [notification, setNotification] = useState(null);
  const { user, logout } = useAuth();

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

  const handleShowListingForm = () => {
    if (!user) {
      setShowAuthModal(true);
      return;
    }
    
    if (user.role !== 'seller') {
      showNotification('error', 'Only sellers can list businesses');
      return;
    }
    
    setShowListingForm(true);
  };

  const handleCloseListingForm = () => {
    setShowListingForm(false);
    setPendingBusiness(null);
  };

  const handleListingSuccess = (business, action) => {
    if (action === 'draft') {
      setShowListingForm(false);
      showNotification('success', 'Draft saved successfully! Please check your email for verification.');
    } else if (action === 'publish') {
      setShowListingForm(false);
      showNotification('success', 'Business created! Please check your email for verification before payment.');
    }
  };

  const handlePaymentSuccess = (paymentData) => {
    setShowPaymentModal(false);
    setPendingBusiness(null);
    showNotification('success', 'Payment successful! Your business listing is now active and visible to buyers.');
    // Refresh business listings
    fetchBusinesses();
  };

  const handleClosePaymentModal = () => {
    setShowPaymentModal(false);
    setPendingBusiness(null);
  };

  const showNotification = (type, message) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  const handleAuthSuccess = () => {
    setShowAuthModal(false);
    showNotification('success', 'Welcome to MoldovaBiz!');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Notification */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
          notification.type === 'success' ? 'bg-green-100 border border-green-400 text-green-700' : 
          'bg-red-100 border border-red-400 text-red-700'
        }`}>
          {notification.message}
        </div>
      )}

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
            <nav className="flex items-center space-x-6">
              <a href="#" className="text-gray-700 hover:text-blue-600">Browse Businesses</a>
              <button 
                onClick={handleShowListingForm}
                className="text-gray-700 hover:text-blue-600"
              >
                List Your Business
              </button>
              {user ? (
                <div className="flex items-center space-x-4">
                  <span className="text-gray-700">
                    Welcome, {user.name}
                    {user.role === 'buyer' && user.subscription_status === 'active' && (
                      <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                        Subscribed
                      </span>
                    )}
                  </span>
                  <button
                    onClick={logout}
                    className="text-gray-700 hover:text-blue-600"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  Sign In
                </button>
              )}
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
            <button 
              onClick={handleShowListingForm}
              className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors"
            >
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
                <li><button onClick={handleShowListingForm} className="hover:text-white">List Your Business</button></li>
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

      {/* Business Listing Form */}
      {showListingForm && (
        <BusinessListingForm
          onClose={handleCloseListingForm}
          onSuccess={handleListingSuccess}
        />
      )}

      {/* Payment Modal */}
      {showPaymentModal && pendingBusiness && (
        <PaymentModal
          business={pendingBusiness}
          onClose={handleClosePaymentModal}
          onPaymentSuccess={handlePaymentSuccess}
        />
      )}

      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          mode={authMode}
          onSwitchMode={setAuthMode}
        />
      )}
    </div>
  );
}

export default App;