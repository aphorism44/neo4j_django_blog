import nltk
import collections
nltk.download("stopwords")
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from polls.ai_calls import get_entry_word_label

language = 'english'

def create_ai_analyzed_map(request, email):
    matched_word_dict = get_matched_words_dict(request, email)
    analyzed_word_dict = {}
    for key, value in matched_word_dict.items():
        tag_list = []
        parallel_id_list = []
        for entry_id in value:
            label = get_entry_word_label(request, key, entry_id)
            tag_list.append(label)
            parallel_id_list.append(entry_id)
        analyzed_word_dict[key] = tag_list, parallel_id_list
    return analyzed_word_dict


def get_matched_words_dict(request, email):
    matched_words_dict = {}
    full_dict = get_full_dict(request, email)
    #change from ID -> words to word -> IDs
    word_set = set()
    for key, value in full_dict.items():
        word_set.update(value)
    for word in word_set:
        id_set = set()
        for key, value in full_dict.items():
            if word in value:
                id_set.add(key)
        if len(id_set) > 1:
            matched_words_dict[word] = id_set
    return matched_words_dict


def get_full_dict(request, email):
    dict_full = {}
    dict_noun = noun_map(request, email)
    dict_proper_noun = proper_noun_map(request, email)
    for key, value in dict_noun.items():
        if key in dict_proper_noun.keys():
            correspond_set = dict_proper_noun[key]
            full_set = value.union(correspond_set)
            dict_full[key] = full_set
    #edge case - empty tokens in any entry
    for key, value in dict_proper_noun.items():
        if key in dict_noun.keys():
            if key not in dict_full.keys():
                dict_full[key] = value
    return dict_full

def noun_map(request, email):
    neo4j_crud = request.neo4j_crud
    list = neo4j_crud.get_all_entries(email)
    list_dict = {}
    for item in list:
        noun_set = set()
        entry_text = "" if item['e']['text'] is None else item['e']['text']
        words_in_text = word_tokenize(entry_text, language=language)
        if len(words_in_text) > 0:
            tagged_words = nltk.pos_tag(words_in_text)
            for word_tags in tagged_words:
                if 'NN' in word_tags[1]:
                    noun_set.add(word_tags[0])
        list_dict[item['entry_id']] = noun_set
    return list_dict

def proper_noun_map(request, email):
    neo4j_crud = request.neo4j_crud
    list = neo4j_crud.get_all_entries(email)
    list_dict = {}
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))
    for item in list:
        entry_text = "" if item['e']['text'] is None else item['e']['text']
        if len(entry_text) > 0:
            words_in_quote = word_tokenize(entry_text, language=language)
            lemmatized_words = [lemmatizer.lemmatize(word) for word in words_in_quote]
            filtered_list = []
            for word in lemmatized_words:
                if word.casefold() not in stop_words:
                    filtered_list.append(word)
            tags = nltk.pos_tag(filtered_list)
            tree = nltk.ne_chunk(tags, binary=True)
            work_set = set(
                 " ".join(i[0] for i in t)
                 for t in tree
                 if hasattr(t, "label") and t.label() == "NE"
             )
            list_dict[item['entry_id']] = work_set
    return list_dict
