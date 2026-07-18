-- Client-only purchase prompt trigger.
-- This script does NOT validate or grant anything. The server is authoritative for ownership
-- and grants. The client merely listens for a "ShopPurchase" remote and opens the correct prompt.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")

local remote = ReplicatedStorage:WaitForChild("RemoteEvents"):WaitForChild("ShopPurchase")

-- Server fires: remote:FireClient(player, "GamePass" | "Product", id)
remote.OnClientEvent:Connect(function(kind, id)
	local player = Players.LocalPlayer
	if kind == "GamePass" then
		MarketplaceService:PromptGamePassPurchase(player, id)
	elseif kind == "Product" then
		MarketplaceService:PromptProductPurchase(player, id)
	end
end)
