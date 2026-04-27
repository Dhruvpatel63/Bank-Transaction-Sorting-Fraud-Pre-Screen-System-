import streamlit as st
import pandas as pd
from datetime import date
import io

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Bank Transaction Fraud Pre-Screen",
    page_icon="🏦",
    layout="wide"
)

# ============================================================
# MERGE SORT IMPLEMENTATION
# This is the main algorithm used in this project.
# Merge Sort works by dividing the list into halves,
# sorting each half, and then merging them back together.
# Time Complexity: O(n log n)
# ============================================================

def merge(left, right, reverse=False):
    """
    This function merges two sorted lists into one sorted list.
    We compare elements from left and right lists one by one
    and add the smaller (or larger, if reverse=True) to the result.

    reverse=False → Ascending order (Low to High)
    reverse=True  → Descending order (High to Low)
    """
    result = []   # This will store the merged sorted list
    i = 0         # Pointer for left list
    j = 0         # Pointer for right list

    # Keep comparing elements from both lists until one runs out
    while i < len(left) and j < len(right):

        # Decide comparison based on sort order chosen by user
        if reverse:
            # Descending: pick the LARGER element first
            condition = left[i]["Amount"] >= right[j]["Amount"]
        else:
            # Ascending: pick the SMALLER element first
            condition = left[i]["Amount"] <= right[j]["Amount"]

        if condition:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # If left list still has remaining elements, add them all
    while i < len(left):
        result.append(left[i])
        i += 1

    # If right list still has remaining elements, add them all
    while j < len(right):
        result.append(right[j])
        j += 1

    return result  # Return the fully merged and sorted list


def merge_sort(transactions, reverse=False):
    """
    This is the main Merge Sort function.
    It splits the list into two halves recursively,
    sorts each half, and merges them using the merge() function.

    Base case: if list has 1 or 0 elements, it is already sorted.

    reverse=False → Sort Low to High (Ascending)
    reverse=True  → Sort High to Low (Descending)
    """
    # Base case: a list with 0 or 1 elements is already sorted
    if len(transactions) <= 1:
        return transactions

    # Find the middle index to divide the list into two halves
    mid = len(transactions) // 2

    # Recursively sort the left half
    left_half = merge_sort(transactions[:mid], reverse)

    # Recursively sort the right half
    right_half = merge_sort(transactions[mid:], reverse)

    # Merge both sorted halves and return the final sorted list
    return merge(left_half, right_half, reverse)


# ============================================================
# FRAUD PRE-SCREEN LOGIC
# Simple rules to flag suspicious transactions.
# Returns list of transactions with "Fraud Status" and "Reason".
# ============================================================

def check_fraud(transactions):
    """
    Checks each transaction against three simple fraud rules:
    Rule 1: Amount > 100,000
    Rule 2: Same user has more than 3 transactions
    Rule 3: Same user made multiple transactions on the same date
    """

    # --- Count total transactions per user ---
    user_count = {}
    for t in transactions:
        name = t["User Name"]
        if name in user_count:
            user_count[name] += 1
        else:
            user_count[name] = 1

    # --- Count transactions per user per date ---
    user_date_count = {}
    for t in transactions:
        key = t["User Name"] + "_" + str(t["Date"])
        if key in user_date_count:
            user_date_count[key] += 1
        else:
            user_date_count[key] = 1

    # --- Label each transaction as Normal or Suspicious ---
    result = []
    for t in transactions:
        status  = "Normal"   # Start by assuming it is normal
        reasons = []         # Collect all reasons for suspicion

        # Rule 1: Very high amount
        if t["Amount"] > 100000:
            status = "Suspicious"
            reasons.append("Amount > ₹1,00,000")

        # Rule 2: Same user has too many transactions
        if user_count[t["User Name"]] > 3:
            status = "Suspicious"
            reasons.append("User has >3 transactions")

        # Rule 3: Same user, same date, multiple transactions
        key = t["User Name"] + "_" + str(t["Date"])
        if user_date_count[key] > 1:
            status = "Suspicious"
            reasons.append("Multiple txns on same date")

        # Build a copy of transaction with status and reason fields added
        t_copy = dict(t)
        t_copy["Fraud Status"] = status
        t_copy["Reason"]       = ", ".join(reasons) if reasons else "—"
        result.append(t_copy)

    return result


