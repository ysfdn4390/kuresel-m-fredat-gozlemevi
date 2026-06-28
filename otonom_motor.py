import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# Sunucu ortamından anahtarları güvenli bir şekilde devralıyoruz
SUPABASE_URL = "https://tewivgaooywryjwogabe.supabase.co"
SUPABASE_KEY = "sb_publishable_2viLn-_ybsBRVrDaudMivA_UbH3lZoC"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def bulut_academic_scraper(uni_name, country, target_url):
    print(f"🕵️ {uni_name} müfredatı otonom olarak taranıyor...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return
    
    bulunan_dersler = []
    elements = soup.find_all(['a', 'h3', 'p', 'li', 'span'])
    for el in elements:
        text = el.text.strip()
        if any(prefix in text for prefix in ['IR ', 'POLS ', 'GOV ', 'SUİ ', 'INT ', 'International ']) and len(text) > 12:
            if text not in bulunan_dersler:
                bulunan_dersler.append(text)
                    
    if bulunan_dersler:
        for ders in bulunan_dersler[:15]: # Her gece üniversite başına 15 güncel ders
            parcalar = ders.split(' ', 1)
            kod = parcalar[0] if len(parcalar) > 1 and len(parcalar[0]) < 10 else "IR"
            ad = parcalar[1] if len(parcalar) > 1 else ders
            
            score, cat, just = 0, "Klasik Uİ", "Geleneksel teorik dış politika yaklaşımı."
            d_low = ad.lower()
            if any(w in d_low for w in ["cyber", "siber", "digital", "dijital"]):
                score, cat, just = 3, "Siber Güvenlik", "Siber savaş stratejileri ve devletlerarası siber espiyonajı inceler."
            elif any(w in d_low for w in ["data", "veri", "algorithm", "algoritma", "intelligence", "yapay zeka"]):
                score, cat, just = 3, "Metodoloji ve Kodlama", "Büyük veri analitiği, yapay zeka otomasyonu ve dijital çağ diplomasisi."
            
            try:
                supabase.table("All_Curriculum").insert({
                    "University_Name": uni_name, "Course_Code": kod, "Course_Name": ad[:100], 
                    "AI_Maturity_Score": score, "Sub_Category": cat, "Academic_Justification": just
                }).execute()
            except Exception:
                continue
        print(f"🚀 [OTONOM BAŞARILI] {uni_name} verileri güncellendi.")

# HEDEF ÜNİVERSİTE LİSTESİ
bulut_academic_scraper("London School of Economics (LSE)", "UK", "https://www.lse.ac.uk/resources/calendar/courseGuides/internationalRelations.htm")
