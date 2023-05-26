from flask import Flask, request
import numpy as np
from datetime import datetime
import csv
from math import radians, sin, cos, acos

# Constants for Earth's radius in kilometers and miles
R_KM = 6371
R_MILES = 3959

HIZ_LIMITI = 90
DONUS_IVME_LIMIT = 3
FREN_HIZLANMA_IVME_LIMIT = 4

HIZIHLAL_PUAN_AGIRLIK = 20
ANIDONUS_PUAN_AGIRLIK = 40
HIZLANMAFREN_PUAN_AGIRLIK = 40


app = Flask(__name__)


@app.route('/skorlama', methods=['POST'])
def skor_hesapla():
    if request.method == 'POST':
        filename = datetime.now().strftime("%d-%m-%YT%H-%M-%S") + ".csv"
        f = open(filename, "w")
        data_array = request.get_json(force=True).get("data")
        for row in data_array:
            f.write(row)
            f.write("\n")
        print("saved to file", filename)

        hiz_ihlali_sayisi = hiz_ihlali_sayisi_bul(data_array)
        f.write(f"HIZ IHLAL SAYISI={hiz_ihlali_sayisi}\n")
        ani_donus_sayisi = ani_donus_sayisi_bul(data_array)
        f.write(f"ANI DONUS IHLAL SAYISI={ani_donus_sayisi}\n")
        ani_fren_hizlanma_sayisi = ani_fren_ve_hizlanma_sayisi_bul(data_array)
        f.write(f"ANI FREN/HIZLANMA SAYISI={ani_fren_hizlanma_sayisi}\n")
        sure = sure_bul(data_array)
        f.write(f"TOPLAM_SURE={sure}\n")
        puan = puan_hesapla(sure, hiz_ihlali_sayisi, ani_donus_sayisi, ani_fren_hizlanma_sayisi)
        f.write(f"PUAN={puan}\n")

        print("HIZ IHLAL SAYISI=", hiz_ihlali_sayisi)
        print("ANI DONUS IHLAL SAYISI=", ani_donus_sayisi)
        print("ANI FREN/HIZLANMA SAYISI=", ani_fren_hizlanma_sayisi)
        print("SURE", sure)
        print("PUAN", puan)

        f.close()
        tarih = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        sonuc = f"Tarih:{tarih}\nHiz Ihlal:{hiz_ihlali_sayisi}\nAni Donus Ihlal:{ani_donus_sayisi}\nAniFrenHizlanma:{ani_fren_hizlanma_sayisi}\nPUAN:{puan}"
        return sonuc

def puan_hesapla(sure, hiz_ihlal_sayisi, ani_donus_sayisi, ani_fren_hizlanma_sayisi):

    puan = (HIZIHLAL_PUAN_AGIRLIK * (1 - min (1, hiz_ihlal_sayisi/ sure))
            + ANIDONUS_PUAN_AGIRLIK * (1 - min (1, ani_donus_sayisi / sure))
            + HIZLANMAFREN_PUAN_AGIRLIK * (1 - min (1, ani_fren_hizlanma_sayisi / sure)))

    return round(puan)

def sure_bul(veriler):
    zamanlar = [float(row.split(",")[0]) for row in veriler]
    baslama = zamanlar[0]
    son = zamanlar[len(zamanlar)-1]
    return son - baslama
    

def hiz_ihlali_sayisi_bul(veriler):
    ihlal_sayisi = 0
    hamveriler = [row.split(",") for row in veriler]
    koordinatlar = [(float(row[0]), float(row[1]), float(row[2])) for row in hamveriler]
    hizlar=[]
    for i in range(len(koordinatlar) - 1):
        seconds1, lat1, long1 = koordinatlar[i]
        seconds2, lat2, long2 = koordinatlar[i + 1]

        # Convert lat, long to radians
        lat1 = radians(lat1)
        long1 = radians(long1)
        lat2 = radians(lat2)
        long2 = radians(long2)

        try:
            # Calculate distance using haversine formula
            hiz = 0
            if seconds2 != seconds1:
                mesafe = R_KM * acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(long1 - long2))
                hiz = round(mesafe * 3600 / (seconds2 - seconds1))
                print(f'Distance between points {i} and {i + 1}: {mesafe} hiz:{hiz} ')
                hizlar.append(hiz)
        except Exception:
            print(f'HATA !')

    window_size = 30 
    # Initialize the filtered data array
    filtered_data = np.zeros(len(hizlar) - window_size + 1)
    # Apply the median filter
    for i in range(len(filtered_data)):
        filtered_data[i] = round(np.median(hizlar[i:i+window_size]))
    print(hizlar)
    print(filtered_data)
    a = [x for x in filtered_data if x > HIZ_LIMITI]
    print(a)


    return len(a)


def ani_donus_sayisi_bul(veriler):
    ivme_ihlal_sayisi = 0
    ivmelenme = [float(row.split(",")[4]) for row in veriler]
    for ivme in ivmelenme:
        if ivme > DONUS_IVME_LIMIT:
            ivme_ihlal_sayisi += 1

    return ivme_ihlal_sayisi


def ani_fren_ve_hizlanma_sayisi_bul(veriler):
    ivme_ihlal_sayisi = 0
    ivmelenme = [float(row.split(",")[5]) for row in veriler]
    for ivme in ivmelenme:
        if ivme > FREN_HIZLANMA_IVME_LIMIT:
            ivme_ihlal_sayisi += 1

    return ivme_ihlal_sayisi
