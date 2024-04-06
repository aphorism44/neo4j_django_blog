from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template import loader

#hardcoded until app is updated for multiuser
email = 'd-jesse@comcast.net'

def index(request):
    template = loader.get_template("polls/index.html")
    return HttpResponse(template.render({}, request))

def editor(request):
    neo4j_crud = request.neo4j_crud
    # ({'created_at': 1712172599628, 'text': 'third entry'}, '4:c3df316c-576d-4e93-8202-9cfd5caf4d33:10')
    # OR None
    latest_entry = neo4j_crud.get_latest_entry(email)
    previous_entry = neo4j_crud.get_previous_entry(email, latest_entry[1])
    next_extry = neo4j_crud.get_next_entry(email, latest_entry[1])
    template = loader.get_template("polls/editor.html")
    context = {
        "entry_id": latest_entry[1],
        "previous_entry_id": None if previous_entry is None else previous_entry[1],
        "next_extry_id": None if next_extry is None else next_extry[1],
    }
    return HttpResponse(template.render(context, request))
    
    
def save(request, entry_id, text):
    neo4j_crud = request.neo4j_crud
    updated_entry = neo4j_crud.update_entry(entry_id, text)
    if not updated_entry:
        raise Http404("Problem")
    template = loader.get_template("polls/editor.html")
    return HttpResponse(template.render({}, None))

def goto_next_entry(request, entry_id, text):
    neo4j_crud = request.neo4j_crud
    updated_entry = neo4j_crud.update_entry(entry_id, text)
    if not updated_entry:
        raise Http404("Problem")
    template = loader.get_template("polls/editor.html")
    return HttpResponse(template.render({}, None))

def goto_previous_entry(request, entry_id, text):
    neo4j_crud = request.neo4j_crud
    updated_entry = neo4j_crud.update_entry(entry_id, text)
    if not updated_entry:
        raise Http404("Problem")
    template = loader.get_template("polls/editor.html")
    return HttpResponse(template.render({}, None))

def lists(request):
    neo4j_crud = request.neo4j_crud
    all_entries = neo4j_crud.get_all_entries(email)
    if not all_entries:
        raise Http404("Problem no entries")
    return render(request, "polls/lists.html", {"entries": all_entries})


#only run this once to populate a test database    
def populate_test_database(request):
    neo4j_crud = request.neo4j_crud
    q1 = neo4j_crud.create_question("Who discovered America?")
    neo4j_crud.add_choice_to_question(q1['id'], "Ferdinand Magellan")
    neo4j_crud.add_choice_to_question(q1['id'], "Vasco de Gama")
    neo4j_crud.add_choice_to_question(q1['id'], "Christopher Columbus")
    neo4j_crud.add_choice_to_question(q1['id'], "Walter Raleigh")
    q2 = neo4j_crud.create_question("Which of these signed the Declaration of Independence?")
    neo4j_crud.add_choice_to_question(q2['id'], "George Washington")
    neo4j_crud.add_choice_to_question(q2['id'], "John Adams")
    neo4j_crud.add_choice_to_question(q2['id'], "Alexander Hamilton")
    neo4j_crud.add_choice_to_question(q2['id'], "James Madison")