#  Comparativo de Plataformas de Modding Bedrock

> **Arquitetura Bedrock Server Mods** | Documento gerado em 2026-06-25

---

## LeviLamina vs Endstone vs BDSX vs PMMP



### LeviLamina (LiteLDev)

- **Linguagem**: C++ nativo + LSE (Lua/JS/Python/Node)
- **Performance**: Máxima - hooks diretos no BDS
- **Compatibilidade**: Windows (Linux via Wine/Proton limitado)
- **Ecossistema**: 1500+ stars, lip package manager, LeviAntiCheat
- **Melhor para**: Servidores grandes, anti-cheat, modificações profundas de gameplay

```cpp
// Exemplo de hook C++ LeviLamina
LL_AUTO_TYPE_INSTANCE_HOOK(
    PlayerJoinEventHook, HookPriority::Normal,
    ServerPlayer, &ServerPlayer::setLocalPlayerAsInitialized,
    void, ()
) {
    auto& player = *this;
    Logger::info("Player joined: {}", player.getRealName());
    origin();
}
```

### Endstone (EndstoneMC)

- **Linguagem**: Python 3.10+ / C++
- **Performance**: Alta - API de alto nível sobre BDS
- **Compatibilidade**: Windows e Linux nativo
- **Ecossistema**: PyPI, Docker, Pterodactyl egg, Endweave (ViaVersion)
- **Melhor para**: Desenvolvimento rápido, cross-platform, devs familiarizados com Bukkit/Paper

```cpp
# Exemplo de plugin Python Endstone
from endstone.plugin import Plugin
from endstone.event import event_handler, PlayerJoinEvent

class WelcomePlugin(Plugin):
    api_version = "0.11"
    
    @event_handler
    def on_player_join(self, event: PlayerJoinEvent):
        event.player.send_message(f"Bem-vindo, {event.player.name}!")
```

### BDSX (Karikera)

- **Linguagem**: Node.js / TypeScript
- **Performance**: Média-Alta - runtime ChakraCore
- **Compatibilidade**: Windows apenas
- **Ecossistema**: NPM packages, type definitions robustas
- **Melhor para**: Devs JavaScript/TypeScript, integrações web

```cpp
// Exemplo BDSX
import { events } from 'bdsx/events';
import { MinecraftPacketIds } from 'bdsx/bds/packetids';

events.packetAfter(MinecraftPacketIds.Text).on((ptr, networkIdentifier, packetId) => {
    console.log(`Chat: ${ptr.message}`);
});
```

### PocketMine-MP (PMMP)

- **Linguagem**: PHP
- **Performance**: Média - reimplementação do protocolo Bedrock
- **Compatibilidade**: Cross-platform (PHP)
- **Ecossistema**: Maturidade, plugins PHP, Poggit
- **Melhor para**: Minigames, servidores pequenos-médios, devs PHP

```cpp
<?php // Exemplo PMMP
use pocketmine\event\player\PlayerJoinEvent;
use pocketmine\event\Listener;

class Main extends PluginBase implements Listener {
    public function onJoin(PlayerJoinEvent $event): void {
        $player = $event->getPlayer();
        $player->sendMessage("Bem-vindo!");
    }
}
```

## Matriz de Decisão

| Critério | LeviLamina | Endstone | BDSX | PMMP |
|----------|------------|----------|------|------|
| Performance | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★☆☆ |
| Facilidade Dev | ★★★☆☆ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| Cross-Platform | ★★☆☆☆ | ★★★★★ | ★★☆☆☆ | ★★★★★ |
| Ecossistema | ★★★★☆ | ★★★★☆ | ★★★☆☆ | ★★★★★ |
| Atualizações | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★★★☆ |
| Anti-Cheat | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★☆☆☆ |

---

*Documento parte da Arquitetura Bedrock Server Mods - Zip 01: Fundação Core*
