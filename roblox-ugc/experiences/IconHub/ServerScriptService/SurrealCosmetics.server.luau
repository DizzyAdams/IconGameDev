-- SurrealCosmetics — server-authoritative visual effects driven by owned GamePasses.
-- Theme: a "dreamscape" (floating trails, auras, wings, halos, pets, capes, banners).
-- Every effect is ORIGINAL (no third-party IP) and applied SERVER-SIDE, so the
-- client can never spoof ownership. Effects read the attributes set by
-- GamePassService (GamePass_<id>). Client never decides anything.

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GamePasses = require(ReplicatedStorage.Config.GamePasses)

-- Attach a neon part to the character root. `weld` = true bonds it in place;
-- `weld` = false leaves it free so a follow-loop can move it (pets).
local function attachPart(root, size, color, offset, weld)
	weld = weld ~= false
	local part = Instance.new("Part")
	part.Name = "SurrealEffect"
	part.Size = size
	part.Color = color
	part.Material = Enum.Material.Neon
	part.CanCollide = false
	part.Anchored = false
	part.Transparency = 0.25
	part.CFrame = root.CFrame * offset
	if weld then
		local w = Instance.new("WeldConstraint")
		w.Part0 = root
		w.Part1 = part
		w.Parent = part
	end
	part.Parent = root
	return part
end

-- Effect builders: (character, root) -> cleanup function.
local EffectBuilders = {}

EffectBuilders["trail"] = function(_character, root)
	local attachment = Instance.new("Attachment")
	attachment.Name = "TrailAttachment"
	attachment.Parent = root
	local trail = Instance.new("Trail")
	trail.Attachment0 = attachment
	trail.Lifetime = 1.2
	trail.MinLength = 0.2
	trail.Color = ColorSequence.new(Color3.fromRGB(180, 120, 255))
	trail.Transparency = NumberSequence.new(0.6, 1)
	trail.FaceCamera = true
	trail.Parent = attachment
	return function()
		trail:Destroy()
		attachment:Destroy()
	end
end

EffectBuilders["aura"] = function(_character, root)
	local attachment = Instance.new("Attachment")
	attachment.Parent = root
	local emitter = Instance.new("ParticleEmitter")
	emitter.Size = NumberSequence.new(0.6)
	emitter.Lifetime = NumberRange.new(0.6, 1.2)
	emitter.Rate = 12
	emitter.Speed = NumberRange.new(1, 3)
	emitter.Color = ColorSequence.new(Color3.fromRGB(120, 220, 255))
	emitter.Parent = attachment
	return function()
		emitter:Destroy()
		attachment:Destroy()
	end
end

EffectBuilders["wings"] = function(_character, root)
	local left = attachPart(root, Vector3.new(2, 3, 0.2), Color3.fromRGB(255, 170, 60), CFrame.new(-1.4, 0.5, -0.6))
	local right = attachPart(root, Vector3.new(2, 3, 0.2), Color3.fromRGB(255, 170, 60), CFrame.new(1.4, 0.5, -0.6))
	return function()
		left:Destroy()
		right:Destroy()
	end
end

EffectBuilders["halo"] = function(_character, root)
	local halo = attachPart(root, Vector3.new(2.2, 0.2, 2.2), Color3.fromRGB(255, 240, 150), CFrame.new(0, 3, 0))
	return function() halo:Destroy() end
end

EffectBuilders["pet"] = function(_character, root)
	local pet = attachPart(root, Vector3.new(1, 1, 1), Color3.fromRGB(80, 200, 160), CFrame.new(2.5, 1, 0), false)
	local conn
	conn = RunService.Heartbeat:Connect(function()
		if pet.Parent and root.Parent then
			local goal = root.Position + Vector3.new(2.5 * math.cos(os.clock() * 2), 1.5 + math.sin(os.clock() * 3), 0)
			pet.CFrame = CFrame.new(goal)
		elseif conn then
			conn:Disconnect()
		end
	end)
	return function()
		if conn then conn:Disconnect() end
		pet:Destroy()
	end
end

EffectBuilders["cape"] = function(_character, root)
	local cape = attachPart(root, Vector3.new(1.6, 2.4, 0.15), Color3.fromRGB(40, 40, 80), CFrame.new(0, -0.2, -0.9))
	return function() cape:Destroy() end
end

EffectBuilders["banner"] = function(_character, root)
	local banner = attachPart(root, Vector3.new(1.4, 2, 0.1), Color3.fromRGB(200, 60, 120), CFrame.new(0, 0.5, -1))
	return function() banner:Destroy() end
end

-- Infer effect keyword from a GamePass benefit string.
local function effectFromBenefit(benefit)
	local lower = string.lower(benefit or "")
	for keyword, _ in pairs(EffectBuilders) do
		if string.find(lower, keyword) then
			return keyword
		end
	end
	return nil
end

local function clearEffects(character)
	local cleanups = character:GetAttribute("SurrealCleanups")
	if cleanups then
		for _, c in ipairs(cleanups) do
			pcall(c)
		end
		character:SetAttribute("SurrealCleanups", nil)
	end
	for _, v in ipairs(character:GetChildren()) do
		if v.Name == "SurrealEffect" then v:Destroy() end
	end
end

local function applyEffects(player, character)
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then return end
	local cleanups = {}
	character:SetAttribute("SurrealCleanups", cleanups)
	for _, pass in ipairs(GamePasses) do
		if player:GetAttribute("GamePass_" .. pass.id) then
			local effect = effectFromBenefit(pass.benefit)
			if effect and EffectBuilders[effect] then
				local ok, cleanup = pcall(EffectBuilders[effect], character, root)
				if ok and cleanup then
					table.insert(cleanups, cleanup)
				end
			end
		end
	end
end

local function onCharacterAdded(player, character)
	clearEffects(character)
	local root = character:WaitForChild("HumanoidRootPart", 10)
	if root then
		applyEffects(player, character)
	end
end

local function onPlayerAdded(player)
	player.CharacterAdded:Connect(function(character)
		onCharacterAdded(player, character)
	end)
	if player.Character then
		onCharacterAdded(player, player.Character)
	end
end

Players.PlayerAdded:Connect(onPlayerAdded)
for _, p in ipairs(Players:GetPlayers()) do
	onPlayerAdded(p)
end
