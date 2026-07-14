# Epic Fantasy RPG - Sistema RPG Completo

> **Downloads**: 900k+ | **Stars/GitHub**: N/A (Addon)
> **Stack**: Behavior Pack + Resource Pack + Script API
> **Repositório**: MCPEDL / CurseForge
> **Documento gerado**: 2026-06-25 | Tendência: Últimos 18 meses

---

## Descrição

Sistema RPG completo com classes, magias, skills, bosses e quests. Tendência em 2025-2026.

## Features Principais

- Classes (Warrior, Mage, Archer, etc)
- Sistema de magias
- Skill trees
- Bosses épicos
- Quest system
- Guild system
- Loot rarities

## Integração com Servidor

### LeviLamina (C++)
```cpp
// Hook para integrar com sistema de eventos
Event::PlayerInteractEvent::subscribe([](const Event::PlayerInteractEvent& e) {
    // Lógica do mod aqui
});
```

### Endstone (Python)
```python
from endstone.plugin import Plugin
from endstone.event import event_handler

class ModPlugin(Plugin):
    @event_handler
    def on_interact(self, event):
        # Lógica do mod aqui
        pass
```

### Script API (JavaScript)
```javascript
import { world, system } from '@minecraft/server';

world.afterEvents.playerInteractWithBlock.subscribe((event) => {
    // Lógica do mod aqui
});
```

## Performance

- Otimizado para 20 TPS
- Uso mínimo de memória
- Cache de entidades quando aplicável

## Compatibilidade

| Plataforma | Suporte | Notas |
|------------|---------|-------|
| Windows BDS | ✅ Sim | Nativo |
| Linux BDS | ⚠️ Parcial | Via Wine/Proton |
| Realms | ❌ Não | Limitação da Mojang |
| Aternos | ⚠️ Parcial | Depende do host |

---

*Documento parte da Arquitetura Bedrock Server Mods - Mods em Alta 2025-2026*