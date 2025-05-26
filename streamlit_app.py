# # # app.py  –  Streamlit multipage (“report” <-> “model output”)
# # # ------------------------------------------------------------
# # # pip install streamlit pandas requests streamlit-aggrid ultralytics pillow
# #
# # import io
# # import requests
# # import streamlit as st
# # import pandas as pd
# # from st_aggrid import AgGrid
# # from PIL import Image
# # from ultralytics import YOLO      # ← demo model; swap with your own .pt
# #
# # # ------------------------------------------------------------
# # # 0️⃣  BASIC PAGE SETUP
# # # ------------------------------------------------------------
# # st.set_page_config(
# #     page_title="🐄 Gau Swastha – AI Health Report",
# #     page_icon="🐄",
# #     layout="wide",
# #     initial_sidebar_state="collapsed",
# # )
# #
# # # ---- Global font patch (unchanged) --------------------------
# # st.markdown(
# #     """
# #     <style>
# #         html, body, [class*="css"]  { font-size:16px !important; }
# #         h1, h2, h3, h4              { font-size:1.35em !important; }
# #         h1                          { font-size:1.6em !important; }
# #         .ag-theme-streamlit .ag-cell,
# #         .ag-theme-streamlit .ag-header-cell-label {
# #             font-size:15px !important; line-height:22px !important;
# #         }
# #     </style>
# #     """,
# #     unsafe_allow_html=True,
# # )
# #
# # # ------------------------------------------------------------
# # # 🔄  HELPER — tiny router via session state
# # # ------------------------------------------------------------
# # if "view" not in st.session_state:
# #     st.session_state["view"] = "report"          # default tab
# # if "img_bytes" not in st.session_state:
# #     st.session_state["img_bytes"] = None
# # if "api_json" not in st.session_state:
# #     st.session_state["api_json"] = None
# # if "yolo_render" not in st.session_state:
# #     st.session_state["yolo_render"] = None
# #
# #
# # def switch_view(target: str):
# #     """Callback that flips the session‐state router."""
# #     st.session_state["view"] = target
# #
# #
# # # ------------------------------------------------------------
# # # 🅰️  PAGE A  – upload + API + REPORT
# # # ------------------------------------------------------------
# # def show_report():
# #     st.title("🐄 Gau Swastha — AI Health Report")
# #
# #     # --- Upload & language picker ---------------------------------
# #     API_URL = "https://dev-scanner.silofortune.com/api/v2_5/cattle-scanner"
# #
# #     img_file = st.file_uploader("Upload *side-profile* image", type=["jpg", "jpeg", "png"])
# #     lang = st.selectbox("Report language", ["en", "hi", "te", "ta"], index=0)
# #
# #     if img_file and st.button("Generate report"):
# #         try:
# #             img_bytes = img_file.read()                       # read once
# #             with st.spinner("Contacting scanner…"):
# #                 res = requests.post(
# #                     API_URL,
# #                     files={"side-img": (img_file.name, img_bytes, "image/jpeg")},
# #                     data={"language": lang},
# #                     timeout=60,
# #                 )
# #                 res.raise_for_status()
# #                 data = res.json()
# #         except Exception as exc:
# #             st.error(f"API call failed: {exc}")
# #             st.stop()
# #
# #         # Save to session so the other page can use them
# #         st.session_state["img_bytes"] = img_bytes
# #         st.session_state["api_json"] = data
# #         st.session_state["yolo_render"] = None     # clear old model run
# #         st.success("Report generated – scroll down or open *View Model Output*")
# #
# #     # --------------------------
# #     # If we already have a report in state, show it:
# #     # --------------------------
# #     if st.session_state["api_json"]:
# #         data = st.session_state["api_json"]
# #         img_bytes = st.session_state["img_bytes"]
# #
# #         # 👉  NAV buttons
# #         col1, col2 = st.columns(2)
# #         with col1:
# #             st.button("🔄 View Report", disabled=True)            # on this page
# #         with col2:
# #             st.button("🖼️ View Model Output", on_click=switch_view, args=("model",))
# #
# #         # 1. image on top
# #         st.image(img_bytes, caption="Uploaded image", use_column_width=True, output_format="JPEG")
# #
# #         # 2. full report (unchanged from your original code) -----
# #         # ── ANIMAL DETAILS ─────────────────────────────────────────
# #         st.subheader("Animal Details")
# #         det = data["animal-details"]
# #         adf = pd.DataFrame(
# #             {
# #                 "Animal Type": [det["animal-type"].title()],
# #                 "Breed": [det["breed"]["breed"].replace("-", " ")],
# #                 "Breed Grade": [det["breed-grade"]["breed-grade"]],
# #                 "Body Weight (kg)": [det["body-weight"]],
# #             }
# #         )
# #         st.table(adf)
# #
# #         # ── ECONOMIC PARAMETERS ────────────────────────────────────
# #         st.subheader("Economic Parameters")
# #         econ = data["animal-economic-status"]
# #         edf = pd.DataFrame(
# #             {
# #                 "Body Condition Score": [econ["bcs"]["value"]],
# #                 "Approx. Milk Yield (L/day)": [econ["milk yield"]],
# #                 "Production Capacity (L/day)": [econ["production-capacity"]],
# #                 "Lactation Yield (L)": [econ["lactation-yield"]],
# #                 "Breeding Capacity": [econ["breeding-capacity"]],
# #                 "Market Value (₹)": [econ["market-value"]],
# #                 "Buying Recommendation": [econ["buying-recommendation"]],
# #             }
# #         )
# #         st.table(edf)
# #
# #         # ── GENERAL HEALTH CONDITIONS ─────────────────────────────
# #         st.subheader("General Health Conditions")
# #         gh_rows = []
# #         for k, v in data["general-health-condition"].items():
# #             if isinstance(v, dict):
# #                 gh_rows.append(
# #                     {
# #                         "Parameter": k.replace("-", " ").title(),
# #                         "Status": v.get("value"),
# #                         "Interpretation": v.get("interpretation"),
# #                         "Recommendation": v.get("recommendation"),
# #                     }
# #                 )
# #             else:
# #                 gh_rows.append(
# #                     {
# #                         "Parameter": k.replace("-", " ").title(),
# #                         "Status": v,
# #                         "Interpretation": "",
# #                         "Recommendation": "",
# #                     }
# #                 )
# #         gh_df = pd.DataFrame(gh_rows)
# #         AgGrid(gh_df, fit_columns_on_grid_load=True, height=300, theme="streamlit")
# #
# #         # ── DISORDER STATUS BY SYSTEM ─────────────────────────────
# #         st.subheader("Disorder Status by System")
# #         sd_rows = []
# #         for system, sys_dict in data["system-of-disorder"].items():
# #             for issue, meta in sys_dict.items():
# #                 sd_rows.append(
# #                     {
# #                         "System": system.replace("-", " ").title(),
# #                         "Issue": issue.replace("-", " ").title(),
# #                         "Detected": meta["value"],
# #                         "Interpretation": meta["interpretation"],
# #                         "Recommendation": meta["recommendation"],
# #                     }
# #                 )
# #         sd_df = pd.DataFrame(sd_rows)
# #         AgGrid(sd_df, fit_columns_on_grid_load=True, height=350, theme="alpine")
# #
# #         # ── DIET RECOMMENDATIONS ──────────────────────────────────
# #         st.subheader("Balanced Ration – Feed / Fodder Plan")
# #         diet_tabs = st.tabs(["Green-Dry Fodder Plan", "Maize-Silage Plan"])
# #         for (plan_key, plan_dict), tab in zip(data["diet"].items(), diet_tabs):
# #             plan_df = (
# #                 pd.Series(plan_dict)
# #                 .rename_axis("Feed / Fodder")
# #                 .to_frame(plan_key.replace("_", " ").upper())
# #             )
# #             with tab:
# #                 st.dataframe(plan_df, use_container_width=True)
# #
# #         # ── RAW JSON (optional) ───────────────────────────────────
# #         with st.expander("🔍 Raw JSON payload", expanded=False):
# #             st.json(data, expanded=False)
# #
# #         st.caption(
# #             "Disclaimer — This is an AI-generated advisory. "
# #             "Always consult a qualified veterinary professional before acting on these recommendations."
# #         )
# #     else:
# #         st.info("Upload an image and click **Generate report** to begin.")
# #
# #
# # # ------------------------------------------------------------
# # # 🅱️  PAGE B  – YOLO model output
# # # ------------------------------------------------------------
# # def show_model_output():
# #     st.title("🖼️ Model Output – YOLO Detection")
# #
# #     # --- Back to report button ------------------------------------
# #     st.button("🔙 View Report", on_click=switch_view, args=("report",))
# #
# #     if st.session_state["img_bytes"] is None:
# #         st.warning("No image found. Please generate a report first, then come back here.")
# #         return
# #
# #     # Run model once & cache result in session_state ---------------
# #     if st.session_state["yolo_render"] is None:
# #         with st.spinner("Running YOLO model…"):
# #             # Load model (replace with your own .pt as needed)
# #             model = YOLO("/Users/aftaabhussain/Major-project/CattleScanner/breed.pt")
# #
# #             # YOLO accepts file-paths, ndarray, or PIL.Image. Convert:
# #             img = Image.open(io.BytesIO(st.session_state["img_bytes"]))
# #             results = model(img)             # list[ultralytics.engine.results.Results]
# #             render = results[0].plot()       # numpy array with bboxes
# #
# #             st.session_state["yolo_render"] = render
# #
# #     # Show the annotated image
# #     st.image(
# #         st.session_state["yolo_render"],
# #         caption="YOLO prediction (demo model)",
# #         use_column_width=True,
# #     )
# #
# #     # Optional: list out detections
# #     results = model(img)[0]  # results already exist above; kept simple
# #     det_df = results.pandas().xyxy[0]
# #     if not det_df.empty:
# #         st.subheader("Detected objects")
# #         st.table(det_df[["name", "confidence"]])
# #
# #     st.caption("Replace `'yolov8n.pt'` with your own model file for production.")
# #
# #
# # # ------------------------------------------------------------
# # # 🚦 ROUTER — render the chosen page
# # # ------------------------------------------------------------
# # if st.session_state["view"] == "report":
# #     show_report()
# # else:
# #     show_model_output()
#
# # app.py – Streamlit multipage (Report <-> Model outputs, multi-model)
# # -------------------------------------------------------------------
# # pip install streamlit pandas requests streamlit-aggrid ultralytics pillow
#
# import io, requests, pathlib
# import streamlit as st
# import pandas as pd
# from st_aggrid import AgGrid
# from PIL import Image
# from ultralytics import YOLO
#
# # -------------------------------------------------------------------
# # 🔧  Configure ALL your YOLO models here
# #      key = label shown on button
# #      val = path or URL to the .pt file
# # -------------------------------------------------------------------
# MODEL_CONFIG = {
#     "Breed Detection": "/Users/aftaabhussain/Major-project/CattleScanner/breed.pt",
#     "Teat Score":      "/Users/aftaabhussain/Major-project/CattleScanner/teat.pt",
#     "Body Segmentation": "/Users/aftaabhussain/Major-project/CattleScanner/side_segmentation_model.pt",
# }
#
# # -------------------------------------------------------------------
# # 0️⃣  BASIC PAGE SETUP
# # -------------------------------------------------------------------
# st.set_page_config(
#     page_title="🐄 Gau Swastha – AI Health Report",
#     page_icon="🐄",
#     layout="wide",
#     initial_sidebar_state="collapsed",
# )
#
# st.markdown(
#     """
#     <style>
#         html, body, [class*="css"]  { font-size:16px !important; }
#         h1, h2, h3, h4              { font-size:1.35em !important; }
#         h1                          { font-size:1.6em !important; }
#         .ag-theme-streamlit .ag-cell,
#         .ag-theme-streamlit .ag-header-cell-label {
#             font-size:15px !important; line-height:22px !important;
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )
#
# # -------------------------------------------------------------------
# # 🔄  SESSION-STATE INITIALISATION
# # -------------------------------------------------------------------
# ss = st.session_state
# ss.setdefault("view", "report")         # which page?
# ss.setdefault("img_bytes", None)
# ss.setdefault("api_json", None)
# ss.setdefault("models", {})             # {model_key: YOLO obj}
# ss.setdefault("renders", {})            # {model_key: np.ndarray}
# ss.setdefault("model_choice", None)     # active model key
#
# # -------------------------------------------------------------------
# # 🔀  MINI ROUTER
# # -------------------------------------------------------------------
# def switch_view(page: str):
#     ss.view = page
#
# # -------------------------------------------------------------------
# # 🔧  MODEL RUNNER
# # -------------------------------------------------------------------
# def run_model_on_image(model_key: str):
#     """
#     Load the YOLO model identified by `model_key` (cached) and
#     run it on the uploaded image.  The rendered ndarray goes to
#     ss.renders[model_key].
#     """
#     if ss.img_bytes is None:
#         st.warning("No image found. Please generate a report first.")
#         return
#
#     if model_key not in ss.models:                # load once
#         with st.spinner(f"Loading {model_key} model…"):
#             model_path = MODEL_CONFIG[model_key]
#             if not pathlib.Path(model_path).exists():
#                 st.error(f"Model file not found: {model_path}")
#                 return
#             ss.models[model_key] = YOLO(model_path)
#
#     if model_key not in ss.renders:
#         with st.spinner(f"Running {model_key}…"):
#             img = Image.open(io.BytesIO(ss.img_bytes))
#             results = ss.models[model_key](img)
#             ss.renders[model_key] = results[0].plot()
#             ss[f"det_df_{model_key}"] = results[0].pandas().xyxy[0]
#
#     ss.model_choice = model_key  # remember which one to display
#
#
# # -------------------------------------------------------------------
# # 🅰️  PAGE – REPORT
# # -------------------------------------------------------------------
# def show_report():
#     st.title("🐄 Gau Swastha — AI Health Report")
#
#     API_URL = "https://dev-scanner.silofortune.com/api/v2_5/cattle-scanner"
#     img_file = st.file_uploader("Upload *side-profile* image", type=["jpg", "jpeg", "png"])
#     lang = st.selectbox("Report language", ["en", "hi", "te", "ta"], index=0)
#
#     if img_file and st.button("Generate report"):
#         try:
#             img_bytes = img_file.read()
#             with st.spinner("Contacting scanner…"):
#                 res = requests.post(
#                     API_URL,
#                     files={"side-img": (img_file.name, img_bytes, "image/jpeg")},
#                     data={"language": lang},
#                     timeout=60,
#                 )
#                 res.raise_for_status()
#                 data = res.json()
#         except Exception as exc:
#             st.error(f"API call failed: {exc}")
#             st.stop()
#
#         ss.img_bytes = img_bytes
#         ss.api_json = data
#         ss.renders.clear()           # clear any previous model outputs
#         ss.models.clear()
#         ss.model_choice = None
#         st.success("Report generated – scroll down or open *View Model Output*")
#
#     if ss.api_json:
#         data, img_bytes = ss.api_json, ss.img_bytes
#
#         col1, col2 = st.columns(2)
#         with col1:
#             st.button("🔄 View Report", disabled=True)
#         with col2:
#             st.button("🖼️ View Model Output", on_click=switch_view, args=("model",))
#
#         st.image(img_bytes, caption="Uploaded image", use_column_width=True)
#
#         # --- (rest of report unchanged) ---------------------------
#         # 1. Animal details
#         st.subheader("Animal Details")
#         det = data["animal-details"]
#         st.table(pd.DataFrame({
#             "Animal Type": [det["animal-type"].title()],
#             "Breed": [det["breed"]["breed"].replace("-", " ")],
#             "Breed Grade": [det["breed-grade"]["breed-grade"]],
#             "Body Weight (kg)": [det["body-weight"]],
#         }))
#
#         # 2. Economic parameters
#         st.subheader("Economic Parameters")
#         econ = data["animal-economic-status"]
#         st.table(pd.DataFrame({
#             "Body Condition Score": [econ["bcs"]["value"]],
#             "Approx. Milk Yield (L/day)": [econ["milk yield"]],
#             "Production Capacity (L/day)": [econ["production-capacity"]],
#             "Lactation Yield (L)": [econ["lactation-yield"]],
#             "Breeding Capacity": [econ["breeding-capacity"]],
#             "Market Value (₹)": [econ["market-value"]],
#             "Buying Recommendation": [econ["buying-recommendation"]],
#         }))
#
#         # 3. General health conditions
#         st.subheader("General Health Conditions")
#         gh_rows = []
#         for k, v in data["general-health-condition"].items():
#             gh_rows.append({
#                 "Parameter": k.replace("-", " ").title(),
#                 "Status": v.get("value") if isinstance(v, dict) else v,
#                 "Interpretation": v.get("interpretation", "") if isinstance(v, dict) else "",
#                 "Recommendation": v.get("recommendation", "") if isinstance(v, dict) else "",
#             })
#         AgGrid(pd.DataFrame(gh_rows), fit_columns_on_grid_load=True, height=300, theme="streamlit")
#
#         # 4. Disorder status
#         st.subheader("Disorder Status by System")
#         sd_rows = []
#         for system, sys_dict in data["system-of-disorder"].items():
#             for issue, meta in sys_dict.items():
#                 sd_rows.append({
#                     "System": system.replace("-", " ").title(),
#                     "Issue": issue.replace("-", " ").title(),
#                     "Detected": meta["value"],
#                     "Interpretation": meta["interpretation"],
#                     "Recommendation": meta["recommendation"],
#                 })
#         AgGrid(pd.DataFrame(sd_rows), fit_columns_on_grid_load=True, height=350, theme="alpine")
#
#         # 5. Diet
#         st.subheader("Balanced Ration – Feed / Fodder Plan")
#         diet_tabs = st.tabs(["Green-Dry Fodder Plan", "Maize-Silage Plan"])
#         for (plan_key, plan_dict), tab in zip(data["diet"].items(), diet_tabs):
#             with tab:
#                 st.dataframe(
#                     pd.Series(plan_dict).rename_axis("Feed / Fodder")
#                     .to_frame(plan_key.replace("_", " ").upper()),
#                     use_container_width=True
#                 )
#
#         with st.expander("🔍 Raw JSON payload"):
#             st.json(data, expanded=False)
#
#         st.caption("Disclaimer — AI-generated advisory. Consult a vet before acting.")
#
#     else:
#         st.info("Upload an image and click **Generate report** to begin.")
#
#
# # -------------------------------------------------------------------
# # 🅱️  PAGE – MODEL OUTPUT (multi-model)
# # -------------------------------------------------------------------
# def show_model_output():
#     st.title("🖼️ Model Outputs")
#
#     st.button("🔙 View Report", on_click=switch_view, args=("report",))
#
#     if ss.img_bytes is None:
#         st.warning("No image found. Generate a report first.")
#         return
#
#     # --- Model selector buttons -----------------------------------
#     cols = st.columns(len(MODEL_CONFIG))
#     for (model_key, _), col in zip(MODEL_CONFIG.items(), cols):
#         col.button(
#             model_key,
#             on_click=run_model_on_image,
#             args=(model_key,),
#             key=f"btn_{model_key}",
#         )
#
#     # --- Display chosen model output ------------------------------
#     if ss.model_choice:
#         st.subheader(f"Output – {ss.model_choice}")
#         st.image(
#             ss.renders[ss.model_choice],
#             caption=f"{ss.model_choice} prediction",
#             use_column_width=True,
#         )
#
#         det_df = ss.get(f"det_df_{ss.model_choice}")
#         if det_df is not None and not det_df.empty:
#             st.subheader("Detected objects")
#             st.table(det_df[["name", "confidence"]])
#
#         st.caption("Loaded from: " + MODEL_CONFIG[ss.model_choice])
#     else:
#         st.info("Click one of the model buttons above to run inference.")
#
#
# # -------------------------------------------------------------------
# # 🚦  ROUTER
# # -------------------------------------------------------------------
# if ss.view == "report":
#     show_report()
# else:
#     show_model_output()

