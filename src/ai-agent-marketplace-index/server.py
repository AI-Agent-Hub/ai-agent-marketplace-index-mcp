import asyncio
import os
import sys
import time
import json

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
server = FastMCP(
    "ai-agent-marketplace-index-mcp",
    prompt="""
# AI Agent Marketplace Index MCP Server

This server provides tools for searching the AI Agent Index and find available AI agents in various categories, including
general AI agents or task-specific AI agents.

## Available Tools

### 1. search_ai_agent

Use this tool for general search of various use scenarios to find available AI Agents from the index and marketplace, including meta information (website, descriptions, etc), functions, web traffic, etc.

web searches. Best for finding information,
websites, articles, and general content.

Example: "Please help me a list of AI coding agents that can help with children programming." 
"I want to file for my taxes and help me find available AI agents to finish the task." 


### 2. add_ai_agent

Use this tool specifically to list your AI Agents builders to public AI agent marketplace and index.

## Guidelines for Use

- Always check if a query would be better served by Agent search
- Keep queries concise and specific for best results
- Search AI Agents by concise category names are preferred, such as Email writing agents, Deep Search Agents, etc.

## Output Format

All search results will be formatted as text with clear sections for each result item, including:

- Search AI Agent: Content Name, Description, Website, Statistic (Google Rank, Bing Rank, Github Stars, etc.)

If the API key is missing or invalid, appropriate error messages will be
returned.
""",
)

API_NAME_SEARCH = "api_search"
API_NAME_ADD_SERVICE = "api_add_service"
API_AI_AGENT_MARKETPLACE_ENDPOINT = "http://www.deepnlp.org/api/ai_agent_marketplace/v1"
MOCK_ACCESS_KEY = "${your_access_key}"
USER_AGENT = "mcp-ai-agent-marketplace-index/1.0"

@server.tool()
async def search_ai_agent(
        q: str, limit: int = 100, timeout: int = 5
    ) -> str:
    """Performs agent search using the DeepNLP AI Agent Marketplace Index Search API for general information
    and websites, and usages.

        Args:
            q: query (required)
            limit: Limit as Number of maximum results
            timeout: timeout for API calling, default to 5
        Output: str, json str with keys:
            content_name: str, e.g. Coding Agent 1
            website: str, e.g www.my-agent.com
            description: str
            field: str
            subfield: str
            statistic: json of metrics, e.g {"Google Rank": 10.0, "Bing Rank": 10.0}
    """
    try:
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json"
        }
        # required param
        input_param = {}
        input_param["q"] = q 
        input_param["limit"] = limit
        input_param["return_fields"] = "statistic"

        search_url = API_AI_AGENT_MARKETPLACE_ENDPOINT
        kwparam_list = []
        for key, value in input_param.items():
            cur_kvparam = "%s=%s" % (str(key), str(value))
            kwparam_list.append(cur_kvparam)
        kvparam = "&".join(kwparam_list)
        if kvparam != "":
            search_url = API_AI_AGENT_MARKETPLACE_ENDPOINT + "?" + kvparam
        else:
            search_url = API_AI_AGENT_MARKETPLACE_ENDPOINT

        async with httpx.AsyncClient() as client:
            result = await client.get(
                search_url, headers=headers, params=input_param, timeout=timeout
            )

            result.raise_for_status()
            
            data = {}
            if result.status_code == 200:
                data = result.json()
            else:
                return "No results found."
            results = []
            items = data["items"] if "items" in data else []
            for item in data["items"]:
                content_name = item["content_name"] if "content_name" in item else ""
                website = item["website"] if "website" in item else ""
                description = item["description"] if "description" in item else ""
                field = item["field"] if "field" in item else ""
                subfield = item["subfield"] if "subfield" in item else ""
                statistic = item["statistic"] if "statistic" in item else {}
                statistic_str = json.dumps(statistic)

                results.append(
                    f"AI Agent Name: {content_name}\n"
                    f"Website: {website}\n"
                    f"Description: {description}\n"
                    f"Field: {field}\n"
                    f"SubField: {subfield}\n"
                    f"Statistic: {statistic_str}\n"
                )
            return "\n\n".join(results)

    except httpx.HTTPError as e:
        return f"Error communicating with DeepNLP AI Agent Marketplace API: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    server.run(transport='stdio')
