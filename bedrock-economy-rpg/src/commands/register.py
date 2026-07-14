def register_all(plugin):
    server = plugin.server
    eco = plugin.economy
    rpg = plugin.rpg
    perm = plugin.permissions
    db = plugin._db

    @server.command("balance", description="Check your balance")
    def balance_command(sender, args):
        xuid = getattr(sender, "xuid", sender.name)
        bal = plugin.server.loop.create_task(eco.get_balance(xuid))
        result = plugin.server.loop.run_until_complete(bal)
        sender.send_message(f"§aBalance: §e{result} coins")

    @server.command("pay", description="Transfer coins to another player")
    def pay_command(sender, args):
        if len(args) < 2:
            sender.send_message("§cUsage: /pay <player> <amount>")
            return
        target, amount_str = args[0], args[1]
        try:
            amount = int(amount_str)
        except ValueError:
            sender.send_message("§cInvalid amount")
            return
        from_xuid = getattr(sender, "xuid", sender.name)
        to_xuid = target
        result = plugin.server.loop.run_until_complete(
            eco.transfer(from_xuid, to_xuid, amount)
        )
        if result:
            sender.send_message(f"§aSent §e{amount} coins §ato {target}")
        else:
            sender.send_message("§cInsufficient funds")

    @server.command("class", description="Set or view your class")
    def class_command(sender, args):
        xuid = getattr(sender, "xuid", sender.name)
        if not args:
            data = plugin.server.loop.run_until_complete(rpg.get_player(xuid))
            sender.send_message(f"§aClass: §e{data['class']} §aLv.{data['level']}")
            return
        cls = args[0].lower()
        result = plugin.server.loop.run_until_complete(rpg.set_class(xuid, cls))
        if result:
            sender.send_message(f"§aClass set to §e{cls}")
        else:
            valid = ", ".join(plugin.cfg["rpg"]["classes"])
            sender.send_message(f"§cValid classes: {valid}")

    @server.command("xp", description="Check your XP")
    def xp_command(sender, args):
        xuid = getattr(sender, "xuid", sender.name)
        data = plugin.server.loop.run_until_complete(rpg.get_player(xuid))
        sender.send_message(
            f"§aLv.{data['level']} §7| §aXP: §e{data['xp']}§7/§e{rpg.xp_for_level(data['level'])}"
        )

    @server.command("setgroup", description="Set player permission group", op=True)
    def setgroup_command(sender, args):
        if len(args) < 2:
            sender.send_message("§cUsage: /setgroup <player> <group>")
            return
        target, group = args[0], args[1]
        result = plugin.server.loop.run_until_complete(
            perm.set_group(target, group)
        )
        if result:
            sender.send_message(f"§aSet {target} to §e{group}")
        else:
            sender.send_message(f"§cInvalid group: {group}")

    @server.command("eco", description="Admin economy commands", op=True)
    def eco_command(sender, args):
        if len(args) < 3:
            sender.send_message("§cUsage: /eco <give|take|set> <player> <amount>")
            return
        action, target, amount_str = args[0], args[1], args[2]
        try:
            amount = int(amount_str)
        except ValueError:
            sender.send_message("§cInvalid amount")
            return
        coro = {
            "give": eco.add,
            "take": lambda x, a: eco.remove(x, a) or None,
            "set": eco.set_balance,
        }.get(action)
        if not coro:
            sender.send_message("§cUsage: /eco <give|take|set> <player> <amount>")
            return
        result = plugin.server.loop.run_until_complete(coro(target, amount))
        sender.send_message(f"§aDone. {target} balance: {plugin.server.loop.run_until_complete(eco.get_balance(target))}")

    @server.command("top", description="Top 10 richest players")
    def top_command(sender, args):
        rows = plugin.server.loop.run_until_complete(
            plugin._db.fetch(
                "SELECT name, coins FROM players ORDER BY coins DESC LIMIT 10"
            )
        )
        msg = "§6=== Top 10 ===\n"
        for i, row in enumerate(rows, 1):
            msg += f"§e{i}. §f{row['name']} §7- §a{row['coins']} coins\n"
        sender.send_message(msg.strip())
