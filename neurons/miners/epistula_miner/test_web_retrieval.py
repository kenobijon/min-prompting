import asyncio
from web_retrieval import get_websites_with_similarity

async def main():
    results = await get_websites_with_similarity(
        query="What are the 5 best phones I can buy this year?",
        n_results=5,
        k=3
    )
    print("Results:")
    for result in results:
        print(f"\nURL: {result['url']}")
        print(f"Relevant content: {result['relevant']}\n")

if __name__ == "__main__":
    asyncio.run(main()) 