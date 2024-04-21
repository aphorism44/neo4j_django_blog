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
                 + "entry that includes that word. Please write a short and descriptive label "
                 + "of 12 words or less to explain what the entry says about that word. Please "
                 + "include the inputed word in the response as the subject of the sentence. Make sure "
                 + "that word is included smoothly within the sentence, and understandable"
                 + "Do not place any words in all-caps besides the inputed word, but make sure to "
                 + "place ONLY the inputed word in all-caps. Write in the first person, from the writer's point of view.")
    prompt_text = ("Please create a sentence of 12 words or less describing how the word "
        + word + " relates to the following passage.Make sure that word is put in all-caps. " + entry_text)
    completion  = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": desc_text},
        {"role": "user", "content": prompt_text}
        ])
    return completion.choices[0].message.content

