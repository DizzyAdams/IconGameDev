-- Developer Products catalog (ModuleScript).
-- NOTE: `id` values 1..10 are PLACEHOLDERS. After uploading the experience, create each
-- Developer Product in the Roblox Creator Dashboard and replace the id with the real one.
-- `grants` describes exactly what the player receives (no random/gambling, no lootboxes).

local DevProducts = {
	{ id = 1,  name = "100 Coins",             priceRobux = 50,  grants = "Adds 100 coins to the player balance" },
	{ id = 2,  name = "500 Coins",             priceRobux = 199, grants = "Adds 500 coins to the player balance" },
	{ id = 3,  name = "1200 Coins",            priceRobux = 399, grants = "Adds 1200 coins to the player balance" },
	{ id = 4,  name = "Respawn Token",         priceRobux = 99,  grants = "Grants one respawn token" },
	{ id = 5,  name = "Name Tag Color",        priceRobux = 149, grants = "Unlocks a custom name tag color" },
	{ id = 6,  name = "2x Coin Potion (1h)",   priceRobux = 149, grants = "Grants 2x coin multiplier for 1 hour" },
	{ id = 7,  name = "Pet Treat Pack",        priceRobux = 99,  grants = "Grants 5 pet treats" },
	{ id = 8,  name = "Emote Unlock Pack",     priceRobux = 199, grants = "Unlocks 3 emotes" },
	{ id = 9,  name = "Teleport Scroll",       priceRobux = 79,  grants = "Grants one teleport scroll" },
	{ id = 10, name = "Vault Slot",            priceRobux = 249, grants = "Unlocks one extra inventory vault slot" },
}

return DevProducts
