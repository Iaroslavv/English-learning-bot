# Project description

It is a simple web service that allows you to train synonyms for English words using telegram bot.
At first you need to register on the website and go to your account where you'll see a personal access link to telegram bot.
Once activated, you can add a list of words, for which you want to get synonyms. 
On study mode you get a random word from your wordlist, for which you need to write a synonym. If it is a synonym, you get a point.
The results are displayed in telegram bot as well as on your account page.

## Installation

```bash
git clone https://github.com/Iaroslavv/English-learning-bot.git
pip install requirements.txt
```
## Running tests

```python
python -m unittest -v app/tests/test_users.py 
```

## Usage

Don't forget to change an email username and password.
To use the searchbar you have to download and install [Elasticsearch](https://www.elastic.co/downloads/elasticsearch). In settings change the http to localhost.
To run the app, launch run.py

## What I've learned
#### - The basics of Elasticsearch
#### - Telebot library
#### - Unittests
#### - One to many db relationship with SQLAlchemy


### P.S.
There are a few bugs that i haven't fixed. They are mainly related to frontend part.
When signing up you have to type your password twice.
Searchbar doesn't work as i expected it to.


