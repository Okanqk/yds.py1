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
        # -------------------- ÜNİTE SİSTEMİ FONKSİYONLARI --------------------
def unite_ilerleme_kaydet(unite_id, bolum_index, tamamlandi=True):
    """Ünite ilerlemesini kaydeder"""
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
    """Ünite ilerlemesini getirir"""
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

def bolum_goster(unite_data, bolum_index, ilerleme):
    """Her bölümü gösterir"""
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

                # Kelime testi - Expander içinde
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
                secilen_cevap = secim[0]  # A, B, C
                dogru_cevap = soru.get("cevap", "")
                
                if secilen_cevap == dogru_cevap:
                    st.success("✅ Doğru!")
                else:
                    st.error(f"❌ Yanlış! Doğru cevap: {dogru_cevap}")
                
                st.write(f"**Çözüm:** {soru.get('cozum', '')}")
            
            st.divider()
    
    # Bölüm tamamlama butonu
    bolum_tamamlandi = bolum_index in ilerleme["tamamlanan_bolumler"]
    
    if bolum_tamamlandi:
        st.success("✅ Bu bölümü tamamladın!")
    else:
        if st.button("✅ Bölümü Tamamla", type="primary", key=f"tamamla_{bolum_index}"):
            if unite_ilerleme_kaydet(unite_data["unite_adi"], bolum_index):
                # İSTATİSTİK KAYDI EKLENDİ
                kelime_sayisi = len(kelimeler) if bolum_tipi == "kelime_tablosu" else 0
                bolum_tamamlandi_kaydet(unite_data["unite_adi"], bolum_index, kelime_sayisi)
                st.success("🎉 Bölüm tamamlandı!")
                st.rerun()
# -------------------- ÜNİTE FONKSİYONLARI BURADA BİTİYOR --------------------
# -------------------- ÜNİTE FONKSİYONLARI BURADA BİTİYOR --------------------
# -------------------- İSTATİSTİK VERİ TOPLAMA SİSTEMİ --------------------
def istatistik_veri_kaydet(olay_tipi, **kwargs):
    """İstatistik verilerini JSON'a kaydeder"""
    try:
        istatistik_dosyasi = "istatistik_verileri.json"
        
        # Mevcut verileri oku veya yeni oluştur
        if os.path.exists(istatistik_dosyasi):
            with open(istatistik_dosyasi, "r", encoding="utf-8") as f:
                veriler = json.load(f)
        else:
            veriler = []
        
        # Yeni kayıt oluştur
        yeni_kayit = {
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "olay_tipi": olay_tipi,
            **kwargs
        }
        
        veriler.append(yeni_kayit)
        
        # Dosyaya kaydet
        with open(istatistik_dosyasi, "w", encoding="utf-8") as f:
            json.dump(veriler, f, ensure_ascii=False, indent=2)
            
        return True
    except Exception as e:
        print(f"İstatistik kayıt hatası: {e}")
        return False

def bolum_tamamlandi_kaydet(unite_adi, bolum_index, kelime_sayisi):
    """Bölüm tamamlandığında istatistik kaydeder"""
    return istatistik_veri_kaydet(
        olay_tipi="bolum_tamamlandi",
        unite_adi=unite_adi,
        bolum_index=bolum_index,
        kelime_sayisi=kelime_sayisi
    )

def test_tamamlandi_kaydet(unite_adi, dogru_sayisi, yanlis_sayisi, toplam_soru):
    """Test tamamlandığında istatistik kaydeder"""
    return istatistik_veri_kaydet(
        olay_tipi="test_tamamlandi",
        unite_adi=unite_adi,
        dogru_sayisi=dogru_sayisi,
        yanlis_sayisi=yanlis_sayisi,
        toplam_soru=toplam_soru,
        basari_orani=dogru_sayisi/toplam_soru if toplam_soru > 0 else 0
    )

