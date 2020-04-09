# -*- coding: utf-8 -*-

import importlib
from inspect import signature
import io
import os
import sys
import pytest

import mirdata
import mirdata.track as track
from tests.test_utils import DEFAULT_DATA_HOME

DATASETS = [importlib.import_module("mirdata.{}".format(d)) for d in mirdata.__all__]
CUSTOM_TEST_TRACKS = {
    'beatles': '0111',
    'guitarset': '03_BN3-119-G_solo',
    'medley_solos_db': 'd07b1fc0-567d-52c2-fef4-239f31c9d40e',
    'medleydb_melody': 'MusicDelta_Beethoven',
    'rwc_classical': 'RM-C003',
    'rwc_jazz': 'RM-J004',
    'rwc_popular': 'RM-P001',
    'salami': '2',
    'tinysol': 'Fl-ord-C4-mf-N-T14d',
}


def test_cite():
    for dataset in DATASETS:
        text_trap = io.StringIO()
        sys.stdout = text_trap
        dataset.cite()
        sys.stdout = sys.__stdout__


def test_download():
    for dataset in DATASETS:
        assert hasattr(dataset, 'download')
        assert hasattr(dataset.download, '__call__')
        params = signature(dataset.download).parameters
        assert 'data_home' in params
        assert params['data_home'].default is None


def test_validate():
    for dataset in DATASETS:
        data_home = os.path.join('tests/resources/mir_datasets', dataset.DATASET_DIR)
        dataset.validate(data_home=data_home)
        dataset.validate(data_home=data_home, silence=True)
        dataset.validate(data_home=None, silence=True)


def test_load_and_trackids():
    for dataset in DATASETS:
        track_ids = dataset.track_ids()
        assert type(track_ids) is list
        trackid_len = len(track_ids)

        data_home = os.path.join('tests/resources/mir_datasets', dataset.DATASET_DIR)
        dataset_data = dataset.load(data_home=data_home)
        assert type(dataset_data) is dict
        assert len(dataset_data.keys()) == trackid_len

        dataset_data_default = dataset.load()
        assert type(dataset_data_default) is dict
        assert len(dataset_data_default.keys()) == trackid_len


def test_track():
    jams_temporary_exceptions = ['dali']
    data_home_dir = 'tests/resources/mir_datasets'

    for dataset in DATASETS:
        # Name of module. e.g. "rwc_classical"
        module_name = dataset.__name__.split('.')[1]

        # Name of dataset, e.g. "RWC Classical"
        dataset_name = dataset.name

        # Name of directory, e.g. "RWC-Classical"
        dir_name = DATASET_DIR

        print(module_name)

        # check that name :
        # * only contains alphanumeric characters, hyphens, underscores, or spaces
        # * begins with a letter (this is important for Python module names)
        # * is at least three characters long
        # * ends with an alphanumeric character
        bool(re.match("^[a-zA-Z][a-zA-Z0-9_\\- ]+[a-zA-Z0-9]$", dataset_name))

        # check that directory name has no space in it
        assert " " not in dir_name

        # check that one can infer module name from directory name
        assert module_name == lower(dir_name.replace("-", "_"))

        # check that module name does not have adjacent underscores
        assert "__" not in module_name

        if module_name in CUSTOM_TEST_TRACKS:
            trackid = CUSTOM_TEST_TRACKS[module_name]
        else:
            trackid = dataset.track_ids()[0]

        track_default = dataset.Track(trackid)
        assert track_default._data_home == os.path.join(
            DEFAULT_DATA_HOME, dataset.DATASET_DIR
        )

        # test data home specified
        data_home = os.path.join(data_home_dir, dataset.DATASET_DIR)
        track_test = dataset.Track(trackid, data_home=data_home)

        assert isinstance(track_test, track.Track)

        assert hasattr(track_test, 'to_jams')

        if module_name not in jams_temporary_exceptions:
            # Validate json schema
            jam = track_test.to_jams()
            assert jam.validate()

        # will fail if something goes wrong with __repr__
        print(track_test)

        with pytest.raises(ValueError):
            dataset.Track('~faketrackid~?!')

        track_custom = dataset.Track(trackid, data_home='casa/de/data')
        assert track_custom._data_home == 'casa/de/data'
