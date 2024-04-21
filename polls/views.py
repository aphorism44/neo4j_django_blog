from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_protect

from .forms import EntryForm
from .analysis import create_ai_analyzed_map, get_matched_words_dict, get_full_dict

#hardcoded until app is updated for multiuser
email = 'd-jesse@comcast.net'
#hardcoded until this is pinned to environment
url_line = "http://127.0.0.1:8000/"

def index(request):
    template = loader.get_template("polls/index.html")
    return HttpResponse(template.render({}, request))

@csrf_protect
def editor(request):
    template = loader.get_template("polls/editor.html")
    neo4j_crud = request.neo4j_crud
    if request.method == "POST":
        original_entry_form = EntryForm(request.POST)
        if (original_entry_form.is_valid()):
            if 'save' in request.POST.dict().keys():
                entry_id = original_entry_form.cleaned_data["entry_id"]
                entry_text = original_entry_form.cleaned_data["text"]
                next_entry_id = original_entry_form.cleaned_data["next_entry_id"]
                previous_entry_id = original_entry_form.cleaned_data["previous_entry_id"]
                neo4j_crud.update_entry(entry_id, entry_text)
                entry_form = EntryForm(initial={
                    "text" : "" if entry_text is None else entry_text,
                    "entry_id": entry_id,
                    "previous_entry_id": None if len(previous_entry_id) < 1 else previous_entry_id,
                    "next_entry_id": None if len(next_entry_id) < 1 else next_entry_id,
                })
            elif 'previous' in request.POST.dict().keys():
                entry_id = original_entry_form.cleaned_data["entry_id"]
                entry_text = original_entry_form.cleaned_data["text"]
                previous_entry_id = original_entry_form.cleaned_data["previous_entry_id"]
                neo4j_crud.update_entry(entry_id, entry_text)
                previous_entry = neo4j_crud.get_previous_entry(email, entry_id)
                new_previous_entry = neo4j_crud.get_previous_entry(email, previous_entry[1])
                entry_form = EntryForm(initial={
                    "text" : "" if previous_entry is None else previous_entry[0]['text'],
                    "entry_id": previous_entry_id,
                    "previous_entry_id": None if new_previous_entry is None else new_previous_entry[1],
                    "next_entry_id": entry_id,
                })
            elif 'next' in request.POST.dict().keys():
                entry_id = original_entry_form.cleaned_data["entry_id"]
                entry_text = original_entry_form.cleaned_data["text"]
                next_entry_id = original_entry_form.cleaned_data["next_entry_id"]
                neo4j_crud.update_entry(entry_id, entry_text)
                next_entry = neo4j_crud.get_next_entry(email, entry_id)
                new_next_entry = neo4j_crud.get_next_entry(email, next_entry_id)
                entry_form = EntryForm(initial={
                    "text" : "" if next_entry is None else next_entry[0]['text'],
                    "entry_id": next_entry_id,
                    "previous_entry_id": None if entry_id is None else entry_id,
                    "next_entry_id": None if new_next_entry is None else new_next_entry[1],
                })
            elif 'new' in request.POST.dict().keys():
                entry_id = original_entry_form.cleaned_data["entry_id"]
                entry_text = original_entry_form.cleaned_data["text"]
                previous_entry_id = original_entry_form.cleaned_data["previous_entry_id"]
                new_entry_id = neo4j_crud.create_empty_entry(email)
                neo4j_crud.link_entry_chain(entry_id, new_entry_id)
                #save the current page
                neo4j_crud.update_entry(entry_id, entry_text)
                #move onto next page
                entry_form = EntryForm(initial={
                    "text" : "",
                    "entry_id": new_entry_id,
                    "previous_entry_id": entry_id,
                    "next_entry_id": None,
                })
    else:
        #user is starting up editor; get latest entry
        latest_entry = neo4j_crud.get_latest_entry(email)
        entry_id = latest_entry[1]
        entry_text = " " if 'text' not in latest_entry[0] else latest_entry[0]['text']
        previous_entry = neo4j_crud.get_previous_entry(email, latest_entry[1])
        entry_form = EntryForm(initial={
            "text" : "" if entry_text is None else entry_text,
            "entry_id": entry_id,
            "previous_entry_id": None if previous_entry is None else previous_entry[1],
            "next_entry_id": None,
        })
    context = { 'form' : entry_form }
    return HttpResponse(template.render(context, request))

