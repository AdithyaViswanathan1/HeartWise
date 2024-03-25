# NECESSARY LIBRARIES
'''
beautifulsoup4
urllib3
requests
nltk
pickle
'''
from bs4 import BeautifulSoup
from urllib import request
from urllib.request import Request
import requests
import os
import nltk
from nltk.corpus import stopwords
from nltk import sent_tokenize
import re
import math
import pickle
import json

stopwords = stopwords.words('english')

# GIVEN LIST OF URLS, SCRAPE THEIR TEXT AND WRITE TO FILE IN RAW_SCRAPE FOLDER
def write_text(urls):
    output_path = "raw_scrape"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    counter = 0
    log_text = "RAW SCRAPE LOG\n\n"
    print("Writing scraped text")
    for i,url in enumerate(urls):
        try:
            req = Request(url , headers={'User-Agent': 'Mozilla/5.0'})
            html = request.urlopen(req).read().decode('utf8')
            soup = BeautifulSoup(html, features="html.parser")

            # kill all script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # extract text
            total_text = []
            texts = soup.find_all('p')
            for text in texts:
                total_text.append(text.get_text())
            
            #check length of text
            lengths = list(map(len, total_text))
            total_length = sum(lengths)
            if total_length < 500:
                continue
            log_text += f"{counter} {total_length} Writing: {url}\n"

            #write to txt file
            with open(f"{output_path}/site{counter}.txt", "w") as f:
                f.write(" ".join(total_text))
            counter += 1
        except Exception as e:
            continue
    
    # write log to file
    with open(f"log.txt", "w") as f:
        f.write(log_text)

# GIVEN URL, CHECK IF IT IS VALID (NOT ON BLACKLIST BUT CONTAINS AT LEAST 1 FROM WHITELIST)
def valid_url(url):
    black_list = ['spanish', 'espanol', 'mailto', 'languages', 'doi', 'journal', 'facebook', 'youtube', 'twitter', 'linkedin', 'instagram', 'snapchat', 'pinterest', 'api', 'salud', '/es/', 'nih.gov', '#', 'pdf', 'disclaimer', 'polic', 'accessibility', 'privacy', 'developer', 'social', 'recipes', 'data-finder', 'puente', 'anatomia', 'glosario', 'tangier', 'william', 'alzheimer']
    white_list = ['heart', 'disease', 'cardio', 'cardiovascular', 'syndrome', 'risk', 'cardiology']

    valid_blacklist = True
    for black in black_list:
        if black in url:
            valid_blacklist = False

    valid_whitelist = False
    for white in white_list:
        if white in url:
            valid_whitelist = True
    
    return valid_whitelist and valid_blacklist and "http" in url and url.count("/") > 3

# GIVEN URL, SCRAPE THAT SITE FOR MORE URLS AND RETURN THEM IN LIST
def scrape_urls(starter_url):
    r = requests.get(starter_url)

    data = r.text
    soup = BeautifulSoup(data,features="html.parser")

    # write urls to a file
    urls = []
    counter = 0
    for link in soup.find_all('a'):
        l = str(link.get('href'))
        if valid_url(l) and l not in urls:
            urls.append(str(link.get('href')))
        counter += 1

    return urls

# GET DOMAIN NAME FROM URL (ex: "https://www.apple.com/" returns "www.apple.com")
def get_domain(url):
    return url.split("/")[2]

# SCRAPE STARTER SITES TO GET ROUND 1 URLS
# THEN, SCRAPE ROUND 1 URLS FOR ROUND 2 URLS
def initiate_scrape():
    #ROUND 1 SCRAPE: Initial 2 sites
    starter_url = "https://medlineplus.gov/heartdiseases.html"
    collected_urls = [starter_url]

    urls1 = scrape_urls(starter_url)[-15:]
    collected_urls.extend(urls1)

    #scrape secondary site to get urls
    starter_url1 = "https://www.medicalnewstoday.com/articles/237191"
    collected_urls.append(starter_url1)
    urls11 = scrape_urls(starter_url1)
    collected_urls.extend(urls11)

    #ROUND 2 SCRAPE: urls to scrape urls off of them
    urls2 = []
    for i,url in enumerate(urls1):
        result = scrape_urls(url)
        #select websites which return > 0 links and add them to urls list
        if len(result) > 0 and get_domain(url) != get_domain(starter_url):
            urls2.extend(result)
    
    #add urls to collection
    collected_urls.extend(urls2)
    print("#URLS", len(collected_urls))

    #Write each URL’s text to a separate file.
    write_text(collected_urls)

# GIVEN WEBSITE CONTENT AS STRING, REMOVE UNICODE CHARS AND TOKENIZE INTO LIST OF SENTENCES
def clean_up(content):
    content = re.sub(r'[\n]',' ', content)
    content = content.replace("\u00a0", " ")
    content = content.replace("\u2019", "\'")
    content = content.replace("\u2026", ". ")
    content = content.replace("\u201c", ' ')
    content = content.replace("\u201d", ' ')
    content = content.replace("diseaseOutlookSummaryCarotid artery ", '')
    
    sentences = sent_tokenize(content)
    for sentence in sentences:
        sentence_tokens = nltk.word_tokenize(sentence)
        # if sentence contains a word where anything other than first word is capitalized, then remove that sentence.
        for word in sentence_tokens:
            if word[1:] != word[1:].lower():
                try:
                    sentences.remove(sentence)
                except:
                    continue
    return sentences

