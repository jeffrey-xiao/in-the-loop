# HackWestern Plan

**Note:** The parts of our app are in the other branches of this repo

## *A live-updated trend-based news-aggregator app*
### Reasoning
Following the recent savage attacks in Paris, the world has seen the chaos that followed during and after the event. Our app aims to provide truthful information aggregated from multiple news sources and is based on Twitter trends. 

### Ideas
- Use machine learning to identify keywords and highlight specific paragraphs
    - Wit.AI, Indico, Google Cloud Platform (Compute Engine, Prediction API, etc.) 
    - Naive Bayes filters
- Get latest events through Twitter trends and maybe other sources?
- Some sort of safety feature for people using it? Live maps? etc. Aggregate user inputed information on important things.

### Technologies
- Use Firebase DB for live information updating
- Web App can be built off of Angular, Meteor, etc.
- Beautiful design! Bootstrap! Semantic UI!
- Mobile android app if possible? Watch Apps? 
- Python News Scraper (or other language equivelant?) https://github.com/codelucas/newspaper
- Very fast backend to periodically scan the web for new things. Possibly written in Python, Ruby (broken on Windows), Node.JS, or PHP. C++ might be too difficult. Are there event hooks for news aggregates? 

### Proposed Algorithmic Steps:
1. Find a shitload of articles relating to the specific trend
2. Find the top keywords from all these articles
3. Get all the paragraphs containing each keyword
4. For each keyword, choose the best paragraph from the best source (length, conciseness, views, etc.)
5. Now you have one paragraph for each important keyword you found
6. Push all this to Firebase. 
7. User interface live updates from Firebase. 
8. Recognize location keywords?? Display on map?? Idk.

