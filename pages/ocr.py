# ocr.py — OCR Scanner: extract text from images using pytesseract
import html
import io
import re
import streamlit as st
from PIL import Image

from config import inject_css
from state import init_state
from components import page_header, badge, empty_state

OCR_LANGUAGES = {
    "eng": "English",
    "nep": "Nepali (नेपाली)",
    "hin": "Hindi (हिन्दी)",
    "chi_sim": "Chinese Simplified (简体)",
    "jpn": "Japanese (日本語)",
    "kor": "Korean (한국어)",
    "fra": "French (Français)",
    "deu": "German (Deutsch)",
    "spa": "Spanish (Español)",
}

IMAGE_TYPES = ["png", "jpg", "jpeg", "webp", "bmp", "tiff"]


def _preprocess_image(
    img: Image.Image,
    grayscale: bool,
    threshold: int,
    upscale: int,
) -> Image.Image:
    """Apply preprocessing steps to an image."""
    # Upscale first if needed
    if upscale > 1:
        new_size = (img.width * upscale, img.height * upscale)
        img = img.resize(new_size, Image.LANCZOS)

    # Convert to grayscale
    if grayscale:
        img = img.convert("L")

    # Apply binary thresholding
    if threshold < 255:
        if img.mode != "L":
            img = img.convert("L")
        img = img.point(lambda x: 255 if x > threshold else 0, "1")

    return img


def _get_average_confidence(data_output: str) -> float:
    """Parse pytesseract image_to_data output and return average confidence."""
    lines = data_output.strip().split("\n")
    total_conf = 0
    count = 0
    for line in lines:
        parts = line.split("\t")
        if len(parts) >= 12 and parts[11] not in ("", "-1", "0"):
            try:
                conf = float(parts[11])
                if conf > 0:
                    total_conf += conf
                    count += 1
            except ValueError:
                continue
    return round(total_conf / count, 1) if count > 0 else 0.0


