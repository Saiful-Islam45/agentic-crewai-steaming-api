# website_builder_api/crew_tasks.py

from crewai import Task
from .crew_agents import (
    demographic_data_analyst_agent,
    niche_demand_analyst_agent,
    market_research_lead_agent
)

# Task for the Demographic Data Analyst Agent
demographic_analysis_task = Task(
    description=(
        "Gather comprehensive demographic data for the specified location, focusing on "
        "population size, age distribution, income levels, and relevant lifestyle preferences. "
        "Analyze how these demographics might impact the demand for services/products in the '{niche}' niche."
    ),
    expected_output="A concise report detailing key demographic insights relevant to the '{niche}' niche in '{location}'.",
    agent=demographic_data_analyst_agent,
    async_execution=False
)

# Task for the Niche Demand Analyst Agent
niche_demand_analysis_task = Task(
    description=(
        "Assess the current market size and demand for the '{niche}' niche in '{location}'. "
        "Identify potential growth areas and gauge overall consumer interest through search volume analysis and industry reports."
    ),
    expected_output="A report quantifying market size, demand, and growth potential, including relevant search volume data for '{niche}' in '{location}'.",
    agent=niche_demand_analyst_agent,
    async_execution=False
)

# Task for the Market Research Lead Agent
market_viability_report_task = Task(
    description=(
        "Synthesize the demographic analysis and niche demand analysis reports. "
        "Based on these findings, calculate an initial market viability confidence score (0-100) "
        "for launching a website in the '{location}' for the '{niche}' niche. "
        "Provide a summary report explaining the score and key insights."
    ),
    expected_output="A market viability report including a confidence score (e.g., 'Confidence Score: 75/100') "
                    "and a brief qualitative summary of market potential and challenges for '{niche}' in '{location}'.",
    agent=market_research_lead_agent,
    context=[demographic_analysis_task, niche_demand_analysis_task],
    async_execution=False
)
