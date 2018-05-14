#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import pytest
from hypothesis import given
from hypothesis.strategies import text

from recval.normalization import normalize, to_indexable_form


def test_basic():
    assert 'hello' == normalize("  hello ")


def test_nfc():
    assert normalize("   phơ\u0309 ") == normalize("pho\u031B\u0309 ")


@given(text())
def test_idempotence(s):
    """
    Normalizing something that is already normalized should not change it.
    """
    assert normalize(s) == normalize(normalize(s))


# ############################# Indexing tests ############################# #

def test_index():
    # i (->) %', # short-i elision
    assert "tanisi" == to_indexable_form("tan'si")

    # â (->) {ā}, # a + combining macron U+0304
    # ê (->) {ē}, # e + combining macron U+0304
    # î (->) {ī}, # i + combining macron U+0304
    # ô (->) {ō}, # o + combining macron U+0304

    # Â (->) {Ā}, # A + combining macron U+0304
    # Ê (->) {Ē}, # E + combining macron U+0304
    # Î (->) {Ī}, # I + combining macron U+0304
    # Ô (->) {Ō}, # O + combining macron U+0304

    # â (->) ā, # a macron
    # ê (->) ē, # e macron
    # î (->) ī, # i macron
    # ô (->) ō, # o macron

    # Â (->) Ā, # A macron
    # Ê (->) Ē, # E macron
    # Î (->) Ī, # I macron
    # Ô (->) Ō, # O macron

    # a (->) Â, # THESE to be deleted when the SoMe variant is running
    # e (->) Ê, # THESE to be deleted when the SoMe variant is running
    # i (->) Î, # THESE to be deleted when the SoMe variant is running
    # o (->) Ô, # THESE to be deleted when the SoMe variant is running

    # â (->) {â}, # a + combining circumflex accent U+0302
    # ê (->) {ê}, # e + combining circumflex accent U+0302
    # î (->) {î}, # i + combining circumflex accent U+0302
    # ô (->) {ô}, # o + combining circumflex accent U+0302

    # Â (->) {Â}, # A + combining circumflex accent U+0302
    # Ê (->) {Ê}, # E + combining circumflex accent U+0302
    # Î (->) {Î}, # I + combining circumflex accent U+0302
    # Ô (->) {Ô}, # O + combining circumflex accent U+0302

    # â (->) a, # THESE to be deleted when the SoMe variant is running
    # ê (->) e, # THESE to be deleted when the SoMe variant is running
    # î (->) i, # THESE to be deleted when the SoMe variant is running
    # ô (->) o, # THESE to be deleted when the SoMe variant is running

    # NS 152 materials consistantly write some vowels as long where Arok's
    # write them as short. E.G. NS 152 give 'askîy' and Arok gives 'askiy.'

    # â (->) A, # THESE to be deleted when the SoMe variant is running
    # ê (->) E, # THESE to be deleted when the SoMe variant is running
    # î (->) I, # THESE to be deleted when the SoMe variant is running
    # ô (->) O,  # THESE to be deleted when the SoMe variant is running

    # a (->) A, # THESE to be deleted when the SoMe variant is running
    # e (->) E, # THESE to be deleted when the SoMe variant is running
    # i (->) I, # THESE to be deleted when the SoMe variant is running
    # o (->) O,  # THESE to be deleted when the SoMe variant is running

    # a (->) â, # THESE to be deleted when the SoMe variant is running
    # e (->) ê, # THESE to be deleted when the SoMe variant is running
    # i (->) î, # THESE to be deleted when the SoMe variant is running
    # o (->) ô # THESE to be deleted when the SoMe variant is running

    # ;

    # # Explanation:
    # # lexical side (->) input
    # # Or, in other words:
    # # correct (->) in use out there
    # """
