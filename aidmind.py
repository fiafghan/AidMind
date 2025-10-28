import os
import io
import json
import re
import argparse
import logging
import difflib
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pycountry
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans
import folium
from branca.colormap import linear
from branca.element import MacroElement, Template


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("AidMind")


def _requests_session() -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s


def _strip_suffix_unit(name: str) -> str:
    # Collapse entries like 'Kabul_1' or 'Kabul-2' to 'Kabul'
    if not isinstance(name, str):
        name = str(name)
    name = re.sub(r"[_-]\d+$", "", name.strip())
    name = re.sub(r"\s+", " ", name)
    return name


def _detect_admin_column(df: pd.DataFrame) -> Optional[str]:
    candidates = [
        "province",
        "admin1",
        "admin_1",
        "region",
        "state",
        "adm1_name",
        "name",
    ]
    lower_cols = {c.lower(): c for c in df.columns}
    for key in candidates:
        if key in lower_cols:
            return lower_cols[key]
    # Fallback: choose the first non-numeric column
    for c in df.columns:
        if not pd.api.types.is_numeric_dtype(df[c]):
            return c
    return None


def _normalize_name(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


def _country_to_iso3(country_name: str) -> str:
    try:
        country = pycountry.countries.search_fuzzy(country_name)[0]
        return country.alpha_3
    except Exception:
        raise ValueError(f"Could not resolve country name to ISO3: {country_name}")


def _fetch_admin1_geojson(iso3: str, admin_level: str = "ADM1", local_path: Optional[str] = None) -> dict:
    if local_path and os.path.exists(local_path):
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info("Loaded boundaries from local file: %s", local_path)
            return data
        except Exception as e:
            logger.warning("Failed to read local GeoJSON at %s: %s; falling back to remote.", local_path, e)
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", "geoboundaries")
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"{iso3}_ADM1.geojson")

    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info("Loaded boundaries from cache: %s", cache_path)
            return data
        except Exception:
            logger.warning("Failed to read cached GeoJSON, will refetch: %s", cache_path)

    session = _requests_session()
    api_url = f"https://www.geoboundaries.org/api/current/gbOpen/{iso3}/{admin_level}"
    logger.info("Fetching boundaries metadata: %s", api_url)
    r = session.get(api_url, timeout=30)
    r.raise_for_status()
    meta = r.json()
    if isinstance(meta, list) and meta:
        meta = meta[0]
    gj_url = meta.get("gjDownloadURL") or meta.get("gjDownloadURLzipped")
    if not gj_url:
        raise RuntimeError("GeoBoundaries API did not return a GeoJSON URL.")
    logger.info("Downloading GeoJSON: %s", gj_url)
    gj = session.get(gj_url, timeout=60)
    gj.raise_for_status()
    data = gj.json()
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        logger.info("Cached boundaries to: %s", cache_path)
    except Exception:
        logger.warning("Could not cache GeoJSON to: %s", cache_path)
    return data


def _prepare_features(df: pd.DataFrame, id_col: str) -> Tuple[pd.DataFrame, np.ndarray, pd.DataFrame]:
    # Keep only numeric columns for ML features (coerce to numeric to detect)
    candidate_cols = [c for c in df.columns if c != id_col]
    numeric_mask = {}
    for c in candidate_cols:
        try:
            pd.to_numeric(df[c], errors="raise")
            numeric_mask[c] = True
        except Exception:
            numeric_mask[c] = False
    feature_cols = [c for c in candidate_cols if numeric_mask.get(c, False)]
    if not feature_cols:
        raise ValueError("No numeric feature columns found in the dataset.")

    # Coerce and clean
    df_num = df[feature_cols].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)

    # Drop columns that are entirely NaN
    all_nan_cols = [c for c in df_num.columns if df_num[c].isna().all()]
    if all_nan_cols:
        logger.warning("Dropping entirely-missing columns: %s", ", ".join(all_nan_cols))
        df_num = df_num.drop(columns=all_nan_cols)
        feature_cols = [c for c in feature_cols if c not in all_nan_cols]
        if not feature_cols:
            raise ValueError("All numeric feature columns are empty (NaN).")

    # Impute missing values with median
    nan_before = int(df_num.isna().sum().sum())
    imputer = SimpleImputer(strategy="median")
    X_imp = imputer.fit_transform(df_num)
    nan_after = int(np.isnan(X_imp).sum())
    if nan_before > 0:
        logger.info("Imputed %d missing values in features (median).", nan_before)
    if nan_after > 0:
        # This should not happen unless columns were all-NaN; guard anyway
        raise ValueError("Missing values remain after imputation; please check your dataset.")

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X_imp)
    features_scaled = pd.DataFrame(Xs, columns=feature_cols, index=df.index)
    return df[[id_col]], Xs, features_scaled


