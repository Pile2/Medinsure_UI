import streamlit as st
from enum import Enum
from datetime import datetime, date
import uuid

# -----------------------------
# DOMAIN MODELS / CONSTANTS
# -----------------------------

class Role(str, Enum):
    PATIENT = "Patient"
    CLINIC_ADMIN = "Clinic Admin"
    CLINIC_BILLING = "Clinic Billing"
    INSURER_ADJUSTER = "Insurer Adjuster"
    INSURER_STAFF = "Insurer Staff"


class ClaimStatus(str, Enum):
    SUBMITTED = "Submitted"
    IN_REVIEW = "In Review"
    INFO_REQUESTED = "Info Requested"
    APPROVED = "Approved"
    DENIED = "Denied"


# -----------------------------
# SESSION-STATE "DATABASE"
# -----------------------------

def init_state():
    if "users" not in st.session_state:
        st.session_state.users = {}  # id -> user dict
    if "claims" not in st.session_state:
        st.session_state.claims = {}  # id -> claim dict
    if "documents" not in st.session_state:
        st.session_state.documents = {}  # id -> doc dict
    if "notifications" not in st.session_state:
        st.session_state.notifications = {}  # id -> note dict
    if "current_user_id" not in st.session_state:
        st.session_state.current_user_id = None


def get_current_user():
    uid = st.session_state.current_user_id
    if uid and uid in st.session_state.users:
        return st.session_state.users[uid]
    return None


def add_notification(user_id: str, message: str):
    note_id = str(uuid.uuid4())
    st.session_state.notifications[note_id] = {
        "id": note_id,
        "user_id": user_id,
        "message": message,
        "created_at": datetime.utcnow(),
        "read": False,
    }


# -----------------------------
# GLOBAL STYLING + LOGO
# -----------------------------