# -------------------- KELİME TESTİ FONKSİYONU --------------------
def kelime_testi_uygulamasi(kelimeler, bolum_index):
    """Basit kelime testi uygulaması"""
    
    if not kelimeler:
        st.warning("⚠️ Bu bölümde test edilecek kelime bulunamadı.")
        return
    
    # Test durumu için session state
    if f'test_durum_{bolum_index}' not in st.session_state:
        st.session_state[f'test_durum_{bolum_index}'] = {
            'cevaplar': {},
            'goster': {},
            'secenekler': {}  # Yeni: Şıkları saklayacağız
        }
    
    st.write("**İngilizce kelimenin Türkçe anlamını seçin:**")
    
    dogru_sayisi = 0
    toplam_soru = len(kelimeler)
    
    for i, kelime in enumerate(kelimeler):
        st.write(f"**{i+1}. {kelime['kelime']}**")
        
        # Şıkları hazırla - SADECE İLK SEFERDE shuffle yap
        secenekler_key = f"secenekler_{i}"
        if secenekler_key not in st.session_state[f'test_durum_{bolum_index}']['secenekler']:
            import random
            diger_kelimeler = [k for k in kelimeler if k != kelime]
            yanlis_secenekler = random.sample(diger_kelimeler, min(2, len(diger_kelimeler)))
            
            secenekler = [kelime['tr_anlam']] + [k['tr_anlam'] for k in yanlis_secenekler]
            random.shuffle(secenekler)
            st.session_state[f'test_durum_{bolum_index}']['secenekler'][secenekler_key] = secenekler
        else:
            secenekler = st.session_state[f'test_durum_{bolum_index}']['secenekler'][secenekler_key]
        
        # Seçim için unique key
        secim_key = f"sec_{i}"
        
        # Seçim yapılmış mı kontrol et (ilk seferde ilk şıkkı seç)
        if secim_key not in st.session_state[f'test_durum_{bolum_index}']['cevaplar']:
            st.session_state[f'test_durum_{bolum_index}']['cevaplar'][secim_key] = secenekler[0]
        
        # Radio butonu
        secim = st.radio(
            "Anlamı nedir?",
            secenekler,
            index=secenekler.index(st.session_state[f'test_durum_{bolum_index}']['cevaplar'][secim_key]),
            key=f"radio_{bolum_index}_{i}"
        )
        
        # Seçimi kaydet
        st.session_state[f'test_durum_{bolum_index}']['cevaplar'][secim_key] = secim
        
        # Cevap göster butonu
        goster_key = f"goster_{i}"
        if st.button("Cevabı Kontrol Et", key=f"btn_{bolum_index}_{i}"):
            st.session_state[f'test_durum_{bolum_index}']['goster'][goster_key] = True
        
        # Cevabı göster
        if goster_key in st.session_state[f'test_durum_{bolum_index}']['goster']:
            if secim == kelime['tr_anlam']:
                st.success("✅ Doğru!")
                dogru_sayisi += 1
            else:
                st.error(f"❌ Yanlış! Doğru cevap: **{kelime['tr_anlam']}**")
            
            # Mini bilgi
            with st.expander("ℹ️ Kelime Detayı"):
                st.write(f"**Tür:** {kelime.get('tur', '')}")
                if kelime.get('es_anlamli'):
                    st.write(f"**Eş Anlamlı:** {', '.join(kelime['es_anlamli'])}")
                if kelime.get('ornek_cumle'):
                    st.write(f"**Örnek:** {kelime['ornek_cumle']}")
        
        st.divider()
    
        # Sonuç
    if toplam_soru > 0:
        st.info(f"**Test Sonucu: {dogru_sayisi}/{toplam_soru} doğru**")
        
        # İSTATİSTİK KAYDI
        if dogru_sayisi + yanlis_sayisi > 0:  # En az 1 soru cevaplanmışsa
            test_tamamlandi_kaydet(
                unite_adi="Kelime Testi", 
                dogru_sayisi=dogru_sayisi,
                yanlis_sayisi=yanlis_sayisi, 
                toplam_soru=toplam_soru
            )
        
        # Testi sıfırla
        if st.button("🔄 Testi Sıfırla", key=f"reset_{bolum_index}"):
            st.session_state[f'test_durum_{bolum_index}'] = {'cevaplar': {}, 'goster': {}, 'secenekler': {}}
            st.rerun()

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

