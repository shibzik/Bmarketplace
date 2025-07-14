from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class IndustryType(str, Enum):
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    FOOD_SERVICE = "food_service"
    TECHNOLOGY = "technology"
    AGRICULTURE = "agriculture"
    CONSTRUCTION = "construction"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    FINANCE = "finance"
    TRANSPORTATION = "transportation"

class RegionType(str, Enum):
    CHISINAU = "chisinau"
    BALTI = "balti"
    TIRASPOL = "tiraspol"
    CAHUL = "cahul"
    UNGHENI = "ungheni"
    SOROCA = "soroca"
    ORHEI = "orhei"
    COMRAT = "comrat"

class RiskGrade(str, Enum):
    A = "A"  # Low risk
    B = "B"  # Medium-low risk
    C = "C"  # Medium risk
    D = "D"  # Medium-high risk
    E = "E"  # High risk

class BusinessStatus(str, Enum):
    DRAFT = "draft"
    PENDING_EMAIL_VERIFICATION = "pending_email_verification"
    PENDING_PAYMENT = "pending_payment"
    ACTIVE = "active"
    PENDING = "pending"
    SOLD = "sold"
    WITHDRAWN = "withdrawn"

class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING = "pending"

# Models
class FinancialData(BaseModel):
    year: int
    revenue: float
    profit_loss: float
    ebitda: float
    assets: float
    liabilities: float
    cash_flow: float

class BusinessListing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    industry: IndustryType
    region: RegionType
    annual_revenue: float
    ebitda: float
    asking_price: float
    risk_grade: RiskGrade
    status: BusinessStatus = BusinessStatus.ACTIVE
    seller_id: str
    seller_name: str
    seller_email: str
    reason_for_sale: str
    growth_opportunities: str
    financial_data: List[FinancialData]
    key_metrics: dict
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    views: int = 0
    inquiries: int = 0
    featured: bool = False
    
class BusinessListingCreate(BaseModel):
    title: str
    description: str
    industry: IndustryType
    region: RegionType
    annual_revenue: float
    ebitda: float
    asking_price: float
    risk_grade: RiskGrade
    seller_name: str
    seller_email: str
    reason_for_sale: str
    growth_opportunities: str
    financial_data: List[FinancialData]
    key_metrics: dict
    status: BusinessStatus = BusinessStatus.DRAFT

class BusinessListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[IndustryType] = None
    region: Optional[RegionType] = None
    annual_revenue: Optional[float] = None
    ebitda: Optional[float] = None
    asking_price: Optional[float] = None
    risk_grade: Optional[RiskGrade] = None
    seller_name: Optional[str] = None
    seller_email: Optional[str] = None
    reason_for_sale: Optional[str] = None
    growth_opportunities: Optional[str] = None
    financial_data: Optional[List[FinancialData]] = None
    key_metrics: Optional[dict] = None
    status: Optional[BusinessStatus] = None

class PaymentRequest(BaseModel):
    business_id: str
    payment_type: str = "listing_fee"
    amount: float = 99.0  # Default listing fee

class PaymentResponse(BaseModel):
    payment_id: str
    status: str
    business_id: str
    amount: float
    message: str

class BusinessListingResponse(BaseModel):
    id: str
    title: str
    description: str
    industry: IndustryType
    region: RegionType
    annual_revenue: float
    ebitda: float
    asking_price: float
    risk_grade: RiskGrade
    status: BusinessStatus
    seller_name: str
    reason_for_sale: str
    growth_opportunities: str
    financial_data: List[FinancialData]
    key_metrics: dict
    created_at: datetime
    views: int
    inquiries: int
    featured: bool

class BusinessCardResponse(BaseModel):
    id: str
    title: str
    industry: IndustryType
    region: RegionType
    annual_revenue: float
    ebitda: float
    asking_price: float
    risk_grade: RiskGrade
    status: BusinessStatus
    created_at: datetime
    views: int
    inquiries: int
    featured: bool

class BusinessFilters(BaseModel):
    industry: Optional[IndustryType] = None
    region: Optional[RegionType] = None
    min_revenue: Optional[float] = None
    max_revenue: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    risk_grade: Optional[RiskGrade] = None
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"