def _compute_need_scores(features_scaled: pd.DataFrame) -> np.ndarray:
    # Unsupervised proxy: average of standardized indicators. Higher => more needy
    scores = features_scaled.mean(axis=1).values
    # Normalize 0..1
    if scores.max() > scores.min():
        scores = (scores - scores.min()) / (scores.max() - scores.min())
    else:
        scores = np.zeros_like(scores)
    return scores


def _cluster_and_rank(Xs: np.ndarray, need_scores: np.ndarray, max_clusters: int = 5) -> Tuple[np.ndarray, dict]:
    n = Xs.shape[0]
    if n < 3:
        labels = np.zeros(n, dtype=int)
        return labels, {0: 0}
    k = min(max_clusters, max(3, min(5, n)))
    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = km.fit_predict(Xs)
    cluster_means = {c: float(need_scores[labels == c].mean()) for c in range(k)}
    ranked = sorted(cluster_means.items(), key=lambda x: x[1], reverse=True)
    rank_map = {cluster_id: rank for rank, (cluster_id, _) in enumerate(ranked)}
    return labels, rank_map


def _merge_with_geojson(df: pd.DataFrame, id_col: str, geojson: dict) -> Tuple[pd.DataFrame, dict, str, str]:
    # Determine geo name property commonly found in geoBoundaries: 'shapeName'
    # Build a mapping from normalized name -> feature id
    features = geojson.get("features", [])
    prop_name_candidates = ["shapeName", "name", "NAME_1", "adm1_name"]
    gj_name_key = None
    if features:
        for key in prop_name_candidates:
            if key in features[0].get("properties", {}):
                gj_name_key = key
                break
    if not gj_name_key:
        raise RuntimeError("Could not find an admin-1 name property in GeoJSON.")

    # Normalize names in both datasets
    df = df.copy()
    if "__norm_name" not in df.columns:
        df["__norm_name"] = df[id_col].astype(str).map(_normalize_name)

    for f in features:
        props = f.get("properties", {})
        props["__norm_name"] = _normalize_name(props.get(gj_name_key, ""))
        f["properties"] = props

    # Try direct merge on normalized name
    gj_records = [f["properties"] for f in features]
    gj_df = pd.DataFrame(gj_records)
    merged = pd.merge(df, gj_df, on="__norm_name", how="left", suffixes=("", "_geo"))

    # Determine the best unique identifier in GeoJSON properties to bind data to features
    # Prefer 'shapeID' if present; else fall back to index
    bind_key = "shapeID" if "shapeID" in gj_df.columns else "__norm_name"

    # Build a lookup from feature bind_key -> feature index for folium
    for i, f in enumerate(features):
        f["properties"]["__feature_index"] = i

    return merged, geojson, bind_key, gj_name_key


