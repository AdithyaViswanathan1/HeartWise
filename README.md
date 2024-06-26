# HeartWise
This is a rules-based chatbot called HeartWise. HeartWise is a chatbot which can talk about heart disease.

Here is a short description of all the files in this project:

- webcrawler.py: The web crawler code + knowledge base builder code
- chatbot.py: The chatbot code
- knowledge.p: Pickle file containing my knowledge base (dictionary)
- kb.json: Same knowledge base but in JSON form (for easy viewing)
- raw_scrape: Files containing scraped text from many sites
- cleaned_up directory: Files containing cleaned-up website text
- users directory: JSON files pertaining to each user
- log.txt: List of websites scraped to create raw_scrape directory, cleaned_up directory, and knowledge base

## HOW TO RUN:

- NOTE: Make sure the libaries listed in the following files are downloaded on your local machine. (Most are pre-installed with Python so only a few need to be taken care of)

- (OPTIONAL) Run webcrawler.py. This will create/overwrite the files & directories: cleaned_up, raw_scrape, kb.json, knowledge_base.p, and log.txt

- (REQUIRED) Run chatbot.py. The chatbot will start in the terminal and all interaction happens there. EXIT keyword will terminate the program at any point.
