#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright (C) 2018 Eddie Antonio Santos <easantos@ualberta.ca>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from librecval.normalization import normalize
from librecval.recording_session import Location, SessionID, TimeOfDay


def choices_from_enum(enum_class):
    """
    Utility for converting a Python 3.4+ Enum into a choices for a Django
    model. Retuns a dictionary suitable for using as keyword arguments for a
    CharField.
    """
    choices = tuple((x.value, x.value) for x in enum_class)
    max_length = max(len(x.value) for x in enum_class)
    return dict(max_length=max_length, choices=choices)


def arguments_for_choices(choices):
    """
    Given a sequence of choices, generates the appropriate keyword arguments
    for a CharField.
    """
    return dict(choices=choices,
                max_length=max(len(choice[0]) for choice in choices))


class Phrase(models.Model):
    """
    A recorded phrase. A phrase may either be a word or a sentence with at
    least one recording. Phrases may be awaiting validation, or may have
    already be validated.
    """

    WORD = 'word'
    SENTENCE = 'sentence'
    KIND_CHOICES = (
        (WORD, 'Word'),
        (SENTENCE, 'Sentence'),
    )

    MASKWACÎS_DICTIONARY = 'MD'
    NEW_WORD = 'new'
    ORIGIN_CHOICES = (
        (MASKWACÎS_DICTIONARY, 'Maskwacîs Dictionary'),
        (NEW_WORD, 'New word'),
    )

    transcription = models.CharField(help_text="The transciption of the Cree phrase.",
                                     blank=False,
                                     max_length=256)
    translation = models.CharField(help_text="The English translation of the phrase.",
                                   blank=False,
                                   max_length=256)
    kind = models.CharField(help_text="Is this phrase a word or a sentence?",
                            blank=False,
                            **arguments_for_choices(KIND_CHOICES))
    validated = models.BooleanField(help_text="Has this phrase be validated?",
                                    default=False)
    # TODO: during the import process, try to determine automatically whether
    # the word came from the Maswkacîs dictionary.
    origin = models.CharField(help_text="How did we get this phrase?",
                              null=True, default=NEW_WORD,
                              **arguments_for_choices(ORIGIN_CHOICES))

    ALLOWED_TRANSCRIPTION_CHARACTERS = set('ptkcsmnywh rl êiîoôaâ ()')

    def clean(self):
        """
        Cleans the text fields.

        TODO: It can also check if the transcription is valid Cree.
        """
        self.transcription = normalize(self.transcription).lower()
        assert all(c in self.ALLOWED_TRANSCRIPTION_CHARACTERS for c in self.transcription)

    def __str__(self) -> str:
        return self.transcription


class Speaker(models.Model):
    """
    A person who spoke at the recording sessions.
    """

    # We store gender so that we can categorize how their voice sounds.
    # The community is interested in hear each word with both a male and a
    # female voice.
    # Although I believe gender is a spectrum (and can even be null!),
    # we personally know all of the speakers, and they all identifiy as either
    # male or female ().
    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )

    code = models.CharField(help_text='Short code assigned to speaker in the ellicitation metadata.',
                            max_length=8, primary_key=True)
    # Initially, gender and full name in the database will be imported as
    # None/null, but they should ultimately be set manually.
    full_name = models.CharField(help_text="The speaker's full name.",
                                 max_length=128)
    gender = models.CharField(help_text='Gender of the voice.',
                              max_length=1, choices=GENDER_CHOICES,
                              null=True)

    def clean(self):
        self.code = self.code.strip().upper()
        if not re.match(r'\A[A-Z]+[0-9]?\Z', self.code):
            raise ValidationError(_('Speaker code must be a single all-caps word, '
                                    'optionally followed by a digit'))


class RecordingSession(models.Model):
    """
    A session during which a number of recordings were made.

    Example sessions:

    2017-11-01-AM-OFF-_:
        Happended on the morning of November 1, 2017 in the office.
    """

    # See librecval for the appropriate choices:

    date = models.DateField(help_text="The day the session occured.")
    time_of_day = models.CharField(help_text="The time of day the session occured. May be empty.",
                                   blank=True, default='',
                                   **choices_from_enum(TimeOfDay))
    location = models.CharField(help_text="The location of the recordings. May be empty.",
                                blank=True, default='',
                                **choices_from_enum(Location))
    subsession = models.IntegerField(help_text="The 'subsession' number, if applicable.",
                                     null=True, blank=True)

    @classmethod
    def create_from(cls, session_id):
        """
        Create the model from the internal data class.
        """
        return cls(date=session_id.date,
                   # `and` prevents accessing attributes on a None value.
                   time_of_day=session_id.time_of_day and session_id.time_of_day.value,
                   location=session_id.location and session_id.location.value,
                   subsession=session_id.subsession)

    def as_session_id(self):
        """
        Converts back into a SessionID object.
        """
        return SessionID(date=self.date,
                         # `and` prevents calling .parse() on a None value.
                         time_of_day=self.time_of_day and TimeOfDay.parse(self.time_of_day),
                         location=self.location and Location.parse(self.location),
                         subsession=self.subsession)

    def __str__(self):
        return str(self.as_session_id())
