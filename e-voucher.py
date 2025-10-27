import re
import json
import streamlit as st

st.title("JSON Data Converter 🧠")

# Initialize session state variables if they don't exist
if 'evoucher_output' not in st.session_state:
    st.session_state.evoucher_output = None
if 'phone_output' not in st.session_state:
    st.session_state.phone_output = None

# Create two columns for inputs
col1, col2 = st.columns(2)

with col1:
    st.subheader("E-Voucher Data")
    raw_data = st.text_area("Paste your raw data here:")

    if st.button("Convert E-Voucher"):
        try:
            order_id = re.search(r'"order-id":"([^"]+)"', raw_data)
            date = re.search(r'"date":"([^"]+)"', raw_data)
            pin_code = re.search(r'"pin-code":"([^"]+)"', raw_data)

            st.session_state.evoucher_output = {
                "DATE": date.group(1) if date else None,
                "CODE": pin_code.group(1) if pin_code else None,
                "ORDER_ID": order_id.group(1) if order_id else None
            }
            st.success("✅ E-Voucher Conversion Successful!")

        except Exception as e:
            st.error(f"❌ Error parsing data: {e}")
    
    # Display E-Voucher output if it exists
    if st.session_state.evoucher_output:
        st.json(st.session_state.evoucher_output)

with col2:
    st.subheader("Phone Number Format")
    phone_number = st.text_input("Enter phone number (starting with 00):")

    if st.button("Format Phone Number"):
        try:
            if phone_number.startswith("00"):
                formatted_number = phone_number[2:]  # Remove the first two zeros
                st.session_state.phone_output = {
                    "subscriberId": formatted_number,
                    "phone": formatted_number,
                    "whatsappNumber": formatted_number
                }
                st.success("✅ Phone Number Formatting Successful!")
            else:
                st.error("❌ Phone number must start with '00'")

        except Exception as e:
            st.error(f"❌ Error formatting phone number: {e}")
    
    # Display Phone output if it exists
    if st.session_state.phone_output:
        st.json(st.session_state.phone_output)
