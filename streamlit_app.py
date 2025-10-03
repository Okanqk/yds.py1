# -------------------- TEMEL İMPORTLAR ve AYARLAR --------------------
import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="YDS Test Uygulaması", page_icon="📄", layout="wide")
st.title("📄 YDS Test Uygulaması v4.0")
# -------------------- TEMEL İMPORTLAR BURADA BİTİYOR --------------------
# -------------------- GEMINI JSON İŞLEYİCİ MODÜLÜ --------------------
def gemini_json_isleyici(gelen_veri):
    """
    Gemini'den gelen JSON'u işler ve kaydeder
    """
    try:
        # JSON'u kontrol et
        if isinstance(gelen_veri, str):
            veri = json.loads(gelen_veri)
        else:
            veri = gelen_veri
            
        if not isinstance(veri, dict):
            return False, "❌ JSON bir obje olmalı"
            
        icerik_tipi = veri.get("icerik_tipi")
        if not icerik_tipi:
            return False, "❌ 'icerik_tipi' alanı gerekli"
        
        # Başarılı
        return True, f"✅ {icerik_tipi} içeriği başarıyla alındı!"
        
    except json.JSONDecodeError:
        return False, "❌ Geçersiz JSON formatı"
    except Exception as e:
        return False, f"❌ İşleme hatası: {e}"

