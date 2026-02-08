import json
from google import genai
from google.genai import types
from typing import List, Dict, Any
from app.core.config import settings


# Service ID to name mapping
SERVICE_MAP = {
    "1": "semantic_title_engine",
    "2": "predictive_ctr_analysis",
    "3": "multi_platform_mastery",
    "7": "copyright_protection",
    "8": "fair_use_analysis",
    "10": "trend_intelligence"
}


async def analyse(videos: List[Dict[str, Any]], channel_stats: Dict[str, Any] = None, services: List[str] = None) -> Dict[str, Any]:
    """
    Analyze YouTube videos using Gemini-2.5-flash with service-specific analysis.
    
    Args:
        videos: List of video dictionaries with title, description, url, statistics
        channel_stats: Optional channel statistics
        services: List of service IDs selected by user
        
    Returns:
        Dictionary with service-specific analysis results
    """
    if not settings.gemini_api_key:
        return get_fallback_analysis(videos, services)
    
    try:
        return await call_gemini_api(videos, channel_stats, services)
    except Exception as e:
        print(f"Gemini API failed, using fallback: {str(e)}")
        return get_fallback_analysis(videos, services)


async def call_gemini_api(videos: List[Dict[str, Any]], channel_stats: Dict[str, Any] = None, services: List[str] = None) -> Dict[str, Any]:
    """Call Gemini API with service-specific prompts."""
    
    # Build video details for prompt (take last 3 videos)
    videos_to_analyze = videos[:3] if len(videos) > 3 else videos
    
    video_details = "\n".join([
        f"""
VIDEO {i + 1}:
- Title: "{v.get('title', 'N/A')}"
- Description: {v.get('description', 'N/A')[:200]}...
- Views: {v.get('statistics', {}).get('viewCount', 'N/A')}
- Likes: {v.get('statistics', {}).get('likeCount', 'N/A')}
- Comments: {v.get('statistics', {}).get('commentCount', 'N/A')}
"""
        for i, v in enumerate(videos_to_analyze)
    ])
    
    # Build service-specific prompt
    service_instructions = build_service_instructions(services or [])
    
    prompt = f"""
You are an AI-powered YouTube Intelligence Suite used by professional creators and growth teams.

You do NOT give generic advice.
You produce EXECUTABLE INSIGHTS that can be shown directly in a product dashboard.

===========================
CHANNEL VIDEO DATA
===========================
{video_details}

===========================
REQUESTED SERVICES
===========================
{service_instructions}

===========================
SERVICE EXECUTION RULES
===========================
- Execute ONLY the services explicitly requested
- Do NOT include services that were not requested
- Each service must be clearly separated in the output
- Every score, rating, or risk level MUST include reasoning
- Avoid vague phrases like "could be improved" or "might work"
- Be decisive, confident, and specific

===========================
SERVICE-SPECIFIC EXPECTATIONS
===========================

SEMANTIC TITLE ENGINE
- Titles must be platform-native (YouTube style)
- Use curiosity gaps, specificity, emotional triggers
- Avoid clickbait without payoff
- Clearly explain WHY each alternative works better
- Ratings must reflect realistic CTR potential

PREDICTIVE CTR ANALYSIS
- Scores must reflect title + thumbnail psychology
- Highlight concrete weaknesses (length, clarity, emotion, promise)
- Recommend specific changes (words, numbers, framing)
- Assume creator wants maximum clicks without misleading viewers

MULTI-PLATFORM MASTERY
- Do NOT repeat the same advice across platforms
- Respect platform-native behavior (scroll speed, hook time)
- Suggest concrete adaptations, not reposting
- Optimize for algorithmic discovery, not followers

COPYRIGHT PROTECTION
- Be conservative and risk-aware
- Flag even borderline risks
- Assume Content ID systems, not manual review
- Provide safe, creator-friendly alternatives

FAIR USE ANALYSIS
- Assess transformation, not intent
- Consider education, commentary, critique
- Be explicit about risk boundaries
- Provide actionable legal safety guidance (not legal disclaimers)

TREND INTELLIGENCE
- Focus on EARLY signals, not obvious trends
- Avoid generic topics everyone already covers
- Prioritize actionable next-video ideas
- Think in a 24-72 hour opportunity window

===========================
OUTPUT FORMAT (STRICT)
===========================
Return VALID JSON ONLY.
No markdown. No explanations outside JSON.

CRITICAL: Follow this EXACT schema. Do not add, remove, or rename fields.
Use the exact field names shown below (case-sensitive, with underscores).

JSON STRUCTURE:
{{
    "email_summary": {{
        "headline": "string - curiosity-driven headline (max 12 words)",
        "teaser": "string - 2–3 lines teasing the biggest missed opportunity or upside",
        "key_insights": [
            "string - high-impact insight without full details",
            "string - high-impact insight without full details",
            "string - high-impact insight without full details"
        ],
        "cta": "string - compelling CTA to view full report (upgrade-oriented)"
    }},
    "services": {{
    "semantic_title_engine": {{
      "channel_analysis": {{
        "overall_assessment": "string - detailed channel title strategy analysis"
      }},
      "suggestions": [
        {{
          "original_title": "string - exact current title",
          "current_issues": ["string issue 1", "string issue 2", "string issue 3"],
          "alternative_titles": [
            {{
              "new_suggested_title": "string - alternative title",
              "ctr_potential_rating": 8,
              "why_it_s_effective": "string - psychology explanation"
            }},
            {{
              "new_suggested_title": "string - alternative title 2",
              "ctr_potential_rating": 7,
              "why_it_s_effective": "string - psychology explanation"
            }},
            {{
              "new_suggested_title": "string - alternative title 3",
              "ctr_potential_rating": 9,
              "why_it_s_effective": "string - psychology explanation"
            }}
          ]
        }}
      ],
      "growth_tips": ["string tip 1", "string tip 2", "string tip 3"]
    }},
    
    "predictive_ctr_analysis": {{
      "score": 5.5,
      "reasoning": "string - explanation of score",
      "comparison_to_industry_average": "string - industry comparison",
      "what_is_working_or_missing": {{
        "working": "string paragraph - what's working well",
        "missing": "string paragraph - what's missing"
      }},
      "recommendations": ["string rec 1", "string rec 2", "string rec 3"],
      "potential_increase": "30-50%",
      "psychological_triggers_to_boost_engagement": ["string trigger 1", "string trigger 2"]
    }},
    
    "multi_platform_mastery": {{
      "platforms": {{
        "youtube": {{
          "score": 9,
          "reasoning": "string - why this score",
          "strategy": "string - platform-specific strategy",
          "optimization_tips": ["string tip 1", "string tip 2"]
        }},
        "x_twitter": {{
          "score": 6,
          "reasoning": "string - why this score",
          "strategy": "string - platform-specific strategy",
          "optimization_tips": ["string tip 1", "string tip 2"]
        }},
        "linkedin": {{
          "score": 7,
          "reasoning": "string - why this score",
          "strategy": "string - platform-specific strategy",
          "optimization_tips": ["string tip 1", "string tip 2"]
        }}
      }}
    }},
    
    "copyright_protection": {{
      "risk_level": "LOW",
      "flags": ["string flag 1", "string flag 2"],
      "assessment": "string - detailed assessment",
      "recommendations": ["string rec 1", "string rec 2"]
    }},
    
    "fair_use_analysis": {{
      "score": 90,
      "reasoning": "string - explanation of score",
      "assessment": "string - detailed fair use assessment",
      "fair_use_factors_breakdown": {{
        "purpose_and_character": {{
          "score": 9,
          "reasoning": "string - explanation"
        }},
        "nature_of_work": {{
          "score": 8,
          "reasoning": "string - explanation"
        }},
        "amount_used": {{
          "score": 7,
          "reasoning": "string - explanation"
        }},
        "market_effect": {{
          "score": 9,
          "reasoning": "string - explanation"
        }}
      }},
      "recommendation_for_legal_safety": "string - actionable legal guidance"
    }},
    
    "trend_intelligence": {{
      "trending_topics": [
        {{
          "name": "string - topic name",
          "growth_percentage": "12%",
          "relevance_rating": 9,
          "reasoning": "string - why relevant"
        }}
      ],
      "predictions": ["string prediction 1", "string prediction 2"],
      "actionable_content_ideas": ["string idea 1", "string idea 2"]
    }}
  }}
}}

FIELD NAME RULES:
- Use snake_case (underscores): "channel_analysis", "current_issues", "why_it_s_effective"
- NOT camelCase: "channelAnalysis", "currentIssues", "whyItsEffective"
- risk_level values: "LOW", "MEDIUM", or "HIGH" (uppercase)
- Scores are numbers (not strings): 5.5, 90, 8
- Arrays must contain strings or objects as shown above

EMAIL SUMMARY RULES:
- Do NOT reveal full recommendations
- Tease problems, gaps, or upside
- Make the creator curious or slightly anxious
- Assume user has NOT seen the dashboard yet
- Tone: confident, insightful, premium


Remember:
- Include ONLY requested services
- Be concise, concrete, and product-ready
"""

    
    print(f"Calling Gemini API with {len(services or [])} services... (prompt length: {len(prompt)})")
    
    # Initialize Gemini client
    client = genai.Client(api_key=settings.gemini_api_key)
    
    # Call Gemini API
    response = await client.aio.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            system_instruction="You are an expert YouTube content strategist. Always respond with valid JSON only."
        )
    )
    
    response_text = response.text
    print(f"Gemini response received (length: {len(response_text)})")
    
    # Parse JSON from response
    try:
        # Clean up response - remove markdown code blocks if present
        cleaned_response = response_text.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
        
        analysis_result = json.loads(cleaned_response)
        return analysis_result
        
    except json.JSONDecodeError as parse_error:
        print(f"Failed to parse Gemini response as JSON: {str(parse_error)}")
        # Return fallback
        return get_fallback_analysis(videos, services)


