# Age Rating — IARC Certificate Template

Microsoft uses the **IARC** (International Age Rating Coalition) system. During
Partner Center submission you answer a short questionnaire and receive a rating
certificate automatically. This template records the answers and the resulting
rating for our packs.

## IARC questionnaire (key questions)

| # | Question | Our typical answer |
|---|----------|--------------------|
| Q1 | Violence / realistic violence? | No / Fantasy only |
| Q2 | Language / profanity? | No |
| Q3 | Nudity / sexual content? | No |
| Q4 | Drugs / alcohol / tobacco? | No |
| Q5 | Gambling / loot boxes? | No |
| Q6 | Fear / horror? | Mild (some packs) |
| Q7 | Discrimination / hate? | No |
| Q8 | In-game purchases? | Via Minecoins (platform) |

## Resulting ratings

| Board | Rating |
|-------|--------|
| ESRB (US) | **E** (Everyone) — or **E10+** for fantasy-combat/world packs |
| PEGI (EU) | **3** — or **7** for fantasy violence |
| USK / others | Mapped by IARC automatically |

## Certificate record (one per pack)

```
Pack:            <pack-name>
Product type:    <skin_pack | resources | world_template | mashup>
IARC ID:         <auto-assigned at submission>
ESRB:            E / E10+
PEGI:            3 / 7
Descriptors:     <e.g. "Fantasy Violence">
Submitted:       <YYYY-MM-DD>
Certificate URL: <Partner Center link>
```

## Defaults we use

- Skin packs (original themes): **ESRB E / PEGI 3**
- Texture packs: **ESRB E / PEGI 3**
- World templates with scare themes: **ESRB E10+ / PEGI 7**

Never publish an offer without a generated IARC certificate — uncertified
offers are rejected at certification.
