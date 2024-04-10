import os
from openai import OpenAI
from decouple import config

client = OpenAI(
  api_key=config('OPEN_AI_KEY'),
)

def get_entry_word_label(request, word, entry_id):
    neo4j_crud = request.neo4j_crud
    entry = neo4j_crud.get_entry_by_id(entry_id)
    entry_text = entry[0]['text']
    desc_text = ("You are a blog writer's assistant. You will be given a single word, and a blog "
                 + "entry that includes that word. Please write a short and descriptive sentence "
                 + "of less than 10 characters to explain what the entry says about that word. "
                 + "Remember that the blogger is writing personal things in this blog.")
    prompt_text = ("Please create a sentence of 10 words or less describing how the word "
        + word + " relates to the following passage, keeping all proper names intact. " + entry_text)
    completion  = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": desc_text},
        {"role": "user", "content": prompt_text}
        ])
    return completion.choices[0].message.content

