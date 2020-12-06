# sarathi

The bot for my private discord channel.

## Introduction

[I maintain a TIL page on my blog.](https://stonecharioteer.com/til.html)
It's becoming a bit tiresome to maintain it, so I've been
meaning to write a bot on any platform to manage it. Lately, I've started using discord and
I like it. The API is well documented and doesn't seem to change out of the blue. So I'm
setting myself a task to create a bot that updates the TIL page, and maintains a usable set
of commands that I can continue to add to.

## Feature List

I maintain a comprehensive list of features and roadmap in my TODO file maintained in this repo.

## Installation

```bash

conda create -n sarathi python=3.9
conda activate sarathi
pip install -r requirements.txt
```

## Configuration

Create a .env file with the following variables:

```python
DISCORD_TOKEN="Token Here"
DISCORD_GUILD="Guild Name here"
TIL_JSON_PATH="Absolute path to TIL JSON here"
BLOG_PATH="Absolute path to checked out clone of blog here"
```

## Running

### Development

```bash
python -u sarathi.py
```

### With `systemd`

Configure the systemd service file to `~/.config/systemd/user/sarathi.service` and run:

```
systemctl --user daemon-reload
systemctl --user enable sarathi
systemctl --user start sarathi
```

# Development

This project uses `python=3.9` and `pytest` for development.

# References:

1. [Real Python - Creating a Discord Bot](https://realpython.com/how-to-make-a-discord-bot-python/#how-to-make-a-discord-bot-in-python)
2. [Discord Developer Documentation](https://discord.com/developers/docs/intro)
