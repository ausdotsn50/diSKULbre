import pandas as pd

def filter_schools(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    slice_df = df.copy()
    search = filters.get("search", None)

    for key, value in filters.items():
        if key == "search" or key not in slice_df.columns: # skip values
            continue
        slice_df = slice_df[slice_df[key] == value]

    if search:
        slice_df = slice_df[
            slice_df["name"].str.contains(search, case=False, na=False)
        ] # additional filter

    return slice_df

def cascade_options(df: pd.DataFrame, filters: dict) -> dict:
    eff = dict(filters)

    # Cascade-up: infer parents from child selections
    if eff.get("district") and (not eff.get("division") or not eff.get("region")):
        rows = df[df["district"] == eff["district"]]
        if not rows.empty:
            eff.setdefault("division", rows.iloc[0]["division"])
            eff.setdefault("region", rows.iloc[0]["region"])
    if eff.get("division") and not eff.get("region"):
        rows = df[df["division"] == eff["division"]]
        if not rows.empty:
            eff.setdefault("region", rows.iloc[0]["region"])

    # Cascade-down: narrow options based on active filters
    f = df
    if eff.get("region"):
        f = f[f["region"] == eff["region"]]
    divisions = f["division"].dropna().unique().tolist()

    if eff.get("division"):
        f = f[f["division"] == eff["division"]]
    districts = f["district"].dropna().unique().tolist()

    return {
        "divisions": divisions,
        "districts": districts,
        "effective_region": eff.get("region", ""),
        "effective_division": eff.get("division", ""),
    }