# Initialize sample data
async def init_sample_data():
    # Check if data already exists
    existing_count = await db.business_listings.count_documents({})
    if existing_count > 0:
        return
        
    sample_businesses = [
        {
            "id": str(uuid.uuid4()),
            "title": "Moldovan Wine Production Company",
            "description": "Established wine production facility with 50 hectares of vineyards and modern processing equipment. Export relationships with EU markets.",
            "industry": IndustryType.MANUFACTURING,
            "region": RegionType.CHISINAU,
            "annual_revenue": 2500000.0,
            "ebitda": 450000.0,
            "asking_price": 3500000.0,
            "risk_grade": RiskGrade.B,
            "status": BusinessStatus.ACTIVE,
            "seller_id": str(uuid.uuid4()),
            "seller_name": "Alexandru Popescu",
            "seller_email": "a.popescu@example.com",
            "reason_for_sale": "Owner retiring after 25 years",
            "growth_opportunities": "Expand EU distribution, add organic wine line, develop wine tourism",
            "financial_data": [
                {"year": 2023, "revenue": 2500000, "profit_loss": 380000, "ebitda": 450000, "assets": 4200000, "liabilities": 1800000, "cash_flow": 420000},
                {"year": 2022, "revenue": 2300000, "profit_loss": 350000, "ebitda": 420000, "assets": 4000000, "liabilities": 1900000, "cash_flow": 400000},
                {"year": 2021, "revenue": 2100000, "profit_loss": 320000, "ebitda": 380000, "assets": 3800000, "liabilities": 2000000, "cash_flow": 360000}
            ],
            "key_metrics": {
                "employees": 45,
                "years_in_business": 25,
                "export_percentage": 60,
                "production_capacity": "500,000 bottles/year"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "views": 145,
            "inquiries": 8,
            "featured": True
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Retail Chain - 5 Locations",
            "description": "Profitable retail chain with 5 locations across Moldova. Specializes in electronics and household goods with strong customer base.",
            "industry": IndustryType.RETAIL,
            "region": RegionType.BALTI,
            "annual_revenue": 1800000.0,
            "ebitda": 270000.0,
            "asking_price": 2200000.0,
            "risk_grade": RiskGrade.C,
            "status": BusinessStatus.ACTIVE,
            "seller_id": str(uuid.uuid4()),
            "seller_name": "Maria Ionescu",
            "seller_email": "m.ionescu@example.com",
            "reason_for_sale": "Relocating to another country",
            "growth_opportunities": "E-commerce expansion, add 2-3 new locations, develop private label products",
            "financial_data": [
                {"year": 2023, "revenue": 1800000, "profit_loss": 220000, "ebitda": 270000, "assets": 2500000, "liabilities": 1200000, "cash_flow": 250000},
                {"year": 2022, "revenue": 1650000, "profit_loss": 200000, "ebitda": 240000, "assets": 2300000, "liabilities": 1300000, "cash_flow": 220000},
                {"year": 2021, "revenue": 1500000, "profit_loss": 180000, "ebitda": 210000, "assets": 2100000, "liabilities": 1400000, "cash_flow": 190000}
            ],
            "key_metrics": {
                "employees": 28,
                "years_in_business": 12,
                "locations": 5,
                "avg_daily_customers": 450
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "views": 89,
            "inquiries": 5,
            "featured": False
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Restaurant Chain - Traditional Moldovan Cuisine",
            "description": "Well-established restaurant chain with 3 locations serving traditional Moldovan cuisine. Strong brand recognition and loyal customer base.",
            "industry": IndustryType.FOOD_SERVICE,
            "region": RegionType.CHISINAU,
            "annual_revenue": 950000.0,
            "ebitda": 142500.0,
            "asking_price": 1400000.0,
            "risk_grade": RiskGrade.B,
            "status": BusinessStatus.ACTIVE,
            "seller_id": str(uuid.uuid4()),
            "seller_name": "Vasile Moldovan",
            "seller_email": "v.moldovan@example.com",
            "reason_for_sale": "Focus on other business ventures",
            "growth_opportunities": "Franchise model, catering services, food delivery expansion",
            "financial_data": [
                {"year": 2023, "revenue": 950000, "profit_loss": 115000, "ebitda": 142500, "assets": 1600000, "liabilities": 800000, "cash_flow": 130000},
                {"year": 2022, "revenue": 880000, "profit_loss": 105000, "ebitda": 130000, "assets": 1500000, "liabilities": 850000, "cash_flow": 120000},
                {"year": 2021, "revenue": 820000, "profit_loss": 95000, "ebitda": 115000, "assets": 1400000, "liabilities": 900000, "cash_flow": 105000}
            ],
            "key_metrics": {
                "employees": 45,
                "years_in_business": 15,
                "locations": 3,
                "avg_daily_covers": 200
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "views": 67,
            "inquiries": 3,
            "featured": True
        },
        {
            "id": str(uuid.uuid4()),
            "title": "IT Services & Software Development",
            "description": "Growing technology company providing software development and IT services to local and international clients. Strong portfolio of recurring contracts.",
            "industry": IndustryType.TECHNOLOGY,
            "region": RegionType.CHISINAU,
            "annual_revenue": 750000.0,
            "ebitda": 225000.0,
            "asking_price": 1200000.0,
            "risk_grade": RiskGrade.A,
            "status": BusinessStatus.ACTIVE,
            "seller_id": str(uuid.uuid4()),
            "seller_name": "Dmitri Volkov",
            "seller_email": "d.volkov@example.com",
            "reason_for_sale": "Founder wants to start new venture",
            "growth_opportunities": "Scale international client base, develop SaaS products, expand team",
            "financial_data": [
                {"year": 2023, "revenue": 750000, "profit_loss": 190000, "ebitda": 225000, "assets": 850000, "liabilities": 350000, "cash_flow": 210000},
                {"year": 2022, "revenue": 650000, "profit_loss": 165000, "ebitda": 195000, "assets": 750000, "liabilities": 400000, "cash_flow": 180000},
                {"year": 2021, "revenue": 520000, "profit_loss": 130000, "ebitda": 155000, "assets": 650000, "liabilities": 450000, "cash_flow": 140000}
            ],
            "key_metrics": {
                "employees": 18,
                "years_in_business": 8,
                "recurring_revenue_percentage": 75,
                "international_clients": 12
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "views": 123,
            "inquiries": 12,
            "featured": False
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Agricultural Processing Facility",
            "description": "Modern grain processing facility with storage capacity and distribution network. Serves local farmers and food manufacturers.",
            "industry": IndustryType.AGRICULTURE,
            "region": RegionType.CAHUL,
            "annual_revenue": 3200000.0,
            "ebitda": 480000.0,
            "asking_price": 4500000.0,
            "risk_grade": RiskGrade.C,
            "status": BusinessStatus.ACTIVE,
            "seller_id": str(uuid.uuid4()),
            "seller_name": "Gheorghe Mihai",
            "seller_email": "g.mihai@example.com",
            "reason_for_sale": "Consolidating business operations",
            "growth_opportunities": "Organic certification, direct farmer contracts, export expansion",
            "financial_data": [
                {"year": 2023, "revenue": 3200000, "profit_loss": 384000, "ebitda": 480000, "assets": 5500000, "liabilities": 2800000, "cash_flow": 450000},
                {"year": 2022, "revenue": 2950000, "profit_loss": 354000, "ebitda": 440000, "assets": 5200000, "liabilities": 2900000, "cash_flow": 420000},
                {"year": 2021, "revenue": 2700000, "profit_loss": 320000, "ebitda": 400000, "assets": 4900000, "liabilities": 3000000, "cash_flow": 380000}
            ],
            "key_metrics": {
                "employees": 32,
                "years_in_business": 20,
                "storage_capacity": "5,000 tons",
                "processing_capacity": "200 tons/day"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "views": 78,
            "inquiries": 4,
            "featured": False
        }
    ]
    
    await db.business_listings.insert_many(sample_businesses)

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Moldovan Business Marketplace API"}

@api_router.get("/businesses", response_model=List[BusinessCardResponse])
async def get_businesses(
    industry: Optional[IndustryType] = None,
    region: Optional[RegionType] = None,
    min_revenue: Optional[float] = None,
    max_revenue: Optional[float] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    risk_grade: Optional[RiskGrade] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    featured_first: Optional[bool] = True
):
    # Build query filter
    query_filter = {"status": BusinessStatus.ACTIVE}
    
    if industry:
        query_filter["industry"] = industry
    if region:
        query_filter["region"] = region
    if min_revenue:
        query_filter["annual_revenue"] = {"$gte": min_revenue}
    if max_revenue:
        if "annual_revenue" in query_filter:
            query_filter["annual_revenue"]["$lte"] = max_revenue
        else:
            query_filter["annual_revenue"] = {"$lte": max_revenue}
    if min_price:
        query_filter["asking_price"] = {"$gte": min_price}
    if max_price:
        if "asking_price" in query_filter:
            query_filter["asking_price"]["$lte"] = max_price
        else:
            query_filter["asking_price"] = {"$lte": max_price}
    if risk_grade:
        query_filter["risk_grade"] = risk_grade
    
    # Build sort criteria
    sort_criteria = []
    if featured_first:
        sort_criteria.append(("featured", -1))
    
    sort_direction = -1 if sort_order == "desc" else 1
    sort_criteria.append((sort_by, sort_direction))
    
    # Execute query
    businesses = await db.business_listings.find(query_filter).sort(sort_criteria).to_list(100)
    
    return [BusinessCardResponse(**business) for business in businesses]

@api_router.get("/businesses/{business_id}", response_model=BusinessListingResponse)
async def get_business(business_id: str):
    business = await db.business_listings.find_one({"id": business_id})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Increment views
    await db.business_listings.update_one(
        {"id": business_id},
        {"$inc": {"views": 1}}
    )
    
    return BusinessListingResponse(**business)

@api_router.post("/businesses", response_model=BusinessListingResponse)
async def create_business(business: BusinessListingCreate):
    business_dict = business.dict()
    business_dict["id"] = str(uuid.uuid4())
    business_dict["seller_id"] = str(uuid.uuid4())  # In real app, this would be the authenticated user ID
    business_dict["created_at"] = datetime.utcnow()
    business_dict["updated_at"] = datetime.utcnow()
    business_dict["views"] = 0
    business_dict["inquiries"] = 0
    business_dict["featured"] = False
    
    await db.business_listings.insert_one(business_dict)
    return BusinessListingResponse(**business_dict)

@api_router.put("/businesses/{business_id}", response_model=BusinessListingResponse)
async def update_business(business_id: str, business: BusinessListingUpdate):
    # Check if business exists
    existing_business = await db.business_listings.find_one({"id": business_id})
    if not existing_business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Update only provided fields
    update_dict = {k: v for k, v in business.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    await db.business_listings.update_one(
        {"id": business_id},
        {"$set": update_dict}
    )
    
    updated_business = await db.business_listings.find_one({"id": business_id})
    return BusinessListingResponse(**updated_business)

@api_router.get("/businesses/seller/{seller_id}")
async def get_seller_businesses(seller_id: str):
    businesses = await db.business_listings.find({"seller_id": seller_id}).to_list(100)
    return [BusinessListingResponse(**business) for business in businesses]

@api_router.post("/businesses/{business_id}/payment", response_model=PaymentResponse)
async def process_payment(business_id: str, payment: PaymentRequest):
    # Check if business exists
    business = await db.business_listings.find_one({"id": business_id})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Mock payment processing
    payment_id = str(uuid.uuid4())
    
    # Simulate payment success (90% success rate for demo)
    import random
    success = random.random() < 0.9
    
    if success:
        # Update business status to active
        await db.business_listings.update_one(
            {"id": business_id},
            {"$set": {"status": BusinessStatus.ACTIVE, "updated_at": datetime.utcnow()}}
        )
        
        return PaymentResponse(
            payment_id=payment_id,
            status="success",
            business_id=business_id,
            amount=payment.amount,
            message="Payment successful! Your business listing is now active."
        )
    else:
        return PaymentResponse(
            payment_id=payment_id,
            status="failed",
            business_id=business_id,
            amount=payment.amount,
            message="Payment failed. Please try again."
        )

@api_router.get("/industries")
async def get_industries():
    return [{"value": industry.value, "label": industry.value.replace("_", " ").title()} for industry in IndustryType]

@api_router.get("/regions")
async def get_regions():
    return [{"value": region.value, "label": region.value.replace("_", " ").title()} for region in RegionType]

@api_router.get("/risk-grades")
async def get_risk_grades():
    return [
        {"value": "A", "label": "A - Low Risk"},
        {"value": "B", "label": "B - Medium-Low Risk"},
        {"value": "C", "label": "C - Medium Risk"},
        {"value": "D", "label": "D - Medium-High Risk"},
        {"value": "E", "label": "E - High Risk"}
    ]

# Initialize sample data on startup
@app.on_event("startup")
async def startup_event():
    await init_sample_data()

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()