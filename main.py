import math
from urllib.parse import urlencode

import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from data.load import load_schools
from slicer.filters import *
from slicer.aggregates import compute_aggregates

app = FastAPI(title="BEIS Project")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

PER_PAGE = 50
DF = load_schools('data/beis_masterlist.csv')

# Unique values
OPTIONS = {
    "regions": DF["region"].dropna().unique().tolist(),
    "sectors": DF["sector"].dropna().unique().tolist(),
    "urban_rural": DF["urban_rural"].dropna().unique().tolist(),
    "offerings": DF["offering"].dropna().unique().tolist(),
    "subclasses": DF["subclass"].dropna().unique().tolist(),
}


def main():
    """Entry point. Starts the Uvicorn development server."""
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


# Routes
@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> Response:
    return templates.TemplateResponse(request, "base.html")


@app.get("/explore")
async def explore(
    request: Request,
    search: str = Query(default=""),
    region: str = Query(default=""),
    division: str = Query(default=""),
    district: str = Query(default=""),
    municipality: str = Query(default=""),
    sector: str = Query(default=""),
    urban_rural: str = Query(default=""),
    offering: str = Query(default=""),
    subclass: str = Query(default=""),
    page: int = Query(default=1, ge=1),
) -> Response:
    filters = {
        k: v for k, v in {
            "search": search,
            "region": region,
            "division": division,
            "district": district,
            "municipality": municipality,
            "sector": sector,
            "urban_rural": urban_rural,
            "offering": offering,
            "subclass": subclass,
        }.items() if v
    }

    cascade_opts = cascade_options(DF, filters)

    # Sync geographic filters with effective values: handles cascade-up (inferred parents)
    # and stale values (e.g. division=Leyte sent after switching region to Region I).
    for key, eff_key in [
        ("region", "effective_region"),
        ("division", "effective_division"),
        ("district", "effective_district"),
        ("municipality", "effective_municipality"),
    ]:
        effective = cascade_opts[eff_key]
        if effective:
            filters[key] = effective
        else:
            filters.pop(key, None)

    slice_df = filter_schools(DF, filters)
    aggregates = compute_aggregates(slice_df)

    total_results = len(slice_df)
    total_pages = max(1, math.ceil(total_results / PER_PAGE))
    page = min(page, total_pages)
    start = (page - 1) * PER_PAGE
    schools = slice_df.iloc[start : start + PER_PAGE].to_dict(orient="records")

    context = {
        "schools": schools,
        "filters": filters,
        "aggregates": aggregates,
        "options": {**OPTIONS, **cascade_opts},
        "pagination": {
            "page": page,
            "total_pages": total_pages,
            "total_results": total_results,
            "per_page": PER_PAGE,
            "base_url": f"/explore?{urlencode(filters)}" if filters else "/explore",
        },
    }

    if request.headers.get("HX-Request"):
        qs = urlencode(filters)
        if page > 1:
            qs += f"&page={page}"
        clean_url = f"/explore?{qs}" if qs else "/explore"

        # Cascade-up: district (or division) inferred parent values — redirect so
        # the full page re-renders with all dropdowns correctly populated.
        cascade_up = (
            (cascade_opts["effective_region"] and not region) or
            (cascade_opts["effective_division"] and not division) or
            (cascade_opts["effective_municipality"] and not municipality)
        )
        if cascade_up:
            return Response(content="", headers={"HX-Redirect": clean_url})

        response = templates.TemplateResponse(request, "partials/results_htmx.html", context)
        response.headers["HX-Push-Url"] = clean_url
        return response

    qs = urlencode(filters)
    if page > 1:
        qs += f"&page={page}"
    dirty_qs = str(request.query_params)
    if dirty_qs != qs:
        return RedirectResponse(f"/explore?{qs}" if qs else "/explore")
    return templates.TemplateResponse(request, "explore.html", context)


# Check accuracy of school route
@app.get("/school/{school_id}", response_class=HTMLResponse)
async def school_detail(request: Request, school_id: str) -> Response:
    row = DF[DF["school_id"] == school_id]
    if row.empty:
        return templates.TemplateResponse(request, "status/404.html", status_code=404)

    school = row.iloc[0].to_dict()

    # Modify for context stats in school
    context_stats = {
        "in_municipality": int((DF["municipality"] == school["municipality"]).sum()),
        "in_district": int((DF["district"] == school["district"]).sum()),
        "public_in_municipality": int(
            ((DF["municipality"] == school["municipality"]) & (DF["sector"] == "Public")).sum()
        ),
        "in_division": int((DF["division"] == school["division"]).sum()),
        "same_offering_in_division": int(
            ((DF["division"] == school["division"]) & (DF["offering"] == school["offering"])).sum()
        ),
        "in_region": int(
            (DF["region"] == school["region"]).sum()
        ),
    }

    return templates.TemplateResponse(request, "school.html", {
        "school": school,
        "context_stats": context_stats,
        "aggregates": None,
    })

if __name__ == '__main__':
    main()
