-- Server-authoritative Developer Product processing with an idempotent receipt ledger.
-- A DataStore tracks each ProductReceiptId so already-processed purchases are NEVER granted twice.
local DataStoreService = game:GetService("DataStoreService")
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local DevProducts = require(ReplicatedStorage.Config.DevProducts)

-- Build fast lookup for runtime validation.
local ProductById = {}
for _, p in ipairs(DevProducts) do
	ProductById[p.id] = p
end

local receiptStore = DataStoreService:GetDataStore("DevProductReceipts")

local function findProduct(id)
	return ProductById[id]
end

-- Applies the clearly-stated grant server-side. Replace the attribute write with your real
-- economy/profile system (e.g. add coins to leaderstats). Client is not involved.
local function grantProduct(player, product)
	local attr = "DevProduct_" .. product.id
	player:SetAttribute(attr, (player:GetAttribute(attr) or 0) + 1)
end

local function processReceipt(receiptInfo)
	local product = findProduct(receiptInfo.ProductId)
	local key = receiptInfo.PlayerId .. "_" .. receiptInfo.ProductReceiptId

	local success = pcall(function()
		receiptStore:UpdateAsync(key, function(prev)
			if prev == true then
				return true -- Already granted: idempotent, do NOT grant again.
			end
			local player = Players:GetPlayerByUserId(receiptInfo.PlayerId)
			if not player then
				error("player_offline") -- Not processed yet; Roblox will retry until online.
			end
			if product then
				grantProduct(player, product)
			end
			return true
		end)
	end)

	if success then
		return Enum.ProductPurchaseDecision.PurchaseGranted
	else
		-- Return NotProcessedYet so Roblox retries the receipt (safe: ledger prevents double grants).
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end
end

MarketplaceService.ProcessReceipt = processReceipt
