# ICE-CRAWLER UI

This folder contains the Tkinter UI surface for ICE-CRAWLER. The UI is an
observational control surface driven by run fossils written to
`state/runs/<run>/` and never runs git directly.

## IDE-style layout

The UI uses a VS Code-inspired layout with collapsible sidebars, a bottom
terminal, and a persistent footer. Everything is pure Tkinter + ttk with
zero additional dependencies.

```
+------+-----------------------------------+--------+
| LEFT |         MAIN CONTENT              | RIGHT  |
| SIDE |  Title / URL Input / Submit       | SIDE   |
| BAR  |  Progress Bar                     | BAR    |
|      |  Output Residue / Artifacts       |        |
| [<<] |                                   | [>>]   |
| Phase|                                   | CMD    |
| Tree |                                   | Stream |
| Agent|                                   | CMD    |
| Info |                                   | Trace  |
|      |                                   | Thread |
+------+-----------------------------------+--------+
| TERMINAL (tabbed: Output | Events)          [^/v] |
+----------------------------------------------------+
| FOOTER: Run path | Frost | Glacier | Crystal | Res |
+----------------------------------------------------+
```

### Panel nesting

```
tk.Tk
  bg_canvas (place, full window)
  shell (tk.Frame, place relwidth/relheight=1)
    footer (pack side=bottom, fill=x) -- Footer panel
    vpane (tk.PanedWindow orient=VERTICAL)
      upper (tk.Frame)
        hpane (tk.PanedWindow orient=HORIZONTAL)
          left_wrapper  -- toggle btn + LeftSidebar
          main_content  -- MainContent
          right_wrapper -- toggle btn + RightSidebar
      terminal_panel -- TerminalPanel
```

### Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+B` | Toggle left sidebar |
| `Ctrl+J` | Toggle terminal |
| `Ctrl+Shift+B` | Toggle right sidebar |

All panel dividers are draggable sashes.

## Key behavior

- **Event truth ladder**: stage locks and reveal phrases are driven by
  `ui_events.jsonl` (`FROST_VERIFIED`, `GLACIER_VERIFIED`,
  `CRYSTAL_VERIFIED`, `RESIDUE_EMPTY_LOCK`).
- **Artifact handoff**: `ai_handoff_path.txt` provides the final output
  folder; the UI renders this path and opens it on click.
- **Completion banner**: appears when `RUN_COMPLETE` is seen in the
  run event stream.
- **CMD stream hook**: the right sidebar `CMD STREAM` panel captures live
  orchestrator stdout into `ui_cmd_stream.log` and keeps it visible after
  completion for analysis.
- **Terminal mirroring**: the bottom terminal Output tab mirrors the CMD
  stream in real time; the Events tab shows raw `ui_events.jsonl`.

## File structure

```
ui/
  ice_ui.py                       # App shell: layout, wiring, collapse controllers
  panels/
    __init__.py                   # Package exports
    base_panel.py                 # BasePanel(tk.Frame) base class with shared colors
    left_sidebar.py               # Phase ladder + agent status + handoff badge
    main_content.py               # Header, URL input, submit, progress, output residue
    right_sidebar.py              # CMD Stream, CMD Trace, Run Thread log boxes
    terminal_panel.py             # Bottom tabbed terminal (Output | Events)
    footer.py                     # Status bar + horizontal execution timeline
  design/
    __init__.py                   # Package init
    theme.py                      # Color constants (BG, CYAN, IDE chrome colors)
    ide_style.py                  # ttk.Style for notebook tabs, sash styling
    layout.py                     # Legacy layout helper (unused by IDE shell)
    asset_loader.py               # Asset path resolution (MEIPASS-aware)
  animations/
    __init__.py                   # Animation exports
    sequencing/
      snowflake.py                # Snowflake icon glow animator
      ladder.py                   # StageLadderAnimator (phase state machine)
      triangle.py                 # RitualTriangleButton (submit control)
      handoff_badge.py            # HandoffCompleteBadge (completion indicator)
      status_indicator.py         # StatusIndicator (header status text)
      timeline.py                 # ExecutionTimeline (vertical or horizontal)
  hooks/
    __init__.py                   # Hook exports
    cmd_stream.py                 # CommandStreamHook (subprocess stdout capture)
  assets/                         # Icons, backgrounds (optional)
```

## Compatibility bridge

The app shell (`ice_ui.py`) aliases panel widget references to the top-level
`IceCrawlerUI` instance so that all existing animation/event methods work
without modification:

```python
self.stream_text   = self.right_sidebar.stream_text
self.phase_labels  = self.left_sidebar.phase_labels
self.status_line   = self.footer.status_line
# ... etc
```

This means `_animate()`, `_pump()`, `_refresh_from_fossils()`,
`_update_stream_box()`, `_update_cmd_box()`, `_update_thread_box()`,
`on_submit()`, `_lock()`, `_reset_phase_ladder()` all work without changes
to their method bodies.

## Animation hooks

Animation helpers live in `ui/animations/sequencing/`. The UI imports and
starts them at startup; no engine changes are required.
