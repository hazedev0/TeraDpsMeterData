# TeraDpsMeterData
Data for Tera DPS meter

How to read the database: 
----------------------
https://github.com/gothos-folly/TeraDataTools

Decrypted Database repository:
----------------------
https://neowutran.ovh/teraDB/

File formats:
----------------------
HotDot*.tsv:

AbnormalId	AbnormalType	AbnormalClass	IsBuff	Method	Time	Tick	Amount	Name	Itemid	ItemName	Tooltip	IconName	EffectIconName	IsShow


skills*.tsv:

SkillId	Race	Gender	Class	SkillName	Chained	SkillDetailedInfo IconName


pet-skills*.tsv:

HuntingZoneId	TemplateId	SummonName	SkillId	SkillName	IconName

note that game send pet skills id as (HuntingZoneId<<16 + SkillId)

glyph*.tsv

GliphId	SkillName	SkillId	SkillIconName	GlyphName	GlyphIcon	Tooltip

There are some issues in glyph*.tsv, skill Id and icon can be wrong or even absent, especially for non-english files

Updating data for TCC:
----------------------
TCC downloads the files listed in `database-hashes.json` from this branch whenever its local copy has a different hash.
After changing any data file, run `python tools/update_hashes.py` and commit the hash file together with the data.
Keep column layouts unchanged: TCC and ShinraMeter read these files by column index.
