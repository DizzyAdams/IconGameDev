import random
import math


class Casino:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = plugin._db

    async def _play(self, xuid, bet, outcome_multiplier):
        if bet <= 0:
            return False, "Bet must be positive", 0
        async with self.db.acquire() as conn:
            async with conn.transaction():
                player = await conn.fetchrow("SELECT coins FROM players WHERE xuid = $1 FOR UPDATE", xuid)
                if not player or player["coins"] < bet:
                    return False, "Insufficient funds", 0
                winnings = int(bet * outcome_multiplier)
                net = winnings - bet
                if net >= 0:
                    await conn.execute("UPDATE players SET coins = coins + $1 WHERE xuid = $2", net, xuid)
                else:
                    await conn.execute("UPDATE players SET coins = coins - $1 WHERE xuid = $2", abs(net), xuid)
                await conn.execute(
                    "INSERT INTO economy_transactions (from_xuid, to_xuid, amount, type) "
                    "VALUES ($1, NULL, $2, 'casino')", xuid, -net
                )
        return True, winnings, net

    async def slot_machine(self, xuid, bet):
        reels = [random.choices(
            ["DIAMOND", "GOLD", "IRON", "COAL", "STONE", "DIRT"],
            weights=[1, 3, 8, 15, 25, 48], k=3
        ) for _ in range(3)]
        symbols = [reels[0][0], reels[1][0], reels[2][0]]
        multiplier = self._slot_payout(symbols)
        ok, msg, net = await self._play(xuid, bet, multiplier)
        return ok, {"reels": symbols, "multiplier": multiplier, "winnings": msg if ok else 0, "net": net}

    def _slot_payout(self, symbols):
        counts = {}
        for s in symbols:
            counts[s] = counts.get(s, 0) + 1
        best = max(counts.values())
        if best == 3:
            return {"DIAMOND": 10, "GOLD": 5, "IRON": 3}.get(symbols[0], 2)
        if best == 2:
            for s, c in counts.items():
                if c == 2 and s in ("DIAMOND", "GOLD", "IRON", "COAL"):
                    return {"DIAMOND": 2.5, "GOLD": 2, "IRON": 1.5, "COAL": 1.2}.get(s, 1)
        return 0

    async def coinflip(self, xuid, bet, choice):
        choice = choice.lower()
        if choice not in ("heads", "tails"):
            return False, "Choose heads or tails", 0
        result = random.choice(["heads", "tails"])
        won = result == choice
        multiplier = 2.0 if won else 0
        ok, msg, net = await self._play(xuid, bet, multiplier)
        return ok, {"result": result, "won": won, "winnings": msg if ok else 0, "net": net}

    async def dice(self, xuid, bet, guess):
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        total = d1 + d2
        if guess == "over7":
            won = total > 7
            multiplier = 2.0 if won else 0
        elif guess == "under7":
            won = total < 7
            multiplier = 2.5 if won else 0
        elif guess == "7":
            won = total == 7
            multiplier = 6.0 if won else 0
        else:
            return False, "Guess must be over7, under7, or 7", 0
        ok, msg, net = await self._play(xuid, bet, multiplier)
        return ok, {"dice": (d1, d2), "total": total, "won": won, "winnings": msg if ok else 0, "net": net}

    async def blackjack(self, xuid, bet):
        deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4
        random.shuffle(deck)

        def hand_value(hand):
            v = sum(hand)
            aces = hand.count(11)
            while v > 21 and aces:
                v -= 10
                aces -= 1
            return v

        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]

        player_score = hand_value(player_hand)
        dealer_score = hand_value(dealer_hand)

        if player_score == 21 and dealer_score == 21:
            result = "push"
            multiplier = 1.0
        elif player_score == 21:
            result = "blackjack"
            multiplier = 2.5
        else:
            while player_score < 17:
                player_hand.append(deck.pop())
                player_score = hand_value(player_hand)
            if player_score > 21:
                result = "bust"
                multiplier = 0
            else:
                while dealer_score < 17:
                    dealer_hand.append(deck.pop())
                    dealer_score = hand_value(dealer_hand)
                if dealer_score > 21 or player_score > dealer_score:
                    result = "win"
                    multiplier = 2.0
                elif player_score == dealer_score:
                    result = "push"
                    multiplier = 1.0
                else:
                    result = "lose"
                    multiplier = 0

        ok, msg, net = await self._play(xuid, bet, multiplier)
        return ok, {
            "player_hand": player_hand, "player_score": player_score,
            "dealer_hand": dealer_hand, "dealer_score": dealer_score,
            "result": result, "multiplier": multiplier,
            "winnings": msg if ok else bet, "net": net
        }
