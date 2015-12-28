Change log
==========

Current version: 0.5

- Version 0.6 in progress

    * `cha_lines` optimized
    * Methods added: `tagged_words`, `words`, `tagged_sents`, `sents`
    * Tier detection revamped. `tier_sniffer` method removed, with `self.tier_markers` in `SingleReader` now being a set of %-tier markers.
    * Static methods in classes pulled out
    * `len()` for `SingleReader` added
    * Submodule `grammar` added, with class `DependencyGraph` being set up
    * `word_frequency()` for `SingleReader` added

- Version 0.5 2015-12-16

    * New `utterances` method for extracting utterances from transcripts
    * `_clean_utterance` method developed for filtering CHAT annotations away in utterances
    * Standardizing terminology: use "participant(s)" consistently instead of "speaker(s)"

- Version 0.4 2015-12-13

    * New `number_of_utterances` method for both `Reader` and `SingleReader`
    * To avoid confusion, `metadata` method is removed
    * Extraction of utterances and tiers with dict `index_to_tiers`

- Version 0.3 2015-12-09

    * class `Reader` can read multiple `.cha` files. The methods associated with `Reader` are mostly a dict mapping from a absolute-path filename to something. `Reader` depends on the class `SingleReader` for a single `.cha` file.
    * Following the conventional CHILDES and CHAT terminology, the `metadata` method in `Reader` is renamed `headers` (though a "new" `metadata` method is defined and points to `headers` for convenience).

- Version 0.2 2015-12-05

    * new methods for class `Reader`: `languages`, `date`, `participants`, `participant_codes`

- Version 0.1 2015-12-04

    * first commit; set up the `chat` submodule
    * class `Reader` defined for reading `.cha` files, with methods `cha_lines`, `metadata`, and `age`

