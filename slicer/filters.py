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

    # Municipality cascade-up: infer division if municipality maps to exactly one division
    if eff.get("municipality") and not eff.get("division"):
        rows = df[df["municipality"] == eff["municipality"]]
        if not rows.empty:
            divs = rows["division"].dropna().unique()
            if len(divs) == 1:
                eff.setdefault("division", str(divs[0]))
                eff.setdefault("region", str(rows.iloc[0]["region"]))

    # Cascade-down: narrow options based on active filters
    f = df
    if eff.get("region"):
        f = f[f["region"] == eff["region"]]
    divisions = f["division"].dropna().unique().tolist()

    # Discard stale division if it doesn't belong to the current region
    if eff.get("division") and eff["division"] not in divisions:
        eff.pop("division")
        eff.pop("district", None)
        eff.pop("municipality", None)

    if eff.get("division"):
        f = f[f["division"] == eff["division"]]
    districts = f["district"].dropna().unique().tolist()
    municipalities = f["municipality"].dropna().unique().tolist()

    # Discard stale district
    if eff.get("district") and eff["district"] not in districts:
        eff.pop("district")

    # Discard stale municipality
    if eff.get("municipality") and eff["municipality"] not in municipalities:
        eff.pop("municipality")

    return {
        "divisions": divisions,
        "districts": districts,
        "municipalities": municipalities,
        "effective_region": eff.get("region", ""),
        "effective_division": eff.get("division", ""),
        "effective_district": eff.get("district", ""),
        "effective_municipality": eff.get("municipality", ""),
    }
