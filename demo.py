"""
Paáré — Phase 2 Demo
---------------------
Tests the classifier with hardcoded sample URLs.
No scraping needed yet — pure AI classification proof of concept.

Usage:
    python demo.py

Make sure your API key is set in classifier.py before running.
"""

from classifier import classify_urls, print_results, save_results

# ─── Sample URLs (replace with real ones later) ──────────────────────────────
# Simulates what the Phase 1 discovery engine will eventually feed in.
# Covers the main content types you'll encounter in the wild.

TEST_URLS = [
    {
        "url": "https://www.instagram.com/p/Abc123XYZ/",
        "page_title": "Sarah Johnson on Instagram: 'wild night lmaoo 🍾'",
        "snippet": "Photo post from 2019 showing a party scene, tagged location: Lagos. 847 likes."
    },
    {
        "url": "https://twitter.com/sarahj_2004/status/1234567890",
        "page_title": "Sarah Johnson on X: 'I hate my boss so much rn'",
        "snippet": "Tweet from 2021. Quote: 'literally going to quit tomorrow, this place is a dump'. 12 retweets."
    },
    {
        "url": "https://www.reddit.com/r/relationship_advice/comments/abc123/my_boyfriend_cheated/",
        "page_title": "My boyfriend cheated and I don't know what to do : r/relationship_advice",
        "snippet": "Post from u/sarah_throwaway2019 detailing a personal relationship situation. 234 comments."
    },
    {
        "url": "https://www.facebook.com/sarah.johnson.9847/photos/123456789",
        "page_title": "Sarah Johnson — Photos",
        "snippet": "Profile photo album. Account appears to be the user's own account, still active."
    },
    {
        "url": "https://punchng.com/lagos-student-caught-in-campus-brawl-sarah-johnson/",
        "page_title": "Lagos student caught in campus brawl | Punch Newspapers",
        "snippet": "2020 news article naming Sarah Johnson as a student involved in an incident at university. Still indexed on Google."
    },
    {
        "url": "https://www.spokeo.com/Sarah-Johnson/Nigeria",
        "page_title": "Sarah Johnson — Spokeo People Search",
        "snippet": "Data broker listing showing name, approximate age, city, possible relatives and past addresses."
    },
    {
        "url": "https://www.youtube.com/watch?v=abc123xyz",
        "page_title": "Me and my friends doing the #tiktoklipsync challenge 2019",
        "snippet": "Video uploaded by user sarahj04 in 2019. 1.2k views. Comments section active."
    },
    {
        "url": "https://web.archive.org/web/20190801/https://oldblog.wordpress.com/sarah-diary",
        "page_title": "Sarah's Diary — Wayback Machine Archive",
        "snippet": "Archived version of a personal blog with diary-style entries from 2018-2019. Original blog deleted."
    },
]


if __name__ == "__main__":
    print("\n  Paáré — Phase 2 Classification Engine")
    print(f"   Sending {len(TEST_URLS)} URLs for analysis...\n")

    results = classify_urls(TEST_URLS)
    print_results(results)
    save_results(results, "scan_results.json")