#this is for initial setup - need to find way to do it piecemeal
def analysis(request):
    neo4j_crud = request.neo4j_crud
    full_dict = {}
    # of the format   keyWord -> List(of labels), parallel List (of entry IDs they refer to)
    # need to add these key words to Neo4j schema (MERGE)
    # {'time': (['TIME is crucial as the blogger tests a new blog engine and plans upgrades.'
    #, "The passage reflects on Joey's struggles with drugs over TIME in his short life."]
    # , ['4:c3df316c-576d-4e93-8202-9cfd5caf4d33:8', '4:c3df316c-576d-4e93-8202-9cfd5caf4d33:4'])}
    full_dict = create_ai_analyzed_map(request, email)
    for key, value in full_dict.items():
        neo4j_crud.add_keyword(email, key)
        phrase_array = value[0]
        entry_id_array = value[1]
        for idx, phrase in enumerate(phrase_array, start=0):
            entry_id = entry_id_array[idx]
            neo4j_crud.attach_keyword_to_entry(email, entry_id, phrase, key)
    return render(request, "polls/analysis.html", {"word_map": full_dict})

@csrf_protect
def blog_entry(request, entry_id = None):
    template = loader.get_template("polls/blog_entry.html")
    neo4j_crud = request.neo4j_crud
    if entry_id is not None:
        current_entry, entry_id = neo4j_crud.get_entry_by_id(email, entry_id)
        entry_text = current_entry['text']
        next_response = neo4j_crud.get_next_entry(email, entry_id)
        if next_response is None:
            next_entry_id = None
        else:
            next_entry_id = next_response[1]
        previous_response = neo4j_crud.get_previous_entry(email, entry_id)
        if previous_response is None:
            previous_entry_id = None
        else:
            previous_entry_id = previous_response[1]
    elif 'next' in request.POST.dict().keys():
        current_entry_id = request.POST.dict()['entry_id']
        current_next_entry_id = request.POST.dict()['next_entry_id']
        entry, entry_id = neo4j_crud.get_entry_by_id(email, current_next_entry_id)
        entry_text = entry['text']
        previous_entry_id = current_entry_id
        next_response = neo4j_crud.get_next_entry(email, entry_id)
        if next_response is None:
            next_entry_id = None
        else:
            next_entry_id = next_response[1]
    elif 'previous' in request.POST.dict().keys():
        current_entry_id = request.POST.dict()['entry_id']
        current_previous_entry_id = request.POST.dict()['previous_entry_id']
        entry, entry_id = neo4j_crud.get_entry_by_id(email, current_previous_entry_id)
        entry_text = entry['text']
        previous_response = neo4j_crud.get_previous_entry(email, entry_id)
        if previous_response is None:
            previous_entry_id = None
        else:
            previous_entry_id = previous_response[1]
        next_entry_id = current_entry_id
    elif len(request.POST.dict()) < 1:
        first_entry, entry_id = neo4j_crud.get_first_entry(email)
        entry_text = first_entry['text']
        previous_entry_id =  None
        next_entry, next_entry_id = neo4j_crud.get_next_entry(email, entry_id)
    #update text with links
    entry_keywords = neo4j_crud.get_all_entry_keywords(email, entry_id)
    used_keyword = set()
    if entry_keywords is not None:
        for result in entry_keywords:
            word = result['keyword']
            if word not in used_keyword:
                used_keyword.add(word)
                entry_text = entry_text.replace(word, '<a href="' + url_line + '/polls/blog_keyword/' + word + '">' + word + '</a>')
    context = {
        'entry_id': entry_id,
        'entry_text': entry_text,
        'previous_entry_id': previous_entry_id,
        'next_entry_id': next_entry_id
    }
    return HttpResponse(template.render(context, request))

@csrf_protect
def blog_keyword(request, keyword):
    template = loader.get_template("polls/blog_keyword.html")
    neo4j_crud = request.neo4j_crud
    entry_keywords = neo4j_crud.get_all_keyword_entries(email, keyword)
    context = { "keyword": keyword }
    item_list = []
    if entry_keywords is not None:
        for record in entry_keywords:
            phrase = '<a href="' + url_line + '/polls/blog_entry/' + record['entry_id'] + '">' + record['phrase'] + '</a>'
            item_list.append(phrase)
    print(item_list)
    context['item_list'] = item_list
    print(context)
    return HttpResponse(template.render(context, request))