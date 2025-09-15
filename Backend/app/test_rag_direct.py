#!/usr/bin/env python3
"""
Test RAG functionality directly without the REACT agent
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.RAG import rag_tool

async def test_rag_direct():
    """Test RAG tool directly"""
    print("=== Testing RAG Tool Directly ===")
    
    try:
        # Test query
        query = "Netsol growth 2023"
        print(f"Query: {query}")
        
        # Search documents
        results = await rag_tool.search_documents(query, limit=3)
        print(f"Number of results: {len(results)}")
        
        if results:
            print("\n=== RAG Results ===")
            for i, result in enumerate(results, 1):
                print(f"{i}. Filename: {result['filename']}")
                print(f"   Similarity: {result['similarity']:.4f}")
                print(f"   Text: {result['text'][:200]}...")
                print()
        else:
            print("No results found!")
            
        # Test formatting
        formatted = rag_tool.format_results(results)
        print("=== Formatted Results ===")
        print(formatted)
        
    except Exception as e:
        print(f"Error testing RAG: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_rag_direct())
