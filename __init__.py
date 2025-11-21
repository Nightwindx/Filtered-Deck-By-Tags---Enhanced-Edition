from aqt import mw
from aqt.qt import *
from aqt.utils import showText
from aqt.utils import tooltip, getText, showInfo
from anki.collection import SearchNode
from aqt.browser import SidebarItem, SidebarTreeView, SidebarItemType
from aqt.gui_hooks import browser_sidebar_will_show_context_menu
from anki.consts import (
    DYN_OLDEST,
    DYN_RANDOM,
    DYN_SMALLINT,
    DYN_BIGINT,
    DYN_LAPSES,
    DYN_ADDED,
    DYN_DUE,
    DYN_REVADDED,
    DYN_DUEPRIORITY,
)
CURRENT_VERSION = "21-11-2025"  # change this every time you ship a new version


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


# ---------- Sidebar hook & context menu ----------


def _filteredDeckFromTag(sidebar, menu, item, index):
    # Make sure quick-create is installed (harmless if already done)
    _ensure_quick_create(sidebar)

    if item.item_type == SidebarItemType.TAG:
        menu.addSeparator()
        if len(config["supplementalSearchTexts"]) == 0:
            menu.addAction(
                "Create Filtered Deck",
                lambda: _createFilteredDeck(item, "", ""),
            )
        else:
            for i in range(len(config["supplementalSearchTexts"])):
                supplementalSearchText = config["supplementalSearchTexts"][i]
                shortName = config["shortNames"][i]
                caption = "Create Filtered Deck"
                if shortName != "":
                    caption += " - %s" % shortName

                menu.addAction(
                    caption,
                    lambda sst=supplementalSearchText, sn=shortName: _createFilteredDeck(
                        item, sst, sn
                    ),
                )


# ---------- Order parsing ----------


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


# ---------- Main creation helpers ----------


def _build_default_deck_name(item: SidebarItem) -> str:
    """Build default deck name from tag, with optional parent tag prefix."""
    leaf_part = _formatDeckNameFromTag(item.name)
    defaultName = leaf_part

    if config.get("prependMainParentTagCaps", False):
        parent_caps = _getMainParentTagCaps(item)
        if parent_caps:
            # NOTE: we add " - " between parent and child
            defaultName = f"{parent_caps} - {leaf_part}"

    return defaultName


def _build_search_for_item(item: SidebarItem, supplementalSearchText: str = "") -> str:
    """
    Build the full search string:
    - tag:<full tag>
    - optional per-menu supplemental search
    - optional global suffix from config (e.g. '(is:due OR is:new)')
    """
    col = mw.col
    base = col.build_search_string(SearchNode(tag=item.full_name))

    parts = [base]

    sst = (supplementalSearchText or "").strip()
    if sst:
        parts.append(sst)

    global_suffix = (config.get("globalSearchSuffix", "") or "").strip()
    if global_suffix:
        parts.append(global_suffix)

    return " ".join(parts)


def _createFilteredDeck(item: SidebarItem, supplementalSearchText, shortName):
    """Standard creation (with name prompt)."""

    if not item.full_name or len(item.full_name) < 2:
        return

    col = mw.col
    if col is None:
        raise Exception("collection is not available")

    search = _build_search_for_item(item, supplementalSearchText)

    # Build default deck name and allow user to edit it
    defaultName = _build_default_deck_name(item)

    name, ok = getText("Name for filtered deck:", default=defaultName)
    if not ok or not name.strip():
        tooltip("Canceled.")
        return

    deckName = name.strip()
    _create_filtered_deck_core(col, deckName, search, item.name)


def _createFilteredDeck_quick(item: SidebarItem):
    """
    Quick creation without prompt – used for Alt+Click.
    Uses same default naming logic as the normal creation.
    """
    if not item.full_name or len(item.full_name) < 2:
        return

    col = mw.col
    if col is None:
        raise Exception("collection is not available")

    search = _build_search_for_item(item)

    deckName = _build_default_deck_name(item)

    _create_filtered_deck_core(col, deckName, search, item.name)


def _create_filtered_deck_core(col, deckName: str, search: str, tag_display_name: str):
    """Shared logic: actually create the filtered deck with given params."""
    numberCards = 300

    # modifications based on config
    if config:
        if config.get("numCards", 0) > 0:
            numberCards = config["numCards"]
        if config.get("unsuspendAutomatically", True):
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
    tooltip(f"Created filtered deck from tag {tag_display_name}")


# ---------- Tag → deck-name formatting ----------


def _formatDeckNameFromTag(tagName: str) -> str:
    """
    Format tag names into readable, title-cased deck names.
    - Keeps numeric parts (no stripping leading numbers).
    - Splits on underscores.
    - Preserves all-caps words (e.g. AK -> AK).
    """
    pieces = tagName.split("_")

    def _format_piece(word: str) -> str:
        if word.isupper():
            return word
        return word.capitalize()

    return " ".join(_format_piece(word) for word in pieces if word)


def _getMainParentTagCaps(item: SidebarItem) -> str:
    """
    Return the main parent tag in ALL CAPS (formatted) or '' if none / same as leaf.
    Uses item.full_name, which is typically 'Parent::Child::Grandchild'.
    """
    full = item.full_name or ""
    if not full:
        return ""

    # First component is the main parent in Anki's tag hierarchy.
    if "::" in full:
        main_parent = full.split("::", 1)[0]
    else:
        main_parent = full

    # Avoid duplicating if the "parent" is actually the same as the leaf.
    if main_parent == item.name:
        return ""

    formatted_parent = _formatDeckNameFromTag(main_parent)
    return formatted_parent.upper() if formatted_parent else ""


