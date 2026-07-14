"""Economy + RPG Endstone Plugin for Minecraft Bedrock Edition."""
from endstone.plugin import Plugin


class EconomyRpgPlugin(Plugin):
    """Main plugin entry point — orchestrates all subsystems."""

    api_version = "0.11"

    def on_enable(self) -> None:
        self.logger.info("=== Bedrock Economy+RPG v1.0.0 ===")
        self._load_config()
        loop = self.server.loop
        loop.create_task(self._init_async())
        self._init_economy()
        self._init_rpg()
        self._init_permissions()
        self._init_chat()
        self._init_anticheat()
        self._register_commands()
        self.register_events(self)
        self.logger.info("Plugin enabled — loading subsystems async...")

    async def _init_async(self):
        await self._init_db()
        await self._init_cache()
        self.logger.info("Database & cache connected.")

    def on_disable(self) -> None:
        self.logger.info("Disabling Bedrock Economy+RPG...")
        if hasattr(self, "_db"):
            self.server.loop.create_task(self._db.close())
        if hasattr(self, "_cache"):
            self.server.loop.create_task(self._cache.close())
        self.logger.info("Plugin disabled.")

    # ------------------------------------------------------------------
    # Initialization helpers
    # ------------------------------------------------------------------

    def _load_config(self) -> None:
        from src.core.config import ConfigManager
        self.config_mgr = ConfigManager(self)
        self.cfg = self.config_mgr.load()

    async def _init_db(self) -> None:
        from src.db.postgres import PostgresPool
        self._db = PostgresPool(self.cfg["database"])
        await self._db.connect()

    async def _init_cache(self) -> None:
        from src.db.redis_cache import RedisCache
        self._cache = RedisCache(self.cfg["cache"])
        await self._cache._client.ping()

    def _init_economy(self) -> None:
        from src.economy.engine import EconomyEngine
        self.economy = EconomyEngine(self)

    def _init_rpg(self) -> None:
        from src.rpg.engine import RpgEngine
        self.rpg = RpgEngine(self)

    def _init_permissions(self) -> None:
        from src.permissions.engine import PermissionEngine
        self.permissions = PermissionEngine(self)

    def _init_chat(self) -> None:
        from src.chat.engine import ChatEngine
        self.chat = ChatEngine(self)

    def _init_anticheat(self) -> None:
        from src.anticheat.engine import AntiCheatEngine
        self.anticheat = AntiCheatEngine(self)

    def _register_commands(self) -> None:
        from src.commands.register import register_all
        register_all(self)

    # ------------------------------------------------------------------
    # Event Handlers
    # ------------------------------------------------------------------

    from endstone.event import event_handler, PlayerJoinEvent, PlayerQuitEvent, PlayerChatEvent

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent) -> None:
        player = event.player
        self.server.loop.create_task(
            self._ensure_player_data(player)
        )
        self.chat.send.ActionBar(
            player,
            f"§aWelcome {player.name}! Type /help for commands.",
        )

    @event_handler
    def on_player_quit(self, event: PlayerQuitEvent) -> None:
        player = event.player
        self.server.loop.create_task(
            self._save_player_data(player)
        )

    @event_handler
    def on_player_chat(self, event: PlayerChatEvent) -> None:
        if not self.chat.process(event):
            event.cancelled = True

    # ------------------------------------------------------------------
    # Player data lifecycle
    # ------------------------------------------------------------------

    async def _ensure_player_data(self, player) -> None:
        xuid = player.xuid if hasattr(player, "xuid") else player.name
        row = await self._db.fetchrow(
            "SELECT perm_group FROM players WHERE xuid = $1", xuid,
        )
        if row:
            player._group = row["perm_group"]
        else:
            await self._db.execute(
                "INSERT INTO players (xuid, name, class, level, xp, coins, gems, perm_group) "
                "VALUES ($1, $2, 'adventurer', 1, 0, 100, 0, 'default')",
                xuid, player.name,
            )
            player._group = "default"
        player._prefix = self.permissions.get_prefix(player._group)

    async def _save_player_data(self, player) -> None:
        pass  # handled by subsystems on demand
