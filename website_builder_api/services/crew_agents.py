# website_builder_api/crew_agents.py

from crewai import Agent, LLM
import os

from my_website_builder.config import Config

# Ensure environment variables are loaded if this file is run independently


llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7,
    api_key=Config.GOOGLE_API_KEY,
)
market_research_lead_agent = Agent(
    role="Chief Market Viability Analyst",
    goal="Provide a comprehensive market viability score and detailed report for a given location and niche.",
    backstory=(
        "A seasoned strategist with a deep understanding of market dynamics and data analysis, "
        "capable of synthesizing complex information into actionable insights. "
        "Oversees the entire market viability assessment process."
    ),
    verbose=True,
    allow_delegation=True,
    llm=llm
)

# Demographic Data Analyst Agent
demographic_data_analyst_agent = Agent(
    role="Demographic Data Specialist",
    goal="Identify and analyze key demographic indicators and their relevance to the target niche in the specified location.",
    backstory=(
        "Expert in demographic trends and their impact on market demand. "
        "Proficient in utilizing demographic APIs to extract relevant population data."
    ),
    verbose=True,
    llm=llm
    # Tools will be added in a later step (e.g., Demographic APIs)
)

# Niche Demand Analyst Agent
niche_demand_analyst_agent = Agent(
    role="Niche Demand Forecaster",
    goal="Quantify market size, demand, and potential growth for the given niche in the specified location.",
    backstory=(
        "A keen observer of consumer behavior and market trends, adept at identifying unmet needs and emerging opportunities. "
        "Specializes in analyzing search volume and industry trends."
    ),
    verbose=True,
    llm=llm
    # Tools will be added in a later step (e.g., SEO/Keyword APIs, Industry Trends APIs)
)