# -------------------- YENİ PASSAGEWORK SAYFASI (ÜNİTE SİSTEMİ) --------------------
elif menu == "📚 PassageWork Çalışma":
    st.header("📚 PassageWork Çalışma - Ünite Sistemi")
    
    # İçerikleri yükle
    try:
        with open("gemini_icerikler.json", "r", encoding="utf-8") as f:
            tum_icerikler = json.load(f)
    except Exception as e:
        st.error(f"❌ Dosya okuma hatası: {e}")
        tum_icerikler = []
    
    # Sadece ünite içeriklerini filtrele
    unite_icerikler = [icerik for icerik in tum_icerikler if icerik.get("icerik_tipi") == "unite"]
    
    if not unite_icerikler:
        st.info("📝 Henüz ünite eklenmemiş. Önce 'İçerik Ekle' sekmesinden ÜNİTE JSON'u ekle!")
        
        # Örnek ünite formatı
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
    },
    {
      "bolum_tipi": "paragraf",
      "baslik": "Okuma Parçası",
      "ingilizce_paragraf": "Organising your financial affairs is not easy...",
      "turkce_ceviri": "Finansal işlerinizi organize etmek kolay değildir...",
      "onemli_kelimeler": ["financial", "grant", "organising"]
    },
    {
      "bolum_tipi": "dilbilgisi_analizi", 
      "baslik": "Dilbilgisi Notları",
      "aciklama": "Bu paragraftaki önemli dilbilgisi yapıları",
      "notlar": ["Present Simple tense", "Conditional sentences"]
    },
    {
      "bolum_tipi": "test",
      "baslik": "Ünite Testi", 
      "sorular": [
        {
          "soru_no": 1,
          "soru_metni": "'Financial' kelimesinin eş anlamlısı hangisidir?",
          "siklar": ["A) monetary", "B) overseas", "C) grant"],
          "cevap": "A",
          "cozum": "'Financial' = finansal, 'monetary' = parasal"
        }
      ]
    }
  ]
}
            """, language="json")
    
    else:
        # Ünite seçimi
        st.success(f"✅ {len(unite_icerikler)} ünite bulundu!")
        
        # Ünite listesi
        secilen_unite_index = st.selectbox(
            "📋 Çalışmak istediğin üniteyi seç:",
            range(len(unite_icerikler)),
            format_func=lambda i: f"{unite_icerikler[i].get('unite_adi', 'İsimsiz')} - Seviye: {unite_icerikler[i].get('seviye', 'unknown')}"
        )
        
        secilen_unite = unite_icerikler[secilen_unite_index]
        unite_adi = secilen_unite.get("unite_adi", "İsimsiz Ünite")
        bolumler = secilen_unite.get("bolumler", [])
        
        # İlerlemeyi getir
        ilerleme = unite_ilerleme_getir(unite_adi)
        
        # İlerleme çubuğu
        tamamlanan_sayi = len(ilerleme["tamamlanan_bolumler"])
        toplam_bolum = len(bolumler)
        ilerleme_yuzdesi = (tamamlanan_sayi / toplam_bolum) * 100 if toplam_bolum > 0 else 0
        
        st.subheader(f"📊 İlerleme: %{ilerleme_yuzdesi:.0f}")
        st.progress(ilerleme_yuzdesi / 100)
        st.write(f"✅ {tamamlanan_sayi}/{toplam_bolum} bölüm tamamlandı")
        
        # Bölüm seçimi
        bolum_isimleri = [f"{i+1}. {bolum['baslik']} ({bolum['bolum_tipi']})" for i, bolum in enumerate(bolumler)]
        
        # Otomatik olarak son kaldığın bölümü seç
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
        
        # Seçilen bölümü göster
        bolum_goster(secilen_unite, secilen_bolum_index, ilerleme)
        
        # Navigasyon butonları
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
# -------------------- YENİ PASSAGEWORK SAYFASI BURADA BİTİYOR --------------------
# -------------------- İÇERİK EKLEME SİSTEMİ --------------------
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
                # JSON'u işle
                success, mesaj = gemini_json_isleyici(json_input)
                if success:
                    veri = json.loads(json_input)
                    
                    # HEMEN KAYDET (butona gerek yok)
                    save_success, save_mesaj = icerik_dosyasina_kaydet(veri)
                    if save_success:
                        st.success("✅ İçerik başarıyla kaydedildi!")
                        st.balloons()
                        
                        # Otomatik yenile
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
# AYARLAR SEKMESİNE BUNU EKLE:
elif menu == "🔧 Ayarlar":
    st.header("🔧 Ayarlar")
    
    # DEBUG: Dosya içeriğini göster
    st.subheader("🐛 Debug - Dosya İçeriği")
    try:
        with open("gemini_icerikler.json", "r", encoding="utf-8") as f:
            icerikler = json.load(f)
        st.write(f"**Dosyadaki içerik sayısı:** {len(icerikler)}")
        st.json(icerikler)  # Tüm içeriği göster
    except Exception as e:
        st.error(f"❌ Dosya okunamadı: {e}")
# -------------------- İSTATİSTİKLERİM SAYFASI --------------------
elif menu == "📊 İstatistiklerim":
    st.header("📊 İstatistiklerim")
    
    # İstatistik verilerini yükle
    try:
        with open("istatistik_verileri.json", "r", encoding="utf-8") as f:
            istatistik_verileri = json.load(f)
    except:
        istatistik_verileri = []
        st.info("📝 Henüz istatistik verisi yok. Biraz çalışmaya başla!")
    
    if not istatistik_verileri:
        st.info("📝 Henüz istatistik verisi yok. Biraz çalışmaya başla!")
    else:
        # TEMEL METRİKLER
        st.subheader("🏆 Genel İlerleme")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Toplam çalışılan gün sayısı
            tarihler = set([veri["tarih"][:10] for veri in istatistik_verileri])
            st.metric("📅 Çalışılan Gün", len(tarihler))
        
        with col2:
            # Toplam bölüm sayısı
            bolum_sayisi = len([v for v in istatistik_verileri if v["olay_tipi"] == "bolum_tamamlandi"])
            st.metric("✅ Tamamlanan Bölüm", bolum_sayisi)
        
        with col3:
            # Toplam kelime sayısı
            toplam_kelime = sum([v.get("kelime_sayisi", 0) for v in istatistik_verileri])
            st.metric("📚 Toplam Kelime", toplam_kelime)
        
        with col4:
            # Ortalama başarı oranı
            testler = [v for v in istatistik_verileri if v["olay_tipi"] == "test_tamamlandi"]
            if testler:
                ortalama_basari = sum([v.get("basari_orani", 0) for v in testler]) / len(testler)
                st.metric("📊 Başarı Oranı", f"%{ortalama_basari*100:.0f}")
            else:
                st.metric("📊 Başarı Oranı", "%-")
        
        # GÜNLÜK AKTİVİTE
        st.subheader("📈 Günlük Aktivite")
        
        # Son 7 günlük veri
        from datetime import datetime, timedelta
        bugun = datetime.now().date()
        son_7_gun = [(bugun - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
        
        gunluk_veriler = []
        for gun in son_7_gun:
            gun_verileri = [v for v in istatistik_verileri if v["tarih"][:10] == gun]
            gunluk_veriler.append(len(gun_verileri))
        
        # Çizgi grafik
        chart_data = {"Günler": son_7_gun, "Aktivite": gunluk_veriler}
        st.line_chart(chart_data, x="Günler", y="Aktivite")
        
        # DETAYLI LİSTE
        st.subheader("📋 Detaylı Kayıtlar")
        
        for veri in reversed(istatistik_verileri[-10:]):  # Son 10 kayıt
            with st.expander(f"{veri['tarih']} - {veri['olay_tipi']}"):
                if veri["olay_tipi"] == "bolum_tamamlandi":
                    st.write(f"**Ünite:** {veri.get('unite_adi', '')}")
                    st.write(f"**Bölüm:** {veri.get('bolum_index', '') + 1}")
                    st.write(f"**Kelime Sayısı:** {veri.get('kelime_sayisi', 0)}")
                elif veri["olay_tipi"] == "test_tamamlandi":
                    st.write(f"**Doğru:** {veri.get('dogru_sayisi', 0)}")
                    st.write(f"**Yanlış:** {veri.get('yanlis_sayisi', 0)}")
                    st.write(f"**Başarı:** %{veri.get('basari_orani', 0)*100:.0f}")
        
        # AI ANALİZ BUTONU (şimdilik boş)
        st.divider()
        if st.button("🤖 AI ile Detaylı Analiz Yap"):
            st.info("🚧 AI analiz özelliği yakında eklenecek...")

# -------------------- İSTATİSTİK SAYFASI BİTTİ --------------------
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