# PARSE THROUGH FRESHLY SCRAPED FILES, CLEAN THEM UP AND WRITE TO FILES (CLEANED_UP DIRECTORY)
def initiate_cleanup():
    input_path = "raw_scrape"
    output_path = "cleaned_up"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    files = os.listdir(input_path)
    for file in files:
        with open(f"{input_path}/{file}",'r') as f:
            content = f.read()
        content = clean_up(content)
        
        with open(f"{output_path}/{file}", 'w') as fwrite:
            fwrite.write(" ".join(content))
        
# GIVEN DOCUMENT, CREATE TERM FREQUENCY DICTIONARY
def create_tf_dict(doc):
    tf_dict = {}
    tokens = nltk.word_tokenize(doc)
    tokens = [w for w in tokens if w.isalpha() and w not in stopwords]
     
    # get term frequencies
    for t in tokens:
        if t in tf_dict:
            tf_dict[t] += 1
        else:
            tf_dict[t] = 1
            
    # get term frequencies in a more Pythonic way
    token_set = set(tokens)
    tf_dict = {t:tokens.count(t) for t in token_set}
    
    # normalize tf by number of tokens
    for t in tf_dict.keys():
        tf_dict[t] = tf_dict[t] / len(tokens)
        
    return tf_dict

# GIVEN TF AND IDF DICTIONARY, CREATE TFIDF DICTIONARY
def create_tfidf(tf, idf):
    tf_idf = {}
    for t in tf.keys():
        tf_idf[t] = tf[t] * idf[t] 
        
    return tf_idf

# PARSE THROUGH CLEANED-UP FILES AND CALCULATE TF-IDF VALUES (LIST OF IMPORTANT TERMS)
def tf_idf_calc():
    # variables: list of tf dicts, list of idf dicts
    # iterate through files
    tf_dicts = []
    tf_idfs = []
    vocab = set()
    input_path = "cleaned_up"
    files = os.listdir(input_path)
    # for each file:
    for file in files:
        with open(f"{input_path}/{file}",'r') as f:
            content = f.read()
        # tf dict calculation
        curr_tf_dict = create_tf_dict(content)
        tf_dicts.append(curr_tf_dict)
        # add to vocabulary
        vocab = vocab.union(set(curr_tf_dict.keys()))

    # idf dict calculation
    idf_dict = {}

    vocab_by_topic = []
    for tf in tf_dicts:
        vocab_by_topic.append(tf.keys())

    for term in vocab:
        temp = ['x' for voc in vocab_by_topic if term in voc]
        idf_dict[term] = math.log((1+len(files)) / (1+len(temp))) 
    
    # calculate tf-idf
    for tf in tf_dicts:
        tf_idfs.append(create_tfidf(tf, idf_dict))
    
    return files,tf_idfs

# EXTRACT MOST IMPORTANT TERMS FROM TF-IDF LIST
def extract_terms(files,tf_idfs):
    top25 = []
    for file,tf_idf in zip(files,tf_idfs):
        weights = sorted(tf_idf.items(), key=lambda x:x[1], reverse=True)
        #print(file, weights[:5],"\n")
        for weight in weights[:5]:
            if weight[0].lower() not in stopwords:
                top25.append(weight[0])  
    print("TOP 25 WORDS\n", top25)

    # Select words from tf-idf calculation and add some of my own
    trimmed_from_tfidf = ['ischemia', 'help', 'failure', 'valve', 'pain', 'congenital', 'cholesterol']
    top_terms = [ ' term ','risk', 'prevent', 'cure','medicine', 'symptom', 'attack', 'treatment', 'cause', "type", "foods", "hypertension"]
    top_terms.extend(trimmed_from_tfidf)
    return top_terms

# GIVEN LIST OF TERMS, FIND SENTENCES CONTAINING THOSE TERMS AND CREATE A TERM:SENTENCE DICTIONARY (AKA KNOWLEDGE BASE)
def build_kb(top_terms):
    kb = {}
    for term in top_terms:
        kb[term] = []
    input_path = "cleaned_up"
    files = os.listdir(input_path)
    for file in files:
        with open(f"{input_path}/{file}",'r') as f:
            content = f.read()
            sentences = sent_tokenize(content)
            for sentence in sentences:
                sentence = sentence.lower().capitalize()
                for term in top_terms:
                    if term in sentence and "READ MORE" not in sentence and "https" not in sentence.lower() and "?" not in sentence and "Espa" not in sentence and "Index" not in sentence and sentence not in kb[term] and "site content" not in sentence.lower() and "centers for disease control" not in sentence.lower() and "learn about" not in sentence.lower() and "learn more" not in sentence.lower():
                        matches = re.findall(r'\s{4,}', sentence)
                        if not matches:
                            kb[term].append(sentence)
                            
    #print(kb)
    kb['definition'] = kb.pop(' term ')
    print(f"\n{len(kb.keys())} Most Important Terms:\n{list(kb.keys())}")
    pickle.dump(kb, open(f'knowledge_base.p', 'wb'))
    with open("kb.json", "w") as outfile: 
        json.dump(kb, outfile, indent=4)

# MAIN PROGRAM CALLS
print("Raw Scrape")
initiate_scrape()
print("Clean-up")
initiate_cleanup()
print("TF-IDF Calc and Keywords")
files, tf_idfs = tf_idf_calc()
top_terms = extract_terms(files,tf_idfs)
print("Building Knowledge Base")
build_kb(top_terms)