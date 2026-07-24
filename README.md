# Seicode

Bu depo, Seicode'dan her 24 saatte bir güncellenen anime verilerini içerir.

## Metrikler
- **Toplam Anime:** 168
- **Toplam Bölüm:** 1915
- **Toplam Stream (Video Linki):** 6902
- **Son Güncelleme:** 2026-07-24 01:49:37

## Çıktılar (`dump/` klasörü)
- `anime.json`: Tüm verilerin standart JSON formatı.
- `anime.jsonl`: Satır satır (JSONL) veri dökümü.
- `anime.csv`: Tablo yapısında CSV dosyası.
- `anime.parquet`: Sıkıştırılmış sütun tabanlı Parquet dosyası.
- `anime.xml`: Hiyerarşik XML formatı.
- `anime.sqlite`: SQLite veritabanı.
- `anime.sql`: SQL döküm dosyası.

## Tablo Yapısı
| Kolon Adı | Veri Tipi | Açıklama |
| --- | --- | --- |
| `id` | String | Animasyona ait benzersiz ID |
| `slug` | String | URL için kullanılan kısa ad (Örn: akane-banashi) |
| `type` | String | Yayın tipi (Örn: tv) |
| `english` | String | İngilizce adı |
| `episodeRuntime` | Integer | Bölüm süresi (dakika) |
| `firstAirDate` | String | İlk yayın tarihi |
| `tmdbScore` | Float | TMDB Puanı |
| `summary` | String | Konu özeti |
| `malIDs` | String | MyAnimeList ID'leri (virgülle ayrılmış) |
| `genres` | String | Türler (virgülle ayrılmış) |
| `numberOfEpisodes` | Integer | Toplam bölüm sayısı |
