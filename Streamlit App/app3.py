import PyPDF2
from openai import OpenAI
import streamlit as st

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text() + '\n'
    return text

def main():
    st.title("PDF ile Sohbet Uygulaması")

    uploaded_file = st.file_uploader("PDF belgesi yükleyin", type=["pdf"])

    if uploaded_file is not None:
        # PDF içeriğini oku
        pdf_text = read_pdf(uploaded_file)

        if pdf_text:
            st.subheader("PDF İçeriği:")
            st.write(pdf_text)

            user_input = st.text_input("Belge hakkında bir soru sorun:")

            if st.button("Sohbet Et"):
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key="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",
                )

                completion = client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": "<YOUR_SITE_URL>",
                        "X-Title": "<YOUR_SITE_NAME>",
                    },
                    extra_body={},
                    model="google/gemma-3n-e4b-it:free",
                    messages=[
                        {
                            "role": "user",
                            "content": f"{user_input}\n\n{pdf_text}"
                        }
                    ]
                )
                st.write(completion.choices[0].message.content)
        else:
            st.write("PDF'den metin çıkarılamadı.")

if __name__ == "__main__":
    main()