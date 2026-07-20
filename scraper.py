import os
import json
import csv
import sqlite3
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def reconstruct(data, index):
    if not isinstance(index, int) or index < 0 or index >= len(data):
        return index
    
    val = data[index]
    if isinstance(val, dict):
        return {k: reconstruct(data, v) for k, v in val.items()}
    elif isinstance(val, list):
        return [reconstruct(data, v) for v in val]
    else:
        return val

def dict_to_xml(tag, d):
    elem = ET.Element(tag)
    for key, val in d.items():
        child = ET.Element(str(key).replace(" ", "_"))
        if isinstance(val, dict):
            child.append(dict_to_xml("item", val))
        elif isinstance(val, list):
            for item in val:
                child.append(dict_to_xml("item", {"value": item} if not isinstance(item, dict) else item))
        else:
            child.text = str(val)
        elem.append(child)
    return elem

def main():
    base_url = "https://next.seicode.net/anime?page={}"
    detail_url = "https://seicode.net/anime/{}/__data.json?x-sveltekit-invalidated=010"
    
    animes = []
    total_episodes = 0
    total_streams = 0
    
    first_page = requests.get(base_url.format(1)).json()
    total_pages = first_page.get("totalPages", 1)
    
    for page in range(1, total_pages + 1):
        print(f"Fetching page {page}/{total_pages}")
        res = requests.get(base_url.format(page)).json()
        
        for item in res.get("animes", []):
            slug = item.get("slug")
            print(f"Fetching details for {slug}")
            try:
                detail_res = requests.get(detail_url.format(slug)).json()
                nodes = detail_res.get("nodes", [])
                if len(nodes) > 1 and "data" in nodes[1]:
                    data_array = nodes[1]["data"]
                    anime_detail = reconstruct(data_array, 1)
                    
                    if not isinstance(anime_detail, dict):
                        continue
                    
                    flat_anime = {
                        "id": str(anime_detail.get("id", "")),
                        "slug": str(anime_detail.get("slug", "")),
                        "type": str(anime_detail.get("type", "")),
                        "english": str(anime_detail.get("english", "")),
                        "episodeRuntime": anime_detail.get("episodeRuntime", 0),
                        "firstAirDate": str(anime_detail.get("firstAirDate", "")),
                        "tmdbScore": anime_detail.get("tmdbScore", 0),
                        "summary": str(anime_detail.get("summary", "")),
                        "malIDs": ",".join(map(str, anime_detail.get("malIDs", []))),
                        "genres": ",".join(map(str, anime_detail.get("genres", []))),
                        "numberOfEpisodes": anime_detail.get("numberOfEpisodes", 0)
                    }
                    animes.append(flat_anime)
                    
                    seasons = anime_detail.get("seasons", [])
                    if isinstance(seasons, list):
                        total_episodes += len(seasons)
                        for ep in seasons:
                            if isinstance(ep, dict):
                                video_links = ep.get("video_links", {})
                                if isinstance(video_links, dict):
                                    total_streams += len(video_links)
            except Exception as e:
                print(f"Error fetching {slug}: {e}")

    total_anime = len(animes)
    print(f"Total Anime: {total_anime}, Total Episodes: {total_episodes}, Total Streams: {total_streams}")
    
    os.makedirs("dump", exist_ok=True)
    
    with open("dump/anime.json", "w", encoding="utf-8") as f:
        json.dump(animes, f, ensure_ascii=False, indent=2)
        
    with open("dump/anime.jsonl", "w", encoding="utf-8") as f:
        for a in animes:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")
            
    df = pd.DataFrame(animes)
    df.to_csv("dump/anime.csv", index=False, encoding="utf-8")
    
    df.to_parquet("dump/anime.parquet", index=False)
    
    root = ET.Element("Animes")
    for a in animes:
        root.append(dict_to_xml("Anime", a))
    tree = ET.ElementTree(root)
    tree.write("dump/anime.xml", encoding="utf-8", xml_declaration=True)
    
    conn = sqlite3.connect("dump/anime.sqlite")
    df.to_sql("anime", conn, if_exists="replace", index=False)
    
    with open("dump/anime.sql", "w", encoding="utf-8") as f:
        for line in conn.iterdump():
            f.write("%s\n" % line)
    conn.close()
    
    readme_content = f"""# Seicode

Bu depo, Seicode'dan her 24 saatte bir güncellenen anime verilerini içerir.

## Metrikler
- **Toplam Anime:** {total_anime}
- **Toplam Bölüm:** {total_episodes}
- **Toplam Stream (Video Linki):** {total_streams}
- **Son Güncelleme:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

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
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

if __name__ == "__main__":
    main()
