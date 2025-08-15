import requests
from bs4 import BeautifulSoup
from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
from transformers import pipeline

# Change to smaller model if needed
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def scrape_headlines(company):
    search_url = f"https://news.google.com/search?q={company}&hl=en"
    response = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = []
    for link in soup.select('a.DY5T1d'):  # Correct CSS selector for news title links
        title = link.text.strip()
        href = link.get('href')
        if href and href.startswith('./articles/'):
            url = "https://news.google.com" + href[1:]
            headlines.append({"title": title, "url": url})
        if len(headlines) >=3:
            break
    return headlines




class ActionGetNews(Action):
    def name(self):
        return "action_get_news"

    def run(self, dispatcher, tracker, domain):
        company = next(tracker.get_latest_entity_values("company"), None)
        if not company:
            dispatcher.utter_message("Please enter a valid company name.")
            return []

        headlines = scrape_headlines(company)
        if not headlines:
            dispatcher.utter_message(f"Sorry, I couldn't find the latest news for {company}.")
            return []

        summary_input = " ".join(h['title'] for h in headlines)
        summary = summarizer(summary_input, max_length=50, min_length=15, do_sample=False)[0]['summary_text']

        response = f"Latest news for *{company}*:\n"
        for h in headlines:
            response += f"- {h['title']} ({h['url']})\n"
        response += f"\n**Summary:** {summary}"
        dispatcher.utter_message(response)
        return []
