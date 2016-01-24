# -*- coding: utf-8 -*-

from __future__ import division

def get_MLUm(tagged_sents, pos_to_ignore=None):
    """Mean length of utterance (MLU) in morphemes"""
    # *tagged_sents* are already filtered for the desired participant like 'CHI'
    total_utterance_count = 0
    total_morpheme_count = 0

    for tagged_sent in tagged_sents:
        total_utterance_count += 1

        for tagged_word in tagged_sent:
            pos = tagged_word[1]
            morph = tagged_word[2]

            if pos_to_ignore and pos in pos_to_ignore:
                continue

            total_morpheme_count += 1
            total_morpheme_count += morph.count('-')
            total_morpheme_count += morph.count('~')

    if total_utterance_count:
        return total_morpheme_count / total_utterance_count
    else:
        return 0


def get_MLUw(sents, words_to_ignore=None):
    """Mean length of utterance (MLU) in words"""
    # *sents* are already filtered for the desired participant like 'CHI'
    total_utterance_count = 0
    total_word_count = 0

    for sent in sents:
        total_utterance_count += 1

        for word in sent:
            if words_to_ignore and word in words_to_ignore:
                continue
            total_word_count += 1

    if total_utterance_count:
        return total_word_count / total_utterance_count
    else:
        return 0


def get_TTR(word_freq_dict):
    """Type-token ratio (TTR)"""
    # *word_freq_dict* already filtered for the desired participant like 'CHI'
    return len(word_freq_dict) / sum(word_freq_dict.values())


def get_IPSyn():
    """Index of Productive Syntax (IPSyn)"""
    return  # TODO: work in progress
