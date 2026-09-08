
import streamlit as st
import joblib
import re

# -----------------------------------
# Page Configuration
# -----------------------------------

st.set_page_config(
    page_title="Spam & Email Filtering",
    page_icon="📧",
    layout="centered"
)

# -----------------------------------
# Load Model
# -----------------------------------

@st.cache_resource
def load_model():
    return joblib.load("spam_email_model.pkl")


model = load_model()

# -----------------------------------
# Promotional / Spam Keywords
# -----------------------------------

SPAM_KEYWORDS = [
    "free",
    "winner",
    "won",
    "prize",
    "cash",
    "reward",
    "discount",
    "offer",
    "limited time",
    "buy now",
    "click here",
    "claim now",
    "urgent",
    "congratulations",
    "lottery",
    "promotion",
    "promotional",
    "subscribe now",
    "exclusive deal",
    "earn money",
    "get rich",
    "bonus",
    "coupon",
    "special offer"
]


def find_spam_keywords(text):
    text = text.lower()

    detected = []

    for keyword in SPAM_KEYWORDS:
        if keyword in text:
            detected.append(keyword)

    return detected


# -----------------------------------
# Title
# -----------------------------------

st.title("📧 Spam & Email Filtering System")

st.write(
    """
    This application analyzes an email using **Machine Learning**
    and simple **email-agent reasoning rules** to decide whether
    the email should be sent to the **Inbox** or **Spam/Junk** folder.
    """
)

st.divider()

# -----------------------------------
# Sender Information
# -----------------------------------

st.subheader("👤 Sender Information")

sender_email = st.text_input(
    "Sender Email Address",
    placeholder="example@gmail.com"
)

sender_status = st.radio(
    "Do you know this sender?",
    ["Known Sender", "Unknown Sender"],
    horizontal=True
)

# -----------------------------------
# Email Content
# -----------------------------------

st.subheader("✉️ Email Content")

email_text = st.text_area(
    "Enter the email message",
    height=250,
    placeholder="""
Example:

Congratulations!
You have won a FREE cash prize.
Click here now to claim your reward.
"""
)

# -----------------------------------
# Prediction
# -----------------------------------

if st.button("🔍 Analyze Email", use_container_width=True):

    if email_text.strip() == "":
        st.warning("⚠️ Please enter an email message.")

    else:

        # -------------------------------
        # Machine Learning Prediction
        # -------------------------------

        prediction = model.predict([email_text])[0]

        probabilities = model.predict_proba([email_text])[0]

        normal_probability = probabilities[0]
        spam_probability = probabilities[1]

        # -------------------------------
        # Rule-Based Analysis
        # -------------------------------

        detected_keywords = find_spam_keywords(email_text)

        reasons = []

        rule_score = 0

        # Unknown sender rule
        if sender_status == "Unknown Sender":
            rule_score += 1
            reasons.append("Email is from an unknown sender.")

        # Promotional keyword rules
        if len(detected_keywords) > 0:
            reasons.append(
                "Promotional/suspicious keywords detected: "
                + ", ".join(detected_keywords)
            )

        if len(detected_keywords) >= 2:
            rule_score += 1

        if len(detected_keywords) >= 4:
            rule_score += 1

        # Excessive links
        links = re.findall(
            r'https?://\S+|www\.\S+',
            email_text
        )

        if len(links) >= 2:
            rule_score += 1
            reasons.append(
                "Multiple links detected in the email."
            )

        # Excessive exclamation marks
        if email_text.count("!") >= 4:
            rule_score += 1
            reasons.append(
                "Email contains excessive exclamation marks."
            )

        # -------------------------------
        # Final Agent Decision
        # -------------------------------

        if prediction == 1:
            final_prediction = "SPAM"

        elif rule_score >= 2:
            final_prediction = "SPAM"

        else:
            final_prediction = "NORMAL"

        # -------------------------------
        # Display Results
        # -------------------------------

        st.divider()

        st.subheader("📊 Analysis Result")

        if final_prediction == "SPAM":

            st.error(
                "🚨 SPAM / JUNK EMAIL"
            )

            st.write(
                "This email should be routed to the **Spam/Junk folder**."
            )

        else:

            st.success(
                "✅ NORMAL / SAFE EMAIL"
            )

            st.write(
                "This email can be routed to the **Inbox**."
            )

        # -------------------------------
        # Probability
        # -------------------------------

        st.subheader("🤖 Machine Learning Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Normal Probability",
                f"{normal_probability * 100:.2f}%"
            )

        with col2:
            st.metric(
                "Spam Probability",
                f"{spam_probability * 100:.2f}%"
            )

        st.progress(float(spam_probability))

        # -------------------------------
        # Rule Analysis
        # -------------------------------

        st.subheader("🧠 Email Agent Reasoning")

        st.write(
            "**Sender Status:**",
            sender_status
        )

        if detected_keywords:

            st.write(
                "**Suspicious Keywords:**"
            )

            for keyword in detected_keywords:
                st.write("•", keyword)

        else:

            st.write(
                "No obvious promotional keywords detected."
            )

        # -------------------------------
        # Reasons
        # -------------------------------

        if reasons:

            st.subheader("⚠️ Reasons")

            for reason in reasons:
                st.write("•", reason)

        else:

            st.write(
                "✅ No major spam rules were triggered."
            )

        # -------------------------------
        # Final Routing
        # -------------------------------

        st.divider()

        st.subheader("📂 Email Routing")

        if final_prediction == "SPAM":
            st.error(
                "📧 ➜ 🗑️ Route to SPAM / JUNK"
            )
        else:
            st.success(
                "📧 ➜ 📥 Route to INBOX"
            )
