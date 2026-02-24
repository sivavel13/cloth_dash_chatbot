from question_matcher import match_question
from difflib import get_close_matches
from typing import Optional
import pandas as pd


# -------------------------
# Load dataset
# -------------------------
df = pd.read_csv("D:\\Data Analysis\\Clothing Sales Transactions Dataset\\sales-dashboard\\data\\Clothing Sales Data_UTF.csv")

df["saleDate"] = pd.to_datetime(df["saleDate"], dayfirst=True)

df["month"] = df["saleDate"].dt.month_name()

# Ensure numeric column
df["totalAmount"] = pd.to_numeric(df["totalAmount"], errors="coerce")


# --------------------------------------------------
# GLOBAL INTENT DETECTION
# --------------------------------------------------
def detect_global_intent(text: str) -> str:
    text = text.lower()
    global_intent = ""
    intent_type = "glob"
    if any(word in text for word in ["hi", "hello", "hey"]):
        global_intent = "greeting"
        return global_intent, intent_type

    if any(word in text for word in ["thank", "thanks", "thank you"]):
        global_intent = "thanks"
        return global_intent, intent_type

    if any(word in text for word in ["bye", "exit", "quit", "see you later", "goodbye"]):
        global_intent = "goodbye"
        return global_intent, intent_type

    if any(word in text for word in ["help", "support", "what can you do"]):
        global_intent = "help"
        return global_intent, intent_type
    
    return "", "dash"


def process_glob_intent(intent):

    if intent == "greeting":
        return "👋 Hi! I’m your sales dashboard assistant. Ask me about sales, products, or categories."

    if intent == "thanks":
        return "😊 You’re welcome! Happy to help."

    if intent == "goodbye":
        return "👋 Goodbye! Come back anytime."

    if intent == "help":
        return (
            "ℹ️ I can help you with:\n"
            "- Sales summary\n"
            "- Top products\n"
            "- Category performance\n"
            "- Monthly analysis\n\n"
            "Try asking: *Top selling product in June*"
        )


# --------------------------------------------------
# ENTITY EXTRACTION
# --------------------------------------------------
def extract_entity(text: str):
    text = text.lower()
    months = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]
    for month in months:
        if month in text:
            return {
                "type": "month", "value": month
                }
    categories = ["men", "women", "kids", "accessories"]
    for cat in categories:
        if cat in text:
            return {"type": "category", "value": cat}

    return None

# --------------------------------------------------
# QUESTION MATCHING (PDF QUESTIONS)
# --------------------------------------------------

def match_question(user_message: str, allowed_questions: list):
    matches = get_close_matches(
        user_message,
        allowed_questions,
        n=1,
        cutoff=0.6
    )
    return matches[0] if matches else None

# --------------------------------------------------
# DASHBOARD INTENT DETECTION
# --------------------------------------------------

def dashboard_intent(text: str) -> str:
    if "total sales" in text or "overall sales" in text:
        return "total_sales"

    if "top" in text and "product" in text:
        return "top_product"

    if "category" in text:
        return "category_sales"

    if "month" in text or any(
        m in text for m in [
            "january","february","march","april","may","june",
            "july","august","september","october","november","december"
        ]
    ):
        return "monthly_sales"
    


def extract_entity(text: str) -> Optional[dict]:
    text = text.lower()

    months = [
        "january","february","march","april","may","june",
        "july","august","september","october","november","december"
    ]

    for month in months:
        if month in text:
            return {"type": "month", "value": month}

    categories = df["productCategory"].dropna().unique()
    for cat in categories:
        if cat.lower() in text:
            return {"type": "category", "value": cat}

    return None


def process_intent(intent: str, entity: Optional[dict]):

    # -----------------------
    # TOTAL SALES
    # -----------------------
    if intent == "total_sales":
        total_sales = df["totalAmount"].sum()
        return f"📊 **Total Sales:** ₹{total_sales:,.2f}"

    # -----------------------
    # TOP PRODUCT
    # -----------------------
    if intent == "top_product":
        top_product = (
            df.groupby("productName")["totalAmount"]
            .sum()
            .sort_values(ascending=False)
            .head(1)
        )

        name = top_product.index[0]
        value = top_product.iloc[0]

        return f"🏆 **Top Selling Product:** {name} (₹{value:,.2f})"

    # -----------------------
    # CATEGORY SALES
    # -----------------------
    if intent == "category_sales" and entity:
        category = entity["value"]
        total = df[df["productCategory"] == category]["totalAmount"].sum()

        return f"📦 **Total Sales for {category}:** ₹{total:,.2f}"

    # -----------------------
    # MONTHLY SALES
    # -----------------------
    if intent == "monthly_sales" and entity:
        month = entity["value"]

        df["orderMonth"] = pd.to_datetime(
            df["orderDate"], dayfirst=True, errors="coerce" 
        ).dt.month_name().str.lower()

        total = df[df["orderMonth"] == month]["totalAmount"].sum()

        return f"📅 **Sales in {month.title()}:** ₹{total:,.2f}"

    return "❌ Sorry, I couldn’t find data for that."


# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------

def chatbot_pipeline(user_message: str, allowed_questions: list):

    """
    Chatbot flow:
    1. Detect intent
    2. Handle global intents
    3. Validate dashboard queries via PDF
    4. Extract entity
    5. Respond
    """

    # STEP 1: Detect Global Intent FIRST
    intent = detect_global_intent(user_message)

    # STEP 2: Global Intents (No PDF needed)
    if intent[1] == "glob":
        print("Global Intent")
        return process_glob_intent(intent[0])

    # STEP 3: Dashboard questions must match PDF
    matched_question = match_question(user_message, allowed_questions)
    print(matched_question)
    if not matched_question:
        return (
            "❌ I can answer only dashboard-related questions.\n"
            "Try asking about sales, products, categories, or months."
        )

    # STEP 4: Process dashboard intent
    dash_intent = dashboard_intent(user_message)
    print(dash_intent)

    # STEP 5: Extract entity
    entity = extract_entity(user_message)
    print(entity)

    # STEP 6: Generate response
    return process_intent(dash_intent, entity)
