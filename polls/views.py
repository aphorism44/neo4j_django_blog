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
    latest_entry = neo4j_crud.get_latest_entry_id(email)
    print(latest_entry)
    previous_entry = neo4j_crud.get_previous_entry(email, 8)
    print(previous_entry)
    next_extry = neo4j_crud.get_next_entry(email, 10)
    print(next_extry)
    template = loader.get_template("polls/editor.html")
    '''context = {
        "entry_id": latest_question_list,
        "previous_entry_id": previous_entry_id,
        "next_extry_id": next_extry_id,
    }
    return HttpResponse(template.render(context, request))
    '''
    return HttpResponse(template.render({}, request))
    
    
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