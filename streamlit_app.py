# -------------------- YDS TEST UYGULAMASI - TAM KOD --------------------
import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="YDS Test Uygulaması", page_icon="📄", layout="wide")
st.title("📄 YDS Test Uygulaması v4.0")

# -------------------- GEMINI JSON İŞLEYİCİ MODÜLÜ --------------------
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

# -------------------- ANA MENÜ --------------------
menu = st.sidebar.radio(
    "📋 Menü",
    ["🏠 Ana Sayfa", "📚 PassageWork Çalışma", "🎯 YDS Çalışma Soruları", "📝 Deneme Testleri", "🏆 Çıkmış Sorular", "➕ İçerik Ekle", "🔧 Ayarlar"],
    key="main_menu"
)

# -------------------- ANA SAYFA --------------------
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

# -------------------- PASSAGEWORK ÇALIŞMA SAYFASI --------------------
elif menu == "📚 PassageWork Çalışma":
    st.header("📚 PassageWork Çalışma")
    
    # YENİLE BUTONU EKLE
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🔄 Yenile", key="refresh_passagework"):
            st.rerun()
    with col2:
        st.write("İçerikleri yenilemek için tıkla")
    
    # ... geri kalan kod aynı
elif menu == "📚 PassageWork Çalışma":
    st.header("📚 PassageWork Çalışma")
    
    # İçerikleri yükle
    try:
        with open("gemini_icerikler.json", "r", encoding="utf-8") as f:
            tum_icerikler = json.load(f)
    except Exception as e:
        st.error(f"❌ Dosya okuma hatası: {e}")
        tum_icerikler = []
    
    # İçerik yoksa bilgi göster
    if not tum_icerikler:
        st.info("📝 Henüz içerik eklenmemiş. Önce 'İçerik Ekle' sekmesinden JSON ekle!")
        
        # Hızlı test butonu
        if st.button("🧪 Test İçeriği Oluştur"):
            test_icerik = {
                "icerik_tipi": "kelime_tablosu",
                "baslik": "TEST - Financial Terms",
                "kelimeler": [
                    {
                        "kelime": "financial",
                        "tur": "adjective", 
                        "tr_anlam": "finansal",
                        "es_anlamli": ["monetary", "economic"],
                        "ornek_cumle": "Financial planning is essential for students."
                    }
                ]
            }
            success, mesaj = icerik_dosyasina_kaydet(test_icerik)
            if success:
                st.success("✅ Test içeriği eklendi! Sayfayı yenile...")
                st.rerun()
    
    else:
        # İçerikleri göster
        st.success(f"✅ {len(tum_icerikler)} içerik bulundu!")
        
        # Her içeriği göster
        for icerik in tum_icerikler:
            icerik_tipi = icerik.get('icerik_tipi', 'bilinmeyen')
            baslik = icerik.get('baslik', 'İsimsiz İçerik')
            icerik_id = icerik.get('id', 'unknown')
            
            with st.expander(f"📁 {baslik} ({icerik_tipi}) - ID: {icerik_id}"):
                
                if icerik_tipi == "kelime_tablosu":
                    kelimeler = icerik.get('kelimeler', [])
                    st.write(f"**Toplam {len(kelimeler)} kelime**")
                    
                    for i, kelime in enumerate(kelimeler, 1):
                        st.write(f"**{i}. {kelime.get('kelime', '')}** (*{kelime.get('tur', '')}*)")
                        st.write(f"**Türkçe:** {kelime.get('tr_anlam', '')}")
                        st.write(f"**Eş Anlamlı:** {', '.join(kelime.get('es_anlamli', []))}")  # DÜZELTİLDİ!
                        st.write(f"**Örnek:** {kelime.get('ornek_cumle', '')}")
                        st.divider()
                
                elif icerik_tipi == "paragraf":
                    st.subheader("🇺🇸 İngilizce Paragraf")
                    st.write(icerik.get('ingilizce_paragraf', ''))
                    st.subheader("🇹🇷 Türkçe Çeviri") 
                    st.write(icerik.get('turkce_ceviri', ''))
                
                elif icerik_tipi == "test_sorulari":
                    st.write("Test soruları burada gösterilecek")
                
                # Sil butonu
                if st.button(f"🗑️ Sil", key=f"sil_{icerik_id}"):
                    yeni_icerikler = [i for i in tum_icerikler if i.get('id') != icerik_id]
                    with open("gemini_icerikler.json", "w", encoding="utf-8") as f:
                        json.dump(yeni_icerikler, f, ensure_ascii=False, indent=2)
                    st.success("✅ İçerik silindi!")
                    st.rerun()
# -------------------- İÇERİK EKLEME SİSTEMİ --------------------
elif menu == "➕ İçerik Ekle":
    st.header("➕ İçerik Ekle")
    
    st.subheader("🚀 Gemini JSON İçeriği Ekle")
    
    json_input = st.text_area(
        "Gemini'den gelen JSON'u buraya yapıştır:",
        height=200,
        placeholder='{"icerik_tipi": "kelime_tablosu", "baslik": "Örnek", "kelimeler": [...]}'
    )
    
    if st.button("📤 İçeriği İşle", type="primary"):
        if json_input.strip():
            try:
                success, mesaj = gemini_json_isleyici(json_input)
                if success:
                    st.success(mesaj)
                    st.balloons()
                    
                    veri = json.loads(json_input)
                    with st.expander("📋 Alınan JSON'u Gör"):
                        st.json(veri)
                        
                    if st.button("💾 Dosyaya Kaydet"):
                        save_success, save_mesaj = icerik_dosyasina_kaydet(veri)
                        if save_success:
                            st.success(save_mesaj)
                        else:
                            st.error(save_mesaj)
                else:
                    st.error(mesaj)
            except Exception as e:
                st.error(f"❌ Hata: {e}")
        else:
            st.warning("⚠️ Lütfen JSON yapıştırın")

# -------------------- AYARLAR SAYFASI --------------------
elif menu == "🔧 Ayarlar":
    st.header("🔧 Ayarlar")
    
    st.subheader("💾 Veri Yönetimi")
    
    if st.button("📦 Yedek Oluştur"):
        try:
            with open("gemini_icerikler.json", "r", encoding="utf-8") as f:
                icerikler = json.load(f)
            
            yedek_adi = f"yds_yedek_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(yedek_adi, "w", encoding="utf-8") as f:
                json.dump(icerikler, f, ensure_ascii=False, indent=2)
            
            st.success(f"✅ Yedek oluşturuldu: {yedek_adi}")
            
        except Exception as e:
            st.error(f"❌ Yedekleme hatası: {e}")

# -------------------- BOŞ SAYFALAR --------------------
elif menu == "🎯 YDS Çalışma Soruları":
    st.header("🎯 YDS Çalışma Soruları")
    st.info("🚧 Bu bölüm yakında eklenecek...")

elif menu == "📝 Deneme Testleri":
    st.header("📝 Deneme Testleri")
    st.info("🚧 Bu bölüm yakında eklenecek...")

elif menu == "🏆 Çıkmış Sorular":
    st.header("🏆 Çıkmış Sorular")
    st.info("🚧 Bu bölüm yakında eklenecek...")

# -------------------- UYGULAMA SONU --------------------
