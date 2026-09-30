# Third-Party Sources

mod-native-instance-maps transforms third-party instance-map data for use with
mod-content-manager and a World of Warcraft 3.3.5a client.

## WDM-patch

Original project:

https://github.com/Trimitor/WDM-patch

Author/project maintainer: Trimitor

The source data and artwork under:

    upstream/WDM-patch/Stable/

originate from WDM-patch.

mod-native-instance-maps does not claim authorship or ownership of those
original assets.

The exact upstream revision and cryptographic fingerprints of the imported
source are recorded in:

    upstream/WDM-patch/SOURCE.md
    upstream/WDM-patch/SHA256SUMS

## WDM-addons

Reference project:

https://github.com/Trimitor/WDM-Addons

Author/project maintainer: Trimitor

The eleven client locale string tables under:

    upstream/WDM-addons/WDM/locales/global/

originate from WDM-addons. They are the sole source of this project's dungeon
floor labels: the names published as `DUNGEON_FLOOR_<INSTANCE><n>` are read
verbatim from these files and are never retyped or translated here. The
import reads only the vendored copies, never a network checkout, so regenerating
a manifest needs nothing outside this repository.

The upstream revision and cryptographic fingerprints are recorded in:

    upstream/WDM-addons/SOURCE.md
    upstream/WDM-addons/SHA256SUMS

WDM publishes no `itIT` or `ptBR` table. Those two client locales therefore keep
the stock client label for every map, which is stock behaviour rather than a gap
in the import.

The Caverns and Mines addon functionality remains outside the instance-map
import scope.

## WoW 3.3.5a client data

Author/publisher: Blizzard Entertainment

The stock client table of contents under:

    upstream/wow-3.3.5a-build-12340/Interface/FrameXML/FrameXML.toc

is extracted unmodified from:

    Data/enUS/locale-enUS.MPQ   member  Interface\FrameXML\FrameXML.toc
    build 12340

It is vendored so the digest a package declares can be reviewed without the
client installed, and so the EPF is self-contained. `mod-content-manager` does
not regenerate FrameXML: it verifies this exact file's SHA-256
(`36ccfed8ad8e424fb312c942a75bd17c6091dd264df8653f117dcfe8417d91a3`) and inserts
a single module line after the stock `## add new modules above here` marker. No
other stock FrameXML file is read, replaced or required.

The container, member path, digest and byte count are recorded in:

    upstream/wow-3.3.5a-build-12340/SOURCE.json
    upstream/wow-3.3.5a-build-12340/SHA256SUMS

This file is redistributed unmodified for interoperability with an owned local
client. It is not authored by this project.
