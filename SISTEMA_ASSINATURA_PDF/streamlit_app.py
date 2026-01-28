import streamlit as st
import uuid
import os
from reportlab.pdfgen import canvas
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# ===============================
# CONFIG
# ===============================
st.set_page_config(page_title="Assinatura Digital", layout="centered")

BASE = "arquivos"
ORIG = f"{BASE}/originais"
SIGN = f"{BASE}/assinados"

os.makedirs(ORIG, exist_ok=True)
os.makedirs(SIGN, exist_ok=True)

# ===============================
# QUERY PARAMS (FORMA ESTÁVEL)
# ===============================
params = st.experimental_get_query_params()
token = params.get("token", [None])[0]

# ===============================
# MODO 1 — ENVIAR DOCUMENTO
# ===============================
if token is None:
    st.title("📄 Enviar documento para assinatura")

    pdf = st.file_uploader("Selecione o PDF", type=["pdf"])

    if pdf:
        token = str(uuid.uuid4())
        caminho = f"{ORIG}/{token}.pdf"

        with open(caminho, "wb") as f:
            f.write(pdf.read())

        app_url = "https://engsa20.streamlit.app"
        link = f"{app_url}/?token={token}"

        st.success("Documento pronto para assinatura!")
        st.code(link)

        msg = f"Olá! Assine este documento: {link}".replace(" ", "%20")
        st.markdown(f"[📲 Enviar pelo WhatsApp](https://wa.me/?text={msg})")

# ===============================
# MODO 2 — ASSINAR DOCUMENTO
# ===============================
else:
    st.title("✍️ Assinar documento")

    pdf_path = f"{ORIG}/{token}.pdf"

    if not os.path.exists(pdf_path):
        st.error("Documento não encontrado.")
        st.stop()

    st.write("Desenhe sua assinatura abaixo:")

    canvas_result = st_canvas(
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=200,
        width=400,
        drawing_mode="freedraw",
        key="assinatura_unica",
    )

    if st.button("Confirmar assinatura"):
        if canvas_result.image_data is None:
            st.error("Assinatura vazia.")
        else:
            img = Image.fromarray(canvas_result.image_data.astype("uint8"))
            assinatura_png = f"{SIGN}/{token}.png"
            img.save(assinatura_png)

            pdf_assinado = f"{SIGN}/assinado_{token}.pdf"
            c = canvas.Canvas(pdf_assinado)
            c.drawImage(assinatura_png, 100, 100, width=200, height=80)
            c.drawString(100, 85, "Assinado eletronicamente")
            c.save()

            st.success("Documento assinado!")

            with open(pdf_assinado, "rb") as f:
                st.download_button(
                    "⬇️ Baixar PDF assinado",
                    f,
                    file_name="documento_assinado.pdf",
                    mime="application/pdf"
                )
