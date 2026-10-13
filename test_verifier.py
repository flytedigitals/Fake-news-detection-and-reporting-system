from online_verifier import verify_news_online

# Test with a fake news example
test_text = "Dangote announces new refinery opening date in Lagos"
result = verify_news_online(test_text)

print("=" * 50)
print("VERIFICATION RESULT:")
print("=" * 50)
print(f"Verified: {result['verified']}")
print(f"Search Engine: {result.get('search_engine', 'N/A')}")
print(f"Message: {result['message']}")
print(f"Topic: {result.get('topic', 'N/A')}")

if result.get('sources'):
    print("\nSources Found:")
    for i, source in enumerate(result['sources'][:3]):
        print(f"  {i+1}. {source.get('title', '')[:60]}")
