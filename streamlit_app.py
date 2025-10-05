# ==================== YDS TEST UYGULAMASI - TAM KOD ====================
import streamlit as st
import json
import os
from datetime import datetime
import random
import zipfile
import io

st.set_page_config(page_title="YDS Test Uygulaması", page_icon="📄", layout="wide")
st.title("📄 YDS Test Uygulaması v4.0")

# ==================== GEMINI JSON İŞLEYİCİ MODÜLÜ ====================
def gemini_json_isleyici(gelen_veri):
    try:
        if isinstance(gelen_veri, str):
            veri = json.loads(gelen_veri)
        else:
            veri = gelen_veri
            
        if not isinstance(veri, dict):
            return False, "❌ JSON bir obje olmalı"
            
        icerik_tipi = veri.get("icerik_tipi")
        if not icerik_tipi:
            return False, "❌ 'icerik_tipi' alanı gerekli"
        
        return True, f"✅ {icerik_tipi} içeriği başarıyla alındı!"
        
    except json.JSONDecodeError:
        return False, "❌ Geçersiz JSON formatı"
    except Exception as e:
        return False, f"❌ İşleme hatası: {e}"

def icerik_dosyasina_kaydet(veri, dosya_adi="gemini_icerikler.json"):
    try:
        if os.path.exists(dosya_adi):
            with open(dosya_adi, "r", encoding="utf-8") as f:
                mevcut_icerik = json.load(f)
        else:
            mevcut_icerik = []
            
        veri["eklenme_tarihi"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        veri["id"] = len(mevcut_icerik) + 1
        
        mevcut_icerik.append(veri)
        
        with open(dosya_adi, "w", encoding="utf-8") as f:
            json.dump(mevcut_icerik, f, ensure_ascii=False, indent=2)
            
        return True, f"✅ İçerik başarıyla kaydedildi! (Dosya: {dosya_adi})"
        
    except Exception as e:
        return False, f"❌ Kaydetme hatası: {e}"

# ==================== ÜNİTE SİSTEMİ FONKSİYONLARI ====================
def unite_ilerleme_kaydet(unite_id, bolum_index, tamamlandi=True):
    try:
        ilerleme_dosyasi = "unite_ilerleme.json"
        
        if os.path.exists(ilerleme_dosyasi):
            with open(ilerleme_dosyasi, "r", encoding="utf-8") as f:
                ilerlemeler = json.load(f)
        else:
            ilerlemeler = {}
        
        if unite_id not in ilerlemeler:
            ilerlemeler[unite_id] = {"tamamlanan_bolumler": [], "son_bolum": 0}
        
        if tamamlandi and bolum_index not in ilerlemeler[unite_id]["tamamlanan_bolumler"]:
            ilerlemeler[unite_id]["tamamlanan_bolumler"].append(bolum_index)
        
        ilerlemeler[unite_id]["son_bolum"] = bolum_index
        
        with open(ilerleme_dosyasi, "w", encoding="utf-8") as f:
            json.dump(ilerlemeler, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        st.error(f"İlerleme kaydetme hatası: {e}")
        return False

def unite_ilerleme_getir(unite_id):
    try:
        ilerleme_dosyasi = "unite_ilerleme.json"
        
        if os.path.exists(ilerleme_dosyasi):
            with open(ilerleme_dosyasi, "r", encoding="utf-8") as f:
                ilerlemeler = json.load(f)
                return ilerlemeler.get(unite_id, {"tamamlanan_bolumler": [], "son_bolum": 0})
        else:
            return {"tamamlanan_bolumler": [], "son_bolum": 0}
    except:
        return {"tamamlanan_bolumler": [], "son_bolum": 0}

# ==================== İSTATİSTİK VERİ TOPLAMA SİSTEMİ ====================
def istatistik_veri_kaydet(olay_tipi, **kwargs):
    try:
        istatistik_dosyasi = "istatistik_verileri.json"
        
        if os.path.exists(istatistik_dosyasi):
            with open(istatistik_dosyasi, "r", encoding="utf-8") as f:
                veriler = json.load(f)
        else:
            veriler = []
        
        yeni_kayit = {
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "olay_tipi": olay_tipi,
            **kwargs
        }
        
        veriler.append(yeni_kayit)
        
        with open(istatistik_dosyasi, "w", encoding="utf-8") as f:
            json.dump(veriler, f, ensure_ascii=False, indent=2)
            
        return True
    except Exception as e:
        print(f"İstatistik kayıt hatası: {e}")
        return False

def bolum_tamamlandi_kaydet(unite_adi, bolum_index, kelime_sayisi):
    return istatistik_veri_kaydet(
        olay_tipi="bolum_tamamlandi",
        unite_adi=unite_adi,
        bolum_index=bolum_index,
        kelime_sayisi=kelime_sayisi
    )

def test_tamamlandi_kaydet(unite_adi, dogru_sayisi, yanlis_sayisi, toplam_soru):
    return istatistik_veri_kaydet(
        olay_tipi="test_tamamlandi",
        unite_adi=unite_adi,
        dogru_sayisi=dogru_sayisi,
        yanlis_sayisi=yanlis_sayisi,
        toplam_soru=toplam_soru,
        basari_orani=dogru_sayisi/toplam_soru if toplam_soru > 0 else 0
    )

# ==================== YEDEKLEME SİSTEMİ ====================
def zip_yedek_olustur():
    try:
        zip_buffer = io.BytesIO()
        
        dosyalar = [
            "gemini_icerikler.json",
            "unite_ilerleme.json",
            "istatistik_verileri.json"
        ]
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for dosya in dosyalar:
                if os.path.exists(dosya):
                    zip_file.write(dosya)
                else:
                    zip_file.writestr(dosya, json.dumps([], ensure_ascii=False))
            
            yedek_bilgi = {
                "yedek_tarihi": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "dosya_sayisi": len(dosyalar),
                "uygulama": "YDS Test Uygulaması v4.0"
            }
            zip_file.writestr("yedek_bilgi.json", json.dumps(yedek_bilgi, ensure_ascii=False, indent=2))
        
        zip_buffer.seek(0)
        return True, zip_buffer
        
    except Exception as e:
        return False, f"Yedekleme hatası: {e}"

def zip_yedek_yukle(yuklu_dosya):
    try:
        with zipfile.ZipFile(yuklu_dosya, 'r') as zip_file:
            dosya_listesi = zip_file.namelist()
            
            yuklu_dosyalar = []
            for dosya_adi in dosya_listesi:
                if dosya_adi.endswith('.json') and dosya_adi != 'yedek_bilgi.json':
                    dosya_icerigi = zip_file.read(dosya_adi)
                    
                    with open(dosya_adi, 'wb') as f:
                        f.write(dosya_icerigi)
                    
                    yuklu_dosyalar.append(dosya_adi)
            
            if 'yedek_bilgi.json' in dosya_listesi:
                yedek_bilgi = json.loads(zip_file.read('yedek_bilgi.json'))
            else:
                yedek_bilgi = {"yedek_tarihi": "Bilinmiyor"}
            
            return True, yuklu_dosyalar, yedek_bilgi
            
    except Exception as e:
        return False, [], {"hata": str(e)}

# ==================== KELİME TESTİ FONKSİYONU ====================
def kelime_testi_uygulamasi(kelimeler, bolum_index):
    if not kelimeler:
        st.warning("⚠️ Bu bölümde test edilecek kelime bulunamadı.")
        return
    
    if f'test_durum_{bolum_index}' not in st.session_state:
        st.session_state[f'test_durum_{bolum_index}'] = {
            'cevaplar': {},
            'goster': {},
            'secenekler': {}
        }
    
    st.write("**İngilizce kelimenin Türkçe anlamını seçin:**")
    
    dogru_sayisi = 0
    yanlis_sayisi = 0
    toplam_soru = len(kelimeler)

    for i, kelime in enumerate(kelimeler):
        st.write(f"**{i+1}. {kelime['kelime']}**")
        
        secenekler_key = f"secenekler_{i}"
        if secenekler_key not in st.session_state[f'test_durum_{bolum_index}']['secenekler']:
            diger_kelimeler = [k for k in kelimeler if k != kelime]
            yanlis_secenekler = random.sample(diger_kelimeler, min(2, len(diger_kelimeler)))
            
            secenekler = [kelime['tr_anlam']] + [k['tr_anlam'] for k in yanlis_secenekler]
            random.shuffle(secenekler)
            st.session_state[f'test_durum_{bolum_index}']['secenekler'][secenekler_key] = secenekler
        else:
            secenekler = st.session_state[f'test_durum_{bolum_index}']['secenekler'][secenekler_key]
        
        secim_key = f"sec_{i}"
        
        if secim_key not in st.session_state[f'test_durum_{bolum_index}']['cevaplar']:
            st.session_state[f'test_durum_{bolum_index}']['cevaplar'][secim_key] = secenekler[0]
        
        secim = st.radio(
            "Anlamı nedir?",
            secenekler,
            index=secenekler.index(st.session_state[f'test_durum_{bolum_index}']['cevaplar'][secim_key]),
            key=f"radio_{bolum_index}_{i}"
        )
        
        st.session_state[f'test_durum_{bolum_index}']['cevaplar'][secim_key] = secim
        
        goster_key = f"goster_{i}"
        if st.button("Cevabı Kontrol Et", key=f"btn_{bolum_index}_{i}"):
            st.session_state[f'test_durum_{bolum_index}']['goster'][goster_key] = True
        
        if goster_key in st.session_state[f'test_durum_{bolum_index}']['goster']:
            if secim == kelime['tr_anlam']:
                st.success("✅ Doğru!")
                dogru_sayisi += 1
            else:
                st.error(f"❌ Yanlış! Doğru cevap: **{kelime['tr_anlam']}**")
                yanlis_sayisi += 1
            
            with st.expander("ℹ️ Kelime Detayı"):
                st.write(f"**Tür:** {kelime.get('tur', '')}")
                if kelime.get('es_anlamli'):
                    st.write(f"**Eş Anlamlı:** {', '.join(kelime['es_anlamli'])}")
                if kelime.get('ornek_cumle'):
                    st.write(f"**Örnek:** {kelime['ornek_cumle']}")
        
        st.divider()
    
    if toplam_soru > 0:
        st.info(f"**Test Sonucu: {dogru_sayisi}/{toplam_soru} doğru**")
        
        if dogru_sayisi + yanlis_sayisi > 0:
            test_tamamlandi_kaydet(
                unite_adi="Kelime Testi", 
                dogru_sayisi=dogru_sayisi,
                yanlis_sayisi=yanlis_sayisi, 
                toplam_soru=toplam_soru
            )
        
        if st.button("🔄 Testi Sıfırla", key=f"reset_{bolum_index}"):
            st.session_state[f'test_durum_{bolum_index}'] = {'cevaplar': {}, 'goster': {}, 'secenekler': {}}
            st.rerun()

# ==================== BÖLÜM GÖSTERME FONKSİYONU ====================
def bolum_goster(unite_data, bolum_index, ilerleme):
    bolum = unite_data["bolumler"][bolum_index]
    bolum_tipi = bolum["bolum_tipi"]
    
    st.header(f"📖 {bolum['baslik']}")
    
    if bolum_tipi == "kelime_tablosu":
        st.subheader("📝 Kelime Çalışması")
        kelimeler = bolum.get("kelimeler", [])
        
        for i, kelime in enumerate(kelimeler, 1):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.write(f"**{kelime.get('kelime', '')}**")
                st.write(f"*{kelime.get('tur', '')}*")
            with col2:
                st.write(f"**Türkçe:** {kelime.get('tr_anlam', '')}")
                st.write(f"**Eş Anlamlı:** {', '.join(kelime.get('es_anlamli', []))}")
                st.write(f"**Örnek:** {kelime.get('ornek_cumle', '')}")
            st.divider()

        with st.expander("🧪 Kelimeleri Test Et", expanded=False):
            kelime_testi_uygulamasi(kelimeler, bolum_index)
    
    elif bolum_tipi == "paragraf":
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🇺🇸 İngilizce")
            st.write(bolum.get("ingilizce_paragraf", ""))
        with col2:
            st.subheader("🇹🇷 Türkçe Çeviri")
            st.write(bolum.get("turkce_ceviri", ""))
        
        st.subheader("🔑 Önemli Kelimeler")
        st.write(", ".join(bolum.get("onemli_kelimeler", [])))
    
    elif bolum_tipi == "dilbilgisi_analizi":
        st.write(bolum.get("aciklama", ""))
        st.subheader("📚 Dilbilgisi Notları")
        for not_item in bolum.get("notlar", []):
            st.write(f"• {not_item}")
    
    elif bolum_tipi == "test":
        sorular = bolum.get("sorular", [])
        for soru in sorular:
            st.write(f"**Soru {soru.get('soru_no', '')}:** {soru.get('soru_metni', '')}")
            
            secenekler = soru.get("siklar", [])
            secim = st.radio("Seçenekler:", secenekler, key=f"soru_{soru.get('soru_no', '')}")
            
            if st.button("Cevapla", key=f"cevap_{soru.get('soru_no', '')}"):
                secilen_cevap = secim[0]
                dogru_cevap = soru.get("cevap", "")
                
                if secilen_cevap == dogru_cevap:
                    st.success("✅ Doğru!")
                else:
                    st.error(f"❌ Yanlış! Doğru cevap: {dogru_cevap}")
                
                st.write(f"**Çözüm:** {soru.get('cozum', '')}")
            
            st.divider()
    
    bolum_tamamlandi = bolum_index in ilerleme["tamamlanan_bolumler"]
    
    if bolum_tamamlandi:
        st.success("✅ Bu bölümü tamamladın!")
    else:
        if st.button("✅ Bölümü Tamamla", type="primary", key=f"tamamla_{bolum_index}"):
            if unite_ilerleme_kaydet(unite_data["unite_adi"], bolum_index):
                kelime_sayisi = len(bolum.get("kelimeler", [])) if bolum_tipi == "kelime_tablosu" else 0
                bolum_tamamlandi_kaydet(unite_data["unite_adi"], bolum_index, kelime_sayisi)
                st.success("🎉 Bölüm tamamlandı!")
                st.rerun()

# ==================== DEEPSEEK AI ENTEGRASYONU ====================
def deepseek_analiz_yap(istatistik_verileri):
    try:
        api_key = st.session_state.get('deepseek_api_key', "")
        
        if not api_key:
            return "🔑 Lütfen DeepSeek API key'inizi '🔧 Ayarlar' sayfasına ekleyin."
        
        basit_veriler = {
            "toplam_gun": len(set([v["tarih"][:10] for v in istatistik_verileri])),
            "tamamlanan_bolum": len([v for v in istatistik_verileri if v["olay_tipi"] == "bolum_tamamlandi"]),
            "toplam_kelime": sum([v.get("kelime_sayisi", 0) for v in istatistik_verileri]),
            "test_basari": [],
            "son_7_gun_aktivite": []
        }
        
        testler = [v for v in istatistik_verileri if v["olay_tipi"] == "test_tamamlandi"]
        for test in testler:
            basit_veriler["test_basari"].append(test.get("basari_orani", 0))
        
        mock_analiz = f"""
🤖 **AI ANALİZ RAPORU**

🎯 **Genel Değerlendirme:**
Toplam {basit_veriler['toplam_gun']} gün çalışmışsın ve {basit_veriler['tamamlanan_bolum']} bölüm tamamlamışsın. {basit_veriler['toplam_kelime']} kelime öğrenmişsin - harika başlangıç! 

📈 **Performans Analizi:**
{len(testler)} test tamamlamışsın. Ortalama başarı oranın: %{sum(basit_veriler['test_basari'])/len(basit_veriler['test_basari'])*100:.0f if testler else 0}

💡 **Öneriler:**
1. Her gün en az 15 dakika çalışmaya devam et
2. Zorlandığın kelimeleri tekrar et
3. Testlerde yanlış yaptığın soruları gözden geçir

🚀 **Motivasyon:**
Bu tempoyla 1 ay sonra 500+ kelime öğrenebilirsin!
"""
        
        return mock_analiz
        
    except Exception as e:
        return f"❌ AI analiz hatası: {str(e)}"

def ai_cevap_uret(soru):
    soru_kucuk = soru.lower()
    
    if "anlam" in soru_kucuk or "ne demek" in soru_kucuk:
        return "🔍 Kelime anlamı için PassageWork bölümündeki kelime tablolarına bakabilirsin. Hangi kelimeyi öğrenmek istiyorsun?"
    
    elif "dilbilgisi" in soru_kucuk or "grammar" in soru_kucuk:
        return "📖 Dilbilgisi konusunda hangi yapı hakkında yardım istiyorsun? (Örn: Present Perfect, Conditionals)"
    
    elif "plan" in soru_kucuk or "program" in soru_kucuk:
        return """📅 **Önerilen Haftalık Plan:**
- Pazartesi: 2 ünite kelime çalışması
- Salı: Paragraf okuma + test
- Çarşamba: Dilbilgisi + tekrar
- Perşembe: Deneme testi
- Cuma: Yanlış sorular tekrarı
- Cumartesi: 3 ünite yeni kelime
- Pazar: Genel tekrar"""
    
    elif "test" in soru_kucuk or "sınav" in soru_kucuk:
        return """🎯 **Test Çözme Stratejisi:**
1. Önce kolay soruları çöz
2. Zor soruları işaretle, sonra dön
3. Her şıkkı dikkatlice oku
4. Elimine yöntemini kullan
5. Zamanını iyi yönet"""
    
    elif "motivasyon" in soru_kucuk or "vazgeç" in soru_kucuk:
        return "💪 Başarı bir yolculuktur! Her gün küçük adımlar atmaya devam et. Bugün zorlandığın kelimeler yarın en güçlü tarafın olacak! 🚀"
    
    else:
        return f"🤖 '{soru}' hakkında yardımcı olmaya çalışayım. Daha spesifik sorabilir misin? Örneğin: kelime anlamları, dilbilgisi, test stratejisi, çalışma planı..."

# ==================== SIDEBAR İÇİNDEKİLER VE AI ASISTAN ====================
st.sidebar.title("📚 YDS Uygulaması")

with st.sidebar.expander("📑 İçindekiler / Kod Haritası", expanded=False):
    st.markdown("""
    **📦 Modüller:**
    - Gemini JSON İşleyici
    - Ünite Sistemi
    - İstatistik Toplama
    - Kelime Testi
    - DeepSeek AI Entegrasyonu
    
    **📄 Sayfalar:**
    - 🏠 Ana Sayfa
    - 📚 PassageWork Çalışma
    - 📊 İstatistiklerim
    - 🎯 YDS Çalışma Soruları
    - 📝 Deneme Testleri
    - 🏆 Çıkmış Sorular
    - ➕ İçerik Ekle
    - 🔧 Ayarlar
    - 🤖 AI Asistan
    
    **📊 Veri Dosyaları:**
    - gemini_icerikler.json
    - unite_ilerleme.json
    - istatistik_verileri.json
    """)

with st.sidebar.expander("🤖 AI Asistan & Koç", expanded=False):
    st.write("**Soru sor, yardım al!**")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    kullanici_sorusu = st.text_input(
        "Sorunuz:",
        placeholder="Örn: Bu kelimeyi nasıl kullanırım?",
        key="ai_soru_sidebar"
    )
    
    if st.button("Gönder", key="ai_gonder_sidebar"):
        if kullanici_sorusu:
            cevap = f"🤖 **AI Cevap:** '{kullanici_sorusu}' sorunuz için detaylı yardım almak ister misin? '🤖 AI Asistan' sayfasına git!"
            st.session_state.chat_history.append({
                "soru": kullanici_sorusu,
                "cevap": cevap
            })
            st.info(cevap)
    
    if st.session_state.chat_history:
        st.write("**Son sorular:**")
        for i, chat in enumerate(reversed(st.session_state.chat_history[-3:])):
            with st.container():
                st.caption(f"S: {chat['soru'][:30]}...")

st.sidebar.divider()

# ==================== ANA MENÜ ====================
menu = st.sidebar.selectbox(
    "📋 Ana Menü",
    ["🏠 Ana Sayfa", "📚 PassageWork Çalışma", "📊 İstatistiklerim", "🤖 AI Asistan", "🎯 YDS Çalışma Soruları", "📝 Deneme Testleri", "🏆 Çıkmış Sorular", "➕ İçerik Ekle", "🔧 Ayarlar"],
    key="main_menu"
)

# ==================== ANA SAYFA ====================
if menu == "🏠 Ana Sayfa":
    st.header("🏠 YDS Test Uygulamasına Hoş Geldin!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **📚 PassageWork Çalışma**
        • Kelime tabloları
        • Paragraf çalışmaları
        • Dilbilgisi analizleri
        """)
    
    with col2:
        st.info("""
        **🎯 Test Sistemleri**
        • YDS çalışma soruları
        • Deneme testleri
        • Çıkmış sorular
        """)
    
    with col3:
        st.info("""
        **🚀 Akıllı Sistem**
        • Gemini JSON ithalatı
        • Dosya yükleme
        • Otomatik işleme
        """)
    
    st.success("🎯 **Başlamak için soldaki menüden bir bölüm seç!**")

# ==================== PASSAGEWORK ÇALIŞMA ====================
elif menu == "📚 PassageWork Çalışma":
    st.header("📚 PassageWork Çalışma - Ünite Sistemi")
    
    try:
        with open("gemini_icerikler.json", "r", encoding="utf-8") as f:
            tum_icerikler = json.load(f)
    except Exception as e:
        st.error(f"❌ Dosya okuma hatası: {e}")
        tum_icerikler = []
    
    unite_icerikler = [icerik for icerik in tum_icerikler if icerik.get("icerik_tipi") == "unite"]
    
    if not unite_icerikler:
        st.info("📝 Henüz ünite eklenmemiş. Önce 'İçerik Ekle' sekmesinden ÜNİTE JSON'u ekle!")
        
        with st.expander("🎯 Örnek Ünite JSON Formatı"):
            st.code("""
{
  "icerik_tipi": "unite",
  "unite_adi": "MONEY - Banking for Students",
  "unite_no": 1,
  "seviye": "intermediate",
  "bolumler": [
    {
      "bolum_tipi": "kelime_tablosu",
      "baslik": "Önemli Kelimeler",
      "kelimeler": [
        {
          "kelime": "financial",
          "tur": "adjective",
          "tr_anlam": "finansal",
          "es_anlamli": ["monetary", "economic"],
          "ornek_cumle": "Organising your financial affairs is not easy."
        }
      ]
    }
  ]
}
            """, language="json")
    
    else:
        st.success(f"✅ {len(unite_icerikler)} ünite bulundu!")
        
        secilen_unite_index = st.selectbox(
            "📋 Çalışmak istediğin üniteyi seç:",
            range(len(unite_icerikler)),
            format_func=lambda i: f"{unite_icerikler[i].get('unite_adi', 'İsimsiz')} - Seviye: {unite_icerikler[i].get('seviye', 'unknown')}"
        )
        
        secilen_unite = unite_icerikler[secilen_unite_index]
        unite_adi = secilen_unite.get("unite_adi", "İsimsiz Ünite")
        bolumler = secilen_unite.get("bolumler", [])
        
        ilerleme = unite_ilerleme_getir(unite_adi)
        
        tamamlanan_sayi = len(ilerleme["tamamlanan_bolumler"])
        toplam_bolum = len(bolumler)
        ilerleme_yuzdesi = (tamamlanan_sayi / toplam_bolum) * 100 if toplam_bolum > 0 else 0
        
        st.subheader(f"📊 İlerleme: %{ilerleme_yuzdesi:.0f}")
        st.progress(ilerleme_yuzdesi / 100)
        st.write(f"✅ {tamamlanan_sayi}/{toplam_bolum} bölüm tamamlandı")
        
        bolum_isimleri = [f"{i+1}. {bolum['baslik']} ({bolum['bolum_tipi']})" for i, bolum in enumerate(bolumler)]
        
        son_bolum = ilerleme["son_bolum"]
        if son_bolum >= len(bolum_isimleri):
            son_bolum = 0
        
        secilen_bolum_index = st.selectbox(
            "🎯 Çalışmak istediğin bölümü seç:",
            range(len(bolumler)),
            index=son_bolum,
            format_func=lambda i: bolum_isimleri[i]
        )
        
        st.divider()
        
        bolum_goster(secilen_unite, secilen_bolum_index, ilerleme)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if secilen_bolum_index > 0:
                if st.button("⬅️ Önceki Bölüm"):
                    unite_ilerleme_kaydet(unite_adi, secilen_bolum_index - 1, False)
                    st.rerun()
        
        with col3:
            if secilen_bolum_index < len(bolumler) - 1:
                if st.button("Sonraki Bölüm ➡️"):
                    unite_ilerleme_kaydet(unite_adi, secilen_bolum_index + 1, False)
                    st.rerun()
            elif tamamlanan_sayi == toplam_bolum:
                st.success("🎉 TEBRİKLER! Bu üniteyi tamamladın!")

# ==================== İSTATİSTİKLERİM ====================
elif menu == "📊 İstatistiklerim":
    st.header("📊 İstatistiklerim")
    
    try:
        with open("istatistik_verileri.json", "r", encoding="utf-8") as f:
            istatistik_verileri = json.load(f)
    except:
        istatistik_verileri = []
    
    if not istatistik_verileri:
        st.info("📝 Henüz istatistik verisi yok. Biraz çalışmaya başla!")
    else:
        st.subheader("🏆 Genel İlerleme")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            tarihler = set([veri["tarih"][:10] for veri in istatistik_verileri])
            st.metric("📅 Çalışılan Gün", len(tarihler))
        
        with col2:
            bolum_sayisi = len([v for v in istatistik_verileri if v["olay_tipi"] == "bolum_tamamlandi"])
            st.metric("✅ Tamamlanan Bölüm", bolum_sayisi)
        
        with col3:
            toplam_kelime = sum([v.get("kelime_sayisi", 0) for v in istatistik_verileri])
            st.metric("📚 Toplam Kelime", toplam_kelime)
        
        with col4:
            testler = [v for v in istatistik_verileri if v["olay_tipi"] == "test_tamamlandi"]
            if testler:
                ortalama_basari = sum([v.get("basari_orani", 0) for v in testler]) / len(testler)
                st.metric("📊 Başarı Oranı", f"%{ortalama_basari*100:.0f}")
            else:
                st.metric("📊 Başarı Oranı", "%-")
        
        st.subheader("📈 Günlük Aktivite")
        
        from datetime import timedelta
        bugun = datetime.now().date()
        son_7_gun = [(bugun - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
        
        gunluk_veriler = []
        for gun in son_7_gun:
            gun_verileri = [v for v in istatistik_verileri if v["tarih"][:10] == gun]
            gunluk_veriler.append(len(gun_verileri))
        
        chart_data = {"Günler": son_7_gun, "Aktivite": gunluk_veriler}
        st.line_chart(chart_data, x="Günler", y="Aktivite")
        
        st.subheader("📋 Detaylı Kayıtlar")
        
        for veri in reversed(istatistik_verileri[-10:]):
            with st.expander(f"{veri['tarih']} - {veri['olay_tipi']}"):
                if veri["olay_tipi"] == "bolum_tamamlandi":
                    st.write(f"**Ünite:** {veri.get('unite_adi', '')}")
                    st.write(f"**Bölüm:** {veri.get('bolum_index', '') + 1}")
                    st.write(f"**Kelime Sayısı:** {veri.get('kelime_sayisi', 0)}")
                elif veri["olay_tipi"] == "test_tamamlandi":
                    st.write(f"**Doğru:** {veri.get('dogru_sayisi', 0)}")
                    st.write(f"**Yanlış:** {veri.get('yanlis_sayisi', 0)}")
                    st.write(f"**Başarı:** %{veri.get('basari_orani', 0)*100:.0f}")
        
        st.divider()
        st.subheader("🤖 AI İle Detaylı Analiz")
        
        if st.button("🎯 AI Analiz Yap", type="primary"):
            with st.spinner("AI verilerinizi analiz ediyor..."):
                ai_rapor = deepseek_analiz_yap(istatistik_verileri)
                st.success("AI analiz tamamlandı!")
                st.markdown(ai_rapor)

# ==================== AI ASISTAN SAYFASI ====================
elif menu == "🤖 AI Asistan":
    st.header("🤖 AI Asistan & Kişisel Koç")
    
    st.info("""
    💡 **AI Asistanın şunlarda yardımcı olabilir:**
    - Kelime anlamları ve kullanımları
    - Dilbilgisi kuralları
    - Test stratejileri
    - Çalışma planı önerileri
    - Motivasyon ve hedef belirleme
    """)
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    st.subheader("💬 Sohbet")
    
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["soru"])
        with st.chat_message("assistant"):
            st.write(chat["cevap"])
    
    kullanici_mesaji = st.chat_input("Sorunuzu yazın...")
    
    if kullanici_mesaji:
        with st.chat_message("user"):
            st.write(kullanici_mesaji)
        
        with st.chat_message("assistant"):
            with st.spinner("Düşünüyorum..."):
                cevap = ai_cevap_uret(kullanici_mesaji)
                st.write(cevap)
        
        st.session_state.chat_history.append({
            "soru": kullanici_mesaji,
            "cevap": cevap
        })
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ Sohbeti Temizle"):
            st.session_state.chat_history = []
            st.rerun()
    
    st.divider()
    
    st.subheader("⚡ Hızlı Sorular")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 Bugün ne çalışmalıyım?"):
            cevap = "Öncelikle tamamlamadığın ünitelere bakmanı öneririm. Sonra kelime testlerini tekrarla!"
            st.info(cevap)
            st.session_state.chat_history.append({
                "soru": "Bugün ne çalışmalıyım?",
                "cevap": cevap
            })
    
    with col2:
        if st.button("🎯 Hedef belirleme"):
            cevap = "Haftalık hedef: 50 yeni kelime, 3 ünite tamamla, 2 deneme testi çöz!"
            st.info(cevap)
            st.session_state.chat_history.append({
                "soru": "Hedef belirleme",
                "cevap": cevap
            })
    
    with col3:
        if st.button("💪 Motivasyon"):
            cevap = "Her gün küçük adımlar büyük başarılar yaratır! Bugün 15 dakika çalış, yarın daha iyisini yap! 🚀"
            st.success(cevap)
            st.session_state.chat_history.append({
                "soru": "Motivasyon",
                "cevap": cevap
            })

# ==================== İÇERİK EKLE ====================
elif menu == "➕ İçerik Ekle":
    st.header("➕ İçerik Ekle")
    
    st.subheader("🚀 Gemini JSON İçeriği Ekle")
    
    json_input = st.text_area(
        "Gemini'den gelen JSON'u buraya yapıştır:",
        height=200,
        placeholder='{"icerik_tipi": "kelime_tablosu", "baslik": "Örnek", "kelimeler": [...]}'
    )
    
    if st.button("📤 İçeriği İşle ve Kaydet", type="primary"):
        if json_input.strip():
            try:
                success, mesaj = gemini_json_isleyici(json_input)
                if success:
                    veri = json.loads(json_input)
                    
                    save_success, save_mesaj = icerik_dosyasina_kaydet(veri)
                    if save_success:
                        st.success("✅ İçerik başarıyla kaydedildi!")
                        st.balloons()
                        
                        st.info("🔄 PassageWork sekmesine gidip içeriği görebilirsin")
                        
                        with st.expander("📋 Kaydedilen İçerik"):
                            st.json(veri)
                    else:
                        st.error(save_mesaj)
                else:
                    st.error(mesaj)
            except Exception as e:
                st.error(f"❌ Hata: {e}")
        else:
            st.warning("⚠️ Lütfen JSON yapıştırın")

# ==================== AYARLAR ====================
elif menu == "🔧 Ayarlar":
    st.header("🔧 Ayarlar")
    
    st.subheader("🤖 DeepSeek API Ayarları")
    
    if 'deepseek_api_key' not in st.session_state:
        st.session_state.deepseek_api_key = ""
    
    api_key = st.text_input(
        "DeepSeek API Key:", 
        value=st.session_state.deepseek_api_key,
        type="password",
        placeholder="sk-... şeklinde API key'inizi girin"
    )
    
    if api_key:
        st.session_state.deepseek_api_key = api_key
        st.success("✅ API key kaydedildi!")
    
    st.info("""
    **DeepSeek API Key Nasıl Alınır?**
    1. https://platform.deepseek.com/ adresine git
    2. Üye ol/giriş yap
    3. API Keys bölümünden yeni key oluştur
    4. Buraya 'sk-...' şeklindeki key'i yapıştır
    """)
    
    st.divider()
    
    st.subheader("💾 Yedekleme Sistemi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📦 Yedek Oluştur**")
        st.caption("Tüm verilerinizi ZIP olarak indir")
        
        if st.button("💾 Yedek İndir", type="primary", use_container_width=True):
            with st.spinner("Yedek oluşturuluyor..."):
                success, result = zip_yedek_olustur()
                
                if success:
                    tarih = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dosya_adi = f"yds_yedek_{tarih}.zip"
                    
                    st.download_button(
                        label="⬇️ ZIP Dosyasını İndir",
                        data=result,
                        file_name=dosya_adi,
                        mime="application/zip",
                        use_container_width=True
                    )
                    
                    st.success("✅ Yedek hazır! İndir butonuna tıkla")
                else:
                    st.error(f"❌ {result}")
    
    with col2:
        st.write("**📂 Yedek Yükle**")
        st.caption("Önceki verilerinizi geri getir")
        
        yuklu_zip = st.file_uploader(
            "ZIP dosyasını seç:",
            type=['zip'],
            key="zip_yukle"
        )
        
        if yuklu_zip is not None:
            if st.button("📥 Yedek Geri Yükle", type="secondary", use_container_width=True):
                with st.spinner("Yedek yükleniyor..."):
                    success, yuklu_dosyalar, yedek_bilgi = zip_yedek_yukle(yuklu_zip)
                    
                    if success:
                        st.success("✅ Yedek başarıyla yüklendi!")
                        st.balloons()
                        
                        st.write(f"**Yedek Tarihi:** {yedek_bilgi.get('yedek_tarihi', 'Bilinmiyor')}")
                        st.write(f"**Yüklenen Dosyalar:** {', '.join(yuklu_dosyalar)}")
                        
                        st.info("🔄 Sayfa yenileniyor...")
                        st.rerun()
                    else:
                        st.error(f"❌ Yükleme hatası: {yedek_bilgi.get('hata', 'Bilinmeyen hata')}")
    
    st.divider()
    
    with st.expander("📋 Eski Yedekleme (Sadece JSON)", expanded=False):
        if st.button("📄 JSON Yedek Oluştur"):
            try:
                with open("gemini_icerikler.json", "r", encoding="utf-8") as f:
                    icerikler = json.load(f)
                
                yedek_adi = f"yds_yedek_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(yedek_adi, "w", encoding="utf-8") as f:
                    json.dump(icerikler, f, ensure_ascii=False, indent=2)
                
                st.success(f"✅ JSON yedek oluşturuldu: {yedek_adi}")
                
            except Exception as e:
                st.error(f"❌ Yedekleme hatası: {e}")
    
    st.divider()
    
    st.subheader("🐛 Debug - Dosya İçeriği")
    
    tab1, tab2, tab3 = st.tabs(["📚 İçerikler", "📊 İlerleme", "📈 İstatistikler"])
    
    with tab1:
        try:
            with open("gemini_icerikler.json", "r", encoding="utf-8") as f:
                icerikler = json.load(f)
            st.write(f"**Dosyadaki içerik sayısı:** {len(icerikler)}")
            st.json(icerikler)
        except Exception as e:
            st.error(f"❌ Dosya okunamadı: {e}")
    
    with tab2:
        try:
            with open("unite_ilerleme.json", "r", encoding="utf-8") as f:
                ilerleme = json.load(f)
            st.write(f"**Ünite sayısı:** {len(ilerleme)}")
            st.json(ilerleme)
        except Exception as e:
            st.warning("ℹ️ Henüz ilerleme kaydı yok")
    
    with tab3:
        try:
            with open("istatistik_verileri.json", "r", encoding="utf-8") as f:
                istatistikler = json.load(f)
            st.write(f"**Kayıt sayısı:** {len(istatistikler)}")
            st.json(istatistikler[-10:])
        except Exception as e:
            st.warning("ℹ️ Henüz istatistik verisi yok")
    
    st.divider()
    
    st.subheader("⚠️ Tehlikeli Alan")
    with st.expander("🗑️ Tüm Verileri Sil", expanded=False):
        st.warning("⚠️ DİKKAT: Bu işlem geri alınamaz!")
        
        onay = st.checkbox("Tüm verileri silmek istediğimi onaylıyorum")
        
        if onay:
            if st.button("🗑️ TÜM VERİLERİ SİL", type="secondary"):
                try:
                    dosyalar = ["gemini_icerikler.json", "unite_ilerleme.json", "istatistik_verileri.json"]
                    for dosya in dosyalar:
                        if os.path.exists(dosya):
                            os.remove(dosya)
                    st.success("✅ Tüm veriler silindi!")
                    st.info("🔄 Sayfa yenileniyor...")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Silme hatası: {e}")

# ==================== BOŞ SAYFALAR ====================
elif menu == "🎯 YDS Çalışma Soruları":
    st.header("🎯 YDS Çalışma Soruları")
    st.info("🚧 Bu bölüm yakında eklenecek...")

elif menu == "📝 Deneme Testleri":
    st.header("📝 Deneme Testleri")
    st.info("🚧 Bu bölüm yakında eklenecek...")

elif menu == "🏆 Çıkmış Sorular":
    st.header("🏆 Çıkmış Sorular")
    st.info("🚧 Bu bölüm yakında eklenecek...")

# ==================== UYGULAMA SONU ====================