# ============================================================
# HELPER: Convert DataFrame to CSV bytes for download button
# ============================================================

def convert_df_to_csv(df):
    """
    Converts a pandas DataFrame to CSV format held in memory.
    io.StringIO is used to write it as a string buffer,
    then encoded to bytes so Streamlit can serve it as a download.
    """
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


# ============================================================
# STREAMLIT UI STARTS HERE
# ============================================================

st.title("🏦 Bank Transaction Sorting & Fraud Pre-Screen System")
st.write("---")

# Short explanation about the algorithm
st.info(
    "📌 **Algorithm Used: Merge Sort** — "
    "Merge Sort is used because it is efficient with O(n log n) time complexity. "
    "It works by dividing the list into halves, sorting each half recursively, "
    "and merging them back in sorted order. This makes it much faster than simple "
    "sorting methods like Bubble Sort (O(n²)) for large transaction data."
)

st.write("---")

# ============================================================
# SESSION STATE INITIALIZATION
# Streamlit re-runs the whole script on every button click.
# We use session_state to remember data across those reruns.
#
# Variables stored:
#   transactions → list of all added transaction dictionaries
#   form_key     → counter used to reset input fields after adding
# ============================================================
if "transactions" not in st.session_state:
    st.session_state.transactions = []

if "form_key" not in st.session_state:
    st.session_state.form_key = 0


# ============================================================
# SECTION 1: ADD TRANSACTION FORM
#
# form_key trick:
#   Each widget gets a key like f"txn_id_{form_key}".
#   When form_key is incremented, Streamlit sees a brand-new
#   widget and renders it with its default (empty) value.
#   This is how we "reset" the form after adding a transaction.
# ============================================================
st.subheader("➕ Add a Transaction")

fk = st.session_state.form_key   # Shortcut to current form key

col1, col2, col3 = st.columns(3)

with col1:
    txn_id    = st.text_input("Transaction ID",  placeholder="e.g. TXN001",      key=f"txn_id_{fk}")
    user_name = st.text_input("User Name",       placeholder="e.g. Rahul Sharma", key=f"user_name_{fk}")

with col2:
    amount   = st.number_input("Amount (₹)", min_value=0.0, step=100.0,          key=f"amount_{fk}")
    txn_type = st.selectbox("Transaction Type", ["Credit", "Debit"],             key=f"txn_type_{fk}")

with col3:
    txn_date = st.date_input("Date", value=date.today(),                         key=f"txn_date_{fk}")

# --- Add Transaction Button ---
if st.button("➕ Add Transaction"):

    # Validation 1: Required fields must not be empty
    if txn_id.strip() == "" or user_name.strip() == "":
        st.warning("⚠️ Please fill in Transaction ID and User Name.")

    # Validation 2: Duplicate Transaction ID check
    # NEW FEATURE — loops through existing transactions to check if ID is already used
    elif any(t["Transaction ID"] == txn_id.strip() for t in st.session_state.transactions):
        st.error(f"❌ Transaction ID '{txn_id.strip()}' already exists! Please use a unique ID.")

    else:
        # Build the transaction dictionary and add to list
        new_txn = {
            "Transaction ID": txn_id.strip(),
            "User Name":      user_name.strip(),
            "Amount":         amount,
            "Type":           txn_type,
            "Date":           txn_date
        }
        st.session_state.transactions.append(new_txn)

        # Increment form_key to reset all form widgets to blank
        st.session_state.form_key += 1

        st.success(f"✅ Transaction '{txn_id.strip()}' added! Form cleared for next entry.")
        st.rerun()

st.write("---")

