-- Server-authoritative GamePass ownership check + purchase prompt.
-- Benefits are cosmetic or clearly stated. The client is NEVER trusted for ownership or grants.
local Players = game:GetService("Players")
local MarketplaceService = game:GetService("MarketplaceService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GamePasses = require(ReplicatedStorage.Config.GamePasses)

-- Build fast lookup for runtime validation.
local PassById = {}
for _, p in ipairs(GamePasses) do
	PassById[p.id] = p
end

-- Applies a pass benefit server-side by recording ownership on the player.
-- Downstream systems (cosmetics, coin multipliers) read these attributes; client input is ignored.
local function applyBenefit(player, pass)
	player:SetAttribute("GamePass_" .. pass.id, true)
	player:SetAttribute("GamePassName_" .. pass.id, pass.name)
end

-- Queries actual ownership through MarketplaceService (authoritative source of truth).
local function checkPasses(player)
	if not player or not player:IsA("Player") then
		return
	end
	for _, pass in ipairs(GamePasses) do
		local ok, owns = pcall(function()
			return MarketplaceService:UserOwnsGamePassAsync(player.UserId, pass.id)
		end)
		if ok and owns then
			applyBenefit(player, pass)
		end
	end
end

-- Prompts a purchase for a given pass id. Triggered by the client remote but validated here.
local function promptPurchase(player, id)
	local pass = PassById[id]
	if not pass then
		warn("Rejected GamePass prompt for unknown id:", id, "player:", player.Name)
		return
	end
	local ok, err = pcall(function()
		MarketplaceService:PromptGamePassPurchase(player, pass.id)
	end)
	if not ok then
		warn("PromptGamePassPurchase failed for", pass.name, "player:", player.Name, "error:", err)
	end
end

-- ShopPurchase remote: server decides what to prompt. Client only sends intent ("GamePass", id).
-- We validate the id against the known allowlist to prevent spoofed requests.
local remote = ReplicatedStorage:WaitForChild("RemoteEvents"):WaitForChild("ShopPurchase")
remote.OnServerEvent:Connect(function(player, kind, id)
	if not player or not player:IsA("Player") then
		return
	end
	if kind == "GamePass" and type(id) == "number" then
		promptPurchase(player, id)
	end
end)

-- Re-check ownership after a completed purchase (ownership changed event is not reliable, so re-poll).
MarketplaceService.PromptGamePassPurchaseFinished:Connect(function(player, gamePassId, wasPurchased)
	if player and wasPurchased then
		checkPasses(player)
	end
end)

-- Handle joins (covers late joiners already in the game).
Players.PlayerAdded:Connect(checkPasses)
for _, player in ipairs(Players:GetPlayers()) do
	checkPasses(player)
end
