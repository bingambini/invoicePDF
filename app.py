import streamlit as st
import yaml
import pandas as pd
from io import BytesIO
from opendataloader_pdf import convert
from pathlib import Path

# Load configurable fields
with open("config/fields.yaml") as f:
    config = yaml.safe_load(f)

fields = config["fields"]

st.set_page_config(page_title="Georgian Invoice Extractor", layout="wide")
st.title("📄 Georgian Invoice Extractor")

uploaded_files = st.file_uploader("ატვირთე PDF ინვოისები", type="pdf", accept_multiple_files=True)

# ველების არჩევა (მოქნილად)
selected_keys = st.multiselect(
    "აირჩიე ველები ამოღებისთვის",
    options=[f["key"] for f in fields],
    default=[f["key"] for f in fields if f.get("required", False)]
)

if st.button("🚀 დამუშავება", type="primary") and uploaded_files:
    results = []
    progress = st.progress(0)

    for i, file in enumerate(uploaded_files):
        with st.spinner(f"მუშავდება: {file.name}"):
            # OpenDataLoader PDF
            output = convert(
                input_path=file,
                format="json",           # ან "markdown,json"
                mode="hybrid"            # ან "fast"
            )
            
            # აქ მოდის extraction ლოგიკა (rule-based + fallback)
            extracted = extract_data(output["json"], file.name, selected_keys)
            results.append(extracted)

        progress.progress((i + 1) / len(uploaded_files))

    df = pd.DataFrame(results)
    
    # Manual Review (editable table)
    st.subheader("📋 შედეგები (შეგიძლია ხელით შეასწორო)")
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    # Excel Download
    output = BytesIO()
    edited_df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    st.download_button(
        label="📥 გადმოწერე Excel",
        data=output,
        file_name=f"invoices_{pd.Timestamp.now().strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
