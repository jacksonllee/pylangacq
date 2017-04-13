Change log
==========

Current stable release version: 0.8

Version 0.9.0 in progress

* Phonetics and phonology -- develop capabilities to handle PhonBank data:
  * Recognize and parse `%pho` and `%mod` tiers
  * Improve `clean_utterance()`
* Add parameter `encoding` in `read_chat()`
* Add `get_lemma_from_mor()`
* Add `date_of_recording()` and `date_of_birth()`; deprecate `date()`
* Add `clean_word()`
* Restrict `get_IPSyn()` to only the first 100 utterances

Version 0.8 2016-01-30

* Library now compatible only with Python 3.4 or above
* For class `Reader`:

  * Define `read_chat()` for initializing a `Reader` object
  * Add parameter `by_files` to various methods; remove the "all_" methods
  * Add reader manipulation methods:
    `update()`, `add()`, `remove()`, `clear()`
  * Add parameter `sorted_by_age` in `filenames()`
  * Add parameter `month` in `age()`
  * Add `word_ngrams()`
  * Add `find_filename()`
  * Add language development measures: `MLUm()`, `MLUw()`, `TTR()`, `IPSyn()`
  * Add `search()` and `concordance()`
  * Allow regular expression matching for parameter `participant`
  * Add output formats for dependency graphs: `to_tikz()` and `to_conll()`
  * Distinguish `participant_name` and `participant_role` in metadata
  * The `@Languages` header contents are treated as a list
    but not a set now for ordering in bi/multilingualism
  * "Undo" collapses in transcriptions such as `[x 4]`
  * Various bug fixes

Version 0.7 2016-01-06

* Add `part_of_speech_tags()` in `SingleReader`
* Add "all X" methods in `Reader`
* Bug fixes: `clean_utterance()`, `DependencyGraph`

Version 0.6 2015-12-27

* `cha_lines` optimized
* Methods added: `tagged_words()`, `words()`, `tagged_sents()`, `sents()`
* Tier detection revamped. `tier_sniffer()` method removed,
  with `self.tier_markers` in `SingleReader`
  now being a set of %-tier markers.
* `len()` for `SingleReader` added
* `word_frequency()` for `SingleReader` added
* Module `grammar` added, with class `DependencyGraph` being set up
* Static methods in classes pulled out

Version 0.5 2015-12-16

* New `utterances()` method for extracting utterances from transcripts
* `_clean_utterance` method developed
  for filtering CHAT annotations away in utterances
* Standardizing terminology:
  use "participant(s)" consistently instead of "speaker(s)"

Version 0.4 2015-12-13

* New `number_of_utterances()` method for both `Reader` and `SingleReader`
* To avoid confusion, `metadata()` method is removed.
* Extraction of utterances and tiers with dict `index_to_tiers`

Version 0.3 2015-12-09

* Class `Reader` can read multiple `.cha` files.
  The methods associated with `Reader` are mostly a dict mapping
  from a absolute-path filename to something.
  `Reader` depends on the class `SingleReader` for a single CHAT file.
* Following the conventional CHILDES and CHAT terminology,
  the `metadata()` method in `Reader` is renamed `headers()`
  (though a "new" `metadata()` method is defined and points to
  `headers()` for convenience).

Version 0.2 2015-12-05

* new methods for class `Reader`:
  `languages()`, `date()`, `participants()`, `participant_codes()`

Version 0.1 2015-12-04

* first commit; set up the `chat` submodule
* class `Reader` defined for reading CHAT files,
  with methods `cha_lines()`, `metadata()`, and `age()`