def apply_theme():
    """
    Inject custom CSS for MedInsure branding:
    - Subtle gradient background
    - Blue sidebar
    - Card components
    - Simple square "M" logo
    """
    st.markdown(
        """
        <style>
        /* App background */
        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at top left, #E3F2FF 0, #F7FAFF 40%, #F5F7FB 100%);
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: #0B1F3B;
            color: #E5E7EB;
        }

        [data-testid="stSidebar"] * {
            color: #E5E7EB !important;
        }

        /* Logo header */
        .med-header {
            display: flex;
            align-items: center;
            gap: 0.9rem;
            margin-bottom: 1.4rem;
        }
        .med-logo-square {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            background: linear-gradient(135deg, #1456C4, #1F7AE0);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 800;
            font-size: 1.4rem;
            box-shadow: 0 10px 24px rgba(20, 86, 196, 0.45);
        }
        .med-title h1 {
            font-size: 1.6rem;
            margin: 0;
            color: #0B1F3B;
            letter-spacing: 0.03em;
        }
        .med-title p {
            margin: 0;
            color: #6B7280;
            font-size: 0.9rem;
        }

        /* Generic card */
        .med-card {
            background: #FFFFFFF0;
            border-radius: 18px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
            backdrop-filter: blur(6px);
            margin-bottom: 1.2rem;
        }

        .med-section-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #0B1F3B;
            margin-bottom: 0.6rem;
        }

        /* Metrics */
        div[data-testid="stMetricValue"] {
            color: #0B1F3B;
        }

        /* Tables */
        .med-card table {
            border-radius: 10px;
            overflow: hidden;
        }

        /* Reduce padding at very top */
        .block-container {
            padding-top: 1.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Top header with logo
    st.markdown(
        """
        <div class="med-header">
            <div class="med-logo-square">M</div>
            <div class="med-title">
                <h1>MedInsure</h1>
                <p>Clear, connected health insurance management.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# AUTH SCREENS
# -----------------------------

def register_screen():
    st.markdown('<div class="med-card">', unsafe_allow_html=True)
    st.markdown('<div class="med-section-title">Create a MedInsure Account</div>', unsafe_allow_html=True)

    name = st.text_input("Full name")
    email = st.text_input("Email")
    role_label = st.selectbox(
        "Role",
        [Role.PATIENT.value, Role.CLINIC_ADMIN.value,
         Role.CLINIC_BILLING.value, Role.INSURER_ADJUSTER.value,
         Role.INSURER_STAFF.value],
        index=0,
    )
    clinic_id = st.text_input("Clinic ID (if clinic staff)", value="")

    if st.button("Register"):
        if not name or not email:
            st.error("Name and email are required.")
        else:
            # unique email check
            for u in st.session_state.users.values():
                if u["email"].lower() == email.lower():
                    st.error("That email is already registered.")
                    break
            else:
                user_id = str(uuid.uuid4())
                user = {
                    "id": user_id,
                    "name": name,
                    "email": email,
                    "role": role_label,
                    "clinic_id": clinic_id or None,
                }
                st.session_state.users[user_id] = user
                st.session_state.current_user_id = user_id
                st.success(f"Welcome to MedInsure, {name}.")
                st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def login_screen():
    st.markdown('<div class="med-card">', unsafe_allow_html=True)
    st.markdown('<div class="med-section-title">Log in to MedInsure</div>', unsafe_allow_html=True)

    email = st.text_input("Email used at registration")

    if st.button("Log in"):
        for u in st.session_state.users.values():
            if u["email"].lower() == email.lower():
                st.session_state.current_user_id = u["id"]
                st.success(f"Logged in as {u['name']} ({u['role']}).")
                st.experimental_rerun()
                break
        else:
            st.error("No account found with that email. Try registering.")

    st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# PATIENT FLOWS
# -----------------------------

def patient_dashboard(user):
    st.markdown('<div class="med-card">', unsafe_allow_html=True)
    st.markdown('<div class="med-section-title">My Overview</div>', unsafe_allow_html=True)

    # Notifications
    st.markdown("**Notifications**")
    user_notes = [
        n for n in st.session_state.notifications.values()
        if n["user_id"] == user["id"]
    ]
    user_notes = sorted(user_notes, key=lambda x: x["created_at"], reverse=True)

    if not user_notes:
        st.info("No notifications yet.")
    else:
        for n in user_notes[:5]:
            st.write(f"• {n['message']}  (at {n['created_at'].strftime('%Y-%m-%d %H:%M')})")

    st.markdown("---")

    # Claim summary
    st.markdown("**Claim Summary**")

    my_claims = [
        c for c in st.session_state.claims.values()
        if c["patient_id"] == user["id"]
    ]
    if not my_claims:
        st.info("You don't have any claims yet. Create one from 'New Claim' in the sidebar.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    submitted = sum(1 for c in my_claims if c["status"] == ClaimStatus.SUBMITTED.value)
    in_review = sum(1 for c in my_claims if c["status"] == ClaimStatus.IN_REVIEW.value)
    approved = sum(1 for c in my_claims if c["status"] == ClaimStatus.APPROVED.value)
    denied = sum(1 for c in my_claims if c["status"] == ClaimStatus.DENIED.value)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Submitted", submitted)
    col2.metric("In Review", in_review)
    col3.metric("Approved", approved)
    col4.metric("Denied", denied)

    st.markdown("### Recent Claims")
    for c in sorted(my_claims, key=lambda x: x["created_at"], reverse=True)[:5]:
        with st.expander(f"Claim {c['id'][-6:]} • {c['status']} • ${c['amount']:.2f}"):
            st.write(f"**Service Date:** {c['service_date'].strftime('%Y-%m-%d')}")
            st.write(f"**Description:** {c['description']}")
            if c.get("decision_reason"):
                st.write(f"**Decision Reason:** {c['decision_reason']}")
            docs = [
                d for d in st.session_state.documents.values()
                if d["claim_id"] == c["id"]
            ]
            if docs:
                st.write("**Documents:**")
                for d in docs:
                    st.write(f"- {d['filename']} ({d['doc_type']})")

    st.markdown('</div>', unsafe_allow_html=True)


def new_claim_screen(user):
    st.markdown('<div class="med-card">', unsafe_allow_html=True)
    st.markdown('<div class="med-section-title">Submit a New Claim</div>', unsafe_allow_html=True)

    clinic_id = st.text_input("Clinic ID (optional)")
    description = st.text_area("Describe the visit or service")
    amount = st.number_input("Claim amount (USD)", min_value=0.0, value=0.0, step=10.0)
    service_date = st.date_input("Service date", value=date.today())
    uploaded_files = st.file_uploader(
        "Upload supporting documents (PDF, images, etc.)",
        accept_multiple_files=True,
    )

    if st.button("Submit Claim"):
        if amount <= 0 or not description:
            st.error("Please enter a description and a positive amount.")
        else:
            claim_id = str(uuid.uuid4())
            claim = {
                "id": claim_id,
                "patient_id": user["id"],
                "clinic_id": clinic_id or None,
                "description": description,
                "amount": amount,
                "service_date": service_date,
                "created_at": datetime.utcnow(),
                "status": ClaimStatus.SUBMITTED.value,
                "decision_reason": None,
            }
            st.session_state.claims[claim_id] = claim

            for f in uploaded_files or []:
                doc_id = str(uuid.uuid4())
                st.session_state.documents[doc_id] = {
                    "id": doc_id,
                    "claim_id": claim_id,
                    "uploaded_by": user["id"],
                    "filename": f.name,
                    "doc_type": "attachment",
                    "uploaded_at": datetime.utcnow(),
                }

            add_notification(
                user_id=user["id"],
                message=f"Your claim {claim_id[-6:]} was submitted successfully."
            )
            st.success("Claim submitted. You can track its status under 'My Claims'.")

    st.markdown('</div>', unsafe_allow_html=True)


def my_claims_screen(user):
    st.markdown('<div class="med-card">', unsafe_allow_html=True)
    st.markdown('<div class="med-section-title">My Claims</div>', unsafe_allow_html=True)

    my_claims = [
        c for c in st.session_state.claims.values()
        if c["patient_id"] == user["id"]
    ]
    if not my_claims:
        st.info("You have no claims yet.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    st.table([
        {
            "ID": c["id"][-6:],
            "Service Date": c["service_date"].strftime("%Y-%m-%d"),
            "Amount": f"${c['amount']:.2f}",
            "Status": c["status"],
        }
        for c in sorted(my_claims, key=lambda x: x["created_at"], reverse=True)
    ])

    st.markdown("---")
    st.markdown("### Claim Details")

    claim_options = {f"{c['id'][-6:]} • {c['status']}": c["id"] for c in my_claims}
    label = st.selectbox("Select a claim to inspect", list(claim_options.keys()))
    selected_id = claim_options[label]
    c = st.session_state.claims[selected_id]

    st.write(f"**Claim ID:** {c['id']}")
    st.write(f"**Status:** {c['status']}")
    st.write(f"**Amount:** ${c['amount']:.2f}")
    st.write(f"**Service Date:** {c['service_date'].strftime('%Y-%m-%d')}")
    st.write(f"**Description:** {c['description']}")
    if c.get("decision_reason"):
        st.write(f"**Decision Reason:** {c['decision_reason']}")

    docs = [
        d for d in st.session_state.documents.values()
        if d["claim_id"] == c["id"]
    ]
    if docs:
        st.write("**Documents:**")
        for d in docs:
            st.write(f"- {d['filename']} ({d['doc_type']})")

    st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# CLINIC / INSURER VIEWS
# -----------------------------

def clinic_dashboard_screen(user):
    st.markdown('<div class="med-card">', unsafe_allow_html=True)
    st.markdown('<div class="med-section-title">Clinic Dashboard</div>', unsafe_allow_html=True)

    clinic_id = user.get("clinic_id")
    if not clinic_id:
        st.info("No clinic ID associated with this account.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    clinic_claims = [
        c for c in st.session_state.claims.values()
        if c["clinic_id"] == clinic_id
    ]
    if not clinic_claims:
        st.info("No claims submitted for this clinic yet.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    total_amount = sum(c["amount"] for c in clinic_claims)
    c1, c2 = st.columns(2)
    c1.metric("Total Claims", len(clinic_claims))
    c2.metric("Total Billed Amount", f"${total_amount:,.2f}")

    st.markdown("### Claims by Status")
    for status in ClaimStatus:
        count = sum(1 for c in clinic_claims if c["status"] == status.value)
        st.write(f"- {status.value}: {count}")

    st.markdown('</div>', unsafe_allow_html=True)


def insurer_review_screen(user):
    st.markdown('<div class="med-card">', unsafe_allow_html=True)
    st.markdown('<div class="med-section-title">Insurer Claim Review</div>', unsafe_allow_html=True)

    all_claims = list(st.session_state.claims.values())
    if not all_claims:
        st.info("No claims submitted yet.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    claim_options = {
        f"{c['id'][-6:]} • {c['status']} • ${c['amount']:.2f}": c["id"]
        for c in sorted(all_claims, key=lambda x: x["created_at"], reverse=True)
    }
    label = st.selectbox("Select a claim to review", list(claim_options.keys()))
    cid = claim_options[label]
    c = st.session_state.claims[cid]

    st.write(f"**Claim ID:** {c['id']}")
    st.write(f"**Patient ID:** {c['patient_id']}")
    st.write(f"**Clinic ID:** {c['clinic_id']}")
    st.write(f"**Amount:** ${c['amount']:.2f}")
    st.write(f"**Description:** {c['description']}")
    st.write(f"**Current Status:** {c['status']}")

    status = st.selectbox(
        "Update status",
        [s.value for s in ClaimStatus],
        index=[s.value for s in ClaimStatus].index(c["status"]),
    )
    reason = st.text_area("Decision notes (visible to patient)", value=c.get("decision_reason") or "")

    if st.button("Save Decision"):
        c["status"] = status
        c["decision_reason"] = reason or None
        st.session_state.claims[cid] = c

        add_notification(
            user_id=c["patient_id"],
            message=f"Your claim {c['id'][-6:]} status was updated to '{status}'."
        )
        st.success("Decision saved and patient notified.")

    st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# MAIN APP
# -----------------------------

def main():
    st.set_page_config(page_title="MedInsure", page_icon="M", layout="wide")
    init_state()
    apply_theme()

    st.sidebar.title("MedInsure")

    user = get_current_user()
    if not user:
        choice = st.sidebar.radio("Start", ["Log In", "Register"])
        if choice == "Log In":
            login_screen()
        else:
            register_screen()
        st.markdown('<div class="med-card">', unsafe_allow_html=True)
        st.write(
            "MedInsure provides a simple way for patients, clinics, and insurers "
            "to submit, review, and track health insurance claims."
        )
        st.write("Use the sidebar to log in or create your first account.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Logged-in sidebar
    st.sidebar.markdown(f"**Signed in as:** {user['name']}")
    st.sidebar.caption(user["role"])

    if st.sidebar.button("Log out"):
        st.session_state.current_user_id = None
        st.experimental_rerun()

    # Navigation based on role
    if user["role"] == Role.PATIENT.value:
        page = st.sidebar.radio(
            "Navigation",
            ["Dashboard", "New Claim", "My Claims"],
        )
        if page == "Dashboard":
            patient_dashboard(user)
        elif page == "New Claim":
            new_claim_screen(user)
        elif page == "My Claims":
            my_claims_screen(user)

    elif user["role"] in (Role.CLINIC_ADMIN.value, Role.CLINIC_BILLING.value):
        st.sidebar.radio("Navigation", ["Clinic Dashboard"], index=0)
        clinic_dashboard_screen(user)

    elif user["role"] in (Role.INSURER_ADJUSTER.value, Role.INSURER_STAFF.value):
        st.sidebar.radio("Navigation", ["Review Claims"], index=0)
        insurer_review_screen(user)

    else:
        st.write("Unknown role.")


if __name__ == "__main__":
    main()
