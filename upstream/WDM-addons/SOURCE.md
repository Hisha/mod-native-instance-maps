# WDM-addons Reference

WDM-addons is an upstream companion project associated with WDM-patch.

Upstream project:

https://github.com/Trimitor/WDM-Addons

Vendored from:

    revision  621d4de79f9b9a24586a9d7cdce0f57d8c78e395
    tree      08ffdb7a41f0504ad564701a23c849b624469f13  (WDM/locales/global)
    date      2026-08-07

## What is vendored here

`WDM/locales/global/*.lua` -- the eleven locale string tables WDM ships. These
are the authoritative source of this project's dungeon floor labels: the
Karazhan names published as `DUNGEON_FLOOR_KARAZHAN1..17` are WDM's own
strings, read verbatim and never retyped or translated here.

Files are byte-for-byte copies. `SHA256SUMS` records them:

    sha256sum -c SHA256SUMS   # run from upstream/WDM-addons

`itIT` and `ptBR` are not published by WDM and are therefore not vendored. Those
locales fall back to the stock client label, which is the stock behaviour.

## What is not vendored

The Stable Classic and Burning Crusade instance-map DBC and artwork import
continues to consume WDM-patch, not WDM-addons.

The WDM optional Caverns and Mines functionality may require additional
addon-side components and remains outside the instance-map import scope.