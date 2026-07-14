# GSit - Sentar em Qualquer Bloco

> **Downloads**: 195k+ | **Stars/GitHub**: 800+
> **Stack**: Java + Bedrock Bridge / Script API
> **Repositório**: https://github.com/Gecolay/GSit
> **Documento gerado**: 2026-06-25 | Tendência: Últimos 18 meses

---

## Descrição

Permite jogadores sentarem, deitarem, e interagir com blocos de forma imersiva. Um dos mods mais baixados em 2025.

## Features Principais

- Sentar em escadas, lajes, blocos
- Deitar em camas e blocos
- Pose system com animações
- API para outros plugins
- Configuração por mundo

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