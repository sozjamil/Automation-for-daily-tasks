import re
import json
import streamlit as st
from streamlit.components.v1 import html

st.title("Text format Automating ")

# Initialize session state variables if they don't exist
if 'evoucher_output' not in st.session_state:
    st.session_state.evoucher_output = None
if 'phone_output' not in st.session_state:
    st.session_state.phone_output = None

# Create two columns for inputs
col1, col2 = st.columns(2)

with col1:
    # header and paste button on the same row
    col1_hdr, col1_btn = st.columns([9,1])
    with col1_hdr:
        st.subheader("E-Voucher Data")
    with col1_btn:
        # paste button runs inside an iframe so the click is a valid user gesture
        html('''
            <button id="paste_btn" style="height:34px; width:88px; cursor:pointer;">📋 Paste</button>
            <script>
              async function pasteToParent(){
                try {
                  const text = await navigator.clipboard.readText();
                  const ta = parent.document.querySelector('textarea[aria-label="Paste your raw data here:"]');
                  if(!ta) {
                    alert("Paste failed: textarea not found");
                    return;
                  }
                  ta.focus();
                  ta.value = text;
                  ta.dispatchEvent(new Event('input', { bubbles: true }));
                } catch(e) {
                  alert('Paste failed: ' + e);
                }
              }
              document.getElementById('paste_btn').addEventListener('click', pasteToParent);
            </script>
        ''', height=60)

    raw_data = st.text_area("Paste your raw data here:")

    if st.button("Convert E-Voucher"):
        try:
            # support multiple JSON/text lines: parse each non-empty line separately
            lines = [ln for ln in (raw_data or "").splitlines() if ln.strip()]
            blocks = []

            for line in lines:
                order_id = ''
                date = ''
                pin_code = ''

                # 1) try to parse as JSON (preferred)
                parsed = None
                try:
                    parsed = json.loads(line)
                except Exception:
                    parsed = None

                if parsed:
                    # order_id/date usually inside orderResponse
                    order_resp = parsed.get("orderResponse") or parsed.get("order_response") or {}
                    order_id = order_resp.get("order_id") or parsed.get("order_id") or ""
                    date = order_resp.get("date") or parsed.get("date") or ""
                    # pin_code usually under vouchers -> first item -> pin_code
                    vouchers = order_resp.get("vouchers") if isinstance(order_resp, dict) else None
                    if isinstance(vouchers, list) and vouchers:
                        pin_code = vouchers[0].get("pin_code") or vouchers[0].get("pin-code") or ""
                    pin_code = pin_code or parsed.get("pin_code") or parsed.get("pin-code") or ""
                else:
                    # 2) fallback to regex extraction from arbitrary text line
                    m_order = re.search(r'"order[_-]?id"\s*:\s*"([^"]+)"', line)
                    m_date = re.search(r'"date"\s*:\s*"([^"]+)"', line)
                    m_pin = re.search(r'"pin[_-]?code"\s*:\s*"([^"]+)"', line) or re.search(r'"pin_code"\s*:\s*"([^"]+)"', line)
                    if m_order:
                        order_id = m_order.group(1)
                    if m_date:
                        date = m_date.group(1)
                    if m_pin:
                        pin_code = m_pin.group(1)

                # Build the literal formatted JSON block (commas/newlines preserved)
                block = (
                    '{\n'
                    '  "DATE": "' + (date or '') + '",\n'
                    '  "CODE": "' + (pin_code or '') + '",\n'
                    '  "ORDER_ID": "' + (order_id or '') + '"\n'
                    '}'
                )
                blocks.append(block)

            if not blocks:
                st.error("No valid lines found to convert.")
            else:
                # join multiple blocks with a blank line between them
                ev_text = "\n\n".join(blocks)
                st.session_state.evoucher_output = ev_text
                st.success(f"✅ Converted {len(blocks)} item(s)")

        except Exception as e:
            st.error(f"❌ Error parsing data: {e}")
    
    # Display E-Voucher output if it exists (literal text with commas)
    if st.session_state.evoucher_output:
        ev_text = st.session_state.evoucher_output
        # render pre + copy button inside a component iframe so user click works reliably
        html(f'''
            <div style="display:flex; gap:8px; align-items:flex-start;">
              <div style="flex:1; overflow:auto; max-height:260px; border:1px solid #eee; padding:8px; background:#fafafa;">
                <pre id="ev_pre" style="white-space:pre-wrap; margin:0; font-family: monospace;"></pre>
              </div>
              <div style="width:96px; display:flex; align-items:flex-start;">
                <button id="copy_ev" style="height:36px; width:88px; cursor:pointer;">📋 Copy</button>
              </div>
            </div>
            <script>
              const text = {json.dumps(ev_text)};
              document.getElementById('ev_pre').innerText = text;
              document.getElementById('copy_ev').addEventListener('click', async function() {{
                try {{
                  await navigator.clipboard.writeText(text);
                  this.innerText = 'Copied';
                }} catch(e) {{
                  alert('Copy failed: ' + e);
                }}
              }});
            </script>
        ''', height=220)

