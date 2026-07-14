import time, math
from collections import defaultdict

MAX_SPEED = 20.0
MAX_FLY_TICKS = 5
MAX_REACH = 6.0
MAX_CLICK_RATE = 15


class AntiCheatEngine:
    def __init__(self, plugin):
        self.plugin = plugin
        self._movements = defaultdict(list)
        self._clicks = defaultdict(list)
        self._flags = defaultdict(int)
        self._last_pos = {}
        self._violations = defaultdict(int)

    def check_movement(self, player, to):
        xuid = getattr(player, "xuid", player.name)
        now = time.time()
        prev = self._last_pos.get(xuid)
        self._last_pos[xuid] = to

        if prev:
            dt = max(now - self._movements[xuid][-1][0] if self._movements[xuid] else 0.05, 0.05)
            dx = to.x - prev.x
            dy = to.y - prev.y
            dz = to.z - prev.z
            speed = math.sqrt(dx*dx + dy*dy + dz*dz) / dt

            if speed > MAX_SPEED:
                return self._flag(xuid, "speed", speed)
            if dy < -0.5 and not player.is_on_ground:
                return self._flag(xuid, "fly", dy)

        self._movements[xuid].append((now, to.y))
        self._movements[xuid] = [m for m in self._movements[xuid] if now - m[0] < 5]
        return True

    def check_reach(self, player, distance):
        xuid = getattr(player, "xuid", player.name)
        if distance > MAX_REACH:
            return self._flag(xuid, "reach", distance)
        return True

    def check_click(self, player):
        xuid = getattr(player, "xuid", player.name)
        now = time.time()
        self._clicks[xuid].append(now)
        self._clicks[xuid] = [c for c in self._clicks[xuid] if now - c < 1]
        if len(self._clicks[xuid]) > MAX_CLICK_RATE:
            return self._flag(xuid, "autoclicker", len(self._clicks[xuid]))
        return True

    def _flag(self, xuid, check_type, value):
        self._violations[xuid] += 1
        self._flags[xuid] += 1
        if self._violations[xuid] >= 10:
            self.plugin.server.dispatch_command(
                f"kick {xuid} §c[AntiCheat] {check_type.upper()} detected"
            )
            self._violations[xuid] = 0
            return False
        return True

    def reset_violations(self, xuid):
        self._violations[xuid] = 0
