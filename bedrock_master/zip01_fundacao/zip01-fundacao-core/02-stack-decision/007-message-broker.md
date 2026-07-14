# Message Broker

> **Categoria**: Zip01 Fundacao Core | **Subcategoria**: 02 Stack Decision
> **Documento**: #19 | **Gerado**: 2026-06-25

---

## Visão Geral

Este documento cobre aspectos técnicos de **Message Broker** dentro da arquitetura Bedrock Server Mods.

## Conceitos Fundamentais

- **Conceito Principal**: Message Broker é fundamental para o ecossistema de modding Bedrock.
- **Integração**: Este componente se conecta com LegacyScriptEngine.
- **Performance**: Otimizado para servidores com 20 TPS (ticks per second).

## Stack Recomendada

**Stack Principal**: Node.js 20 + TypeScript + BDSX + Prisma + PostgreSQL

**Bibliotecas Essenciais**:
- fmt - Modern formatting library for C++
- nlohmann/json - JSON for Modern C++
- cpp-httplib - C++ HTTP/HTTPS library

## Exemplo de Implementação (CPP)

```cpp
LL_AUTO_TYPE_INSTANCE_HOOK(
    CustomHook, HookPriority::Normal,
    ServerPlayer, &ServerPlayer::setLocalPlayerAsInitialized,
    void, ()
) {
    auto& player = *this;
    Logger::info("Player joined: {}", player.getRealName());
    origin();
}
```

## Design Pattern Aplicável

Factory Pattern - Dynamic creation of entities and items

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
│   Client    │────▶│   BDS Core  │────▶│  Message Bro│
└─────────────┘     └─────────────┘     └─────────────┘
```

---

*Documento parte da Arquitetura Bedrock Server Mods - Zip01 Fundacao Core*