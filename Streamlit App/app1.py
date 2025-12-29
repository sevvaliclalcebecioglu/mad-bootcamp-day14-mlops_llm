import streamlit as st        # Web arayüzü oluşturmak için Streamlit kütüphanesi
import ollama                 # Ollama modeli ile etkileşim kurmak için
from PIL import Image         # Görsel işlemek için Pillow kütüphanesi
import io                     # Görsel verilerini byte olarak işlemek için

# Uygulamanın üst başlığı
st.title("OCR App using Ollama Llama3.2-Vision")
st.write("Upload an image and extract its text using Llama3.2-Vision")

# Kullanıcının görsel yüklemesi için dosya yükleme alanı
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Yüklenen görseli görüntüye dönüştür
    img = Image.open(uploaded_file)

    # Kullanıcıya yüklenen görseli göster
    st.image(img, caption="Uploaded Image", width=400)

    # Ollama'nın anlayabilmesi için görseli byte formatına çeviriyoruz
    img_bytes = uploaded_file.read()

    # Kullanıcı "Extract Text" butonuna bastığında çalışacak kısım
    if st.button("Extract Text"):

        # İşlem yapılırken "Processing..." animasyonu göster
        with st.spinner("Processing..."):

            # Ollama Vision modeline istek gönderiyoruz
            res = ollama.chat(
                model="llama3.2-vision:latest",  # Görsel algılayabilen Llama modeli
                messages=[
                    {
                        "role": "user",  # Mesaj sahibi biziz
                        "content": "Extract text from this image.",  # Fotoğraftaki metni çıkar
                        "images": [img_bytes],  # Görsel verisini byte olarak gönder
                    }
                ],
            )

            # Modelden dönen metni alıyoruz
            text_output = res["message"]["content"]

        # Elde edilen metni kullanıcıya gösteriyoruz
        st.subheader("Extracted Text")
        st.text_area("", text_output, height=200)
