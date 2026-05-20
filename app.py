import streamlit as st
import yaml
import pandas as pd
from io import BytesIO
from pathlib import Path
from opendataloader_pdf import convert
from extractor import extract_data

# ===================== CONFIG =====================
with open("config/fields.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)

all_fields = config["fields"]
field_dict = {f["key"]: f for f in all_fields}

st.set_page_config(page_title="Georgian Invoice Extractor", layout="wide")
st.title("📄 Georgian Invoice Extractor")
st.markdown("**OpenDataLoader PDF + Rule-based** — მაქსიმალური სიზუსტე")

# ===================== UI =====================
uploaded_files = st.file_uploader(
    "ატვირთე PDF ინვოისები", 
    type="pdf", 
    accept_multiple_files=True
)

selected_keys = st.multiselect(
    "აირჩიე ველები ამოღებისთვის",
    options=[f["key"] for f in all_fields],
    default=[f["key"] for f in all_fields if f.get("required", False)],
    format_func=lambda x: field_dict[x]["label"]
)

if st.button("🚀 დამუშავება", type="primary") and uploaded_files:
    results = []
    progress_bar = st.progress(0)

    for i, uploaded_file in enumerate(uploaded_files):
        with st.spinner(f"მუშავდება: {uploaded_file.name}"):
            try:
                # OpenDataLoader PDF
                result = convert(
                    input_path=uploaded_file,
                    format="markdown,json",
                    mode="hybrid"          # ან "fast" უფრო სწრაფად
                )
                
                extracted = extract_data(result, uploaded_file.name, selected_keys)
                results.append(extracted)
            except Exception as e:
                results.append({"filename": uploaded_file.name, "error": str(e)})

        progress_bar.progress((i + 1) / len(uploaded_files))

    # ===================== RESULTS =====================
    df = pd.DataFrame(results)
    
    st.success(f"✅ დამუშავდა {len(results)} ფაილი")
    
    st.subheader("📋 შედეგები (შეგიძლია ხელით შეასწორო)")
    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        num_rows="dynamic",
        hide_index=True
    )

    # ===================== DOWNLOAD =====================
    output = BytesIO()
    edited_df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    st.download_button(
        label="📥 გადმოწერე Excel ფაილი",
        data=output,
        file_name=f"invoices_{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )
