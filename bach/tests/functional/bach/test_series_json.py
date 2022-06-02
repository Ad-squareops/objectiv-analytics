"""
Copyright 2021 Objectiv B.V.
"""
from sql_models.util import is_postgres, is_bigquery
from tests.functional.bach.test_data_and_utils import get_df_with_json_data, assert_equals_data
import pytest

# We want to run all tests here for all supported databases, and thus we have the 'engine' argument on all
# tests. Or at least soon we'll have that, for now we use 'pg_engine'.
# Additionally, on Postgres we have two json dtypes: 'json' and 'jsonb' that should support the same
# operations. Therefore, we also have the 'dtype' argument. On all other databases than postgres we skip
# the tests for dtype 'jsonb' as those databases only support 'json'


pytestmark = [pytest.mark.parametrize('dtype', ('json', 'json_postgres'))]


@pytest.fixture(autouse=True, scope='function')
def skip_jsonb_if_not_postgres(request):
    try:
        # TODO: remove this try-except when we support json on BigQuery and stop using 'pg_engine' here
        engine = request.getfixturevalue('engine')
    except pytest.FixtureLookupError:
        engine = request.getfixturevalue('pg_engine')
    if request.getfixturevalue('dtype') == 'json_postgres' and not is_postgres(engine):
        pytest.skip(msg='json_postgres dtype is only supported on Postgres. Skipping for other databases')


def test_json_get_value(engine, dtype):
    bt = get_df_with_json_data(engine=engine, dtype=dtype)
    bts = bt.mixed_column.json.get_value('a')
    assert_equals_data(
        bts,
        use_to_pandas=True,
        expected_columns=['_index_row', 'mixed_column'],
        expected_data=[
            [0, "b"],
            [1, None],
            [2, "b"],
            [3, None]
        ]
    )


def test_json_get_single_value(engine, dtype):
    bt = get_df_with_json_data(engine=engine, dtype=dtype)
    a = bt.mixed_column[2]
    assert a == {'a': 'b', 'c': {'a': 'c'}}



@pytest.mark.skip_bigquery
def test_json_compare(engine, dtype):
    # These less-than-or-equals compares check that the left hand is contained in the right hand, on
    # Postgres. On BigQuery we cannot support this, so we skip this function for BQ on purpose.
    # TODO: maybe get rid of the Postgres support too?
    bt = get_df_with_json_data(engine=engine, dtype=dtype)
    bts = {"a": "b"} <= bt.mixed_column
    assert_equals_data(
        bts,
        expected_columns=['_index_row', 'mixed_column'],
        expected_data=[
            [0, True],
            [1, False],
            [2, True],
            [3, False]
        ]
    )
    bts = ["a"] <= bt.mixed_column
    assert_equals_data(
        bts,
        expected_columns=['_index_row', 'mixed_column'],
        expected_data=[
            [0, False],
            [1, True],
            [2, False],
            [3, False]
        ]
    )


def test_json_getitem(engine, dtype):
    # TODO: make this a one-query test
    bt = get_df_with_json_data(engine=engine, dtype=dtype)
    bts = bt.mixed_column.json[0]
    assert_equals_data(
        bts,
        use_to_pandas=True,
        expected_columns=['_index_row', 'mixed_column'],
        expected_data=[
            [0, None],
            [1, "a"],
            [2, None],
            [3, {"_type": "WebDocumentContext", "id": "#document"}]
        ]
    )
    bts = bt.mixed_column.json[-2]
    assert_equals_data(
        bts,
        use_to_pandas=True,
        expected_columns=['_index_row', 'mixed_column'],
        expected_data=[
            [0, None],
            [1, "c"],
            [2, None],
            [3, {"_type": "SectionContext", "id": "top-10"}]
        ]
    )
    bts = bt.mixed_column.json["a"]
    assert_equals_data(
        bts,
        use_to_pandas=True,
        expected_columns=['_index_row', 'mixed_column'],
        expected_data=[
            [0, "b"],
            [1, None],
            [2, "b"],
            [3, None]
        ]
    )


def test_json_getitem_special_chars(engine, dtype):
    # We support 'special' characters, except for double quotes because of limitations in BigQuery
    # see comments in bach.series.series_json.JsonBigQueryAccessor.get_value for more information
    df = get_df_with_json_data(engine=engine, dtype=dtype)
    df = df[['row']][:1].materialize()
    data = {
        'test.test': 'a',
        'test': {'test': 'b'},
        '123test': 'c',
        '[{}@!{R#(!@(!': 'd',
    }
    df['data'] = data
    df['select_a'] = df['data'].json['test.test']
    df['select_b'] = df['data'].json['test'].json['test']
    df['select_c'] = df['data'].json['123test']
    df['select_d'] = df['data'].json['[{}@!{R#(!@(!']
    print(f'\n\n\n{df.view_sql()}\n\n\n')
    assert_equals_data(
        df,
        use_to_pandas=True,
        expected_columns=['_index_row', 'row', 'data', 'select_a', 'select_b', 'select_c', 'select_d'],
        expected_data=[[0, 0, data, 'a', 'b', 'c', 'd']]
    )


