import os
from dotenv import load_dotenv
import google.generativeai as genai

# 1. Coba load file .env
print("--- DIAGNOSA MULAI ---")
loaded = load_dotenv()
if loaded:
    print("✅ File .env ditemukan.")
else:
    print("❌ File .env TIDAK ditemukan. Pastikan nama filenya benar (ada titik di depan).")

# 2. Cek API Key
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    # Tampilkan 5 huruf pertama saja biar aman
    print(f"✅ API Key terbaca: {api_key[:5]}...****")
    
    # 3. Tes Koneksi ke Google
    print("⏳ Sedang mencoba menghubungi Google Gemini...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash') # Kita coba model yang lebih baru
        response = model.generate_content("Apa itu Python? Jawab 1 kata saja.")
        print(f"✅ SUKSES! Jawaban Google: {response.text}")
    except Exception as e:
        print(f"❌ GAGAL KONEK KE GOOGLE. Errornya:\n{e}")

else:
    print("❌ API Key KOSONG. Cek lagi isi file .env Anda.")
    print("Pastikan tulisannya: GOOGLE_API_KEY=AIzaSy...")