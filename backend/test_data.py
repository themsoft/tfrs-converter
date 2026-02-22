"""Örnek mizan dosyası oluştur (test için)."""
import pandas as pd

data = [
    {"Hesap Kodu": "100", "Hesap Adı": "Kasa", "Borç Bakiye": 150000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "102", "Hesap Adı": "Bankalar", "Borç Bakiye": 2500000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "120", "Hesap Adı": "Alıcılar", "Borç Bakiye": 1800000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "121", "Hesap Adı": "Alacak Senetleri", "Borç Bakiye": 500000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "128", "Hesap Adı": "Şüpheli Ticari Alacaklar", "Borç Bakiye": 200000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "129", "Hesap Adı": "Şüpheli Ticari Alacak Karşılığı (-)", "Borç Bakiye": 0, "Alacak Bakiye": 100000},
    {"Hesap Kodu": "150", "Hesap Adı": "İlk Madde ve Malzeme", "Borç Bakiye": 350000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "153", "Hesap Adı": "Ticari Mallar", "Borç Bakiye": 750000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "180", "Hesap Adı": "Gelecek Aylara Ait Giderler", "Borç Bakiye": 80000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "190", "Hesap Adı": "Devreden KDV", "Borç Bakiye": 120000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "252", "Hesap Adı": "Binalar", "Borç Bakiye": 3000000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "253", "Hesap Adı": "Tesis, Makine ve Cihazlar", "Borç Bakiye": 2000000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "254", "Hesap Adı": "Taşıtlar", "Borç Bakiye": 800000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "255", "Hesap Adı": "Demirbaşlar", "Borç Bakiye": 400000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "257", "Hesap Adı": "Birikmiş Amortismanlar (-)", "Borç Bakiye": 0, "Alacak Bakiye": 1500000},
    {"Hesap Kodu": "260", "Hesap Adı": "Haklar", "Borç Bakiye": 300000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "264", "Hesap Adı": "Özel Maliyetler", "Borç Bakiye": 200000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "268", "Hesap Adı": "Birikmiş İtfalar (-)", "Borç Bakiye": 0, "Alacak Bakiye": 150000},
    {"Hesap Kodu": "300", "Hesap Adı": "Banka Kredileri", "Borç Bakiye": 0, "Alacak Bakiye": 1200000},
    {"Hesap Kodu": "320", "Hesap Adı": "Satıcılar", "Borç Bakiye": 0, "Alacak Bakiye": 1400000},
    {"Hesap Kodu": "321", "Hesap Adı": "Borç Senetleri", "Borç Bakiye": 0, "Alacak Bakiye": 300000},
    {"Hesap Kodu": "335", "Hesap Adı": "Personele Borçlar", "Borç Bakiye": 0, "Alacak Bakiye": 250000},
    {"Hesap Kodu": "340", "Hesap Adı": "Alınan Avanslar", "Borç Bakiye": 0, "Alacak Bakiye": 180000},
    {"Hesap Kodu": "360", "Hesap Adı": "Ödenecek Vergi ve Fonlar", "Borç Bakiye": 0, "Alacak Bakiye": 320000},
    {"Hesap Kodu": "361", "Hesap Adı": "Ödenecek SGK Kesintileri", "Borç Bakiye": 0, "Alacak Bakiye": 150000},
    {"Hesap Kodu": "370", "Hesap Adı": "Dönem Karı Vergi Karşılığı", "Borç Bakiye": 0, "Alacak Bakiye": 280000},
    {"Hesap Kodu": "372", "Hesap Adı": "Kıdem Tazminatı Karşılığı", "Borç Bakiye": 0, "Alacak Bakiye": 200000},
    {"Hesap Kodu": "400", "Hesap Adı": "Banka Kredileri (Uzun Vadeli)", "Borç Bakiye": 0, "Alacak Bakiye": 2000000},
    {"Hesap Kodu": "472", "Hesap Adı": "Kıdem Tazminatı Karşılığı (Uzun)", "Borç Bakiye": 0, "Alacak Bakiye": 500000},
    {"Hesap Kodu": "500", "Hesap Adı": "Sermaye", "Borç Bakiye": 0, "Alacak Bakiye": 2000000},
    {"Hesap Kodu": "540", "Hesap Adı": "Yasal Yedekler", "Borç Bakiye": 0, "Alacak Bakiye": 300000},
    {"Hesap Kodu": "570", "Hesap Adı": "Geçmiş Yıllar Karları", "Borç Bakiye": 0, "Alacak Bakiye": 800000},
    {"Hesap Kodu": "590", "Hesap Adı": "Dönem Net Karı", "Borç Bakiye": 0, "Alacak Bakiye": 520000},
    {"Hesap Kodu": "600", "Hesap Adı": "Yurtiçi Satışlar", "Borç Bakiye": 0, "Alacak Bakiye": 8500000},
    {"Hesap Kodu": "601", "Hesap Adı": "Yurtdışı Satışlar", "Borç Bakiye": 0, "Alacak Bakiye": 1500000},
    {"Hesap Kodu": "610", "Hesap Adı": "Satıştan İadeler (-)", "Borç Bakiye": 250000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "611", "Hesap Adı": "Satış İskontoları (-)", "Borç Bakiye": 150000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "620", "Hesap Adı": "Satılan Mamüller Maliyeti (-)", "Borç Bakiye": 5200000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "621", "Hesap Adı": "Satılan Ticari Mallar Maliyeti (-)", "Borç Bakiye": 1300000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "630", "Hesap Adı": "Ar-Ge Giderleri (-)", "Borç Bakiye": 200000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "631", "Hesap Adı": "Pazarlama Giderleri (-)", "Borç Bakiye": 450000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "632", "Hesap Adı": "Genel Yönetim Giderleri (-)", "Borç Bakiye": 680000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "642", "Hesap Adı": "Faiz Gelirleri", "Borç Bakiye": 0, "Alacak Bakiye": 180000},
    {"Hesap Kodu": "646", "Hesap Adı": "Kambiyo Karları", "Borç Bakiye": 0, "Alacak Bakiye": 320000},
    {"Hesap Kodu": "654", "Hesap Adı": "Karşılık Giderleri (-)", "Borç Bakiye": 150000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "656", "Hesap Adı": "Kambiyo Zararları (-)", "Borç Bakiye": 280000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "660", "Hesap Adı": "Kısa Vadeli Borçlanma Giderleri (-)", "Borç Bakiye": 350000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "661", "Hesap Adı": "Uzun Vadeli Borçlanma Giderleri (-)", "Borç Bakiye": 250000, "Alacak Bakiye": 0},
    {"Hesap Kodu": "691", "Hesap Adı": "Dönem Karı Vergi Karşılıkları (-)", "Borç Bakiye": 280000, "Alacak Bakiye": 0},
]

df = pd.DataFrame(data)
import os
output_dir = os.path.dirname(os.path.abspath(__file__))
df.to_excel(os.path.join(output_dir, "test_mizan.xlsx"), index=False)
df.to_csv(os.path.join(output_dir, "test_mizan.csv"), index=False, encoding="utf-8")
print(f"Test files created: {len(data)} rows")
