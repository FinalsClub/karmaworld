#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
from __future__ import division
from collections import defaultdict
import nltk
import itertools
from operator import itemgetter
from pygraph.classes.digraph import digraph
from pygraph.algorithms.pagerank import pagerank
from pygraph.classes.exceptions import AdditionError


def _filter(tagged, tags=('NN', 'JJ', 'NNP')):
    pos_filtered = [item[0] for item in tagged if item[1] in tags]
    stopwords_filtered = [word.lower() for word in pos_filtered if not word.lower() in nltk.corpus.stopwords.words('english')]
    remove_punc = [item.replace('.', '') for item in stopwords_filtered]
    return remove_punc


def _normalize(words):
    lower = [word.lower() for word in words]
    remove_punc = [item.replace('.', '') for item in lower]
    return remove_punc


def _unique_everseen(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in itertools.ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def _common_ngrams(normalized_words, top_ordered_keywords, n):
    ngrams_in_top_keywords = set()
    common_ngrams = []

    for ngram_words in itertools.product(top_ordered_keywords, repeat=n):
        target_ngram = list(ngram_words)
        for i in range(len(normalized_words)):
            ngram = normalized_words[i:i+n]
            if target_ngram == ngram:
                ngrams_in_top_keywords.add(tuple(target_ngram))

    for words in ngrams_in_top_keywords:
        words_usage_in_ngram = 0
        individual_word_usage = defaultdict(lambda: 0)
        for i in range(len(normalized_words)):
            for word in words:
                if normalized_words[i] == word:
                    individual_word_usage[word] += 1
            if normalized_words[i:i+n] == list(words):
                words_usage_in_ngram += 1

        for word in words:
            ratio = words_usage_in_ngram / individual_word_usage[word]
            if ratio > 0.5:
                common_ngrams.append(words)
                break

    return common_ngrams


def find_keywords(document, word_count=10):
    """
    Credit to https://gist.github.com/voidfiles/1646117
    and http://acl.ldc.upenn.edu/acl2004/emnlp/pdf/Mihalcea.pdf
    """
    sentences = nltk.sent_tokenize(document)
    candidate_words = []
    all_words = []
    for sentence in sentences:
        words = nltk.word_tokenize(sentence)
        all_words.extend(words)
        tagged_words = nltk.pos_tag(words)
        filtered_words = _filter(tagged_words)
        candidate_words.extend(filtered_words)

    unique_word_set = _unique_everseen(candidate_words)

    gr = digraph()
    gr.add_nodes(list(unique_word_set))

    window_start = 0
    window_end = 2

    while 1:
        window_words = candidate_words[window_start:window_end]
        if len(window_words) == 2:
            try:
                gr.add_edge((window_words[0], window_words[1]))
            except AdditionError:
                pass
        else:
            break

        window_start += 1
        window_end += 1

    calculated_page_rank = pagerank(gr)
    di = sorted(calculated_page_rank.iteritems(), key=itemgetter(1), reverse=True)
    all_ordered_keywords = [w[0] for w in di]
    top_ordered_keywords = all_ordered_keywords[:word_count]

    normalized_words = _normalize(all_words)

    common_bigrams = _common_ngrams(normalized_words, top_ordered_keywords, 2)
    common_trigrams = _common_ngrams(normalized_words, top_ordered_keywords, 3)
    for words in common_bigrams + common_trigrams:
        for word in words:
            top_ordered_keywords.remove(word)
        top_ordered_keywords.insert(0, ' '.join(words))

    return top_ordered_keywords