with col2:
    # header and paste button on the same row for phone input
    col2_hdr, col2_btn = st.columns([9,1])
    with col2_hdr:
        st.subheader("Phone Number Format")
    with col2_btn:
        # paste button runs inside an iframe so the click is a valid user gesture
        html('''
            <button id="paste_phone_btn" style="height:34px; width:88px; cursor:pointer;">📋 Paste</button>
            <script>
              async function pastePhoneToParent(){
                try {
                  const text = await navigator.clipboard.readText();
                  const inp = parent.document.querySelector('input[aria-label="Enter phone number (with or without 00):"]');
                  if(!inp) {
                    alert("Paste failed: input not found");
                    return;
                  }
                  inp.focus();
                  inp.value = text;
                  inp.dispatchEvent(new Event('input', { bubbles: true }));
                } catch(e) {
                  alert('Paste failed: ' + e);
                }
              }
              document.getElementById('paste_phone_btn').addEventListener('click', pastePhoneToParent);
            </script>
        ''', height=60)

    phone_number = st.text_input("Enter phone number (with or without 00):")

    if st.button("Format Phone Number"):
        try:
            # 1) Trim outer spaces
            s = (phone_number or "").strip()
            # 2) Remove all internal whitespace (user might paste with spaces)
            digits = re.sub(r'\s+', '', s)
            # 3) Remove optional leading "00"
            if digits.startswith("00"):
                digits = digits[2:]
            # 4) Validate: must be exactly 13 digits
            if digits.isdigit() and len(digits) == 13:
                final_number = digits
                formatted_json = (
                    '{\n'
                    '  "subscriberId": "' + final_number + '",\n'
                    '  "phone": "' + final_number + '",\n'
                    '  "whatsappNumber": "' + final_number + '"\n'
                    '}'
                )
                st.session_state.phone_output = formatted_json
                st.success("✅ Phone Number Formatting Successful!")
            else:
                st.error("❌ Result must be exactly 13 digits after trimming spaces and removing optional leading '00'.")

        except Exception as e:
            st.error(f"❌ Error formatting phone number: {e}")
    
    # Display Phone output if it exists (literal text with commas)
    if st.session_state.phone_output:
        ph_text = st.session_state.phone_output
        html(f'''
            <div style="display:flex; gap:8px; align-items:flex-start;">
              <div style="flex:1; overflow:auto; max-height:160px; border:1px solid #eee; padding:8px; background:#fafafa;">
                <pre id="ph_pre" style="white-space:pre-wrap; margin:0; font-family: monospace;"></pre>
              </div>
              <div style="width:96px; display:flex; align-items:flex-start;">
                <button id="copy_ph" style="height:36px; width:88px; cursor:pointer;">📋 Copy</button>
              </div>
            </div>
            <script>
              const text2 = {json.dumps(ph_text)};
              document.getElementById('ph_pre').innerText = text2;
              document.getElementById('copy_ph').addEventListener('click', async function() {{
                try {{
                  await navigator.clipboard.writeText(text2);
                  this.innerText = 'Copied';
                }} catch(e) {{
                  alert('Copy failed: ' + e);
                }}
              }});
            </script>
        ''', height=180)
