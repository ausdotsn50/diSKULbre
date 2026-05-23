import pandas as pd

def compute_aggregates(df: pd.DataFrame) -> dict:
    def counts(col: str) -> dict:
        return df[col].value_counts().to_dict()

    return {
        "total": len(df),
        "by_sector": counts("sector"),
        "by_urban_rural": counts("urban_rural"),
        "by_offering": counts("offering"),
        "by_subclass": counts("subclass"),
    }
