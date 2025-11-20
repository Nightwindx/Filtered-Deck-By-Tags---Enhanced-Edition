

---

**Filtered Deck From Tag — Enhanced Edition**
A modernized fork of Filtered Deck From Tag (AnkiWeb 2058067048)
Originally created by Sachin Govind.

Enhanced and updated for current Anki versions (2.1.65 – 25.xx). It’s designed for people who study by **tag** instead of by deck — especially useful for large decks like AnKing or other tagged hierarchies.

---

### 🪄 Usage

1. Open the **Browser** in Anki.
2. In the left **Tags** sidebar, either:

   * **Right-click** any tag → choose **“Create Filtered Deck”** (or one of your custom variants), *or*
   * **Alt + Left-click** a tag to instantly create a filtered deck with the default settings and name (no dialog).
3. When using the right-click option, you can edit the suggested deck name.
4. A filtered (dynamic) deck is created from that tag with your configured:

   * card count
   * sort / “select by” order
   * card states (New, Learn, Due)

---

### ✨ New Features

* **📝 Custom Deck Name Prompt**
  When creating a filtered deck via right-click, you can type any custom deck name before creation.

* **🔠 Smart, Title-Case Deck Names (with numbers)**
  Tags like `medicine_cardiology` become **Medicine Cardiology** automatically.
  Numeric parts are preserved, so `3_brain_tumors` becomes **3 Brain Tumors**, not just *Brain Tumors*.
  All-caps acronyms (e.g. `AK`) stay in caps.

* **🏷️ Parent Tag Prefix in CAPS (optional)**
  For hierarchical tags like `Neurosurgery::3_brain_tumors`, the default filtered deck name can be:
  **NEUROSURGERY – 3 Brain Tumors**
  This can be turned on/off in the add-on config.

* **⚡ Quick Alt-Click Creation (optional)**
  Hold **Alt** and left-click on a tag in the browser sidebar to instantly create a filtered deck from that tag:

  * Uses the same naming rules (including CAPS parent + “ – ” child if enabled).
  * Skips the name prompt for faster workflow.
  * Can be disabled in the config if you don’t want this behavior.

* **🧠 FSRS / Modern Orders Support**
  Works with all current **Select by** modes, including **Ascending Retrievability** and **Descending Retrievability**.

* **🛡️ Backwards Compatible**
  Graceful fallback to **Order Due** if an unsupported order is selected.

---

### ⚙️ Configuration

Access configuration via:
**Tools → Add-ons → Filtered Deck From Tag — Enhanced Edition → Config**

**Configuration fields:**

* **`supplementalSearchTexts`**
  A list of extra search strings. Each one adds another menu option when right-clicking a tag.

* **`shortNames`**
  A list of labels for those options (same length as `supplementalSearchTexts`). Each label corresponds to an entry in `supplementalSearchTexts`.

* **`numCards`**
  The number of cards to include in the filtered deck (max allowed by Anki is 9999).
  Example: `300` for a daily study subset.

* **`unsuspendAutomatically`**
  Whether to automatically unsuspend cards that match the filter (`true` by default). Set to `false` to leave suspension status unchanged.

* **`defaultOrder`**
  Controls the card order when building the deck (Anki “select by” order):
  `0` – Oldest seen first
  `1` – Random
  `2` – Increasing intervals
  `3` – Decreasing intervals
  `4` – Most lapses
  `5` – Order added
  `6` – Order due
  `7` – Latest added first
  `8` – Ascending retrievability (FSRS)
  `9` – Descending retrievability (FSRS, default)

  To understand what options to choose, see the discussion by Expertium and Dae:
  [https://forums.ankiweb.net/t/improving-sort-orders/50081](https://forums.ankiweb.net/t/improving-sort-orders/50081)

* **`prependMainParentTagCaps`** *(new)*
  If `true`, the main parent tag (first component in the hierarchy) is prepended in ALL CAPS, separated by `" - "`.
  Example: `Neurosurgery::3_brain_tumors` → **NEUROSURGERY – 3 Brain Tumors**.
  If `false`, only the leaf tag is used (e.g. **3 Brain Tumors**).

* **`quickCreateAltClick`** *(new)*
  If `true`, **Alt + Left-click** on a tag in the browser sidebar will instantly create a filtered deck using the default settings and name (no confirmation dialog).
  If `false`, Alt-click does nothing and only the right-click menu is available.

---

### ⚙️ Default Configuration

```json
{
  "numCards": 9999,
  "shortNames": [],
  "supplementalSearchTexts": [],
  "unsuspendAutomatically": true,
  "defaultOrder": "9",
  "prependMainParentTagCaps": true,
  "quickCreateAltClick": true
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
  "defaultOrder": "9",
  "prependMainParentTagCaps": true,
  "quickCreateAltClick": true
}
```

---

### Notes

* This add-on **creates** the filtered deck. It does **not** regularly rebuild that filtered deck. For automatic rebuilding, use one of the “rebuild all filtered decks” add-ons.
* Click **“Contact Author”** on AnkiWeb to view the GitHub page and source code.
* Bug reports and feature requests should be added to the **Issues** page in the GitHub repository.
