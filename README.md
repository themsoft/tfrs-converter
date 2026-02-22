# TFRS Converter

> **WIP (Work in Progress)** — Bu proje aktif geliştirme aşamasındadır. Frontend tarafında bilinen hatalar ve eksik özellikler mevcuttur.

TDHP (Tek Düzen Hesap Planı) mizanlarını IFRS/TFRS (Uluslararası Finansal Raporlama Standartları) formatına dönüştüren web uygulaması.

## Ne Yapar?

1. **Mizan Yükleme** — Excel (.xlsx/.xls) veya CSV formatında mizan dosyası yükleyin
2. **Otomatik Eşleştirme** — TDHP hesap kodları IFRS kategorilerine otomatik eşlenir (~200+ hesap)
3. **IFRS Düzeltmeleri** — 5 standart düzeltme kaydı otomatik oluşturulur:
   - Amortisman farkı (IAS 16)
   - Reeskont (Bugünkü değer indirgemesi)
   - Kıdem tazminatı karşılığı (IAS 19)
   - Beklenen kredi zararı / ECL (IFRS 9)
   - Ertelenmiş vergi (IAS 12)
4. **Raporlama** — Bilanço, gelir tablosu ve düzeltme öncesi/sonrası karşılaştırma

## Bilinen Sorunlar

- [ ] Demo veri akışında raporlar sayfası 404 hatası veriyor (mock session backend'e iletilmiyor)
- [ ] Frontend'de çeşitli UI/UX iyileştirmeleri gerekiyor
- [ ] Backend henüz deploy edilmedi (sadece local çalışıyor)
- [ ] Gerçek dosya yükleme sonrası raporlama akışı test edilmeli

## Tech Stack

### Backend
- Python 3 · FastAPI · Pandas · openpyxl

### Frontend
- React 19 · TypeScript · Tailwind CSS v4 · Vite 7 · Recharts

## Kurulum (Local)

### Backend
```bash
cd backend
python -m venv venv
source venv/Scripts/activate   # Windows
pip install -r requirements.txt
python main.py                 # → http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev                    # → http://localhost:5173
```

Frontend, Vite proxy ile `/api` isteklerini backend'e (`localhost:8000`) yönlendirir.

## Proje Yapısı

```
tfrs-converter/
├── backend/
│   ├── main.py                 # FastAPI app & endpoints
│   ├── services/
│   │   ├── parser.py           # Excel/CSV parse
│   │   ├── mapper.py           # TDHP → IFRS eşleştirme
│   │   ├── adjustments.py      # 5 düzeltme motoru
│   │   └── reporter.py         # Bilanço/Gelir raporlaması
│   ├── config/
│   │   └── mapping.json        # TDHP hesap eşleştirme tablosu
│   └── test_mizan.xlsx         # Örnek mizan dosyası
├── frontend/
│   ├── src/
│   │   ├── pages/              # HomePage, ReportsPage
│   │   ├── components/         # UI bileşenleri
│   │   ├── context/            # Session & Theme state
│   │   ├── utils/              # API client, mock data
│   │   └── types/              # TypeScript tipleri
│   └── vite.config.ts
└── README.md
```

## Lisans

AGPL-3.0 — Detaylar için [LICENSE](LICENSE) dosyasına bakın.