def render():
    """Render the OCR Scanner page."""
    inject_css()
    init_state()

    page_header("OCR Scanner", "Extract text from images — GOD MODE FEATURE")

    # ── Image input ──────────────────────────────────────────────────────────
    st.markdown(
        '<div style="background:var(--card);border:1px solid var(--border);'
        'border-radius:var(--r);padding:1.1rem 1.2rem;margin-bottom:.8rem;">'
        '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
        'margin-bottom:.8rem;letter-spacing:.04em;text-transform:uppercase;">'
        '🖼️ Image Input</div></div>',
        unsafe_allow_html=True,
    )

    upload_col, camera_col = st.columns(2)
    with upload_col:
        uploaded_files = st.file_uploader(
            "Upload image(s)",
            type=IMAGE_TYPES,
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="ocr_uploader",
        )
    with camera_col:
        camera_photo = st.camera_input(
            "Take a photo",
            label_visibility="collapsed",
            key="ocr_camera",
        )

    st.markdown('<div style="margin:.6rem 0;"></div>', unsafe_allow_html=True)

    # ── Preprocessing options ───────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
        'margin-bottom:.6rem;letter-spacing:.04em;text-transform:uppercase;">'
        '⚙️ Preprocessing Options</div>',
        unsafe_allow_html=True,
    )

    opt_col1, opt_col2, opt_col3 = st.columns(3)
    with opt_col1:
        grayscale = st.checkbox("Grayscale", value=True, key="ocr_gray")
    with opt_col2:
        threshold = st.slider(
            "Threshold (0=black, 255=off)",
            min_value=0,
            max_value=255,
            value=128,
            key="ocr_threshold",
        )
    with opt_col3:
        upscale = st.slider(
            "Upscale (1x–4x)",
            min_value=1,
            max_value=4,
            value=1,
            key="ocr_upscale",
        )

    lang_col, btn_col = st.columns([1, 1])
    with lang_col:
        lang = st.selectbox(
            "Language",
            options=list(OCR_LANGUAGES.keys()),
            format_func=lambda x: OCR_LANGUAGES[x],
            label_visibility="collapsed",
            key="ocr_lang",
        )
    with btn_col:
        st.markdown('<div style="margin-top:1.6rem;"></div>', unsafe_allow_html=True)
        extract_clicked = st.button(
            "🔮 Extract Text",
            use_container_width=True,
            key="ocr_extract",
        )

    st.markdown('<div style="margin:.8rem 0;"></div>', unsafe_allow_html=True)

    # ── Process ─────────────────────────────────────────────────────────────
    if extract_clicked:
        # Collect all images
        images_to_process = []

        if uploaded_files:
            for f in uploaded_files:
                try:
                    img = Image.open(io.BytesIO(f.read()))
                    images_to_process.append((img, f.name))
                except Exception as e:
                    st.error(f"Failed to open {f.name}: {e}")

        if camera_photo:
            try:
                cam_img = Image.open(io.BytesIO(camera_photo.getvalue()))
                images_to_process.append((cam_img, "camera_capture.png"))
            except Exception as e:
                st.error(f"Failed to open camera image: {e}")

        if not images_to_process:
            st.warning("Please upload an image or take a photo first.")
        else:
            # Try importing pytesseract
            try:
                import pytesseract
            except ImportError:
                st.markdown(
                    '<div style="background:rgba(244,63,94,.08);border:1px solid rgba(244,63,94,.25);'
                    'border-radius:var(--r);padding:1rem 1.2rem;">'
                    '<div style="color:var(--rose);font-weight:700;font-size:.9rem;margin-bottom:.4rem;">'
                    '⚠️ pytesseract not installed</div>'
                    '<div style="color:var(--ink2);font-size:.82rem;line-height:1.6;">'
                    'Install the required packages:<br>'
                    '<code style="background:var(--surface);padding:2px 8px;border-radius:4px;'
                    'font-size:.78rem;color:var(--teal);">pip install pytesseract Pillow</code><br><br>'
                    'Also install the Tesseract OCR engine:<br>'
                    '• <strong>Ubuntu/Debian:</strong> <code style="background:var(--surface);padding:2px 8px;'
                    'border-radius:4px;font-size:.78rem;color:var(--teal);">sudo apt install tesseract-ocr</code><br>'
                    '• <strong>macOS:</strong> <code style="background:var(--surface);padding:2px 8px;'
                    'border-radius:4px;font-size:.78rem;color:var(--teal);">brew install tesseract</code><br>'
                    '• <strong>Windows:</strong> Download from '
                    '<a href="https://github.com/UB-Mannheim/tesseract/wiki" style="color:var(--sol2);">'
                    'UB-Mannheim/tesseract</a> and add to PATH<br><br>'
                    'For additional languages (e.g. Nepali, Hindi):<br>'
                    '<code style="background:var(--surface);padding:2px 8px;border-radius:4px;'
                    'font-size:.78rem;color:var(--teal);">sudo apt install tesseract-ocr-nep tesseract-ocr-hin</code>'
                    '</div></div>',
                    unsafe_allow_html=True,
                )
                return

            # Process images
            all_text = []
            all_confidence = []

            for idx, (img, fname) in enumerate(images_to_process):
                try:
                    # Preprocess
                    processed = _preprocess_image(img, grayscale, threshold, upscale)

                    # Build config string
                    config_str = f"--psm 3 --oem 3"

                    # Extract text
                    text = pytesseract.image_to_string(processed, lang=lang, config=config_str)
                    all_text.append(text)

                    # Get confidence
                    try:
                        data = pytesseract.image_to_data(
                            processed, lang=lang, config=config_str, output_type=pytesseract.Output.STRING
                        )
                        conf = _get_average_confidence(data)
                        all_confidence.append(conf)
                    except Exception:
                        all_confidence.append(0.0)

                    # Show per-image preview for batch
                    if len(images_to_process) > 1:
                        st.markdown(
                            f'<div style="margin:.6rem 0 .3rem;">'
                            f'{badge(f"Image {idx + 1}: {html.escape(fname)}", "var(--sol)")}'
                            f'{badge(f"{conf:.0f}% confidence" if conf > 0 else "N/A confidence", "var(--amber)")}'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                except Exception as e:
                    st.error(f"Error processing {fname}: {e}")
                    all_text.append("")
                    all_confidence.append(0.0)

            combined_text = "\n\n---\n\n".join(
                t for t in all_text if t.strip()
            )

            avg_confidence = sum(all_confidence) / len(all_confidence) if all_confidence else 0

            # Store in session state
            st.session_state._ocr_text = combined_text
            st.session_state._ocr_confidence = avg_confidence

    # ── Show results ────────────────────────────────────────────────────────
    ocr_text = getattr(st.session_state, "_ocr_text", None)
    ocr_confidence = getattr(st.session_state, "_ocr_confidence", None)

    if ocr_text is not None:
        # Confidence display
        conf_color = "var(--green)" if ocr_confidence >= 80 else "var(--amber)" if ocr_confidence >= 50 else "var(--rose)"
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.6rem;">'
            f'{badge("Extracted Text", "var(--sol)")}'
            f'{badge(f"Confidence: {ocr_confidence:.0f}%" if ocr_confidence > 0 else "Confidence: N/A", conf_color)}'
            f'{badge(f"{len(ocr_text)} chars", "var(--ink3)")}'
            '</div>',
            unsafe_allow_html=True,
        )

        if not ocr_text.strip():
            empty_state("🔍", "No text was detected in the image(s)")
        else:
            # Extracted text area
            st.text_area(
                "Extracted text",
                value=ocr_text,
                height=250,
                label_visibility="collapsed",
                key="ocr_output",
            )

            # Actions row
            act_col1, act_col2, act_col3 = st.columns(3)

            with act_col1:
                # Copy to clipboard note
                st.markdown(
                    '<div style="font-size:.76rem;color:var(--ink3);margin-bottom:.3rem;">'
                    '📋 Copy — select all from the text area above (Ctrl+A)</div>',
                    unsafe_allow_html=True,
                )
                st.code(ocr_text, language=None)

            with act_col2:
                # Download as .txt
                st.download_button(
                    label="⬇️ Download as .txt",
                    data=ocr_text,
                    file_name="nexus_ocr_output.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

            with act_col3:
                # Send to Smart Notes
                if st.button("📝 Send to Smart Notes", use_container_width=True, key="ocr_to_notes"):
                    from datetime import datetime
                    note_key = datetime.now().strftime("OCR_%Y%m%d_%H%M%S")
                    st.session_state.notes[note_key] = {
                        "content": ocr_text,
                        "created": datetime.now().isoformat(),
                    }
                    st.session_state._active_note = note_key
                    st.session_state.page = "Notes"
                    st.rerun()
    else:
        empty_state("🔮", "Upload or capture an image, configure options, and click Extract")
