---
item_ids:
  - auroral:aurora_bloom
  - auroral:aurora_bloom_decorative
  - auroral:frozen_petals
navigation:
  title: Aurora Blooms
  icon: auroral:frozen_petals
  parent: index.md
  position: 30
---

# <Color id="gold">Aurora Blooms</Color>

<Column alignItems="center" fullWidth={true}>
  <ItemImage id="aurora_bloom" scale="2" />

  Magical flowers that spontaneously appear on snow during auroras. The source of <ItemLink id="frozen_petals" /> and the gateway to most of the mod's content.
</Column>

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">Finding Aurora Blooms</Color>
</Column>

During an aurora, Aurora Blooms naturally spawn on cold-biome surfaces. They grow through **four stages** before becoming fully mature. Any blooms left behind when the aurora ends wilt away at sunrise.

Valid surfaces for spawning and survival:

* Snow layers (provided the block beneath is itself a valid snowy surface, so blooms aren't stranded on dirt or stone if the snow melts)
* Snow blocks
* Powder snow (see below)
* Ice, Packed Ice, and Blue Ice (frozen ocean surfaces work)
* <ItemLink id="shimmering_ice" />

<Row>
  <ItemImage id="aurora_bloom" />
  ### <Color id="aqua">Snow-Logged Blooms</Color>
</Row>

When a bloom is placed on a **snow layer** or appears in **powder snow**, the snow type is remembered. Breaking or wilting the bloom restores the original snow in place — a snow layer comes back as a snow layer, powder snow comes back as powder snow. Buried blooms emit a faint trickle of snowflake particles above them so they can still be located if more snow piles on top.

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">Harvesting</Color>
</Column>

Breaking a fully grown (stage 3) Aurora Bloom drops:

* <ItemLink id="frozen_petals" /> (1–4 with Fortune)
* The **living Aurora Bloom** itself, so you can replant it
* A **15% chance** for an additional living bloom on top of that

Breaking an immature bloom yields nothing — patience is rewarded.

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">Preserved Blooms (Silk Touch)</Color>
</Column>

A **Silk Touch** tool on a fully grown Aurora Bloom yields a **decorative Aurora Bloom** instead of Frozen Petals. The decorative variant:

* Never decays at sunrise — it stays forever
* Always shows the stage 3 appearance
* Fits inside a **Flower Pot** for display
* Drops itself when broken, so it can be cloned anywhere

This is the only way to keep an Aurora Bloom outside of an active aurora.

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">Uses for Frozen Petals</Color>
</Column>

* **Awkward Potions** — brew like Nether Wart from a Water Bottle in any brewing stand
* <ItemLink id="cold_brewing_stand" /> — combined with Shimmersteel Ingots
* <ItemLink id="glow_leek_seeds" /> — combined with wheat seeds
* <ItemLink id="frosted_cookies" /> — sweet treat with magical shimmer
* <ItemLink id="aurora_shard" /> — infuse in a Glacial Basin with 1 aura level

<RecipeFor id="glow_leek_seeds" />

<ItemImage id="minecraft:air" scale="0.25"/>
***

<Column alignItems="center" fullWidth={true}>
  ## <Color id="gold">Ender Transformation</Color>
</Column>

<Row>
  <ItemImage id="aurora_ender_shard" />
  ### <Color id="aqua">Right-click with an Ender Pearl</Color>
</Row>

Right-clicking an Aurora Bloom with an **Ender Pearl** transforms it into an <ItemLink id="ender_bloom" /> at the same growth stage. The pearl is consumed in the process. See [Ender Blooms](ender_bloom.md) for the full lifecycle.