def icerik_dosyasina_kaydet(veri, dosya_adi="gemini_icerikler.json"):
    """
    İçeriği JSON dosyasına kaydeder
    """
    try:
        # Dosya varsa oku, yoksa yeni oluştur
        if os.path.exists(dosya_adi):
            with open(dosya_adi, "r", encoding="utf-8") as f:
                mevcut_icerik = json.load(f)
        else:
            mevcut_icerik = []
            
        # Yeni içeriği ekle
        veri["eklenme_tarihi"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        veri["id"] = len(mevcut_icerik) + 1
        
        mevcut_icerik.append(veri)
        
        # Dosyaya yaz
        with open(dosya_adi, "w", encoding="utf-8") as f:
            json.dump(mevcut_icerik, f, ensure_ascii=False, indent=2)
            
        return True, f"✅ İçerik başarıyla kaydedildi! (Dosya: {dosya_adi})"
        
    except Exception as e:
        return False, f"❌ Kaydetme hatası: {e}"
# -------------------- GEMINI MODÜLÜ BURADA BİTİYOR --------------------
# -------------------- ANA MENÜ --------------------
menu = st.sidebar.radio(
    "📋 Menü",
    ["🏠 Ana Sayfa", "📚 PassageWork Çalışma", "🎯 YDS Çalışma Soruları", "📝 Deneme Testleri", "🏆 Çıkmış Sorular", "➕ İçerik Ekle", "🔧 Ayarlar"],
    key="main_menu"
)
# -------------------- ANA MENÜ BURADA BİTİYOR --------------------
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
# -------------------- ANA SAYFA BURADA BİTİYOR --------------------
# -------------------- İÇERİK EKLEME SİSTEMİ --------------------
elif menu == "➕ İçerik Ekle":
    st.header("➕ İçerik Ekle")
    
    st.subheader("🚀 Gemini JSON İçeriği Ekle")
    
    # JSON yapıştırma
    json_input = st.text_area(
        "Gemini'den gelen JSON'u buraya yapıştır:",
        height=200,
        placeholder='{"icerik_tipi": "kelime_tablosu", "baslik": "Örnek", "kelimeler": [...]}'
    )
    
    if st.button("📤 İçeriği İşle", type="primary"):
        if json_input.strip():
            try:
                # Gemini modülünü kullan
                success, mesaj = gemini_json_isleyici(json_input)
                if success:
                    st.success(mesaj)
                    st.balloons()
                    
                    # JSON'u göster
                    veri = json.loads(json_input)
                    with st.expander("📋 Alınan JSON'u Gör"):
                        st.json(veri)
                        
                    # Dosyaya kaydet butonu
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
    
    # Dosya yükleme
    st.subheader("📁 JSON Dosyası Yükle")
    
    uploaded_file = st.file_uploader(
        "JSON dosyası seçin:",
        type=['json', 'txt']
    )
    
    if uploaded_file is not None:
        st.write(f"**Dosya:** {uploaded_file.name}")
        
        if st.button("📁 Dosyayı İşle", key="file_process"):
            try:
                file_content = uploaded_file.getvalue().decode("utf-8")
                
                # Gemini modülünü kullan
                success, mesaj = gemini_json_isleyici(file_content)
                if success:
                    st.success(mesaj)
                    st.balloons()
                    
                    # JSON'u göster
                    veri = json.loads(file_content)
                    with st.expander("📋 Dosya İçeriğini Gör"):
                        st.json(veri)
                        
                    # Dosyaya kaydet butonu
                    if st.button("💾 Dosyaya Kaydet", key="save_file"):
                        save_success, save_mesaj = icerik_dosyasina_kaydet(veri)
                        if save_success:
                            st.success(save_mesaj)
                        else:
                            st.error(save_mesaj)
                else:
                    st.error(mesaj)
            except Exception as e:
                st.error(f"❌ Dosya hatası: {e}")
# -------------------- İÇERİK EKLEME BURADA BİTİYOR --------------------
# -------------------- BOŞ SAYFALAR --------------------
elif menu == "📚 PassageWork Çalışma":
    st.header("📚 PassageWork Çalışma")
    st.info("🚧 Bu bölüm yakında eklenecek...")
    st.write("Gemini'den eklediğin PassageWork içerikleri burada görünecek.")

elif menu == "🎯 YDS Çalışma Soruları":
    st.header("🎯 YDS Çalışma Soruları")
    st.info("🚧 Bu bölüm yakında eklenecek...")

elif menu == "📝 Deneme Testleri":
    st.header("📝 Deneme Testleri")
    st.info("🚧 Bu bölüm yakında eklenecek...")

elif menu == "🏆 Çıkmış Sorular":
    st.header("🏆 Çıkmış Sorular")
    st.info("🚧 Bu bölüm yakında eklenecek...")

elif menu == "🔧 Ayarlar":
    st.header("🔧 Ayarlar")
    st.info("🚧 Bu bölüm yakında eklenecek...")
# -------------------- BOŞ SAYFALAR BURADA BİTİYOR --------------------
# -------------------- TEST SİSTEMİ FONKSİYONLARI --------------------
def test_sorusu_goster(soru_data):
    """
    Test sorusunu gösterir ve cevabı işler
    """
    st.write(f"**Soru {soru_data.get('soru_no', '')}:** {soru_data.get('soru_metni', '')}")
    
    # Seçenekleri göster
    secenekler = soru_data.get('siklar', [])
    secim = st.radio("Seçenekler:", [f"{s['secenek']}) {s['metin']}" for s in secenekler])
    
    # Cevap butonu
    if st.button("Cevapla", key=f"cevap_{soru_data.get('id', '')}"):
        # Seçilen cevabı kontrol et
        secilen_cevap = secim[0]  # A, B, C, D, E
        dogru_cevap = soru_data.get('cevap', '')
        
        if secilen_cevap == dogru_cevap:
            st.success("✅ Doğru!")
        else:
            st.error(f"❌ Yanlış! Doğru cevap: {dogru_cevap}")
        
        # Çözümü göster
        cozum = soru_data.get('cozum', '')
        if cozum:
            with st.expander("💡 Çözüm"):
                st.write(cozum)
    
    st.divider()

def kelime_testi_goster(kelime_data):
    """
    Kelime testi gösterir
    """
    kelime = kelime_data.get('kelime', '')
    st.write(f"**Kelime:** {kelime}")
    
    # Türkçe anlamı sor
    secenekler = kelime_data.get('secenekler', [])
    if secenekler:
        secim = st.radio("Türkçe anlamı nedir?", secenekler)
        
        if st.button("Kontrol Et", key=f"kelime_{kelime}"):
            dogru_cevap = kelime_data.get('tr_anlam', '')
            if secim == dogru_cevap:
                st.success("✅ Doğru!")
            else:
                st.error(f"❌ Yanlış! Doğru cevap: {dogru_cevap}")
    
    st.divider()
# -------------------- TEST FONKSİYONLARI BURADA BİTİYOR --------------------
# -------------------- PASSAGEWORK ÇALIŞMA SAYFASI --------------------
elif menu == "📚 PassageWork Çalışma":
    st.header("📚 PassageWork Çalışma")
    
    # İçerik yükleme
    try:
        with open("gemini_icerikler.json", "r", encoding="utf-8") as f:
            tum_icerikler = json.load(f)
    except:
        tum_icerikler = []
    
    if not tum_icerikler:
        st.info("📝 Henüz içerik eklenmemiş. Önce 'İçerik Ekle' sekmesinden JSON ekle!")
        
        # Örnek içerik göster
        st.subheader("🎯 Örnek JSON Formatları")
        
        with st.expander("📝 Kelime Tablosu Örneği"):
            st.code("""
{
  "icerik_tipi": "kelime_tablosu",
  "baslik": "MONEY - Önemli Kelimeler", 
  "kelimeler": [
    {
      "kelime": "financial",
      "tur": "adjective",
      "tr_anlam": "finansal",
      "es_anlamli": ["monetary", "economic"],
      "ornek_cumle": "Organising financial affairs is important."
    }
  ]
}
            """, language="json")
        
        with st.expander("📄 Paragraf Örneği"):
            st.code("""
{
  "icerik_tipi": "paragraf",
  "baslik": "MONEY - Banking Guide", 
  "ingilizce_paragraf": "Organising your financial affairs is not easy...",
  "turkce_ceviri": "Finansal işlerinizi organize etmek kolay değildir...",
  "onemli_kelimeler": ["financial", "organising", "affairs"]
}
            """, language="json")
        
        with st.expander("❓ Test Sorusu Örneği"):
            st.code("""
{
  "icerik_tipi": "test_sorulari",
  "baslik": "MONEY Test Soruları",
  "sorular": [
    {
      "soru_no": 1,
      "soru_metni": "'Financial' kelimesinin eş anlamlısı hangisidir?",
      "siklar": [
        {"secenek": "A", "metin": "monetary"},
        {"secenek": "B", "metin": "overseas"}, 
        {"secenek": "C", "metin": "grant"}
      ],
      "cevap": "A",
      "cozum": "'Financial' kelimesi 'finansal' demektir. 'Monetary' de 'parasal' anlamında eş anlamlıdır."
    }
  ]
}
            """, language="json")
    
    else:
        # İçerikleri göster
        st.success(f"✅ {len(tum_icerikler)} içerik bulundu!")
        
        for icerik in tum_icerikler:
            icerik_tipi = icerik.get('icerik_tipi', '')
            baslik = icerik.get('baslik', 'İsimsiz İçerik')
            
            with st.expander(f"📁 {baslik} ({icerik_tipi})"):
                
                if icerik_tipi == "kelime_tablosu":
                    st.subheader("📝 Kelimeler")
                    kelimeler = icerik.get('kelimeler', [])
                    
                    for kelime in kelimeler:
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.write(f"**{kelime.get('kelime', '')}**")
                            st.write(f"*{kelime.get('tur', '')}*")
                        with col2:
                            st.write(f"**Anlam:** {kelime.get('tr_anlam', '')}")
                            st.write(f"**Eş Anlamlı:** {', '.join(kelime.get('es_anlamli', []))}")
                            st.write(f"**Örnek:** {kelime.get('ornek_cumle', '')}")
                        st.divider()
                
                elif icerik_tipi == "paragraf":
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("🇺🇸 İngilizce")
                        st.write(icerik.get('ingilizce_paragraf', ''))
                    with col2:
                        st.subheader("🇹🇷 Türkçe")
                        st.write(icerik.get('turkce_ceviri', ''))
                    
                    st.subheader("🔑 Önemli Kelimeler")
                    st.write(", ".join(icerik.get('onemli_kelimeler', [])))
                
                elif icerik_tipi == "test_sorulari":
                    sorular = icerik.get('sorular', [])
                    for soru in sorular:
                        test_sorusu_goster(soru)
                
                # Sil butonu
                if st.button("🗑️ Sil", key=f"sil_{icerik.get('id', '')}"):
                    # Silme işlemi
                    yeni_icerikler = [i for i in tum_icerikler if i.get('id') != icerik.get('id')]
                    with open("gemini_icerikler.json", "w", encoding="utf-8") as f:
                        json.dump(yeni_icerikler, f, ensure_ascii=False, indent=2)
                    st.success("✅ İçerik silindi!")
                    st.rerun()
# -------------------- PASSAGEWORK SAYFASI BURADA BİTİYOR --------------------
# -------------------- AYARLAR SAYFASI --------------------
elif menu == "🔧 Ayarlar":
    st.header("🔧 Ayarlar")
    
    st.subheader("💾 Veri Yönetimi")
    
    # Yedekleme
    if st.button("📦 Yedek Oluştur"):
        try:
            with open("gemini_icerikler.json", "r", encoding="utf-8") as f:
                icerikler = json.load(f)
            
            yedek_adi = f"yds_yedek_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(yedek_adi, "w", encoding="utf-8") as f:
                json.dump(icerikler, f, ensure_ascii=False, indent=2)
            
            st.success(f"✅ Yedek oluşturuldu: {yedek_adi}")
            
            # Yedek dosyasını indirme
            with open(yedek_adi, "r", encoding="utf-8") as f:
                yedek_veri = f.read()
            
            st.download_button(
                "⬇️ Yedeği İndir",
                yedek_veri,
                yedek_adi,
                "application/json"
            )
            
        except Exception as e:
            st.error(f"❌ Yedekleme hatası: {e}")
    
    # İstatistikler
    st.subheader("📊 İstatistikler")
    
    try:
        with open("gemini_icerikler.json", "r", encoding="utf-8") as f:
            icerikler = json.load(f)
        
        toplam_icerik = len(icerikler)
        
        # İçerik tiplerine göre sayım
        tip_sayilari = {}
        for icerik in icerikler:
            tip = icerik.get('icerik_tipi', 'bilinmeyen')
            tip_sayilari[tip] = tip_sayilari.get(tip, 0) + 1
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Toplam İçerik", toplam_icerik)
        with col2:
            st.metric("Kelime Tabloları", tip_sayilari.get('kelime_tablosu', 0))
        with col3:
            st.metric("Test Soruları", tip_sayilari.get('test_sorulari', 0))
        
    except:
        st.info("📝 Henüz içerik yok")
    
    # Temizleme
    st.subheader("🧹 Temizlik")
    
    if st.button("🗑️ Tüm Verileri Temizle", type="secondary"):
        if st.button("⚠️ EMİN MİSİN?", key="confirm_clear"):
            try:
                with open("gemini_icerikler.json", "w", encoding="utf-8") as f:
                    json.dump([], f)
                st.success("✅ Tüm veriler temizlendi!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Temizleme hatası: {e}")
# -------------------- AYARLAR SAYFASI BURADA BİTİYOR --------------------