# ---------- Quick-create: Alt+Click on tag in sidebar ----------


class _QuickCreateAltClickFilter(QObject):
    """
    Event filter installed on the browser sidebar's viewport.

    When quickCreateAltClick is enabled:
    - Alt + Left Click on a tag item → create filtered deck immediately.
    """

    def __init__(self, sidebar: SidebarTreeView):
        # parent = viewport so it gets cleaned up correctly
        super().__init__(sidebar.viewport())
        self._sidebar = sidebar
        self._viewport = sidebar.viewport()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        # We only care about events on the viewport
        if obj is not self._viewport:
            return False

        if event.type() == QEvent.MouseButtonPress and isinstance(event, QMouseEvent):
            # Require Alt+LeftClick
            if (
                event.button() == Qt.LeftButton
                and (event.modifiers() & Qt.AltModifier)
                and config.get("quickCreateAltClick", False)
            ):
                index = self._sidebar.indexAt(event.pos())
                if not index.isValid():
                    return False

                model = self._sidebar.model()
                if not model:
                    return False

                item = None
                # Newer Anki
                if hasattr(model, "item_for_index"):
                    item = model.item_for_index(index)
                # Fallback for older sidebar models
                elif hasattr(model, "item"):
                    try:
                        item = model.item(index)
                    except Exception:
                        item = None

                if not isinstance(item, SidebarItem):
                    return False

                if item.item_type != SidebarItemType.TAG:
                    return False

                _createFilteredDeck_quick(item)
                # We handled this click; don't pass it on
                return True

        # Everything else behaves normally
        return False


def _ensure_quick_create(sidebar: SidebarTreeView) -> None:
    """
    Ensure the Alt+Click quick-create event filter is installed on the sidebar.
    Only installs once per sidebar instance.
    """
    if not config.get("quickCreateAltClick", False):
        return

    # Avoid installing multiple times
    if getattr(sidebar, "_fdft_quick_filter_installed", False):
        return

    sidebar._fdft_quick_filter_installed = True
    filter_obj = _QuickCreateAltClickFilter(sidebar)
    # Keep a reference so it doesn't get garbage-collected
    sidebar._fdft_quick_filter = filter_obj
    # IMPORTANT: install on the viewport, that's where mouse events arrive
    sidebar.viewport().installEventFilter(filter_obj)


# ---------- Config migration ----------


def updateLegacyConfig():
    config = mw.addonManager.getConfig(__name__)
    updatedConfig = config.copy()

    # Old single-text → new list-based config migration
    if (
        "supplementalSearchText" in config
        and "supplementalSearchTexts" not in config
    ):
        updatedConfig["supplementalSearchTexts"] = [
            config["supplementalSearchText"]
        ]
        del updatedConfig["supplementalSearchText"]
        tooltip(str(updatedConfig))
        updatedConfig["shortNames"] = [""]
        mw.addonManager.writeConfig(__name__, {})
        mw.addonManager.writeConfig(__name__, updatedConfig)

    # Ensure new keys exist with safe defaults
    if "prependMainParentTagCaps" not in updatedConfig:
        updatedConfig["prependMainParentTagCaps"] = False

    if "quickCreateAltClick" not in updatedConfig:
        updatedConfig["quickCreateAltClick"] = True

    if "globalSearchSuffix" not in updatedConfig:
        # e.g. "(is:due OR is:new)"
        updatedConfig["globalSearchSuffix"] = ""

    return updatedConfig


config = updateLegacyConfig()
assert len(config["supplementalSearchTexts"]) == len(
    config["shortNames"]
), "Length of supplementalSearchTexts and shortNames are not the same in Filtered Deck From Tag addon configuration."


def show_update_notice():
    cfg = mw.addonManager.getConfig(__name__)
    last_seen = cfg.get("lastSeenVersion")

    # Already showed message for this version
    if last_seen == CURRENT_VERSION:
        return

    msg = f"""
    <b>Filtered Deck From Tag — Enhanced Edition has been updated to {CURRENT_VERSION}.</b><br><br>

    <b>New in this version:</b><br>
    • Alt+Click on a tag to instantly create a filtered deck<br>
    • Optional CAPS parent tag prefix in deck names (PARENT – Child)<br>
    • Global search suffix support (e.g. append <code>(is:due OR is:new)</code>)<br><br>

    You can adjust these in the add-on config.<br>
    See the add-on page for details about new features.<br><br>

    <a href="https://ankiweb.net/shared/info/394377528">https://ankiweb.net/shared/info/394377528</a>
    """

    # Modal dialog with an OK button
    showText(msg, type="html")

    # Remember we've shown the message for this version
    cfg["lastSeenVersion"] = CURRENT_VERSION
    mw.addonManager.writeConfig(__name__, cfg)



# Run once per version
show_update_notice()



# ---------- Monkey-patch SidebarTreeView to auto-install Alt+Click ----------

# Every time a SidebarTreeView is created (i.e. Browser sidebar),
# we automatically install the quick-create event filter.
_original_sidebar_init = SidebarTreeView.__init__


def _fdft_sidebar_init(self, *args, **kwargs):
    _original_sidebar_init(self, *args, **kwargs)
    _ensure_quick_create(self)


SidebarTreeView.__init__ = _fdft_sidebar_init


# Append our option to the context menu
browser_sidebar_will_show_context_menu.append(_filteredDeckFromTag)
