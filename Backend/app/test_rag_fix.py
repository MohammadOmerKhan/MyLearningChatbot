#!/usr/bin/env python3
"""
Test script to verify RAG functionality after fixes.
"""

import asyncio
from tools.RAG import rag_tool

async def test_rag():
    """Test the RAG functionality."""
    print("🧪 Testing RAG functionality...")
    
    try:
        # Test search
        results = await rag_tool.search_documents("test query", limit=3)
        print(f"📊 Search results: {len(results)} documents found")
        
        # Test formatting
        formatted = rag_tool.format_results(results)
        print(f"📝 Formatted results:\n{formatted}")
        
        print("✅ RAG test completed successfully!")
        
    except Exception as e:
        print(f"❌ RAG test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_rag())
