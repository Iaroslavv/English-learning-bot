import requests as req
import json


def find_synonym(*args):
    """Looks for the similar word."""
    try:
        for param in args:
            url = f"https://wordsapiv1.p.rapidapi.com/words/{param}/synonyms"

            headers = {
                'x-rapidapi-key': "7a861b97b1msh795315f8cc4e24dp17d59ajsn01d1cb5156cb",
                'x-rapidapi-host': "wordsapiv1.p.rapidapi.com"
                }

            response = req.request("GET", url, headers=headers)
            get_response = response.text
            answer = json.loads(get_response)
            final_answer = answer["synonyms"]
        return final_answer
    except Exception as e:
        return str(e)
