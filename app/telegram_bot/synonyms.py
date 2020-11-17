import requests as req


def find_synonym(*word):

    url = "https://wordsapiv1.p.rapidapi.com/words/get/synonyms"

    headers = {
        'x-rapidapi-key': "7a861b97b1msh795315f8cc4e24dp17d59ajsn01d1cb5156cb",
        'x-rapidapi-host': "wordsapiv1.p.rapidapi.com"
        }

    response = req.request("GET", url, headers=headers)

    return response.text
