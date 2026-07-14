class ChatEngine:
    def __init__(self, plugin):
        self.plugin = plugin
        self.perms = plugin.permissions

    def process(self, event) -> bool:
        player = event.player
        prefix = getattr(player, "_prefix", "§7")
        event.formatted = f"{prefix}{player.name}§f: {event.message}"
        return True

    def send_ActionBar(self, player, text: str):
        player.send_action_bar(text)
