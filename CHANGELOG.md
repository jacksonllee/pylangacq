# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [0.13.0] - 2021-03-15

**API-breaking changes:**
The `Reader` class has been completely rewritten.
A couple methods have been removed, while others have been renamed.
For methods that remain (renamed or not),
their behavior for output data structure and arguments allowed has been changed.
The details are in the following.

### Added
* New classmethods of `Reader` for reader instantiation:
  - `from_zip`
  - `from_dir`
* New classes to better structure CHAT data:
  - `Utterance`
  - `Token`
  - `Gra`
* New Reader methods:
  - `append_left`, `extend`, `extend_left`, `pop`, `pop_left`
  - `tokens` (which gives `Token` objects, essentially the "tagged words" from before)
* In the header dictionary, each participant's info has the new key `"dob"`
  for date of birth (if the info is available in the CHAT header).
  The corresponding value is a `datetime.date` object.
  (The same info was previously exposed as the `Reader` method `date_of_birth`,
  now removed.)
* The test suite now covers code snippets in both the docstrings and `.rst` doc files.

### Changed
* CHAT parsing in `Reader` instantiation has been completely rewritten.
  The previous private class `_SingleReader` has been removed.
  This private class duplicated a lot of the `Reader` code,
  which made it hard to make changes.
* The `Reader` rewrite has also greatly sped up the reading and parsing of CHAT data.
* The `by_files` argument, which many `Reader` methods has,
  now gives you a simpler list of results for each data file,
  no longer the previous output of a dict that mapped a file path to the file's
  result.
* The `participant` argument, which many `Reader` methods has for specifying
  which participants' data to include in the output, has been renamed as
  `participants` to avoid confusion. There is no change to its behavior of
  handling either a single string (e.g., ``"CHI"``) or a collection of strings
  (e.g., ``{"CHI", "MOT"}``) .
* The following `Reader` methods have been renamed as indicated,
  some for stylistic or Pythonic reasons, others for reasons as given:
   - `age` -> `ages`
   - `number_of_utterances` -> `n_utterances`
   - `number_of_files` -> `n_files`
   - `filenames` -> `file_paths`
   - `MLU` -> `mlu`
   - `MLUm` -> `mlum`
   - `MLUw` -> `mluw`
   - `TTR` -> `ttr`
   - `IPSyn` -> `ipsyn`
   - `word_frequency` -> `word_frequencies`
   - `from_chat_str` -> `from_strs`
   - `from_chat_files` -> `from_files`
   - `add` -> `append`.
     Since the data files in a `Reader` have a natural ordering (by time of
     recording sessions, and therefore commonly by file paths as well),
     a reader is list-like rather than an unordered set of data files,
     which `add` would suggest.
   - `participant_codes` -> `participants`.
     Before this version, the methods `participant_codes` (for CHI, MOT, etc) and
     `participants` (for, say, Eve, Mother, Investigator, etc) co-existed,
     but in practice we mostly only care about CHI, MOT, etc.
     So the method `participants` for Eve etc has been removed,
     and `participant_codes` has been renamed as `participants`.
* Each participant's info in a header dictionary has these keys renamed:
   - `participant_name` -> `name`
   - `participant_role` -> `role`
   - `SES` -> `ses` (socioeconomic status)
* The class `DependencyGraph` has been made private
  (i.e., now `_DependencyGraph` with a leading underscore).
  Its functionality hasn't really changed (it's used in the computation of IPSyn).
  It may be made more visible again in the future if more functionality
  related to grammatical relations is developed in the package.
* Switched to sphinx-rtd-theme as the documentation theme.
* Switched to CircleCI orbs; update dev requirements' versions.

### Deprecated
* The following Reader methods have been deprecated:
  - `tagged_sents` (use `tokens` with `by_utterances=True` instead)
  - `tagged_words` (use `tokens` with `by_utterances=False` instead)
  - `sents` (use `words` with `by_utterances=True` instead)

### Removed
* The following methods of the `Reader` class have been removed:
   - `abspath`. Use `file_paths` instead.
   - `index_to_tiers`. All the unparsed tiers are now available from `utterances`.
   - `participant_codes`. It's been renamed as `participants`, another method now removed; see "Changed" above.
   - `part_of_speech_tags`
   - `update` and `remove`. A reader is a list-like collection of CHAT data files,
     not a set (which `update` and `remove` would suggest). 
   - `search` and `concordance`. To search, use one of
     the `words`, `tokens`, and `utterances` methods to walk through a reader's CHAT data
     and keep track of elements of interest.
   - `date_of_birth`. The info is now available under `headers`, in each participant's
     `"dob"` key.

### Fixed
* Handled `[/-]` in cleaning utterances.
* `[x <number>]` means a repetition of the previous word/item, not repetition
  of the entire utterance.

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
