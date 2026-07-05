import openai

def get_gpt3_response(prompt):
    #you need your own openai api key
    # (openai.api_key = ' ') format
    
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()