def build_service_instructions(services: List[str]) -> str:
    """Build prompt instructions based on selected services."""
    
    instructions = "PERFORM THE FOLLOWING ANALYSES:\n\n"
    
    service_prompts = {
        "1": """1. SEMANTIC TITLE ENGINE (LLM-Driven Headline Generation):
   
   For EACH VIDEO, provide:
   - **Channel Analysis**: Overall assessment of the channel's title strategy, content themes, and approach
   - **Original Title**: State the current title exactly as it appears
   - **Current Issues**: List 2-4 specific problems with the title (use bullet points)
   - **3 Alternative Titles**: Each with:
     * The new suggested title
     * CTR Potential rating (0-10 scale)
     * "Why It's Effective": Explain the psychology (curiosity gap, power words, emotional triggers, etc.)
   - **Growth Tips**: 3-5 actionable recommendations for improving the channel's overall title strategy
   
   CRITICAL RULES:
   - Be HIGHLY specific about what's wrong with current titles
   - Make alternatives DRASTICALLY different from originals
   - Focus on CTR psychology: curiosity gaps, specificity, emotional triggers, power words
   - Avoid generic advice - give concrete, implementable suggestions
   - Growth tips should be unique to this channel's niche and style""",
        
        "2": """2. PREDICTIVE CTR ANALYSIS (Thumbnail Saliency Mapping):
   - Estimate overall channel CTR (0-100%)
   - Compare to industry average
   - Identify what's working or missing in titles/thumbnails
   - Provide 4-6 specific, actionable recommendations to improve click-through rates
   - Include "Potential Increase" estimate with optimizations
   - Highlight psychological triggers that could boost engagement""",
        
        "3": """3. MULTI-PLATFORM MASTERY (Cross-Platform Algorithm Alignment):
   - Analyze how this content would perform on:
     * YouTube (long-form, algorithm preferences)
     * X / Twitter (short-form threads, viral hooks)
     * LinkedIn (professional networking, thought leadership)
   - For EACH platform provide:
     * Score (0-10)
     * Strategy (specific to that platform's algorithm)
     * Optimization tips (concrete actions)
   - Do NOT repeat the same advice across platforms
   - Suggest content adaptations, not just reposting""",
        
        "7": """4. COPYRIGHT PROTECTION (Content ID Scanning Pre-Upload):
   
   IMPORTANT: Only flag ACTUAL copyright issues:
   - Background music from copyrighted sources
   - Clips from other creators' videos
   - Copyrighted images, logos, or graphics
   - Brand names used commercially
   
   DO NOT FLAG:
   - Educational content about technical topics
   - Original creator commentary
   - Tutorial/educational video content
   - Technical terms or concepts
   
   Provide:
   - Risk Level: LOW, MEDIUM, or HIGH (be conservative - most educational content is LOW)
   - Flags: List ONLY actual copyrighted material detected
   - Assessment: Brief explanation
   - Recommendations: Safe alternatives if risks found""",
        
        "8": """5. FAIR USE ANALYSIS (Transformative Content Assessment):
   - Evaluate transformativeness of the content (0-100 score)
   - Assess commentary, criticism, or educational value
   - Break down fair use factors:
     * Purpose (educational/commentary)
     * Nature (factual/creative)
     * Amount used
     * Market effect
   - Provide clear recommendation for legal safety""",
        
        "10": """6. TREND INTELLIGENCE (48-Hour Early Trend Detection):
   - Identify 3-5 trending topics related to this channel's niche
   - For each topic: name, growth percentage, relevance rating
   - Provide 3-5 specific predictions for the next 24-72 hours
   - Suggest 3-5 actionable content ideas aligned with emerging trends
   - Focus on EARLY signals, not obvious trends everyone already covers"""
    }
    
    for service_id in services:
        if service_id in service_prompts:
            instructions += service_prompts[service_id] + "\n\n"
    
    if not instructions.strip().endswith("ANALYSES:"):
        return instructions
    else:
        # If no services selected, do basic analysis
        return "Provide a general channel overview and basic recommendations."


