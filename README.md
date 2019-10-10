# Aparaticos-yt-chat-userlist

Youtube chat processor.

We initially used this to interact with our audience in [our livestreams](https://youtube.com/Aparaticos), hope this can help someone else.

It's still a bit untidy, srry :S.

## Installation

This uses python3. Install libs with:

```
pip install -r requirements.txt
```

Then copy client_secrets_example.json to client_secrets.json

```
cp client_secrets_example.json client_secrets.json
```

Edit client_secrets.json and:

1. Populate with your youtube dev credentials.
2. Remove the steps lines.
3. Save and close.

Then run:

```
python -u yt-chat-userlist.py
```
