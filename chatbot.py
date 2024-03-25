# NECESSARY LIBRARIES
'''
pip install nltk
pip install spacy
python3 -m spacy download en_core_web_sm
(Possibly) pip install scikit-learn
'''
from random import randint
import time
import pickle
import nltk
import difflib
import os
import json
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

wnl = nltk.stem.WordNetLemmatizer()
nlp = spacy.load('en_core_web_sm')

# KEYWORDS, GREETINGS, CONFUSED, AND OTHER STATEMENTS
EXIT_KEYWORD = "exit"
required = f"Enter your question or '{EXIT_KEYWORD}' to exit the program"
starter_prompt = [
    "How can I assist you today with information about heart disease?",
    "I'm here to provide you with answers to any questions you have about heart disease. Ask away!",
    "Let's talk about heart disease and how to keep your heart healthy.",
    "I'm your heart health companion. What would you like to know about heart disease?",
    "I'm here to provide guidance on understanding and managing heart disease. Let's get started.",
    "Let's chat about heart health and how you can maintain a healthy heart."
]
greetings = "Welcome! My name is HeartWise, your heart companion. What is your name?"
confused = [
    "I'm sorry, I didn't quite catch that. Could you please rephrase your question?",
    "Apologies, I'm not sure I follow. Can you clarify or ask a different question?",
    "I'm sorry, I'm not equipped to handle that request. Is there something else I can assist you with?",
    "I'm still learning about heart disease and may not have the answer to that question. Is there anything else you'd like to know?"
]
kb = pickle.load(open('knowledge_base.p', 'rb'))

# HELPER METHODS FOR DISPLAYING TEXT
def display_greeting():
    print(f"\n{greetings}")

def display_confused():
    print(f"\n{confused[randint(0, len(confused)-1)]}")

def display_starter_prompt(name):
    print(f"\nHello {name.capitalize()}! {starter_prompt[randint(0, len(starter_prompt)-1)]}\n{required}")

def tfidf_extract(sentence):
    # Create a TF-IDF Vectorizer and get the feature names
    tokens = nltk.word_tokenize(sentence)
    tfidf_vectorizer = TfidfVectorizer(max_features=5)
    tfidf_vectorizer.fit(tokens)
    keywords = tfidf_vectorizer.get_feature_names_out()
    return keywords

# FROM GIVEN SENTENCE, EXTRACT KEYWORDS
def get_keywords(sentence):
    output = {
        "confirmed_keywords": [],
        "unconfirmed_keywords": []
    }
    if sentence.lower() in kb.keys():
        return [sentence.lower()]
    else:
        sentence = sentence.lower().replace("what is", "definition")
        tokens = tfidf_extract(sentence)
        tokens = [t.lower() for t in tokens]
        tokens = [t for t in tokens if t.isalpha() and
            t not in nltk.corpus.stopwords.words('english')]
        tokens = [wnl.lemmatize(t) for t in tokens]

        for token in tokens:
            if token == "heart":
                continue
            possible_replacement = difflib.get_close_matches(token,kb.keys(),cutoff=0.75)
            if len(possible_replacement) != 0:
                output["confirmed_keywords"].extend(possible_replacement)
            else:
                output["unconfirmed_keywords"].append(token)
        return output

# GIVEN LIST OF KEYWORDS, GRAB ANSWER FROM KB
def select_answer(keywords):
    final_answer = []
    for keyword in keywords['confirmed_keywords']:
        all_answers = kb[keyword]
        valid_answers = []
        for answer in all_answers:
            #Only keep answers which contain all confirmed_keywords
            valid1 = True
            for keyword in keywords['confirmed_keywords']:
                if keyword.lower() == "definition":
                    keyword = "term"
                
                if keyword not in answer:
                    valid1 = False
            
            valid2 = False
            for keyword in keywords['unconfirmed_keywords']:
                if keyword in answer:
                    valid2 = True
            if len(keywords['unconfirmed_keywords']) == 0:
                valid2 = True

            if valid1 and valid2:
                valid_answers.append(answer)
            
        final_answer.extend(valid_answers)

    # For testing purposes: writing potential answers to file
    # with open("answer.txt", 'w') as f:
    #     f.write(f"Answers containing {keywords['confirmed_keywords'] + keywords['unconfirmed_keywords']}\n")
    #     f.write('\n'.join(final_answer))
        
    if len(final_answer) != 0:
        return final_answer[randint(0,len(final_answer)-1)]
    else:
        return None
        