def test_json_getitem_slice(engine, dtype):
    # TODO: make this a one-query test

    bt = get_df_with_json_data(engine=engine, dtype=dtype)
    bts = bt.list_column.json[1:]
    assert_equals_data(
        bts,
        use_to_pandas=True,
        expected_columns=['_index_row', 'list_column'],
        expected_data=[
            [0, [{"c": "d"}]],
            [1, ["b", "c", "d"]],
            [2, [{"_type": "c", "id": "d"}, {"_type": "e", "id": "f"}]],
            [3, [{"_type": "SectionContext", "id": "home"}, {"_type": "SectionContext", "id": "top-10"},
                 {"_type": "ItemContext", "id": "5o7Wv5Q5ZE"}]]
        ]
    )
    bts = bt.list_column.json[1:-1]
    assert_equals_data(
        bts,
        use_to_pandas=True,
        expected_columns=['_index_row', 'list_column'],
        expected_data=[
            [0, []],
            [1, ["b", "c"]],
            [2, [{"_type": "c", "id": "d"}]],
            [3, [{"_type": "SectionContext", "id": "home"}, {"_type": "SectionContext", "id": "top-10"}]]
        ]
    )
    bts = bt.list_column.json[:]
    assert_equals_data(
        bts,
        use_to_pandas=True,
        expected_columns=['_index_row', 'list_column'],
        expected_data=[
            [0, [{'a': 'b'}, {'c': 'd'}]],
            [1, ['a', 'b', 'c', 'd']],
            [2, [{'id': 'b', '_type': 'a'}, {'id': 'd', '_type': 'c'}, {'id': 'f', '_type': 'e'}]],
            [3, [
                {'id': '#document', '_type': 'WebDocumentContext'},
                {'id': 'home', '_type': 'SectionContext'},
                {'id': 'top-10', '_type': 'SectionContext'}, {'id': '5o7Wv5Q5ZE', '_type': 'ItemContext'}]
             ]
        ]
    )

    bts = bt.mixed_column.json[1:-1]
    # slices only work on columns with only lists
    # But behaviour of Postgres and BigQuery is different. For now we just accept that's the way it is.
    if is_postgres(engine):
        with pytest.raises(Exception):
           bts.head()
    if is_bigquery(engine):
        assert_equals_data(
            bts,
            use_to_pandas=True,
            expected_columns=['_index_row', 'mixed_column'],
            expected_data=[
                [0, []],
                [1, ["b", "c"]],
                [2, []],
                [3, [{"_type": "SectionContext", "id": "home"}, {"_type": "SectionContext", "id": "top-10"}]]
            ]
        )


# tests below are for functions kind of specific to the objectiv (location) stack
def test_json_getitem_query(pg_engine, dtype):
    # TODO: BigQuery
    bt = get_df_with_json_data(engine=pg_engine, dtype=dtype)
    # if dict is contained in any of the dicts in the json list, the first index of the first match is
    # returned to the slice.
    bts = bt.list_column.json[{"_type": "SectionContext"}: ]
    assert_equals_data(
        bts,
        expected_columns=['_index_row', 'list_column'],
        expected_data=[
            [0, []],
            [1, []],
            [2, []],
            [3, [{"_type": "SectionContext", "id": "home"}, {"_type": "SectionContext", "id": "top-10"},
                 {"_type": "ItemContext", "id": "5o7Wv5Q5ZE"}]]
        ]
    )
    bts = bt.list_column.json[1:{"id": "d"}]
    assert_equals_data(
        bts,
        expected_columns=['_index_row', 'list_column'],
        expected_data=[
            [0, []],
            [1, []],
            [2, [{"_type": "c", "id": "d"}]],
            [3, []]
        ]
    )
    bts = bt.list_column.json[{'_type': 'a'}: {'id': 'd'}]
    assert_equals_data(
        bts,
        expected_columns=['_index_row', 'list_column'],
        expected_data=[
            [0, []],
            [1, []],
            [2, [{"_type": "a", "id": "b"}, {"_type": "c", "id": "d"}]],
            [3, []]
        ]
    )

    # TODO needs to_pandas() test


def test_json_get_array_length(engine, dtype):
    df = get_df_with_json_data(engine=engine, dtype=dtype)
    s = df.list_column.json.get_array_length()
    assert_equals_data(
        s,
        expected_columns=['_index_row', 'list_column'],
        expected_data=[
            [0, 2],
            [1, 4],
            [2, 3],
            [3, 4]
        ]
    )
