"""PromptBIM Streamlit Web UI.

Usage:
    streamlit run src/promptbim/web/app.py

Provides a browser-based interface for the full PromptBIM pipeline:
land import, AI building generation, 3D preview, compliance check, cost estimate.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import streamlit as st

# Ensure src is on path
_src = str(Path(__file__).resolve().parent.parent.parent)
if _src not in sys.path:
    sys.path.insert(0, _src)

st.set_page_config(
    page_title="PromptBIM",
    page_icon="🏗️",
    layout="wide",
)

st.title("🏗️ PromptBIM — AI-Powered BIM Generator")
st.caption("Generate buildings from natural language on real land parcels")

# --------------------------------------------------------------------------
# Sidebar: Land Input
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("📍 Land Parcel")

    land_method = st.radio("Input method", ["Manual Coordinates", "GeoJSON Upload", "AI Image"])

    land_parcel = None

    if land_method == "Manual Coordinates":
        st.markdown("Enter boundary coordinates (one per line, `x,y` format):")
        coords_text = st.text_area(
            "Coordinates",
            value="0,0\n20,0\n20,15\n0,15",
            height=120,
        )
        land_name = st.text_input("Parcel Name", value="My Land")

        if st.button("Import Land"):
            try:
                coords = []
                for line in coords_text.strip().split("\n"):
                    parts = line.strip().split(",")
                    coords.append((float(parts[0]), float(parts[1])))

                from promptbim.schemas.land import LandParcel

                area = _compute_area(coords)
                land_parcel = LandParcel(
                    name=land_name,
                    boundary=coords,
                    area_sqm=area,
                    source_type="manual",
                )
                st.session_state["land"] = land_parcel
                st.success(f"Imported: {land_name} ({area:.1f} m²)")
            except Exception as e:
                st.error(f"Error: {e}")

    elif land_method == "GeoJSON Upload":
        uploaded = st.file_uploader("Upload GeoJSON", type=["geojson", "json"])
        if uploaded:
            try:
                with tempfile.NamedTemporaryFile(suffix=".geojson", delete=False) as tmp:
                    tmp.write(uploaded.read())
                    tmp_path = tmp.name

                from promptbim.land.parsers.geojson import parse_geojson

                parcels = parse_geojson(tmp_path)
                if parcels:
                    st.session_state["land"] = parcels[0]
                    st.success(f"Imported: {parcels[0].name} ({parcels[0].area_sqm:.1f} m²)")
                else:
                    st.warning("No valid parcels found")
            except Exception as e:
                st.error(f"Error: {e}")

    elif land_method == "AI Image":
        uploaded_img = st.file_uploader("Upload land image", type=["jpg", "jpeg", "png"])
        if uploaded_img:
            st.image(uploaded_img, caption="Uploaded Image", use_container_width=True)
            st.info("AI image recognition requires ANTHROPIC_API_KEY to be set.")

    # Zoning
    st.divider()
    st.header("📏 Zoning Rules")
    zone_type = st.selectbox("Zone Type", ["residential", "commercial", "industrial"])
    far_limit = st.number_input("FAR Limit", value=2.0, step=0.1)
    bcr_limit = st.number_input("BCR Limit", value=0.6, step=0.05)
    height_limit = st.number_input("Height Limit (m)", value=15.0, step=1.0)

    from promptbim.schemas.zoning import ZoningRules

    zoning = ZoningRules(
        zone_type=zone_type,
        far_limit=far_limit,
        bcr_limit=bcr_limit,
        height_limit_m=height_limit,
    )
    st.session_state["zoning"] = zoning


# --------------------------------------------------------------------------
# Main area: Chat + Results
# --------------------------------------------------------------------------
col_chat, col_result = st.columns([1, 1])

with col_chat:
    st.header("💬 Building Prompt")

    prompt = st.text_area(
        "Describe the building you want to generate:",
        placeholder="e.g., 3-story residential house with ground floor parking and rooftop garden",
        height=120,
    )

    if st.button("🚀 Generate Building", type="primary", use_container_width=True):
        land = st.session_state.get("land")
        if land is None:
            st.error("Please import a land parcel first (sidebar).")
        elif not prompt.strip():
            st.warning("Please enter a building description.")
        else:
            with st.spinner("AI is generating your building..."):
                try:
                    from promptbim.agents.orchestrator import Orchestrator

                    output_dir = tempfile.mkdtemp(prefix="promptbim_web_")
                    orch = Orchestrator(output_dir=output_dir)
                    result = orch.generate(prompt, land, zoning)

                    st.session_state["result"] = result
                    st.session_state["plan"] = orch.plan
                    st.session_state["output_dir"] = output_dir

                    if result.success:
                        st.success(f"Generated: {result.building_name}")
                    else:
                        st.error(f"Generation failed: {'; '.join(result.errors)}")
                except Exception as e:
                    st.error(f"Error: {e}")

with col_result:
    st.header("📊 Results")

    result = st.session_state.get("result")
    plan = st.session_state.get("plan")

    if result and plan:
        # Summary metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Stories", result.summary.get("stories", 0))
        m2.metric("BCR", f"{result.summary.get('bcr', 0):.0%}")
        m3.metric("FAR", f"{result.summary.get('far', 0):.2f}")
        m4.metric("Footprint", f"{result.summary.get('footprint_area', 0):.0f} m²")

        # Tabs
        tab_plan, tab_compliance, tab_cost, tab_files = st.tabs(
            ["Plan", "Compliance", "Cost", "Files"]
        )

        with tab_plan:
            st.json(plan.model_dump() if hasattr(plan, "model_dump") else {})

        with tab_compliance:
            if result.compliance_text:
                st.text(result.compliance_text[:3000])
            else:
                st.info("Run compliance check for details.")

        with tab_cost:
            try:
                from promptbim.bim.cost.estimator import CostEstimator

                estimator = CostEstimator()
                estimate = estimator.estimate(plan)
                cost_data = estimate.to_dict()
                st.metric("Total Cost (TWD)", f"NT$ {cost_data.get('total_twd', 0):,.0f}")
                st.metric("Cost / m²", f"NT$ {cost_data.get('cost_per_sqm_twd', 0):,.0f}")
                if cost_data.get("category_breakdown"):
                    st.bar_chart(cost_data["category_breakdown"])
            except Exception as e:
                st.warning(f"Cost estimation unavailable: {e}")

        with tab_files:
            if result.ifc_path and Path(result.ifc_path).exists():
                st.download_button(
                    "📥 Download IFC",
                    data=Path(result.ifc_path).read_bytes(),
                    file_name=Path(result.ifc_path).name,
                )
            if result.usd_path and Path(result.usd_path).exists():
                st.download_button(
                    "📥 Download USD",
                    data=Path(result.usd_path).read_bytes(),
                    file_name=Path(result.usd_path).name,
                )

        if result.warnings:
            with st.expander("Warnings"):
                for w in result.warnings:
                    st.warning(w)
    else:
        st.info("Generate a building to see results here.")


def _compute_area(coords):
    n = len(coords)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += coords[i][0] * coords[j][1]
        area -= coords[j][0] * coords[i][1]
    return abs(area) / 2.0
