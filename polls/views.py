from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_protect

from .forms import EntryForm 

#hardcoded until app is updated for multiuser
email = 'd-jesse@comcast.net'

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

def lists(request):
    neo4j_crud = request.neo4j_crud
    all_entries = neo4j_crud.get_all_entries(email)
    if not all_entries:
        raise Http404("Problem no entries")
    return render(request, "polls/lists.html", {"entries": all_entries})

