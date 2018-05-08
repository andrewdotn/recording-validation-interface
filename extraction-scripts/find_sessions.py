#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright © 2018 Eddie Antonio Santos. All rights reserved.
# Derived from a Praat script by Timothy Mills

import argparse
import logging
from pathlib import Path
from decimal import Decimal

from pydub import AudioSegment  # type: ignore
from textgrid import TextGrid  # type: ignore
from slugify import slugify

from recval.normalization import normalize

here = Path('.')
logger = logging.getLogger(__name__)
info = logger.info
warn = logger.warn

parser = argparse.ArgumentParser()
parser.add_argument('master_directory', default=here, type=Path,
                    help='Where to look for session folders')
parser.add_argument('word_directory', default=here / 'words', type=Path,
                    help='Where to dump words', nargs='?')
parser.add_argument('sentence_directory', default=here / 'sentences', type=Path,
                    help='Where to dump sentences', nargs='?')
parser.add_argument('session_codes', default=here / 'speaker-codes.csv', type=Path,
                    help='A TSV that contains codes for sessions...?', nargs='?')
parser.add_argument('--word-filename', default='word_codes.txt')
parser.add_argument('--sentence-filename', default='word_codes.txt')


WORD_TIER_ENGLISH = 0
WORD_TIER_CREE = 1
SENTENCE_TIER_ENGLISH = 2
SENTENCE_TIER_CREE = 3


def extract_items(sound: AudioSegment,
                  text_grid: TextGrid,
                  word_directory: Path,
                  sentence_directory: Path,
                  word_filename: str,
                  sentence_filename: str,
                  session: str,  # Something like "2015-05-05am"
                  speaker: str,  # Something like "ABC"
                  ) -> None:
    sentence_save = sentence_directory / sentence_filename
    word_save = word_directory / word_filename
    # TODO: select the sound and the text grid

    # Not required: counting words and sentences extracted

    assert len(text_grid.tiers) >= 2, "TextGrid has too few tiers"
    # TODO: Ensure the name of the tier contains \bCREE\b or \bCrk\b.
    cree_words_intervals = text_grid.tiers[WORD_TIER_CREE]
    # TODO: Ensure the name of the tier contains \bEnglish\b, \beng\b or \ben\b.
    english_words_intervals = text_grid.tiers[WORD_TIER_ENGLISH]

    for interval in cree_words_intervals:
        if not interval.mark:
            # This interval is empty, for some reason.
            continue

        transcription = normalize(interval.mark)

        start = to_milliseconds(interval.minTime)
        end = to_milliseconds(interval.maxTime)
        midtime = (interval.minTime + interval.maxTime) / 2
        # TODO: determine if it's an isolated word or an example sentence
        # TODO: Get interval at time sentenceTierCree, midTime
        # TODO: get sentence label

        is_word = True
        if is_word:
            # Get english gloss
            english_interval = english_words_intervals.intervalContaining(midtime)
            translation = normalize(english_interval.mark)

            # Snip out the sounds.
            sound_bite = sound[start:end]
            # tmills: normalize sound levels (some speakers are very quiet)
            sound_bite.normalize(headroom=0.1)  # dB

            # Export it.
            slug = slugify(f"{transcription}-{session}-{speaker}-{start}",
                           to_lower=True)
            sound_bite.export(str(Path('/tmp') / f"{slug}.wav"))

            # import code; code.interact(local=locals())


def to_milliseconds(seconds: Decimal) -> int:
    return int(seconds * 1000)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()

    # TODO: read session codes?

    info('Scanning %s for sessions...', args.master_directory)
    for session_dir in args.master_directory.iterdir():
        if not session_dir.resolve().is_dir():
            info('... rejecting %s; not a directory', session_dir)
            continue

        info(' ... Scanning %s for .TextGrid files', session_dir)
        text_grids = list(session_dir.glob('*.TextGrid'))
        info(' ... %d text grids', len(text_grids))

        for text_grid in text_grids:
            sound_file = text_grid.with_suffix('.wav')
            # TODO: tmill's kludge for certain missing filenames.
            if not sound_file.exists():
                warn(' ... ... could not find cooresponding audio for %s',
                     text_grid)
                continue

            assert text_grid.exists() and sound_file.exists()
            info('... ... Matching sounds file for %s', text_grid)
            # TODO: load "long" sound file
            # TODO: load from file: annotation

            # TODO: "Select" the sessino table ID
            # TODO: something about speaker-codes?
            # TODO: get speaker
            session = session_dir.stem
            speaker = '???'

            info(' ... ... Extract items from %s using speaker ID %s',
                 sound_file, speaker)

            extract_items(AudioSegment.from_file(str(sound_file)),
                          TextGrid.fromFile(str(text_grid)),
                          args.word_directory, args.sentence_directory,
                          args.word_filename, args.sentence_filename,
                          session, speaker)
