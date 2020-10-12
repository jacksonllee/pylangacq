# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [0.12.0] - 2020-10-11

### Added
* Added support for Python 3.9.
* Enabled `black` to enforce styling consistency.

## [0.11.0] - 2020-07-02

### Added
* Started testing Python 3.7 and 3.8 on continuous integration. (#9)
* Add time marker support (available at `_SingleReader`),
  originally contributed at #3 by @hellolzc. (#8)

### Changed
* Switched from Travis CI to CircleCI for autobuilds. (#9)
* Switched README from reStructuredText to Markdown. (#9)
* Removed conversational quotes in utterance processing; updated test CHAT file
  to match the latest CHILDES data. (#7)

### Removed
* Dropped support for Python 2.7, 3.4, and 3.5.
  All code related to Python 2+3 cross compatibility was removed. (#9)

## [0.10.0] - 2017-11-02

* Fixed unicode handling across Python 2 and 3
* Renamed method `find_filename` of `Reader` as `abspath`.
* Fixed bug in `Reader` method decorators
* Handled multiple dates of recording in one CHAT file.
  The method `dates_of_recording` of a `Reader` instance now returns a list
  of dates.
* Implemented the `exclude` parameter in various `Reader` methods for
  excluding specific participants.
* Fixed bug in IPSyn.

## [0.9.0] - 2017-10-25

* Python 2 and 3 cross compatibility
* Renamed the `grammar.py` module as `dependency.py`
    * Rewrite the class `DependencyGraph`;
      do not subclass from networkx's DiGraph anymore
      (and we remove networkx as a dependency of this library)
* Removed multiprocessing in reading data files.
  Datasets are usually small enough that the performance gain, if any,
  wouldn't be worth it for the potential issues w.r.t. spawning multiple
  processes)
* Developed capabilities to handle PhonBank data for
  handling `%pho` and `%mod` tiers
* Improved `clean_utterance()`
* Added parameter `encoding` in `read_chat()`
* Added `get_lemma_from_mor()`
* Added `date_of_recording()` and `date_of_birth()`; remove `date()`
* Added `clean_word()`
* Restricted `get_IPSyn()` to only the first 100 utterances
* Added tests

## [0.8] - 2016-01-30

* Library now compatible only with Python 3.4 or above
* For class `Reader`:

  * Defined `read_chat()` for initializing a `Reader` object
  * Added parameter `by_files` to various methods; remove the "all_" methods
  * Added reader manipulation methods:
    `update()`, `add()`, `remove()`, `clear()`
  * Added parameter `sorted_by_age` in `filenames()`
  * Added parameter `month` in `age()`
  * Added `word_ngrams()`
  * Added `find_filename()`
  * Added language development measures: `MLUm()`, `MLUw()`, `TTR()`, `IPSyn()`
  * Added `search()` and `concordance()`
  * Allowed regular expression matching for parameter `participant`
  * Added output formats for dependency graphs: `to_tikz()` and `to_conll()`
  * Distinguished `participant_name` and `participant_role` in metadata
  * The `@Languages` header contents are treated as a list
    but not a set now for ordering in bi/multilingualism
  * Undid collapses in transcriptions such as `[x 4]`
  * Various bug fixes

## [0.7] - 2016-01-06

* Added `part_of_speech_tags()` in `SingleReader`
* Added "all X" methods in `Reader`
* Bug fixes: `clean_utterance()`, `DependencyGraph`

## [0.6] - 2015-12-27

* `cha_lines` optimized
* Methods added: `tagged_words()`, `words()`, `tagged_sents()`, `sents()`
* Tier detection revamped. `tier_sniffer()` method removed,
  with `self.tier_markers` in `SingleReader`
  now being a set of %-tier markers.
* `len()` for `SingleReader` added
* `word_frequency()` for `SingleReader` added
* Module `grammar` added, with class `DependencyGraph` being set up
* Static methods in classes pulled out

## [0.5] - 2015-12-16

* New `utterances()` method for extracting utterances from transcripts
* `_clean_utterance` method developed
  for filtering CHAT annotations away in utterances
* Standardizing terminology:
  use "participant(s)" consistently instead of "speaker(s)"

## [0.4] - 2015-12-13

* New `number_of_utterances()` method for both `Reader` and `SingleReader`
* To avoid confusion, `metadata()` method is removed.
* Extraction of utterances and tiers with dict `index_to_tiers`

## [0.3] - 2015-12-09

* Class `Reader` can read multiple `.cha` files.
  The methods associated with `Reader` are mostly a dict mapping
  from a absolute-path filename to something.
  `Reader` depends on the class `SingleReader` for a single CHAT file.
* Following the conventional CHILDES and CHAT terminology,
  the `metadata()` method in `Reader` is renamed `headers()`
  (though a "new" `metadata()` method is defined and points to
  `headers()` for convenience).

## [0.2] - 2015-12-05

* new methods for class `Reader`:
  `languages()`, `date()`, `participants()`, `participant_codes()`

## [0.1] - 2015-12-04

* first commit; set up the `chat` submodule
* class `Reader` defined for reading CHAT files,
  with methods `cha_lines()`, `metadata()`, and `age()`
