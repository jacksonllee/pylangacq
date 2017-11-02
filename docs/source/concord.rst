.. _concord:

Word search and concordance
===========================

Searching can be conveniently done by ``search()`` and ``concordance()``:

==========================  =============================================================
Method                      Return object
==========================  =============================================================
search(*search_item*)       list of elements containing *search_item*
concordance(*search_item*)  list of sents (rendered as str and aligned for *search_item*)
==========================  =============================================================

Both methods have the obligatory parameter *search_item*.
They share the following optional parameters:

* ``participant`` -- see :ref:`cds`
* ``by_files`` -- see :ref:`reader_properties`
* ``lemma`` -- default: False. If True, *search_item* refers to the lemma given
  by "mor" in the tagged words. Otherwise, *search_item* refers to the word
  token string.
* ``match_entire_word`` -- default: True. If False, *search_item* can match
  as a substring.


The ``search(search_item)`` method has two additional optional parameters:

* ``output_tagged`` -- default: True. If False, "words" in the return object
  are plain word token strings; otherwise they are tagged words of
  (word, pos, mor, rel).
* ``output_sents`` -- default: True. If False, the return object is a list of
  words (tagged or untagged), rather than a list of sents.
