import openai
from decouple import config

openai.api_key = config('OPEN_AI_KEY')

def get_entry_word_label(word, entry):
    prompt_text = ("Please create a sentence of 10 words or less describing how the word "
        + word + " relates to the following passage, keeping all proper names intact. " + entry)
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=prompt_text,
        temperature=0.7,
        max_tokens=100,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    print(response)
    return response.choices[0].text.strip()

