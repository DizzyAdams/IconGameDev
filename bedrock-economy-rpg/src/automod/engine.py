import re, time
from collections import defaultdict

FILTERED_WORDS = ["spam", "scam", "cheat", "hack", "discord.gg/", "buy", "sell"]
SPAM_WINDOW = 3
SPAM_THRESHOLD = 3


class AutoMod:
    def __init__(self, plugin):
        self.plugin = plugin
        self._messages = defaultdict(list)

    def check_chat(self, xuid, message):
        now = time.time()
        lower = message.lower()

        for word in FILTERED_WORDS:
            if word in lower:
                return False, f"Filtered word: {word}"

        self._messages[xuid].append(now)
        self._messages[xuid] = [t for t in self._messages[xuid] if now - t < SPAM_WINDOW]
        if len(self._messages[xuid]) > SPAM_THRESHOLD:
            return False, "Spam detected"

        caps = sum(1 for c in message if c.isupper())
        if len(message) > 10 and caps / len(message) > 0.7:
            return False, "Too many caps"

        return True, None

    def check_sign(self, text):
        lower = text.lower()
        for word in FILTERED_WORDS:
            if word in lower:
                return False
        return True
