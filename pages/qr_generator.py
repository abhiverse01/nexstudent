# qr_generator.py — QR code generator with styling options and download
import html
import io
import streamlit as st
from PIL import Image

from config import inject_css
from state import init_state
from components import page_header, badge, empty_state


CONTENT_TYPES = ["URL", "Plain Text", "Email", "Phone", "WiFi", "vCard"]


def _build_qr_content(ctype: str, fields: dict) -> str:
    """Build the string to encode in the QR code based on content type."""
    if ctype == "URL":
        return fields.get("url", "").strip()
    elif ctype == "Plain Text":
        return fields.get("text", "").strip()
    elif ctype == "Email":
        email = fields.get("email", "").strip()
        subject = fields.get("subject", "").strip()
        body = fields.get("body", "").strip()
        mailto = f"mailto:{email}"
        params = []
        if subject:
            params.append(f"subject={subject}")
        if body:
            params.append(f"body={body}")
        if params:
            mailto += "?" + "&".join(params)
        return mailto
    elif ctype == "Phone":
        return f"tel:{fields.get('phone', '').strip()}"
    elif ctype == "WiFi":
        ssid = fields.get("ssid", "").strip()
        password = fields.get("wifi_pass", "").strip()
        encryption = fields.get("encryption", "WPA")
        return f"WIFI:T:{encryption};S:{ssid};P:{password};;"
    elif ctype == "vCard":
        name = fields.get("vname", "").strip()
        org = fields.get("vorg", "").strip()
        email = fields.get("vemail", "").strip()
        phone = fields.get("vphone", "").strip()
        lines = ["BEGIN:VCARD", "VERSION:3.0"]
        if name:
            lines.append(f"FN:{name}")
        if org:
            lines.append(f"ORG:{org}")
        if email:
            lines.append(f"EMAIL:{email}")
        if phone:
            lines.append(f"TEL:{phone}")
        lines.append("END:VCARD")
        return "\n".join(lines)
    return ""