def analyze_needs(
    dataset_path: str,
    country_name: str,
    output_html_path: Optional[str] = None,
    *,
    admin_level: str = "ADM1",
    admin_col: Optional[str] = None,
    local_geojson: Optional[str] = None,
    fixed_thresholds: Optional[Tuple[float, float, float]] = None,
) -> str:
    """
    Analyze humanitarian need using unsupervised learning and render a province-level map.

    Parameters
    ----------
    dataset_path : str
        Path to a CSV containing province-level indicators. Must include a province/admin1 name column.
    country_name : str
        Country name (e.g., "Afghanistan").
    output_html_path : Optional[str]
        Where to save the generated HTML. Defaults to AidMind/output/needs_map_<ISO3>.html

    Returns
    -------
    str
        The path to the generated HTML file.
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    df = pd.read_csv(dataset_path)
    if df.empty:
        raise ValueError("Dataset is empty.")

    id_col = admin_col or _detect_admin_column(df)
    if not id_col:
        raise ValueError("Could not detect an admin-1 name column. Add a column like 'province' or 'admin1'.")

    logger.info("Detected admin column: %s", id_col)
    # Aggregate multiple rows per admin by stripping trailing numeric suffixes
    try:
        before_n = int(df[id_col].nunique())
        df[id_col] = df[id_col].astype(str).map(_strip_suffix_unit)
        # Average numeric indicators per admin
        numeric_cols = [c for c in df.columns if c != id_col and pd.api.types.is_numeric_dtype(df[c])]
        if numeric_cols:
            df = (
                df[[id_col] + numeric_cols]
                .groupby(id_col, as_index=False)
                .mean(numeric_only=True)
            )
        after_n = int(df[id_col].nunique())
        if after_n < before_n:
            logger.info("Aggregated multiple rows per admin: %d -> %d unique", before_n, after_n)
    except Exception as e:
        logger.warning("Aggregation step failed; proceeding without aggregation: %s", e)

    id_df, Xs, features_scaled = _prepare_features(df, id_col)
    need_scores = _compute_need_scores(features_scaled)
    labels, rank_map = _cluster_and_rank(Xs, need_scores)

    # Attach results
    result_df = id_df.copy()
    result_df["need_score"] = need_scores
    result_df["cluster"] = labels
    result_df["need_rank"] = result_df["cluster"].map(rank_map)

    # Fetch boundaries
    iso3 = _country_to_iso3(country_name)
    geojson = _fetch_admin1_geojson(iso3, admin_level=admin_level, local_path=local_geojson)

    # Fuzzy name harmonization before merge when needed
    try:
        features = geojson.get("features", [])
        # find a name key in geojson
        name_key = None
        for key in ["shapeName", "name", "NAME_1", "adm1_name"]:
            if features and key in features[0].get("properties", {}):
                name_key = key
                break
        if name_key:
            geo_names = [
                _normalize_name(f.get("properties", {}).get(name_key, ""))
                for f in features
            ]
            # build normalization column to map
            df_res = result_df.copy()
            df_res["__norm_name"] = df_res[id_col].astype(str).map(_normalize_name)
            mapped = []
            for nm in df_res["__norm_name"].tolist():
                if nm in geo_names:
                    mapped.append(nm)
                else:
                    # closest match
                    match = difflib.get_close_matches(nm, geo_names, n=1, cutoff=0.84)
                    mapped.append(match[0] if match else nm)
            # only set mapping if it improves coverage
            before_cov = sum(n in geo_names for n in df_res["__norm_name"]) / max(len(df_res), 1)
            after_cov = sum(n in geo_names for n in mapped) / max(len(mapped), 1)
            if after_cov > before_cov:
                result_df = result_df.copy()
                result_df["__norm_name"] = mapped
                logger.info("Applied fuzzy name harmonization: coverage %.1f%% -> %.1f%%", before_cov*100, after_cov*100)
    except Exception as e:
        logger.warning("Fuzzy harmonization skipped: %s", e)

    # Merge with geojson properties by normalized names
    merged, geojson, bind_key, gj_name_key = _merge_with_geojson(result_df, id_col, geojson)
    # Report match rate
    try:
        if gj_name_key in merged.columns:
            match_rate = float(merged[gj_name_key].notna().mean() * 100.0)
            if match_rate < 80:
                logger.warning("Low admin name match rate: %.1f%%. Consider harmonizing names.", match_rate)
            else:
                logger.info("Admin name match rate: %.1f%%", match_rate)
    except Exception:
        pass

    # Prepare map
    # Center map roughly at country centroid (avg of feature centroids)
    try:
        # Compute centroid average from GeoJSON
        # Fallback to (0,0) if fails
        import shapely.geometry as geom  # optional; may not be installed
        import shapely.ops as ops
        from functools import reduce
        coords = []
        for f in geojson.get("features", []):
            geom_obj = f.get("geometry")
            if not geom_obj:
                continue
            g = geom.shape(geom_obj)
            c = g.representative_point().coords[0]
            coords.append(c)
        if coords:
            avg_lat = float(np.mean([c[1] for c in coords]))
            avg_lon = float(np.mean([c[0] for c in coords]))
            map_center = (avg_lat, avg_lon)
        else:
            map_center = (0.0, 0.0)
    except Exception:
        map_center = (0.0, 0.0)

    m = folium.Map(location=map_center, zoom_start=5, tiles="cartodbpositron")

    # Color scale: red (high need) -> green (low need)
    colormap = linear.RdYlGn_11.scale(1.0, 0.0)  # reverse to make 1 red, 0 green
    colormap.caption = "Need (red = highest)"

    # Build value mapping keyed by bind key
    value_by_key = {}
    rank_by_key = {}
    for _, row in merged.iterrows():
        key = row.get(bind_key)
        if pd.isna(key):
            key = row.get("__norm_name")
        value_by_key[str(key)] = float(row["need_score"]) if not pd.isna(row["need_score"]) else 0.0
        rank_by_key[str(key)] = int(row["need_rank"]) if not pd.isna(row["need_rank"]) else 0

    # Discrete color scheme by quartiles
    values = np.array([v for v in value_by_key.values() if v is not None])
    if fixed_thresholds is not None:
        q25, q50, q75 = fixed_thresholds
    elif values.size:
        q25, q50, q75 = np.quantile(values, [0.25, 0.5, 0.75])
    else:
        q25 = q50 = q75 = 0.0

    def level_for(val: Optional[float]) -> Tuple[str, str]:
        # returns (level_name, hex_color)
        if val is None:
            return ("unknown", "#cccccc")
        if val >= q75:
            return ("high", "#b91c1c")  # highest need
        elif val >= q50:
            return ("medium", "#f87171")  # middle need
        elif val >= q25:
            return ("low", "#86efac")  # low need
        else:
            return ("lowest", "#16a34a")  # lowest need

    # Attach values into GeoJSON properties for tooltips (always set keys to avoid assertion)
    for f in geojson.get("features", []):
        props = f.get("properties", {})
        key = str(props.get(bind_key) or props.get("__norm_name"))
        val = value_by_key.get(key)
        rnk = rank_by_key.get(key)
        props["__need_score"] = round(float(val), 3) if val is not None else "N/A"
        props["__need_rank"] = int(rnk) if rnk is not None else "N/A"
        lvl, hex_color = level_for(val)
        props["__need_level"] = lvl
        props["__need_color"] = hex_color
        f["properties"] = props

    def style_function(feature):
        props = feature.get("properties", {})
        key = str(props.get(bind_key) or props.get("__norm_name"))
        val = value_by_key.get(key)
        _, color = level_for(val)
        return {
            "fillOpacity": 0.8,
            "weight": 0.5,
            "color": "#666666",
            "fillColor": color,
        }

    folium.GeoJson(
        geojson,
        name="Needs",
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=[gj_name_key, "__need_score", "__need_rank", "__need_level"],
            aliases=["Province", "Need Score (0-1)", "Need Rank (0=highest)", "Level"],
            sticky=True,
        ),
        highlight_function=lambda x: {"weight": 2, "color": "#000000"},
    ).add_to(m)

    # Use a custom legend for discrete levels
    try:
        legend_html = """
        {% macro html(this, kwargs) %}
        <div style='position: fixed; bottom: 20px; left: 20px; z-index:9999; background: white; padding: 10px; border: 1px solid #ccc; box-shadow: 0 1px 3px rgba(0,0,0,0.2); font-size: 12px;'>
          <div style='font-weight:600; margin-bottom:6px;'>Need Levels</div>
          <div><span style='display:inline-block; width:14px; height:14px; background:#b91c1c; margin-right:6px; border:1px solid #999;'></span> high</div>
          <div><span style='display:inline-block; width:14px; height:14px; background:#f87171; margin-right:6px; border:1px solid #999;'></span> medium</div>
          <div><span style='display:inline-block; width:14px; height:14px; background:#86efac; margin-right:6px; border:1px solid #999;'></span> low</div>
          <div><span style='display:inline-block; width:14px; height:14px; background:#16a34a; margin-right:6px; border:1px solid #999;'></span> lowest</div>
        </div>
        {% endmacro %}
        """
        legend = MacroElement()
        legend._template = Template(legend_html)
        m.get_root().add_child(legend)
    except Exception:
        pass

    if output_html_path is None:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(out_dir, exist_ok=True)
        output_html_path = os.path.join(out_dir, f"needs_map_{iso3}.html")

    m.save(output_html_path)
    try:
        csv_out = os.path.join(os.path.dirname(output_html_path), f"needs_scores_{iso3}.csv")
        # compute level for each merged row using its score
        levels = []
        for _, row in merged.iterrows():
            val = float(row["need_score"]) if not pd.isna(row["need_score"]) else None
            lvl, _ = level_for(val)
            levels.append(lvl)
        export_df = merged[["__norm_name", "need_score", "need_rank", "cluster"]].rename(columns={"__norm_name": "admin1"})
        export_df["need_level"] = levels
        export_df.to_csv(csv_out, index=False)
        logger.info("Exported scores to: %s", csv_out)
    except Exception as e:
        logger.warning("Could not export CSV: %s", e)
    return output_html_path


def main():
    parser = argparse.ArgumentParser(description="Analyze humanitarian needs and render a province map.")
    parser.add_argument("dataset_path", help="Path to CSV with province-level indicators")
    parser.add_argument("country_name", help="Country name, e.g., 'Afghanistan'")
    parser.add_argument("--output", dest="output", default=None, help="Output HTML path")
    args = parser.parse_args()

    out = analyze_needs(args.dataset_path, args.country_name, args.output)
    print(out)


if __name__ == "__main__":
    main()