# ============================================================================
# app.py ­– Gau Swastha Streamlit app
# Two “pages”: ❶ Health-report (calls API) ❷ Model outputs (multi-model YOLO)
# Fully hardened against:
#   • Streamlit ↔︎ PyTorch watcher crash
#   • Python 3.12+ “no running event loop” warning
#   • Offline/SSL weight downloads
#   • Ultralytics ≥ 0.5 API changes (no .pandas())
# Tested with: python 3.11.9, streamlit 1.45, ultralytics 0.5, torch 2.2
# ============================================================================

# ---------------------------------------------------------------------------
# 🛡  compatibility shims (must run BEFORE importing streamlit)
# ---------------------------------------------------------------------------
import os, asyncio, torch
torch.classes.__path__ = []                                   # fix watcher crash
os.environ.setdefault("STREAMLIT_SERVER_FILE_WATCHER_TYPE", "none")
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# ---------------------------------------------------------------------------
# 📦  standard imports
# ---------------------------------------------------------------------------
import io, pathlib, requests
import streamlit as st
import pandas as pd
from PIL import Image
from st_aggrid import AgGrid
from ultralytics import YOLO

# ---------------------------------------------------------------------------
# 🗂️  list all on-disk YOLO weights you want to expose
# ---------------------------------------------------------------------------
MODEL_CONFIG = {
    "Breed Detection"     : "/Users/aftaabhussain/Major-project/CattleScanner/breed.pt",
    "Breed Grade" : "/Users/aftaabhussain/Major-project/CattleScanner/grade.pt",
    "bcs" : "/Users/aftaabhussain/Major-project/CattleScanner/bcs.pt",
    "Skin Coat" : "/Users/aftaabhussain/Major-project/CattleScanner/coat.pt",
    "Udder type"  : "/Users/aftaabhussain/Major-project/CattleScanner/UdderType.pt",
    "Body Segmentation"   : "/Users/aftaabhussain/Major-project/CattleScanner/side_segmentation_model.pt",
    "Teat score" : "/Users/aftaabhussain/Major-project/CattleScanner/teat.pt",
    "Side Keypoint" : "/Users/aftaabhussain/Major-project/CattleScanner/side_keypoint_model.pt",


}

