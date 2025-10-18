from aqt import mw
from aqt.qt import *
from aqt.utils import tooltip, getText
from anki.collection import SearchNode
from aqt.browser import SidebarItem, SidebarTreeView, SidebarItemType
from aqt.gui_hooks import browser_sidebar_will_show_context_menu
from anki.consts import DYN_OLDEST, DYN_RANDOM, DYN_SMALLINT, DYN_BIGINT, DYN_LAPSES, DYN_ADDED, DYN_DUE, DYN_REVADDED, DYN_DUEPRIORITY

# Try to import retrievability sort constants if your Anki has them.
try:
    from anki.consts import DYN_RETRIEVABILITY_ASC  # new in recent Anki/FSRS builds
except Exception:
    DYN_RETRIEVABILITY_ASC = None

try:
    from anki.consts import DYN_RETRIEVABILITY_DESC
except Exception:
    DYN_RETRIEVABILITY_DESC = None



from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aqt.browser import SidebarTreeView  # type: ignore

def _filteredDeckFromTag(sidebar: "SidebarTreeView",  menu: QMenu, item: SidebarItem, index: QModelIndex):
    # Adds our option to the right click menu for tags in the deck browser
    if item.item_type == SidebarItemType.TAG:
        menu.addSeparator()
        if len(config["supplementalSearchTexts"]) == 0:
            menu.addAction("Create Filtered Deck",
                           lambda: _createFilteredDeck(item, "", ""))
        else:
            for i in range(len(config["supplementalSearchTexts"])):
                supplementalSearchText = config["supplementalSearchTexts"][i]
                shortName = config["shortNames"][i]
                caption = "Create Filtered Deck"
                if shortName != "":
                    caption += " - %s" % shortName
                
                menu.addAction(caption, lambda sst=supplementalSearchText, sn=shortName: _createFilteredDeck(item, sst, sn))

def _parse_default_order(val):
    """
    Accept either an int (Anki's internal code) or a human-readable string.
    Includes new retrievability orders if your build defines them.
    Falls back to DYN_DUE if unrecognized.
    """
    # Legacy aliases → codes
    aliases = {
        "oldest": DYN_OLDEST,
        "random": DYN_RANDOM,
        "increasing intervals": DYN_SMALLINT,
        "decreasing intervals": DYN_BIGINT,
        "most lapses": DYN_LAPSES,
        "order added": DYN_ADDED,
        "order due": DYN_DUE,
        "latest added first": DYN_REVADDED,
        "relative overdueness": DYN_DUEPRIORITY,
        "overdueness": DYN_DUEPRIORITY,
    }

    # Add retrievability if available in this Anki build
    if DYN_RETRIEVABILITY_ASC is not None:
        aliases["ascending retrievability"] = DYN_RETRIEVABILITY_ASC
        aliases["asc retrievability"] = DYN_RETRIEVABILITY_ASC
    if DYN_RETRIEVABILITY_DESC is not None:
        aliases["descending retrievability"] = DYN_RETRIEVABILITY_DESC
        aliases["desc retrievability"] = DYN_RETRIEVABILITY_DESC

    # 1) numeric
    try:
        return int(val)
    except Exception:
        pass

    # 2) string
    if isinstance(val, str):
        key = val.strip().lower()
        if key in aliases:
            return aliases[key]

    # 3) fallback
    return DYN_DUE


def _createFilteredDeck(item: SidebarItem, supplementalSearchText, shortName):
    if not item.full_name or len(item.full_name) < 2:
        return

    col = mw.col
    if col is None:
        raise Exception('collection is not available')

    search = col.build_search_string(SearchNode(tag=item.full_name))
    search += " " + supplementalSearchText

    # build a nice default, but let the user change it
    tag_part = _formatDeckNameFromTag(item.name)
    defaultName = f"{tag_part}" 

    name, ok = getText("Name for filtered deck:", default=defaultName)
    if not ok or not name.strip():
        tooltip("Canceled.")
        return

    deckName = name.strip()
    numberCards = 300


    # modifications based on config
    if config:
        if config["numCards"] > 0:
            numberCards = config["numCards"]
        if config["unsuspendAutomatically"]:
            cidsToUnsuspend = col.find_cards(search)
            col.sched.unsuspend_cards(cidsToUnsuspend)

    defaultOrder = _parse_default_order(config.get("defaultOrder", DYN_DUE))

    
    mw.progress.start()
    did = col.decks.new_filtered(deckName)
    deck = col.decks.get(did)
    deck["terms"] = [[search, numberCards, defaultOrder]]
    col.decks.save(deck)
    col.sched.rebuildDyn(did)
    mw.progress.finish()
    mw.reset()
    tooltip("Created filtered deck from tag %s " % (item.name))

def _formatDeckNameFromTag(tagName: str):
    """Format tag names into readable, title-cased deck names."""
    pieces = tagName.split("_")
    if len(pieces) == 1:
        return tagName.title()  # capitalize even single-word tags
    if pieces[0].isnumeric():
        pieces.pop(0)

    # Capitalize the first letter of each word
    return " ".join(word.capitalize() for word in pieces)


def updateLegacyConfig():
    config = mw.addonManager.getConfig(__name__)
    updatedConfig = config.copy()
    if "supplementalSearchText" in config and "supplementalSearchTexts" not in config: #haven't done the update on this config yet
        updatedConfig["supplementalSearchTexts"] = [config["supplementalSearchText"]]
        del updatedConfig["supplementalSearchText"]
        tooltip(str(updatedConfig))
        updatedConfig["shortNames"] = [""]
        mw.addonManager.writeConfig(__name__, {})
        mw.addonManager.writeConfig(__name__, updatedConfig)

    return updatedConfig

config = updateLegacyConfig()
assert len(config["supplementalSearchTexts"]) == len(config["shortNames"]), "Length of supplementalSearchTexts and shortNames are not the same in Filtered Deck From Tag addon configuration."

# Append our option to the context menu
browser_sidebar_will_show_context_menu.append(_filteredDeckFromTag)