def render():
    """Render the QR Code Generator page."""
    inject_css()
    init_state()

    page_header("QR Generator", "Create styled QR codes for any content type")

    col_left, col_right = st.columns([2, 3])

    # ═══════════════════════════════════════════════════════════════════════════
    # LEFT COLUMN — Input & options
    # ═══════════════════════════════════════════════════════════════════════════
    with col_left:
        st.markdown(
            '<div style="background:var(--card);border:1px solid var(--border);'
            'border-radius:var(--r);padding:1.1rem 1.2rem;">'
            '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
            'margin-bottom:.8rem;letter-spacing:.04em;text-transform:uppercase;">'
            '📱 Content</div></div>',
            unsafe_allow_html=True,
        )

        ctype = st.selectbox(
            "Content type",
            options=CONTENT_TYPES,
            label_visibility="collapsed",
            key="qr_ctype",
        )

        fields = {}

        if ctype == "URL":
            fields["url"] = st.text_input(
                "URL",
                placeholder="https://example.com",
                label_visibility="collapsed",
                key="qr_url",
            )
        elif ctype == "Plain Text":
            fields["text"] = st.text_area(
                "Text",
                placeholder="Enter text to encode…",
                height=100,
                label_visibility="collapsed",
                key="qr_text",
            )
        elif ctype == "Email":
            fields["email"] = st.text_input(
                "Email address",
                placeholder="user@example.com",
                label_visibility="collapsed",
                key="qr_email",
            )
            fields["subject"] = st.text_input(
                "Subject (optional)",
                placeholder="Email subject",
                label_visibility="collapsed",
                key="qr_subject",
            )
            fields["body"] = st.text_area(
                "Body (optional)",
                placeholder="Email body…",
                height=80,
                label_visibility="collapsed",
                key="qr_body",
            )
        elif ctype == "Phone":
            fields["phone"] = st.text_input(
                "Phone number",
                placeholder="+1 234 567 8900",
                label_visibility="collapsed",
                key="qr_phone",
            )
        elif ctype == "WiFi":
            fields["ssid"] = st.text_input(
                "Network name (SSID)",
                placeholder="MyWiFi",
                label_visibility="collapsed",
                key="qr_ssid",
            )
            fields["wifi_pass"] = st.text_input(
                "Password",
                placeholder="WiFi password",
                type="password",
                label_visibility="collapsed",
                key="qr_wifi_pass",
            )
            fields["encryption"] = st.selectbox(
                "Encryption",
                options=["WPA", "WEP", "nopass"],
                label_visibility="collapsed",
                key="qr_encryption",
            )
        elif ctype == "vCard":
            fields["vname"] = st.text_input(
                "Full name",
                placeholder="Jane Doe",
                label_visibility="collapsed",
                key="qr_vname",
            )
            fields["vorg"] = st.text_input(
                "Organization (optional)",
                placeholder="Acme Inc.",
                label_visibility="collapsed",
                key="qr_vorg",
            )
            fields["vemail"] = st.text_input(
                "Email (optional)",
                placeholder="jane@example.com",
                label_visibility="collapsed",
                key="qr_vemail",
            )
            fields["vphone"] = st.text_input(
                "Phone (optional)",
                placeholder="+1 234 567 8900",
                label_visibility="collapsed",
                key="qr_vphone",
            )

        st.markdown('<div style="margin:.8rem 0;"></div>', unsafe_allow_html=True)

        # Style options
        st.markdown(
            '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
            'margin-bottom:.6rem;letter-spacing:.04em;text-transform:uppercase;">'
            '🎨 Style Options</div>',
            unsafe_allow_html=True,
        )

        fg_col, bg_col = st.columns(2)
        with fg_col:
            fg_color = st.color_picker("Foreground", value="#000000", key="qr_fg")
        with bg_col:
            bg_color = st.color_picker("Background", value="#FFFFFF", key="qr_bg")

        size = st.slider("Size (px)", min_value=150, max_value=600, value=300, step=50, key="qr_size")

        ec = st.selectbox(
            "Error correction",
            options=["Low", "Medium", "Quartile", "High"],
            index=1,
            label_visibility="collapsed",
            key="qr_ec",
        )
        ec_map = {"Low": "L", "Medium": "M", "Quartile": "Q", "High": "H"}

        st.markdown('<div style="margin:.6rem 0;"></div>', unsafe_allow_html=True)

        if st.button("⬛ Generate QR Code", use_container_width=True, key="qr_gen"):
            content = _build_qr_content(ctype, fields)
            if not content:
                st.warning("Please enter content to encode.")
                return

            try:
                import qrcode
                from PIL import Image as PILImage

                qr = qrcode.QRCode(
                    version=None,
                    error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{ec_map[ec]}"),
                    box_size=10,
                    border=4,
                )
                qr.add_data(content)
                qr.make(fit=True)

                img = qr.make_image(fill_color=fg_color, back_color=bg_color)

                # Resize to desired size using NEAREST
                img = img.resize((size, size), PILImage.NEAREST)

                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.session_state._qr_img = buf.getvalue()
                st.session_state._qr_data = content
                st.session_state._qr_size = size
                st.rerun()

            except ImportError:
                st.error("qrcode library not installed. Run: pip install qrcode[pil]")

    # ═══════════════════════════════════════════════════════════════════════════
    # RIGHT COLUMN — QR display & actions
    # ═══════════════════════════════════════════════════════════════════════════
    with col_right:
        qr_img = st.session_state._qr_img
        qr_data = st.session_state._qr_data
        qr_size = st.session_state._qr_size

        if not qr_img:
            empty_state("⬛", "Configure content and generate a QR code")
            return

        # Display QR image in a container
        qr_container = st.container()
        with qr_container:
            st.markdown(
                '<div style="display:flex;justify-content:center;margin-bottom:1rem;">'
                f'<img src="data:image/png;base64,{qr_img}" '
                f'alt="QR Code" style="border-radius:var(--r);border:2px solid var(--border);'
                f'max-width:{qr_size}px;width:100%;image-rendering:pixelated;">'
                '</div>',
                unsafe_allow_html=True,
            )

        # Download button
        st.download_button(
            label="⬇️ Download QR Code",
            data=qr_img,
            file_name="nexus_qr_code.png",
            mime="image/png",
            use_container_width=True,
        )

        st.markdown('<div style="margin:.6rem 0;"></div>', unsafe_allow_html=True)

        # Data preview
        with st.expander("📋 Encoded Data Preview"):
            st.code(qr_data, language=None)
            st.markdown(
                f'<div style="font-size:.72rem;color:var(--ink3);margin-top:.3rem;">'
                f'{badge(f"{len(qr_data)} characters", "var(--ink3)")}'
                f'{badge(f"{qr_size}×{qr_size}px", "var(--sol)")}'
                '</div>',
                unsafe_allow_html=True,
            )
