"""Unit tests for csv-product-enricher core functions."""
import json

import pandas as pd
import pytest

from enricher import load_csv, parse_response


def test_load_csv(tmp_path):
    """load_csv returns a DataFrame with the required columns."""
    csv_file = tmp_path / "test_input.csv"
    csv_file.write_text("sku,title,description\nSKU-001,Test Product,A test description.\n")
    df = load_csv(str(csv_file))
    assert isinstance(df, pd.DataFrame)
    assert {"sku", "title", "description"}.issubset(df.columns)
    assert len(df) == 1
    assert df.iloc[0]["sku"] == "SKU-001"


def test_parse_response_valid():
    """parse_response returns a dict with all four required fields and correct types."""
    payload = {
        "seo_tags": "running shoes, trail shoes, sport footwear",
        "category": "Sports > Footwear",
        "enhanced_description": "High-performance trail running shoes built for endurance and comfort.",
        "readability_score": 8.2,
    }
    result = parse_response(json.dumps(payload))
    assert result["seo_tags"] == payload["seo_tags"]
    assert result["category"] == payload["category"]
    assert result["enhanced_description"] == payload["enhanced_description"]
    assert result["readability_score"] == 8.2


def test_parse_response_invalid_json():
    """parse_response raises JSONDecodeError on malformed input."""
    with pytest.raises(json.JSONDecodeError):
        parse_response("not valid json {{{")