# INITIALIZE USER JSON FILE
def create_user_file(name):
    user_dict = {
        "Name": name,
        "Questions": [],
        "Likes": [],
        "Dislikes": [],
        "Feedback": []
        }
    with open(f'users/{name}.json', 'w') as json_file:
        json.dump(user_dict, json_file, indent=4)

# CHECK IF USERNAME.JSON EXISTS
def does_user_exist(name):
    users = []
    if not os.path.exists("users"):
        os.makedirs("users")
    else:
        for file in os.listdir("users"):
            users.append(file.split(".")[0])

    for user in users:
        if name.lower() == user:
            return True    
    return False

# GIVEN NAME AND QUESTION CATEGORY, WRITE USER-INPUT TO APPROPRIATE FILE IN THE RIGHT PLACE
def write_user_question(name, user_input, category):
    #open name.json
    #Get "Questions" attribute.
    with open(f"users/{name}.json", "r") as file:
        user_dict = json.load(file)
    user_dict[category].append(user_input)

    with open(f'users/{name}.json', 'w') as json_file:
        json.dump(user_dict, json_file, indent=4)
    return

# GIVEN CATEGORY, GET PREVIOUS ANSWER (IF EXISTING)
def get_previous_user_answer(name, category):
    with open(f"users/{name}.json", "r") as file:
        user_dict = json.load(file)
    all_previous_answers = user_dict[category]
    if len(all_previous_answers) == 0:
        return None
    else:
        return all_previous_answers[randint(0,len(all_previous_answers)-1)]

# ASK USER A QUESTION ABOUT THEIR LIKES, DISLIKES, OR ASK FOR FEEDBACK
def ask_other_question(name):
    # Questions for each category
    likes = [f"Just wondering {name}, what are your interests?",
            f"Sorry for digress, but can you tell me about your hobbies or interests {name}?",]
    dislikes = [f"Before I forget, I'm curious to know about any activities, foods, or preferences you don't like?",
                "Before we dive deeper into the previous topic, I wanted to ask about your preferences. Are there any particular things that you'd rather pass on or avoid?"]
    feedback = [f"Sorry to interrupt {name}. Can I get some feedback about my chatbot skills?",
                f"Before we move on, do you mind giving me some feedback about how this conversation is going {name}?"]
    
    # Use random number to select type of question. Display it while referencing previous answer (if available)
    topic_num = randint(0,4)
    question_num = randint(0,1)
    if topic_num == 0 or topic_num == 1:
        category = "Likes"
        question = likes[question_num]
        previous_answer = get_previous_user_answer(name,category)
        if previous_answer is not None:
            question += f" You previously said one of your {category.lower()} was \"{previous_answer}\". What else would you like to add on?"

    elif topic_num == 2:
        category = "Dislikes"
        question = dislikes[question_num]
        previous_answer = get_previous_user_answer(name,category)
        if previous_answer is not None:
            question += f" You previously said one of your {category.lower()} was \"{previous_answer}\". What else would you like to add on?"
    else:
        category = "Feedback"
        question = feedback[question_num]
        previous_answer = get_previous_user_answer(name,category)
        if previous_answer is not None:
            question += f" You previously said your {category.lower()} was \"{previous_answer}\". What else would you like to add on?"
    
    return question, category



# MAIN METHOD
def start_bot():
    display_greeting()
    name = input("> ").lower()
    # check if name exists. if yes, then get user info. if not, create file for them.
    if not does_user_exist(name):
        create_user_file(name)
    display_starter_prompt(name)
    user_input = ""
    while user_input != EXIT_KEYWORD:
        #RANDOMLY ASK QUESTIONS LIKE "ARE YOU FEELING SATISFIED WITH THIS CONVERSTAION" OR "WHAT ARE YOUR INTERESTS?" OR ETC
        qnum = randint(1,3)
        # Random question
        if qnum == 3 and user_input != "":
            question, category = ask_other_question(name)
            print("\n",question)
            user_input = input("> ")
            if user_input == EXIT_KEYWORD:
                break
            write_user_question(name, user_input, category)
            print("Thank you for your response!")
            
        # Continue with conversation
        else:
            user_input = input("> ")
            if user_input == EXIT_KEYWORD:
                break
            write_user_question(name, user_input, "Questions")
            time.sleep(randint(1,3))
            keywords = get_keywords(user_input)
            # If there are not keywords, display confused message. Else, display answer.
            if len(keywords['confirmed_keywords']) == 0:
                display_confused()
            else:
                answer = select_answer(keywords)
                if answer is not None:
                    print(answer)
                else:
                    display_confused()

start_bot()