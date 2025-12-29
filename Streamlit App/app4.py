import streamlit as st
import base64
from openai import OpenAI

def main():
    st.title("Görüntü ile Sohbet Uygulaması")

    uploaded_file = st.file_uploader("Resminizi yükleyin (PNG, JPG)", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:

        image_bytes = uploaded_file.read()

        st.image(image_bytes, caption="Yüklenen Resim", use_container_width=True)

        user_input = st.text_input("Bu resim hakkında bir soru sorun:")

        if st.button("Sohbet Et"):

            encoded_image = base64.b64encode(image_bytes).decode("utf-8")

            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key="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",
            )

            response = client.chat.completions.create(
                model="openai/gpt-5.1-codex-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_input},
                            {"type": "image", "image": encoded_image}
                        ]
                    }
                ]
            )

            # Güvenli content okuma
            msg = response.choices[0].message

            if isinstance(msg.content, str):
                st.write(msg.content)
            else:
                final_text = ""
                for part in msg.content:
                    if isinstance(part, dict) and "text" in part:
                        final_text += part["text"] + "\n"
                st.write(final_text)


if __name__ == "__main__":
    main()