# ---------------------------------------------------------------------------
# 🔧  page-wide Streamlit settings + CSS
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="🐄 Gau Swastha – AI Health Report",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(
    """
    <style>
        html, body, [class*="css"]  { font-size:16px !important; }
        h1, h2, h3, h4              { font-size:1.35em !important; }
        h1                          { font-size:1.6em !important; }
        .ag-theme-streamlit .ag-cell,
        .ag-theme-streamlit .ag-header-cell-label {
            font-size:15px !important; line-height:22px !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 🗄️  session-state initialisation
# ---------------------------------------------------------------------------
SS = st.session_state
SS.setdefault("view",         "report")
SS.setdefault("img_bytes",     None)
SS.setdefault("api_json",      None)
SS.setdefault("models",        {})      # {key: YOLO()}
SS.setdefault("renders",       {})      # {key: ndarray}
SS.setdefault("results",       {})      # {key: Results}
SS.setdefault("tables",        {})      # {key: DataFrame}
SS.setdefault("model_choice",  None)

# ---------------------------------------------------------------------------
# 🔀  tiny router helpers
# ---------------------------------------------------------------------------
def switch_view(page: str)          -> None: SS.view = page
def clear_models_and_outputs()      -> None:
    SS.models.clear(); SS.renders.clear()
    SS.results.clear(); SS.tables.clear()
    SS.model_choice = None

# ---------------------------------------------------------------------------
# 🛠  Ultralytics Results → pandas helper  (Ultralytics ≥ 0.5)
# ---------------------------------------------------------------------------
def results_to_df(res) -> pd.DataFrame:
    """Return empty DF if no detections."""
    if res.boxes is None or res.boxes.xyxy is None:
        return pd.DataFrame()
    import numpy as np
    xyxy = res.boxes.xyxy.cpu().numpy()
    conf = res.boxes.conf.cpu().numpy()
    cls  = res.boxes.cls.cpu().numpy().astype(int)
    names = [res.names[int(i)] for i in cls]
    return pd.DataFrame(dict(
        xmin=xyxy[:, 0], ymin=xyxy[:, 1],
        xmax=xyxy[:, 2], ymax=xyxy[:, 3],
        confidence=np.round(conf, 3),
        name=names
    )).sort_values("confidence", ascending=False).reset_index(drop=True)

# ---------------------------------------------------------------------------
# ⚡  model-runner (load-once, run-once, cache)
# ---------------------------------------------------------------------------
def run_model_on_image(model_key: str) -> None:
    if SS.img_bytes is None:
        st.warning("No image found. Please generate a report first.")
        return

    # 1. load model if needed
    if model_key not in SS.models:
        path = pathlib.Path(MODEL_CONFIG[model_key])
        if not path.exists():
            st.error(f"❌ Weight file not found:\n{path}")
            return
        with st.spinner(f"Loading {model_key} …"):
            SS.models[model_key] = YOLO(str(path))

    # 2. run inference if not cached
    if model_key not in SS.renders:
        with st.spinner(f"Running {model_key} …"):
            img = Image.open(io.BytesIO(SS.img_bytes))
            res = SS.models[model_key](img)[0]          # first image
            SS.results[model_key] = res
            SS.renders[model_key] = res.plot()
            SS.tables[model_key]  = results_to_df(res)

    SS.model_choice = model_key

# ---------------------------------------------------------------------------
# 🅰️  REPORT page  (upload → call API → display)
# ---------------------------------------------------------------------------
def show_report():
    st.title("🐄 Gau Swastha — AI Health Report")

    API_URL = "https://dev-scanner.silofortune.com/api/v2_5/cattle-scanner"
    img_file = st.file_uploader("Upload *side-profile* image", type=["jpg", "jpeg", "png"])
    lang     = st.selectbox("Report language", ["en", "hi", "te", "ta"], index=0)

    if img_file and st.button("Generate report"):
        try:
            img_bytes = img_file.read()
            with st.spinner("Contacting scanner …"):
                r = requests.post(
                    API_URL,
                    files={"side-img": (img_file.name, img_bytes, "image/jpeg")},
                    data={"language": lang},
                    timeout=60,
                )
                r.raise_for_status()
        except Exception as e:
            st.error(f"API call failed: {e}")
            st.stop()

        SS.img_bytes = img_bytes
        SS.api_json  = r.json()
        clear_models_and_outputs()
        st.success("Report generated – scroll down or open **Model Output**")

    # ── nav bar ──────────────────────────────────────────────────
    if SS.api_json:
        col1, col2 = st.columns(2)
        col1.button("🔄 View Report", disabled=True)
        col2.button("🖼️ View Model Output", on_click=switch_view, args=("model",))

        st.image(SS.img_bytes, caption="Uploaded image", use_container_width=True)

        data = SS.api_json

        # 1) Animal details
        st.subheader("Animal Details")
        det = data["animal-details"]
        st.table(pd.DataFrame({
            "Animal Type"   : [det["animal-type"].title()],
            "Breed"         : [det["breed"]["breed"].replace("-", " ")],
            "Breed Grade"   : [det["breed-grade"]["breed-grade"]],
            "Body Weight kg": [det["body-weight"]],
        }))

        # 2) Economic parameters
        st.subheader("Economic Parameters")
        econ = data["animal-economic-status"]
        st.table(pd.DataFrame({
            "Body Condition Score"       : [econ["bcs"]["value"]],
            "Approx. Milk Yield (L/day)" : [econ["milk yield"]],
            "Production Capacity (L/day)": [econ["production-capacity"]],
            "Lactation Yield (L)"        : [econ["lactation-yield"]],
            "Breeding Capacity"          : [econ["breeding-capacity"]],
            "Market Value (₹)"           : [econ["market-value"]],
            "Buying Recommendation"      : [econ["buying-recommendation"]],
        }))

        # 3) General health
        st.subheader("General Health Conditions")
        gh_rows = []
        for k, v in data["general-health-condition"].items():
            gh_rows.append({
                "Parameter"     : k.replace("-", " ").title(),
                "Status"        : v.get("value") if isinstance(v, dict) else v,
                "Interpretation": v.get("interpretation", "") if isinstance(v, dict) else "",
                "Recommendation": v.get("recommendation", "") if isinstance(v, dict) else "",
            })
        AgGrid(pd.DataFrame(gh_rows), fit_columns_on_grid_load=True, height=300, theme="streamlit")

        # 4) Disorders
        st.subheader("Disorder Status by System")
        sd_rows = []
        for system, sys_dict in data["system-of-disorder"].items():
            for issue, meta in sys_dict.items():
                sd_rows.append({
                    "System"        : system.replace("-", " ").title(),
                    "Issue"         : issue.replace("-", " ").title(),
                    "Detected"      : meta["value"],
                    "Interpretation": meta["interpretation"],
                    "Recommendation": meta["recommendation"],
                })
        AgGrid(pd.DataFrame(sd_rows), fit_columns_on_grid_load=True, height=350, theme="alpine")

        # 5) Diet
        st.subheader("Balanced Ration – Feed / Fodder Plan")
        diet_tabs = st.tabs(["Green-Dry Fodder Plan", "Maize-Silage Plan"])
        for (key, plan), tab in zip(data["diet"].items(), diet_tabs):
            with tab:
                st.dataframe(
                    pd.Series(plan).rename_axis("Feed / Fodder").to_frame(key.replace("_", " ").upper()),
                    use_container_width=True,
                )

        with st.expander("🔍 Raw JSON payload"):
            st.json(data, expanded=False)

        st.caption("Disclaimer — AI-generated advisory. Always consult a vet.")

    else:
        st.info("Upload an image and click **Generate report** to begin.")

# ---------------------------------------------------------------------------
# 🅱️  MODEL OUTPUT page
# ---------------------------------------------------------------------------
def show_model_output():
    st.title("🖼️ Model Outputs")
    st.button("🔙 View Report", on_click=switch_view, args=("report",))

    if SS.img_bytes is None:
        st.warning("No image found. Generate a report first.")
        return

    # --- model selector buttons -----------------------------------
    cols = st.columns(len(MODEL_CONFIG))
    for (key, _), col in zip(MODEL_CONFIG.items(), cols):
        col.button(key, on_click=run_model_on_image, args=(key,), key=f"btn_{key}")

    # --- display chosen model output ------------------------------
    if SS.model_choice:
        key = SS.model_choice
        st.subheader(f"Output – {key}")
        st.image(SS.renders[key], caption=key, use_container_width=True)

        df = SS.tables[key]
        if not df.empty:
            st.subheader("Detections")
            st.table(df)

        st.caption("Weight file: " + MODEL_CONFIG[key])
    else:
        st.info("Click a model button above to run inference.")

# ---------------------------------------------------------------------------
# 🚦  ROUTE
# ---------------------------------------------------------------------------
if SS.view == "report":
    show_report()
else:
    show_model_output()