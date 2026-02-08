from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any

class SubmitRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    channelName: str = Field(..., description="YouTube channel name or handle")
    services: List[str] = Field(default_factory=list, description="Optional list of extra services")

class VideoInfo(BaseModel):
    title: str
    description: str
    url: str
    statistics: Dict[str, Any]

class JobStatusResponse(BaseModel):
    job_id: str = Field(..., alias="jobId")
    status: str = Field(..., description="Current job status, e.g., queued, channel_resolved, videos_fetched, completed, failed")
    error: Optional[str] = None
    channel_id: Optional[str] = None
    videos: Optional[List[VideoInfo]] = None
    aiReport: Optional[Dict[str, Any]] = None  # Changed from str to Dict to support structured analysis


# Authentication Schemas
class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    user_id: str
    email: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    channel_url: Optional[str] = None
    content_niche: Optional[str] = None
    plan: str
    credits_used: int
    credits_limit: int
    is_verified: bool


class TokenResponse(BaseModel):
    token: str
    user: UserResponse


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = Field(None, min_length=3, max_length=30)
    phone_number: Optional[str] = None
    location: Optional[str] = None
    channel_url: Optional[str] = None
    content_niche: Optional[str] = None


class PlanUpdate(BaseModel):
    plan: str = Field(..., description="Pricing plan: free, pro, or team")


# ============================================================================
# AI SERVICE RESPONSE SCHEMAS
# ============================================================================

# Semantic Title Engine Schemas
class ChannelAnalysis(BaseModel):
    overall_assessment: str = Field(..., description="Detailed channel title strategy analysis")


class AlternativeTitle(BaseModel):
    new_suggested_title: str = Field(..., description="Alternative title suggestion")
    ctr_potential_rating: int = Field(..., ge=0, le=10, description="CTR potential rating 0-10")
    why_it_s_effective: str = Field(..., description="Psychology explanation of why it works")


class TitleSuggestion(BaseModel):
    original_title: str = Field(..., description="Original video title")
    current_issues: List[str] = Field(..., description="List of issues with current title")
    alternative_titles: List[AlternativeTitle] = Field(..., min_items=3, max_items=3, description="Exactly 3 alternative titles")


class SemanticTitleEngine(BaseModel):
    channel_analysis: ChannelAnalysis
    suggestions: List[TitleSuggestion] = Field(..., description="Title suggestions for each video")
    growth_tips: List[str] = Field(..., description="Growth tips for channel")


# Predictive CTR Analysis Schemas
class WhatIsWorkingOrMissing(BaseModel):
    working: str = Field(..., description="What's working well (paragraph)")
    missing: str = Field(..., description="What's missing (paragraph)")


class PredictiveCTRAnalysis(BaseModel):
    score: float = Field(..., ge=0, le=10, description="CTR score 0-10")
    reasoning: str = Field(..., description="Explanation of score")
    comparison_to_industry_average: str = Field(..., description="Industry comparison")
    what_is_working_or_missing: WhatIsWorkingOrMissing
    recommendations: List[str] = Field(..., description="Optimization recommendations")
    potential_increase: str = Field(..., description="Potential increase percentage")
    psychological_triggers_to_boost_engagement: List[str] = Field(..., description="Psychological triggers")


# Multi-Platform Mastery Schemas
class PlatformAnalysis(BaseModel):
    score: int = Field(..., ge=0, le=10, description="Platform score 0-10")
    reasoning: str = Field(..., description="Why this score")
    strategy: str = Field(..., description="Platform-specific strategy")
    optimization_tips: List[str] = Field(..., description="Optimization tips")


class MultiPlatformMastery(BaseModel):
    platforms: Dict[str, PlatformAnalysis] = Field(
        ..., 
        description="Platform analyses (youtube, x_twitter, linkedin)"
    )


# Copyright Protection Schemas
class CopyrightProtection(BaseModel):
    risk_level: str = Field(..., pattern="^(LOW|MEDIUM|HIGH)$", description="Risk level: LOW, MEDIUM, or HIGH")
    flags: List[str] = Field(..., description="Copyright flags")
    assessment: str = Field(..., description="Detailed assessment")
    recommendations: List[str] = Field(..., description="Recommendations")


# Fair Use Analysis Schemas
class FairUseFactor(BaseModel):
    score: int = Field(..., ge=0, le=10, description="Factor score 0-10")
    reasoning: str = Field(..., description="Explanation")


class FairUseFactorsBreakdown(BaseModel):
    purpose_and_character: FairUseFactor
    nature_of_work: FairUseFactor
    amount_used: FairUseFactor
    market_effect: FairUseFactor


class FairUseAnalysis(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Fair use score 0-100")
    reasoning: str = Field(..., description="Explanation of score")
    assessment: str = Field(..., description="Detailed fair use assessment")
    fair_use_factors_breakdown: FairUseFactorsBreakdown
    recommendation_for_legal_safety: str = Field(..., description="Actionable legal guidance")


# Trend Intelligence Schemas
class TrendingTopic(BaseModel):
    name: str = Field(..., description="Topic name")
    growth_percentage: str = Field(..., description="Growth percentage")
    relevance_rating: int = Field(..., ge=0, le=10, description="Relevance rating 0-10")
    reasoning: str = Field(..., description="Why relevant")


class TrendIntelligence(BaseModel):
    trending_topics: List[TrendingTopic] = Field(..., description="Trending topics")
    predictions: List[str] = Field(..., description="Predictions for next 24-72 hours")
    actionable_content_ideas: List[str] = Field(..., description="Content ideas")


# Main AI Services Response Schema
class AIServicesResponse(BaseModel):
    services: Dict[str, Any] = Field(..., description="AI service results")
    
    class Config:
        # Allow extra fields for flexibility
        extra = "allow"


# Typed service response (for validation)
class TypedAIServicesResponse(BaseModel):
    """Fully typed AI services response with all possible services"""
    semantic_title_engine: Optional[SemanticTitleEngine] = None
    predictive_ctr_analysis: Optional[PredictiveCTRAnalysis] = None
    multi_platform_mastery: Optional[MultiPlatformMastery] = None
    copyright_protection: Optional[CopyrightProtection] = None
    fair_use_analysis: Optional[FairUseAnalysis] = None
    trend_intelligence: Optional[TrendIntelligence] = None

# ============================================================================
# EMAIL SUMMARY SCHEMA
# ============================================================================

class EmailSummary(BaseModel):
    headline: str = Field(..., description="Curiosity-driven headline")
    teaser: str = Field(..., description="Short teaser to spark interest")
    key_insights: List[str] = Field(..., min_items=2, max_items=5)
    cta: str = Field(..., description="Call to action")


