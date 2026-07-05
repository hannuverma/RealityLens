import asyncio
from datetime import datetime, timezone
from . import aiCalls


#function for search call
async def searchCall(extraction):
    """Perform web/image searches for the provided extraction dict and
    return formatted search text.

    Args:
        extraction (dict): result from extractionCall containing claim and
            other metadata.
    Returns:
        str: formatted search results text.
    """
    #get the claim and entities from the extraction
    claim = extraction.get("claim", "")
    print(f"🌐 Phase 2: Searching for — {claim}")
    entities = extraction.get("claim_entities", claim)
    
    # Use entities as primary query (concise, search-engine-friendly)
    # Fall back to claim if entities are missing
    primary_query = entities if entities and entities.strip() else claim

    async def do_text_search():
        #run two searches in parallel: one recent news, one unrestricted
        #this catches both breaking news AND older events that time_range="week" would miss
        try:
            recent_results, broad_results = await asyncio.gather(
                aiCalls.tavily_search(primary_query, num_results=5),
                aiCalls.tavily_search_broad(primary_query, num_results=5),
            )
            #deduplicate by URL
            seen_urls = set()
            merged = []
            for r in recent_results + broad_results:
                url = r.get("url", "")
                if url not in seen_urls:
                    seen_urls.add(url)
                    merged.append(r)
            return merged
        except Exception as e:
            #if tavily fails, parallel is faster from what i have seen but its unreliable because it gives claims that are not from credible sources and our scoring relies on the quality of sources 
            print(f"⚠️ Tavily search error: {e}")
            return await aiCalls.parallel_search(primary_query)

    async def do_image_search():
        #if there is an embedded image and image description
        if extraction.get("has_embedded_image") and extraction.get("image_description"):
            print("🖼️ Searching for image origin...")
            try:
                return await aiCalls.tavily_search(extraction["image_description"], num_results=3)
            except Exception as e:
                print(f"⚠️ Image search error: {e}")
                return await aiCalls.parallel_search(extraction["image_description"], num_results=3)
        return []
    #run both text and image search in parallel to make the fastest step in the process even faster (idk)
    search_results, image_results = await asyncio.gather(
        do_text_search(),
        do_image_search()
    )

    search_results += image_results

    # Add today's date header so the scoring model can judge temporal relevance
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    search_text = f"TODAY'S DATE: {today_str}\n\n" + aiCalls.format_search_results(search_results)
    print(f"📰 Found {len(search_results)} search results")
    print(f"{search_results}")
    return search_text
