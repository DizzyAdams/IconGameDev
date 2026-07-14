# Linguagens e Runtimes

> **Categoria**: Zip01 Fundacao Core | **Subcategoria**: 02 Stack Decision
> **Documento**: #14 | **Gerado**: 2026-06-25

---

## Visão Geral

Este documento cobre aspectos técnicos de **Linguagens e Runtimes** dentro da arquitetura Bedrock Server Mods.

## Conceitos Fundamentais

- **Conceito Principal**: Linguagens e Runtimes é fundamental para o ecossistema de modding Bedrock.
- **Integração**: Este componente se conecta com BDSX.
- **Performance**: Otimizado para servidores com 20 TPS (ticks per second).

## Stack Recomendada

**Stack Principal**: C++20 + CMake + LeviLamina + lip + vcpkg

**Bibliotecas Essenciais**:
- fmt - Modern formatting library for C++
- pybind11 - Seamless C++ / Python interoperability
- sentry-native - Crash reporting and error tracking

## Exemplo de Implementação (PYTHON)

```python
from endstone.plugin import Plugin
from endstone.event import event_handler, PlayerJoinEvent

class MyPlugin(Plugin):
    @event_handler
    def on_join(self, event: PlayerJoinEvent):
        event.player.send_message('Hello!')
```

## Design Pattern Aplicável

Repository Pattern - Abstraction layer for data persistence

## Considerações de Performance

- Minimize allocations no tick principal do servidor
- Use object pooling para entidades temporárias
- Cache resultados de queries de banco de dados
- Implemente rate limiting para comandos de jogadores
- Utilize async I/O para operações de rede e disco

## Segurança

- Valide todos inputs de jogadores (sanitização)
- Use prepared statements para queries SQL
- Implemente checksum verification para pacotes customizados
- Restrinja execução de código dinâmico (eval/Function)
- Mantenha logs de auditoria para ações críticas

## Diagrama de Fluxo

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   BDS Core  │────▶│  Linguagens │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

*Documento parte da Arquitetura Bedrock Server Mods - Zip01 Fundacao Core*