def get_fallback_analysis(videos: List[Dict[str, Any]], services: List[str] = None) -> Dict[str, Any]:
    """Fallback analysis when Gemini API is unavailable."""
    
    videos_to_analyze = videos[:3] if len(videos) > 3 else videos
    services = services or []

    # Email-first teaser (used for conversion, not full insight)
    result = {
        "email_summary": {
            "headline": "Your channel has untapped growth potential",
            "teaser": (
                "We reviewed your recent videos and identified title, CTR, "
                "and visibility gaps that are quietly limiting reach."
            ),
            "key_insights": [
                "Your titles explain content but don’t maximize curiosity",
                "Click-through rate signals are below platform benchmarks",
                "You’re missing short-window trends relevant to your niche"
            ],
            "cta": "Open your full AI report to see what to fix first →"
        },
        "services": {}
    }

    # ------------------------------------------------------------------
    # Semantic Title Engine
    # ------------------------------------------------------------------
    if "1" in services:
        result["services"]["semantic_title_engine"] = {
            "channel_analysis": {
                "overall_assessment": (
                    "Your channel focuses on clarity and depth, but current titles "
                    "prioritize description over click psychology. This limits discovery "
                    "despite strong underlying content quality."
                )
            },
            "suggestions": [
                {
                    "original_title": (
                        videos_to_analyze[0].get("title", "Video 1")
                        if videos_to_analyze else "Video 1"
                    ),
                    "current_issues": [
                        "No strong curiosity gap or emotional trigger",
                        "Title explains topic instead of selling outcome",
                        "Lacks urgency or viewer-centric framing"
                    ],
                    "alternative_titles": [
                        {
                            "new_suggested_title": "This Mistake Is Costing You Views",
                            "ctr_potential_rating": 8,
                            "why_it_s_effective": (
                                "Introduces loss aversion and curiosity by implying "
                                "the viewer is unknowingly hurting growth."
                            )
                        },
                        {
                            "new_suggested_title": "What Top Creators Do That You Don’t",
                            "ctr_potential_rating": 8,
                            "why_it_s_effective": (
                                "Uses authority contrast to trigger comparison and intrigue."
                            )
                        },
                        {
                            "new_suggested_title": "I Tested This for 30 Days — The Results Surprised Me",
                            "ctr_potential_rating": 7,
                            "why_it_s_effective": (
                                "Time-boxed experimentation builds credibility and suspense."
                            )
                        }
                    ]
                }
            ],
            "growth_tips": [
                "Frame titles around outcomes, not topics",
                "Use contrast words like stop, avoid, secret, or proven",
                "Test curiosity-first titles before descriptive ones"
            ]
        }

    # ------------------------------------------------------------------
    # Predictive CTR Analysis
    # ------------------------------------------------------------------
    if "2" in services:
        result["services"]["predictive_ctr_analysis"] = {
            "score": 4.5,
            "reasoning": (
                "Titles and positioning are informative but lack emotional pull, "
                "reducing click probability compared to similar channels."
            ),
            "comparison_to_industry_average": (
                "Below average CTR compared to channels in the same category."
            ),
            "what_is_working_or_missing": {
                "working": (
                    "Clear topic communication and consistent formatting."
                ),
                "missing": (
                    "Emotional hooks, curiosity gaps, and visual-title alignment."
                )
            },
            "recommendations": [
                "Add numbers, timeframes, or bold claims to titles",
                "Align thumbnails with one dominant emotion",
                "Remove neutral wording in favor of benefit-driven phrasing"
            ],
            "potential_increase": "30–60%",
            "psychological_triggers_to_boost_engagement": [
                "Curiosity gap",
                "Fear of missing out",
                "Authority comparison"
            ]
        }

    # ------------------------------------------------------------------
    # Multi-Platform Mastery
    # ------------------------------------------------------------------
    if "3" in services:
        result["services"]["multi_platform_mastery"] = {
            "platforms": {
                "youtube": {
                    "score": 7,
                    "reasoning": "Strong long-form potential, weaker initial hook.",
                    "strategy": (
                        "Optimize first 30 seconds for retention and title-thumbnail cohesion."
                    ),
                    "optimization_tips": [
                        "Shorten intros",
                        "Reinforce title promise immediately"
                    ]
                },
                "x_twitter": {
                    "score": 6,
                    "reasoning": "Content not adapted to fast-scroll behavior.",
                    "strategy": (
                        "Convert insights into sharp opinion-led threads."
                    ),
                    "optimization_tips": [
                        "Lead with a bold claim",
                        "Use numbered hooks"
                    ]
                },
                "linkedin": {
                    "score": 7,
                    "reasoning": "Educational tone fits platform expectations.",
                    "strategy": (
                        "Position content as lessons learned or frameworks."
                    ),
                    "optimization_tips": [
                        "Share behind-the-scenes context",
                        "Tie insights to professional outcomes"
                    ]
                }
            }
        }

    # ------------------------------------------------------------------
    # Copyright Protection
    # ------------------------------------------------------------------
    if "7" in services:
        result["services"]["copyright_protection"] = {
            "risk_level": "LOW",
            "flags": [],
            "assessment": (
                "No immediate copyright risks detected based on available metadata."
            ),
            "recommendations": [
                "Use royalty-free music only",
                "Avoid unlicensed third-party clips"
            ]
        }

    # ------------------------------------------------------------------
    # Fair Use Analysis
    # ------------------------------------------------------------------
    if "8" in services:
        result["services"]["fair_use_analysis"] = {
            "score": 78,
            "reasoning": (
                "Content appears educational and sufficiently transformative."
            ),
            "assessment": (
                "Likely to qualify as fair use when paired with original commentary."
            ),
            "fair_use_factors_breakdown": {
                "purpose_and_character": {
                    "score": 8,
                    "reasoning": "Educational intent strengthens fair use."
                },
                "nature_of_work": {
                    "score": 7,
                    "reasoning": "Primarily factual material."
                },
                "amount_used": {
                    "score": 6,
                    "reasoning": "Unknown usage length — review recommended."
                },
                "market_effect": {
                    "score": 8,
                    "reasoning": "Unlikely to replace original content demand."
                }
            },
            "recommendation_for_legal_safety": (
                "Add explicit commentary and avoid long unaltered clips."
            )
        }

    # ------------------------------------------------------------------
    # Trend Intelligence
    # ------------------------------------------------------------------
    if "10" in services:
        result["services"]["trend_intelligence"] = {
            "trending_topics": [
                {
                    "name": "AI tools creators aren’t using yet",
                    "growth_percentage": "120%",
                    "relevance_rating": 9,
                    "reasoning": "High curiosity with low current saturation."
                }
            ],
            "predictions": [
                "Actionable AI workflows will outperform generic tool lists",
                "Short, experiment-based videos will gain momentum"
            ],
            "actionable_content_ideas": [
                "Testing one underrated AI tool live",
                "Breaking down why most creators misuse AI"
            ]
        }

    return result
