Maskwacîs recordings validation
===============================

[![Build Status](https://travis-ci.org/UAlbertaALTLab/recording-validation-interface.svg?branch=master)](https://travis-ci.org/UAlbertaALTLab/recording-validation-interface)
[![pyup.io Dependencies](https://pyup.io/repos/github/UAlbertaALTLab/recording-validation-interface/shield.svg)](https://pyup.io/repos/github/UAlbertaALTLab/recording-validation-interface/)


A Django web app for viewing and validating Cree recordings done in Maskwacîs.


Install
-------

Requires Python 3.7, [Pipenv][], and [ffmpeg].

[Pipenv]: https://github.com/pypa/pipenv#installation
[ffmpeg]: https://www.ffmpeg.org/

### Development environment

To install dependencies and setup for development (e.g., on your laptop):

```sh
make install-dev
```

This will also setup the [git pre-commit hook](https://www.viget.com/articles/two-ways-to-share-git-hooks-with-your-team/).

You will also need:

  - `crk.zhfst` from building [`lang-crk`] with `--enable-spellers`

  - `private/metadata.csv` from downloading the “Master Recordings
    MetaData” document on google drive as CSV

  - some sessions from `sapir:/data/av/backup-mwe/sessions` in
    `/data/sessions`; `2015-03-23-__-___-_` (6GB) is known to work.

[`lang-crk`]: https://github.com/giellalt/lang-crk

### Production

> **NOTE**: Before you continue, you may want to run
> `export PIPENV_VENV_IN_PROJECT=True` so that you can find the
> virtual environment later!

To install dependencies and setup for production (e.g., on the server):

```sh
make install-prod
```

Find configuration files and templates in `private/`.


### Testing

To install dependencies and setup for testing (e.g., on Travis-CI):

```sh
make install-test
```


### Configuring environment variables

The app needs to know:

 - where the raw recording sessions are
 - where to find the "Recordings Master MetaData" CSV file
 - where to place transcoded audio files
 - where to place SQLite3 database
 - [production-only] where to collect (i.e., copy) static files

These are configured in a file called `.env` in the root of this
repository.

> **NOTE**: `make install-*` should have created a `.env` for you to
> append to.

The additional configuration should following this template:

```sh
RECVAL_SESSIONS_DIR=/absolute/path/to/recording/sessions/
RECVAL_METADATA_PATH=/absolute/path/to/master-recordings-metadata.csv
RECVAL_SQLITE_DB_PATH=/absolute/path/to/sqlite3/database.sqlite3
STATIC_ROOT=/absolute/path/to/static/files/directory/  # (production-only)
```

Replace the paths as appropriate.


#### `RECVAL_SESSIONS_DIR`

This directory contains all of the recording sessions. Each
entry in the `RECVAL_SESSIONS_DIR/` is a subdirectory named in the
normalized session format. Each subdirectory has `.TextGrid` and `.wav`
files of the recording session.

For example, if I have sessions for 2018-01-01 and 2018-01-07am in
`/data/av/sessions`, then I will have the following line in `.env`:

```sh
RECVAL_SESSIONS_DIR=/data/av/sessions
```

And if I run the following commands, I should see the directory listing
for my sessions directory:

```sh
. .env
ls -F $RECVAL_SESSIONS_DIR
```

    2018-01-01-__-___-_/
    2018-01-07-AM-___-_/

If I then inspect the directory for 2018-01-07am:

```sh
ls
ls -F $RECVAL_SESSIONS_DIR/2018-01-07-AM-___-_/
```

I should get a directory containing files like this.

    Track 2_001.TextGrid
    Track 2_001.wav
    Track 3_001.TextGrid
    Track 3_001.wav
    Track 4_001.TextGrid
    Track 4_001.wav
    ...

**NOTE**: The `*.wav` files may be in a subdirectory called
`${SESSION_NAME}_Recorded`, if the recordings where done with Adobe
Audition. In this example, the `.wav` files would be in
`2018-01-07am_Recorded`.


#### `RECVAL_METADATA_PATH`

This should point to the "Master Recording MetaData" file, obtained from
Google Drive, downloaded as a CSV file. This file is explained more
thoroughly in [Creating the database for the first time][].


#### `RECVAL_SQLITE_DB_PATH`

This is the absolute path to the SQLite3 database---where all the
validation data, and user data will be stored. This file will be written
and read to *a lot*. It should not become terribly large, however; at
most, it might grow to be 1 GiB, but I expect it to stay much, much
lower.

Make sure this path is configured before running
`pipenv run python ./manage.py migrate`


### `STATIC_ROOT`

> **Note**: this does not need to be configured in development mode.

Where to collect (i.e., copy) static assets. This is needed to place CSS and
JavaScript in the right place so that the static web server can find them.

Set this to path that your web server can... well, serve from! Whenever you
change any static files, or update Django, remember to run:

    python manage.py collectstatic

This will copy all of the various static files to the configured directory.

See more: <https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-STATIC_ROOT>


### Creating the database for the first time

[Creating the database for the first time]: #creating-the-database-for-the-first-time

Before you import any data, you need the "Master Recording MetaData" (sic)
spreadsheet, available on Google Drive. This should have been downloaded using
the `./init` script from earlier, but if you still don't have, either download
it manually as a CSV file as `$RECVAL_METADATA_PATH`.

Then, initialize the database using the following command:

```sh
pipenv run python manage.py migrate
```

This will create all the necessary tables in the SQLite3 database.


### Importing recordings

In order to import recordings on Sapir, type the following:

```sh
pipenv run python manage.py importrecordings
```

This will automatically scan `$RECVAL_SESSIONS_DIR/` (defined in `.env`).

`$RECVAL_SESSIONS_DIR/` should be a directory filled with directories
(or symbolic links to directories) with filenames in the form of:

    {ISOdate}-{AM/PM}-{Location or '___'}-{Subsession or '_'}

For example, on Sapir, I might have something like this:

    $ export RECVAL_SESSIONS_DIR=/data/av/backup-mwe/sessions
    $ ls -1 $RECVAL_SESSIONS_DIR
    2015-05-08-AM-___-_
    2016-05-16-PM-___-_
    2016-11-28-AM-US-2
    2017-05-25-AM-DS-2
    2018-04-18-AM-KCH-_
    ...

Each directory should have `*.TextGrid` files paired with a `*.wav` file:

    $ ls -F1 $RECVAL_SESSIONS_DIR/2015-05-08-AM-___-_/
    2015-05-08-01.TextGrid
    2015-05-08-01.wav
    2015-05-08-02.TextGrid
    2015-05-08-02.wav
    2015-05-08-03.TextGrid
    2015-05-08-03.wav
    ...

### Collecting the static files

> **NOTE**: this is not relevant when in development mode or when `DEBUG=True`

In the production server, you must copy all of the static files to a single
folder where the web server (e.g., Apache, Nginx) can serve them without even
consulting the Django app.

To copy the files, ensure `STATIC_ROOT` is configured properly, then run:

```sh
pipenv run python manage.py collectstatic
```

### Creating a superuser (admin)

To access the admin panel, you'll need at least one admin user. To
create one, run the following command and follow the prompts:

```sh
pipenv run python manage.py createsuperuser
```

For more info, see Django's documentation on [createsuperuser][].

[createsuperuser]: https://docs.djangoproject.com/en/2.1/ref/django-admin/#createsuperuser


Running
-------

To run a development server, use the following.

```sh
pipenv run python manage.py runserver
```

The main site should be available at <http://localhost:8000/>. The admin
interface should be available at <http://localhost:8000/admin>.

The server can also be run through Docker by running:

```
docker-compose up --build
```
on a machine with Docker installed.

Testing
-------

To run the tests, type:

```
make test
```

This will run the [mypy][] static type checker, and then [pytest][].

[mypy]: http://mypy-lang.org/
[pytest]: https://docs.pytest.org/en/latest/

To edit the tests for `librecval`, see `tests/`. For Django tests, look
inside the `validation/tests` directory.


Web API
-------

There is one API call:

    /recording/_search/{query}

Where `{query}` is replaced by one ore more Cree word forms, written in
SRO. If more than one word form is supplied, each word form must be
separated by a single comma (`,`).

This will return a JSON array of recordings of those word forms.

Each entry in the returned array is a JSON object with the following
properties:

 - `wordform`: the word form that was matched by the query
 - `speaker`: the speaker's short code (e.g., something like `"ROS"` or `"JER"`)
 - `gender`: the speaker's gender: either `"M"` or `"F"` (all our speakers identify as male or female).
 - `dialect`: the region of Cree that this person speaks
 - `recording_url`: Absolute URI to the audio, encoded as AAC in an MP4
   container (a `*.m4a` file). This can be used in an `<audio>` tag.
 - `speaker_bio_url`: Absolute URI to the speaker's biography.

### Errors

Will responds with HTTP **404** if no recordings match the query. Note
that the recordings' speaker's _must_ have a non-null gender before they
appear in search results. So make sure all `Speaker` instances have
a non-null value for `gender`!


### Example


Finding recordings of 'nikiskisin' and 'kiskisiw':

```http
GET /recording/_search/nikiskisin,kiskisiw
```

Assume there are six recordings for `nikiskisin`, and none for
`kiskisiw`, this will return:

```json
[
    {
        "anonymous": false,
        "dialect": "Maskwacîs",
        "gender": "F",
        "recording_url": "http://sapir.artsrn.ualberta.ca/validation/recording/7353dda3d48799325ee62de0eceb4b50839382cfcf0ebf96c70d84fd37881201.m4a",
        "speaker": "ROS",
        "speaker_bio_url": "https://www.altlab.dev/maskwacis/Speakers/ROS.html",
        "speaker_name": "Rose Makinaw",
        "wordform": "nikiskisin"
    },
    {
        "anonymous": false,
        "dialect": "Maskwacîs",
        "gender": "F",
        "recording_url": "http://sapir.artsrn.ualberta.ca/validation/recording/dac08c374354594b7a77195daa4fd2e12a88acc5acf4e4894dd612354c1e7a92.m4a",
        "speaker": "ROS",
        "speaker_bio_url": "https://www.altlab.dev/maskwacis/Speakers/ROS.html",
        "speaker_name": "Rose Makinaw",
        "wordform": "nikiskisin"
    },
    {
        "anonymous": false,
        "dialect": "Maskwacîs",
        "gender": "M",
        "recording_url": "http://sapir.artsrn.ualberta.ca/validation/recording/1576034645a6b765ab40275a67390fa197ee3c7ed8cc949907d132df3c0f1c9e.m4a",
        "speaker": "GOR",
        "speaker_bio_url": "https://www.altlab.dev/maskwacis/Speakers/GOR.html",
        "speaker_name": "kîsikâw",
        "wordform": "nikiskisin"
    },
    {
        "anonymous": false,
        "dialect": "Maskwacîs",
        "gender": "M",
        "recording_url": "http://sapir.artsrn.ualberta.ca/validation/recording/a86939d888ff908d091538b2c1a3dc4fb383167b781b5dddddd4253342b0dace.m4a",
        "speaker": "GOR",
        "speaker_bio_url": "https://www.altlab.dev/maskwacis/Speakers/GOR.html",
        "speaker_name": "kîsikâw",
        "wordform": "nikiskisin"
    },
    {
        "anonymous": false,
        "dialect": "Maskwacîs",
        "gender": "F",
        "recording_url": "http://sapir.artsrn.ualberta.ca/validation/recording/2198ff134107ff474115cdb48ee36f88c17168e215fe424da4cc414bab0f4582.m4a",
        "speaker": "LOU",
        "speaker_bio_url": "https://www.altlab.dev/maskwacis/Speakers/LOU.html",
        "speaker_name": "Louise Wildcat",
        "wordform": "nikiskisin"
    },
    {
        "anonymous": false,
        "dialect": "Maskwacîs",
        "gender": "F",
        "recording_url": "http://sapir.artsrn.ualberta.ca/validation/recording/e8dd10846601861c1e9c4edf944b1e4da7670ed669fe027bd0b27e0af954e031.m4a",
        "speaker": "LOU",
        "speaker_bio_url": "https://www.altlab.dev/maskwacis/Speakers/LOU.html",
        "speaker_name": "Louise Wildcat",
        "wordform": "nikiskisin"
    }
]
```

### Generating Transcription Files
These are necessary in order to run Persephone and Simple4All against the current 
set of recordings.

The following steps should be performed from within the `pipenv shell`

First, populate the database by running:

```
python manage.py makemigrations
python manage.py migrate
python manage.py importrecordings
```

Then generate the .wav files:

```
python manage.py importrecording --wav --skip-db
```

This saves all the recording snippets to the `./audio` directory, unless otherwise specified 
(not recommended for this task).

Next, create the transcription files by running:

```
python manage.py writetranscriptions
```

This should create:
* A new folder for each speaker code, eg: `./audio/LOU`
* A copy of the .wav file in the speaker folder, eg: `./audio/LOU/wav/audio_id.wav`
* A transcription file to be used by **Persephone**, eg: `./audio/LOU/label/audio_id.txt`
* A transcription file to be used by **Simple4All**, eg: `./audio/LOU/s4a/audio_id.txt`


Frequently Asked Questions
--------------------------

### What is “recval”?

It's short for **Rec**ordings **val**idation. I didn't want to type that
out all the time, and I didn't want to puts spaces, hyphens or
underscores to refer to it.

### What is `librecval`?

`librecval` is a library for extracting recordings, transcoding
recordings to a normalized format, and combining the recordings with
metadata, as well as representing recordings data in an
framework-agnostic way. This library *should* be devoid of references or
dependencies on any web framework or database backend.

### What is `recvalsite`?

It's the Django project for the **rec**ording **val**idation **site**.
This aggregates all of the Django apps under one deployable website.


License
-------

Copyright (C) 2018 Eddie Antonio Santos <easantos@ualberta.ca>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
