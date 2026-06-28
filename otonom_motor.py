import os
import json
import requests
from bs4 import BeautifulSoup

def kuresel_akademik_kazici(uni_name, country, target_url):
    print(f"🕵️ {uni_name} resmi müfredat ve AKTS paketi taranıyor...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"❌ {uni_name} bağlantı hatası: {e}")
        return []
    
    yeni_dersler = []
    elements = soup.find_all(['a', 'h3', 'h4', 'p', 'li'])
    for el in elements:
        text = el.text.strip().replace('\n', ' ').replace('\r', '')
        
        if any(prefix in text for prefix in ['IR ', 'POLS ', 'GOV ', 'INT ', 'International ', 'Uİ ', 'SUI ', 'Dış Siyaset ']) and len(text) > 12:
            parcalar = text.split(' ', 1)
            kod = parcalar[0] if len(parcalar) > 1 and len(parcalar[0]) < 10 else "IR"
            ad = parcalar[1] if len(parcalar) > 1 else text
            
            ects = "6 ECTS"
            if "acts" in text.lower() or "akts" in text.lower() or "ects" in text.lower():
                ects = "".join([c for c in text if c.isdigit()])[:1] + " ECTS"
            
            score, cat, just = 0, "Klasik Uİ", "Geleneksel teorik dış politika yaklaşımı, uluslararası hukuk ve diplomasi tarihi."
            d_low = ad.lower()
            if any(w in d_low for w in ["cyber", "siber", "digital", "dijital"]):
                score, cat, just = 3, "Siber Güvenlik", "Siber savaş stratejileri, siber istihbarat ve devletlerarası dijital güvenlik protokolleri."
            elif any(w in d_low for w in ["data", "veri", "algorithm", "algoritma", "intelligence", "yapay zeka", "ai"]):
                score, cat, just = 3, "Metodoloji ve Kodlama", "Büyük veri analitiği, algoritmik yönetim süreçleri ve dijital çağ diplomasisi."
            
            if not any(d['Course_Name'] == ad[:100] for d in yeni_dersler):
                yeni_dersler.append({
                    "University_Name": uni_name,
                    "Course_Code": kod[:10],
                    "Course_Name": ad[:100],
                    "Sub_Category": cat,
                    "AI_Maturity_Score": score,
                    "ECTS_Credit": ects,
                    "Academic_Justification": just
                })
                
    return yeni_dersler

# --- ANA VERİ DOSYASI GÜNCELLEME KATMANI ---
existing_data = []
if os.path.exists('veri.json'):
    try:
        with open('veri.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except:
        existing_data = []

# BÜTÜNLEŞİK KÜRESEL HEDEF LİSTESİ
havuz = []
havuz.extend(kuresel_akademik_kazici("London School of Economics (LSE)", "UK", "https://www.lse.ac.uk/resources/calendar/courseGuides/internationalRelations.htm"))
havuz.extend(kuresel_akademik_kazici("Sciences Po", "France", "https://www.sciencespo.fr/college/en/academics/bachelor-degree/course-catalog.html"))
havuz.extend(kuresel_akademik_kazici("Harvard University", "USA", "https://handbook.fas.harvard.edu/book/government"))
havuz.extend(kuresel_akademik_kazici("Middle East Technical University (METU)", "Turkey", "https://catalog.metu.edu.tr/program.php?prog=110"))

# Tekilleştirme ve Üzerine Yazma
for yeni in havuz:
    if not any(old['Course_Name'] == yeni['Course_Name'] and old['University_Name'] == yeni['University_Name'] for old in existing_data):
        existing_data.append(yeni)

with open('veri.json', 'w', encoding='utf-8') as f:
    json.dump(existing_data, f, ensure_ascii=False, indent=2)

print(f"🚀 Otonom tarama başarıyla bitti. Toplam ders sayısı: {len(existing_data)}")
