import os
from datetime import date

import requests
import streamlit as st

API_URL = os.environ.get("NDA_API_URL", "http://localhost:8000/api")

st.set_page_config(page_title="NDA Generator & Tracker", layout="wide")

page = st.sidebar.radio("Navigation", ["Generate NDA", "NDA Registry"])


@st.cache_data(ttl=60)
def get_jurisdictions():
    """Fetch jurisdictions from the API."""
    resp = requests.get(f"{API_URL}/jurisdictions/", timeout=10)
    resp.raise_for_status()
    return resp.json()


# ---- Page: Generate NDA ----
if page == "Generate NDA":
    st.title("Generate NDA")
    st.markdown(
        "Fill in the details below to generate a Mutual Non-Disclosure Agreement."
    )

    jur_data = get_jurisdictions()
    top_jurisdictions = jur_data["top_jurisdictions"]
    all_jurisdictions = jur_data["all_jurisdictions"]

    with st.form("nda_form"):
        st.subheader("Party A (Your Company)")
        col1, col2 = st.columns(2)
        with col1:
            dp_name = st.text_input("Company Name *", key="dp_name")
            dp_signer = st.text_input("Signer Name", key="dp_signer")
        with col2:
            dp_address = st.text_area("Address", key="dp_address", height=80)
            dp_title = st.text_input("Signer Title", key="dp_title")

        st.subheader("Party B (Counterparty)")
        col3, col4 = st.columns(2)
        with col3:
            rp_name = st.text_input("Company Name *", key="rp_name")
            rp_signer = st.text_input("Signer Name", key="rp_signer")
        with col4:
            rp_address = st.text_area("Address", key="rp_address", height=80)
            rp_title = st.text_input("Signer Title", key="rp_title")

        st.subheader("NDA Terms")
        col5, col6 = st.columns(2)
        with col5:
            eff_date = st.date_input("Effective Date", value=date.today())
            term_years = st.selectbox("Term (years)", options=[1, 2, 3, 4, 5], index=1)
            survival_years = st.selectbox(
                "Survival Period (years)", options=[1, 2, 3, 5], index=1
            )
        with col6:
            purpose = st.text_area(
                "Purpose",
                value="evaluating a potential business relationship between the parties",
                height=80,
            )

        st.subheader("Governing Law")

        # Build jurisdiction options: top picks first, then all
        top_names = {j["display_name"] for j in top_jurisdictions}
        jur_options: dict[str, int] = {}
        for j in top_jurisdictions:
            jur_options[f"\u2605 {j['display_name']}"] = j["id"]
        for j in all_jurisdictions:
            if j["display_name"] not in top_names:
                jur_options[j["display_name"]] = j["id"]

        selected_jur_label = st.selectbox(
            "Jurisdiction", options=list(jur_options.keys()), index=0
        )
        selected_jur_id = jur_options[selected_jur_label]

        custom_jur = st.text_input(
            "Or enter a custom jurisdiction (leave blank to use selection above)"
        )

        notes = st.text_area("Internal Notes (not included in NDA)", height=60)

        submitted = st.form_submit_button("Generate NDA", type="primary")

    if submitted:
        if not dp_name or not rp_name:
            st.error("Both party names are required.")
        else:
            # Handle custom jurisdiction
            jurisdiction_id = selected_jur_id
            if custom_jur.strip():
                jur_resp = requests.post(
                    f"{API_URL}/jurisdictions/",
                    json={
                        "country": "Custom",
                        "subdivision": None,
                        "display_name": custom_jur.strip(),
                    },
                    timeout=10,
                )
                if jur_resp.status_code == 201:
                    jurisdiction_id = jur_resp.json()["id"]
                    get_jurisdictions.clear()
                elif jur_resp.status_code == 409:
                    st.warning("Jurisdiction already exists, using existing entry.")
                    fresh_data = requests.get(
                        f"{API_URL}/jurisdictions/", timeout=10
                    ).json()
                    for j in fresh_data["all_jurisdictions"]:
                        if j["display_name"] == custom_jur.strip():
                            jurisdiction_id = j["id"]
                            break

            payload = {
                "disclosing_party_name": dp_name,
                "disclosing_party_address": dp_address,
                "disclosing_party_signer_name": dp_signer,
                "disclosing_party_signer_title": dp_title,
                "receiving_party_name": rp_name,
                "receiving_party_address": rp_address,
                "receiving_party_signer_name": rp_signer,
                "receiving_party_signer_title": rp_title,
                "effective_date": eff_date.isoformat(),
                "term_years": term_years,
                "survival_years": survival_years,
                "purpose": purpose,
                "jurisdiction_id": jurisdiction_id,
                "notes": notes,
            }

            with st.spinner("Generating NDA..."):
                resp = requests.post(f"{API_URL}/ndas/", json=payload, timeout=30)

            if resp.status_code == 201:
                nda = resp.json()
                st.success(f"NDA #{nda['id']} generated successfully!")

                download_resp = requests.get(
                    f"{API_URL}/ndas/{nda['id']}/download", timeout=10
                )
                if download_resp.status_code == 200:
                    st.download_button(
                        label="Download NDA (.docx)",
                        data=download_resp.content,
                        file_name=f"NDA_{rp_name.replace(' ', '_')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
            else:
                st.error(f"Error generating NDA: {resp.text}")


# ---- Page: NDA Registry ----
elif page == "NDA Registry":
    st.title("NDA Registry")

    col1, col2 = st.columns([1, 3])
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All", "draft", "sent", "executed", "expired"],
        )

    params: dict[str, str | int] = {}
    if status_filter != "All":
        params["status"] = status_filter

    resp = requests.get(f"{API_URL}/ndas/", params=params, timeout=10)

    if resp.status_code == 200:
        data = resp.json()
        ndas = data["items"]
        st.metric("Total NDAs", data["total"])

        if ndas:
            for nda in ndas:
                with st.expander(
                    f"#{nda['id']} | {nda['disclosing_party_name']} "
                    f"\u2194 {nda['receiving_party_name']} | "
                    f"{nda['status'].upper()}"
                ):
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.write(f"**Type:** {nda['nda_type']}")
                        st.write(f"**Effective:** {nda['effective_date']}")
                        st.write(f"**Expiry:** {nda['expiry_date']}")
                    with col_b:
                        st.write(f"**Term:** {nda['term_years']} years")
                        st.write(f"**Survival:** {nda['survival_years']} years")
                        st.write(f"**Status:** {nda['status']}")
                    with col_c:
                        st.write(f"**Created:** {nda['created_at'][:10]}")
                        if nda.get("notes"):
                            st.write(f"**Notes:** {nda['notes']}")

                    # Status update
                    new_status = st.selectbox(
                        "Update Status",
                        options=["draft", "sent", "executed", "expired"],
                        index=["draft", "sent", "executed", "expired"].index(
                            nda["status"]
                        ),
                        key=f"status_{nda['id']}",
                    )
                    if st.button("Update", key=f"update_{nda['id']}"):
                        update_resp = requests.patch(
                            f"{API_URL}/ndas/{nda['id']}",
                            json={"status": new_status},
                            timeout=10,
                        )
                        if update_resp.status_code == 200:
                            st.success("Updated!")
                            st.rerun()

                    # Download
                    if nda.get("file_path"):
                        dl_resp = requests.get(
                            f"{API_URL}/ndas/{nda['id']}/download", timeout=10
                        )
                        if dl_resp.status_code == 200:
                            st.download_button(
                                "Download .docx",
                                data=dl_resp.content,
                                file_name=f"NDA_{nda['receiving_party_name'].replace(' ', '_')}.docx",
                                key=f"dl_{nda['id']}",
                            )
        else:
            st.info("No NDAs found. Generate your first NDA from the sidebar.")
    else:
        st.error("Failed to load NDA registry.")
