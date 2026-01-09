
import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Incident Unblocker", page_icon="🟧", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root{
  --brand:#F36F21;
  --brand2:#FF8A3D;
  --ink:#111827;
  --muted:#6B7280;
  --bg:#FFFFFF;
  --soft:#FFF6EF;
  --line:#E5E7EB;
  --good:#10B981;
  --warn:#F59E0B;
  --bad:#EF4444;
}
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
.topbar{
  background: linear-gradient(90deg, var(--brand) 0%, var(--brand2) 100%);
  padding: 18px 22px; border-radius: 18px; color: white;
  box-shadow: 0 10px 25px rgba(17,24,39,.12); margin-bottom: 16px;
}
.topbar h1{ margin:0; font-size: 28px; font-weight: 800; letter-spacing:.2px;}
.topbar p{ margin:6px 0 0 0; opacity:.92; font-size: 14px;}
.card{
  border: 1px solid var(--line); border-radius: 18px; padding: 14px 16px;
  background: var(--bg); box-shadow: 0 6px 18px rgba(17,24,39,.06);
}
.card .label{ color: var(--muted); font-size: 12px; letter-spacing: .2px; }
.card .value{ color: var(--ink); font-size: 24px; font-weight: 800; margin-top: 2px;}
.pill{
  display:inline-block; padding: 3px 10px; border-radius: 999px;
  font-size: 12px; border:1px solid var(--line); background: var(--soft); color: var(--ink);
}
.pill.good{ border-color: rgba(16,185,129,.35); background: rgba(16,185,129,.10); color: var(--good); }
.pill.warn{ border-color: rgba(245,158,11,.40); background: rgba(245,158,11,.12); color: var(--warn); }
.pill.bad{ border-color: rgba(239,68,68,.35); background: rgba(239,68,68,.10); color: var(--bad); }
.section-title{ font-size: 16px; font-weight: 800; color: var(--ink); margin: 6px 0 10px 0; }
.footer-note{
  background: var(--soft); border: 1px dashed rgba(243,111,33,.45);
  border-radius: 14px; padding: 10px 12px; color: var(--ink); font-size: 12px;
}
hr { border: none; border-top: 1px solid var(--line); margin: 16px 0; }
.stButton>button{
  background: var(--brand) !important; color: white !important; border: 0 !important;
  border-radius: 12px !important; padding: 10px 14px !important; font-weight: 700 !important;
}
.stButton>button:hover{ filter: brightness(0.98); transform: translateY(-1px); }
.stTextInput>div>div>input, .stSelectbox>div>div, .stMultiSelect>div>div{ border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(path: str):
    friction = pd.read_excel(path, sheet_name="FRICTION_DATA")
    registry = pd.read_excel(path, sheet_name="OWNERSHIP_REGISTRY")
    incidents = pd.read_excel(path, sheet_name="INCIDENTS")
    try:
        actions = pd.read_excel(path, sheet_name="ACTION_LOG")
    except Exception:
        actions = pd.DataFrame(columns=["timestamp","incident_id","action","actor","details"])

    friction["submitted_datetime"] = pd.to_datetime(friction["submitted_datetime"])
    friction["completed_datetime"] = pd.to_datetime(friction["completed_datetime"], errors="coerce")
    incidents["created_at"] = pd.to_datetime(incidents["created_at"])
    incidents["updated_at"] = pd.to_datetime(incidents["updated_at"])
    return friction, registry, incidents, actions

st.sidebar.markdown("### Settings")
data_file = st.sidebar.text_input("Excel data file", "brown_hackathon_incidents_product.xlsx")
friction, registry, incidents, actions = load_data(data_file)

st.markdown("""
<div class="topbar">
  <h1>Incident Unblocker</h1>
  <p>Unresolved incidents • Ownership routing • “Send Teams Alert” action • Audit trail (hackathon demo)</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚨 Incident Console", "🔎 Ownership Directory", "📊 Friction Insights"])

with tab1:
    unresolved = incidents[incidents["status"] != "Resolved"].copy()
    open_cnt = int((incidents["status"] != "Resolved").sum())
    sev1_cnt = int(((incidents["status"] != "Resolved") & (incidents["severity"] == "Sev1")).sum())
    blocked_cnt = int(((incidents["status"] == "Blocked") & (incidents["status"] != "Resolved")).sum())
    missing_owner_cnt = int(((incidents["status"] != "Resolved") & (incidents["owner_team"].fillna("").str.strip() == "")).sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"""<div class="card"><div class="label">Unresolved incidents</div><div class="value">{open_cnt}</div></div>""", unsafe_allow_html=True)
    c2.markdown(f"""<div class="card"><div class="label">Sev1 unresolved</div><div class="value">{sev1_cnt}</div></div>""", unsafe_allow_html=True)
    c3.markdown(f"""<div class="card"><div class="label">Blocked</div><div class="value">{blocked_cnt}</div></div>""", unsafe_allow_html=True)
    c4.markdown(f"""<div class="card"><div class="label">Missing owner</div><div class="value">{missing_owner_cnt}</div></div>""", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    f1, f2, f3, f4, f5 = st.columns([1.2,1,1.4,1.4,1])
    status_filter = f1.multiselect("Status", sorted(incidents["status"].unique().tolist()),
                                   default=["Open","Investigating","Blocked"])
    sev_filter = f2.multiselect("Severity", sorted(incidents["severity"].unique().tolist()),
                                default=sorted(incidents["severity"].unique().tolist()))
    type_filter = f3.multiselect("Type", sorted(incidents["incident_type"].unique().tolist()),
                                 default=sorted(incidents["incident_type"].unique().tolist()))
    owner_gap_only = f4.checkbox("Only missing owner", value=False)
    search = f5.text_input("Search", "")

    view = incidents.copy()
    if status_filter: view = view[view["status"].isin(status_filter)]
    if sev_filter: view = view[view["severity"].isin(sev_filter)]
    if type_filter: view = view[view["incident_type"].isin(type_filter)]
    if owner_gap_only: view = view[view["owner_team"].fillna("").str.strip()==""]
    if search:
        view = view[
            view["incident_id"].astype(str).str.contains(search, case=False, na=False) |
            view["title"].astype(str).str.contains(search, case=False, na=False) |
            view["asset_name"].astype(str).str.contains(search, case=False, na=False)
        ]

    sev_rank = {"Sev1":0, "Sev2":1, "Sev3":2}
    view["sev_rank"] = view["severity"].map(sev_rank).fillna(9)
    view = view.sort_values(["sev_rank","created_at"], ascending=[True, True])

    st.markdown('<div class="section-title">Unresolved queue</div>', unsafe_allow_html=True)
    st.dataframe(
        view[["incident_id","severity","status","incident_type","title","asset_type","asset_name","owner_team","contact_channel","created_at","updated_at","blocked_reason"]],
        use_container_width=True, hide_index=True
    )

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Action panel</div>', unsafe_allow_html=True)

    if len(unresolved)==0:
        st.success("No unresolved incidents in the dataset.")
    else:
        pick = st.selectbox("Select incident", unresolved.sort_values("created_at")["incident_id"].tolist())
        row = unresolved[unresolved["incident_id"] == pick].iloc[0]

        left, right = st.columns([1.2, 1])

        with left:
            sev = row["severity"]
            pill_cls = "bad" if sev=="Sev1" else ("warn" if sev=="Sev2" else "good")
            st.markdown(f'<span class="pill {pill_cls}">{sev}</span> <span class="pill">{row["status"]}</span>', unsafe_allow_html=True)
            st.markdown(f"**{row['title']}**")
            st.write(f"**Incident ID:** {row['incident_id']}")
            st.write(f"**Type:** {row['incident_type']}")
            st.write(f"**Asset:** {row['asset_type']} — `{row['asset_name']}`")
            if str(row.get("blocked_reason","")).strip():
                st.write(f"**Blocked reason:** {row['blocked_reason']}")
            st.write(f"**Created:** {row['created_at']}")
            st.write(f"**Last updated:** {row['updated_at']}")
            st.caption(str(row.get("description","")).strip())

        with right:
            owner_team = str(row.get("owner_team","") or "").strip()
            contact_channel = str(row.get("contact_channel","") or "").strip()
            resolved_via_registry = False

            if not owner_team:
                match = registry[(registry["asset_type"]==row["asset_type"]) & (registry["asset_name"]==row["asset_name"])]
                if len(match):
                    owner_team = str(match.iloc[0]["owner_team"])
                    contact_channel = str(match.iloc[0]["contact_channel"])
                    resolved_via_registry = True

            if owner_team:
                st.success(f"Owner team: {owner_team}")
                st.write(f"Channel: {contact_channel or '(missing channel)'}")
                if resolved_via_registry:
                    st.caption("Owner resolved via registry.")
            else:
                st.warning("Owner unknown. Add this asset to the registry or route manually.")

            actor = st.text_input("Your name (audit)", "Demo User")
            reason = st.selectbox("Reason", [
                "Need owner confirmation / next steps",
                "Blocked due to unknown owner",
                "Critical incident – immediate triage needed",
                "Waiting on approval / access"
            ])

            colA, colB = st.columns(2)

            if colA.button("✅ Claim"):
                new = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "incident_id": pick,
                    "action": "CLAIMED",
                    "actor": actor,
                    "details": f"Claimed for triage. Reason: {reason}"
                }
                actions = pd.concat([actions, pd.DataFrame([new])], ignore_index=True)
                st.success("Claim recorded (demo).")

            if colB.button("📣 Send Teams Alert"):
                if not owner_team:
                    st.error("Owner missing — cannot route alert. Add ownership first.")
                else:
                    msg = (
                        f"TEAMS ALERT → {contact_channel}\n"
                        f"INCIDENT: {pick} ({row['severity']})\n"
                        f"Title: {row['title']}\n"
                        f"Asset: {row['asset_type']} {row['asset_name']}\n"
                        f"Status: {row['status']} | Blocked: {row.get('blocked_reason','')}\n"
                        f"Requested by: {actor}\n"
                        f"Ask: Please confirm owner + next steps to unblock."
                    )
                    new = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "incident_id": pick,
                        "action": "TEAMS_ALERT_SENT",
                        "actor": actor,
                        "details": f"Posted to {contact_channel}"
                    }
                    actions = pd.concat([actions, pd.DataFrame([new])], ignore_index=True)
                    st.success("Teams alert generated (demo).")
                    st.code(msg)

            st.markdown('<div class="footer-note">Production note: This button would call a Power Automate flow or Teams webhook to post the alert and attach incident context.</div>', unsafe_allow_html=True)

        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Audit trail (latest)</div>', unsafe_allow_html=True)
        st.dataframe(actions.tail(20), use_container_width=True, hide_index=True)

with tab2:
    st.markdown('<div class="section-title">Search ownership</div>', unsafe_allow_html=True)
    a1, a2 = st.columns([1,2])
    asset_type = a1.selectbox("Asset type", sorted(registry["asset_type"].unique().tolist()))
    subset = registry[registry["asset_type"]==asset_type].copy()
    q = a2.text_input("Search asset name", "")
    if q:
        subset = subset[subset["asset_name"].astype(str).str.contains(q, case=False, na=False)]
    st.dataframe(subset, use_container_width=True, hide_index=True)
    if len(subset):
        choice = st.selectbox("Select asset for details", subset["asset_name"].tolist())
        r = subset[subset["asset_name"]==choice].iloc[0]
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Owner card</div>', unsafe_allow_html=True)
        st.success(
            f"**Owner team:** {r['owner_team']}  \n"
            f"**Channel:** {r['contact_channel']}  \n"
            f"**Manager:** {r['manager_email']}  \n"
            f"**Runbook:** {r['runbook_link']}"
        )

with tab3:
    st.markdown('<div class="section-title">Systemic friction (optional)</div>', unsafe_allow_html=True)
    now_demo = friction["submitted_datetime"].max() + pd.Timedelta(hours=12)

    def age_hours(row):
        end = row["completed_datetime"] if pd.notna(row["completed_datetime"]) else now_demo
        return (end - row["submitted_datetime"]).total_seconds()/3600

    if "age_hours" not in friction.columns:
        friction["age_hours"] = friction.apply(age_hours, axis=1)
    if "sla_breached" not in friction.columns:
        friction["sla_breached"] = friction["age_hours"] > friction["sla_hours"]

    completed = friction[friction["status"]=="Completed"]
    waiting = friction[friction["status"]=="Waiting"]

    k1, k2, k3 = st.columns(3)
    k1.markdown(f"""<div class="card"><div class="label">Avg cycle time (hrs)</div><div class="value">{completed["age_hours"].mean():.1f}</div></div>""", unsafe_allow_html=True)
    k2.markdown(f"""<div class="card"><div class="label">% over SLA</div><div class="value">{(friction["sla_breached"].mean()*100):.0f}%</div></div>""", unsafe_allow_html=True)
    k3.markdown(f"""<div class="card"><div class="label">Currently waiting</div><div class="value">{len(waiting)}</div></div>""", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.write("**Avg delay by request type**")
        by_type = friction.groupby("request_type", as_index=False)["age_hours"].mean().sort_values("age_hours", ascending=False)
        st.bar_chart(by_type, x="request_type", y="age_hours")
    with right:
        st.write("**Avg delay by receiving team**")
        by_team = friction.groupby("to_team", as_index=False)["age_hours"].mean().sort_values("age_hours", ascending=False)
        st.bar_chart(by_team, x="to_team", y="age_hours")

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.write("**Top waiting items (SLA-breached)**")
    stuck = waiting[waiting["sla_breached"]==True].sort_values("age_hours", ascending=False).head(10)
    st.dataframe(stuck[["request_id","request_type","from_team","to_team","submitted_datetime","sla_hours","age_hours"]], use_container_width=True, hide_index=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### Demo script")
st.sidebar.write("1) Incident Console → pick Sev1 unresolved → Send Teams Alert.\n"
                 "2) Ownership Directory → search asset → show owner card.\n"
                 "3) Friction Insights → show systemic delays (optional).")
