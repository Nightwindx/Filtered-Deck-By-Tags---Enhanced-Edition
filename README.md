# Filtered Deck From Tag — Enhanced Edition

A modernized fork of [Filtered Deck From Tag (AnkiWeb 2058067048)](https://ankiweb.net/shared/info/2058067048)  
Originally created by **Sachin Govind**.  
Enhanced and updated for current Anki versions (2.1.65 – 25.xx).
It’s designed for people who study **by tag instead of by deck** — especially useful for large decks like AnKing or other tagged hierarchies.

---


## 🪄 Usage

1. Open the **Browser** in Anki.  
2. Right-click any tag in the left sidebar.  
3. Choose **“Create Filtered Deck”** (or a variant if you’ve added short-named options - explained below).  
4. When prompted, enter your desired deck name (defaults to a title-cased version of the tag).  
5. A filtered deck will be created instantly from that tag with pre-configured card number, sort order, and card states (New, Learn, Due)

---

## ✨ New Features

- 📝 **Custom Deck Name Prompt:** When creating a filtered deck from the browser sidebar, you can now type any custom deck name before creation.
- 🔠 **Title-Case Deck Names:** Tags like `medicine_cardiology` become **Medicine Cardiology** automatically.
- 🧠 **FSRS/Modern Orders Support:** Works with all current *Select by* modes, including **Ascending Retrievability** and **Descending Retrievability**.
- 🛡️ **Backwards Compatible:** Graceful fallback to “Order Due” if an unsupported order is selected.

---

## ⚙️ Configuration

Access configuration via  
**Tools → Add-ons → Filtered Deck From Tag — Enhanced Edition → Config**.

Configuration fields:

- **`supplementalSearchTexts`**  
  A list of extra search strings. Each one adds another menu option when right-clicking a tag.

- **`shortNames`**  
  A list of labels for those options (same length as `supplementalSearchTexts`). Each of these labels corresponds to an option in `supplementalSearchTexts`.

- **`numCards`**  
  The number of cards to include in the filtered deck (max allowed by Anki is 9999).  
  Example: `300` for a daily study subset.

- **`unsuspendAutomatically`**  
  Whether to automatically unsuspend cards that match the filter (default: `true`). Can be set to `false`

- **`defaultOrder`**  
  Controls the card order when building the deck.  
	0 - Oldest seen first  
	1 - Random  
	2 - Increasing intervals  
	3 - Decreasing intervals  
	4 - Most lapses  
	5 - Order added  
	6 - Order due 
	7 - Latest added first  
	8 - Ascending retrievability  
	9 - Descending retrievability (default) 

To understand what options to choose, I suggest reading the discussion on the anki forum by Expertium and Dae: https://forums.ankiweb.net/t/improving-sort-orders/50081


## ⚙️ Default Configuration

```json
{
  "numCards": 9999,
  "shortNames": [],
  "supplementalSearchTexts": [],
  "unsuspendAutomatically": true,
  "defaultOrder": "9"
}

```
---

### Example Configuration

```json
{
"numCards": 300,
"shortNames": [
  "High Yield Due",
  "High Yield Due and New",
  "Due and New"
],
"supplementalSearchTexts": [
  "tag:#AK_Step1_v11::^Other::^HighYield::1-HighYield is:due",
  "tag:#AK_Step1_v11::^Other::^HighYield::1-HighYield (is:due OR is:new)",
  "(is:due OR is:new)"
],
"unsuspendAutomatically": true,
"defaultOrder": "9"
}

```
## Notes
- This add-on creates the filtered deck. It does not regularly rebuild that filtered deck. For that, I recommend one of the rebuild all add-ons.
- Bug reports should be added to the issues page in the GitHub repository.
