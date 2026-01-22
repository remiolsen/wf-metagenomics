"""Test abundance table functions."""

import io
import json

import pandas as pd
import pandas.testing as pdt
import pytest
from workflow_glue.abundance_tables import join_abundance_tables, tax_tree
from workflow_glue.tests_wf.static.test_lineages_cases import (
    TEST_1_DF_ALL_RANKS,
    TEST_1_JSON_ALL_RANKS,
    TEST_2_DF_INCOMPLETE_LIN,
    TEST_2_JSON_INCOMPLETE_LIN,
    TEST_3_DF_MIXED_COMPLETENESS_ORDERS,
    TEST_3_JSON_MIXED_COMPLETENESS_ORDERS,
    TEST_4_DF_TWO_SAMPLES_PARTIAL_OVERLAP,
    TEST_4_JSON_TWO_SAMPLES_PARTIAL_OVERLAP,
    TEST_5_DF_REAL_SAMPLE_CLASS,
    TEST_5_DF_REAL_SAMPLE_GENUS,
    TEST_5_DF_REAL_SAMPLE_SPECIES,
    TEST_5_JSON_REAL_SAMPLE,
    TEST_6_DF_CASE03_CLASS,
    TEST_6_DF_CASE03_GENUS,
    TEST_6_JSON_CASE03
)


def _df_from_tsv_string(tsv):
    return pd.read_csv(io.StringIO(tsv), sep="\t")


def _normalize_for_compare(df):
    """Make row/column ordering deterministic for checks."""
    df = df.copy()

    # Determine sample columns (everything except tax/total)
    sample_cols = sorted([c for c in df.columns if c not in {"tax", "total"}])
    df = df[["tax"] + sample_cols + ["total"]]

    # Row order
    df = df.sort_values("tax").reset_index(drop=True)

    return df


@pytest.mark.parametrize(
    "lineages_json, expected_tsv, requested_rank",
    [
        (TEST_1_JSON_ALL_RANKS, TEST_1_DF_ALL_RANKS, "genus"),
        (TEST_2_JSON_INCOMPLETE_LIN, TEST_2_DF_INCOMPLETE_LIN, "genus"),
        (
            TEST_3_JSON_MIXED_COMPLETENESS_ORDERS,
            TEST_3_DF_MIXED_COMPLETENESS_ORDERS,
            "genus",
        ),
        (
            TEST_4_JSON_TWO_SAMPLES_PARTIAL_OVERLAP,
            TEST_4_DF_TWO_SAMPLES_PARTIAL_OVERLAP,
            "genus",
        ),
        (TEST_5_JSON_REAL_SAMPLE, TEST_5_DF_REAL_SAMPLE_CLASS, "class"),
        (TEST_5_JSON_REAL_SAMPLE, TEST_5_DF_REAL_SAMPLE_GENUS, "genus"),
        (TEST_5_JSON_REAL_SAMPLE, TEST_5_DF_REAL_SAMPLE_SPECIES, "species"),
        (TEST_6_JSON_CASE03, TEST_6_DF_CASE03_CLASS, "class"),
        (TEST_6_JSON_CASE03, TEST_6_DF_CASE03_GENUS, "genus"),
    ],
)
def test_create_abundance_tables(lineages_json, expected_tsv, requested_rank):
    """Compare generated df vs. expected one."""
    lineage_dict = json.loads(lineages_json)
    trees = tax_tree(lineage_dict)

    df = join_abundance_tables(trees, requested_rank)
    expected = _df_from_tsv_string(expected_tsv)

    # Ensure order for comparisons
    df_norm = _normalize_for_compare(df)
    expected_norm = _normalize_for_compare(expected)

    pdt.assert_frame_equal(
        df_norm,
        expected_norm,
        check_dtype=False,  # allow int64 vs float64 differences
        check_like=False,
    )