# ============================================================
# SECTION 2: SHOW CURRENT TRANSACTIONS (Before Sorting)
# ============================================================
if len(st.session_state.transactions) > 0:

    st.subheader(f"📋 Transactions Added — Before Sorting  ({len(st.session_state.transactions)} total)")

    before_df = pd.DataFrame(st.session_state.transactions)
    st.dataframe(before_df, use_container_width=True)

    # ----------------------------------------------------------
    # NEW FEATURE: Delete Individual Transaction
    # A selectbox lets the user pick one Transaction ID to remove.
    # Only that specific row is deleted; the rest are kept.
    # ----------------------------------------------------------
    st.write("**Remove a transaction:**")

    all_ids     = [t["Transaction ID"] for t in st.session_state.transactions]
    selected_id = st.selectbox("Select Transaction ID to delete", all_ids, key="delete_select")

    col_del1, col_del2 = st.columns([1, 4])

    with col_del1:
        if st.button("🗑️ Delete Selected"):
            # Filter out only the selected transaction
            st.session_state.transactions = [
                t for t in st.session_state.transactions
                if t["Transaction ID"] != selected_id
            ]
            st.success(f"✅ Transaction '{selected_id}' removed.")
            st.rerun()

    with col_del2:
        if st.button("🗑️ Clear ALL Transactions"):
            st.session_state.transactions = []
            st.rerun()

    st.write("---")

    # ============================================================
    # SECTION 3: PROCESS TRANSACTIONS
    # Sort Order Toggle + Merge Sort + Fraud Check + CSV Export
    # ============================================================
    st.subheader("⚙️ Process Transactions")

    # NEW FEATURE: Sort Order Toggle
    # Simple radio button — user picks ascending or descending.
    # The choice is passed into merge_sort() as the reverse flag.
    sort_order = st.radio(
        "Sort Order (by Amount):",
        ["⬆️ Low to High (Ascending)", "⬇️ High to Low (Descending)"],
        horizontal=True,
        key="sort_order"
    )

    if st.button("⚙️ Process Transactions"):

        if len(st.session_state.transactions) < 2:
            st.warning("⚠️ Please add at least 2 transactions to sort.")

        else:
            # Step 1: Copy the list so we don't modify session_state directly
            txn_list = list(st.session_state.transactions)

            # Step 2: Decide sort direction from radio button
            is_descending = sort_order.startswith("⬇️")

            # Step 3: Run Merge Sort on transactions sorted by Amount
            sorted_txns = merge_sort(txn_list, reverse=is_descending)

            # Step 4: Run fraud pre-screening on the sorted result
            final_result = check_fraud(sorted_txns)

            # Convert to DataFrame for display and export
            result_df = pd.DataFrame(final_result)

            # ---- SORTED + FRAUD STATUS TABLE ----
            order_label = "Descending ⬇️" if is_descending else "Ascending ⬆️"
            st.subheader(f"📊 After Sorting by Amount ({order_label}) + Fraud Status")

            # Apply color highlights to the Fraud Status column
            def highlight_fraud(val):
                if val == "Suspicious":
                    return "background-color: #ffcccc; color: #cc0000; font-weight: bold"
                elif val == "Normal":
                    return "background-color: #ccffcc; color: #007700; font-weight: bold"
                return ""

            styled_df = result_df.style.applymap(highlight_fraud, subset=["Fraud Status"])
            st.dataframe(styled_df, use_container_width=True)

            # ---- SUMMARY METRICS ----
            st.write("---")
            st.subheader("🔍 Summary")

            total            = len(final_result)
            suspicious_count = sum(1 for t in final_result if t["Fraud Status"] == "Suspicious")
            normal_count     = total - suspicious_count

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("📦 Total Transactions", total)
            col_b.metric("🟢 Normal",             normal_count)
            col_c.metric("🔴 Suspicious",         suspicious_count)

            # ---- NEW FEATURE: EXPORT TO CSV ----
            # st.download_button streams a file directly to the user's browser.
            # convert_df_to_csv() converts the DataFrame to bytes using io.StringIO.
            st.write("---")
            st.subheader("📥 Export Results")

            csv_bytes = convert_df_to_csv(result_df)

            st.download_button(
                label="📥 Download Results as CSV",
                data=csv_bytes,
                file_name="transaction_fraud_report.csv",
                mime="text/csv"
            )

            st.caption("The CSV file includes all transactions with their sort order, fraud status, and reason.")

            # ---- FRAUD RULES REMINDER ----
            st.write("---")
            st.subheader("📌 Fraud Detection Rules Used")
            st.write("A transaction is marked **🔴 Suspicious** if ANY of these rules match:")
            st.write("- 💰 Amount is **greater than ₹1,00,000**")
            st.write("- 👤 Same user has **more than 3 transactions** in the list")
            st.write("- 📅 Same user made **multiple transactions on the same date**")

else:
    st.write("👆 Please add at least one transaction using the form above.")

# ============================================================
# FOOTER
# ============================================================
st.write("---")
st.caption("🎓 College Project | Algorithm: Merge Sort O(n log n) | Made with Streamlit")
