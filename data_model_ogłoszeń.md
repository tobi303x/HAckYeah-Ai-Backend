# Dokumentacja bazy danych ofert wolontariatu

Baza danych służy do przechowywania informacji o ofertach wolontariatu w Polsce. Pozwala użytkownikom wyszukiwać oferty na podstawie opisu oraz filtrować je według tagów, lokalizacji, nakładu pracy i formy działalności.

---

## Struktura rekordu

### 1. Nazwa
- **Typ:** string  
- **Opis:** Nazwa ogłoszenia wolontariatu.  
- **Przykład:** `"Zielona Warszawa - wsparcie lokalnych inicjatyw"`

### 2. Opis
- **Typ:** string  
- **Opis:** Szczegółowy opis wolontariatu wyświetlany na stronie. Umożliwia wyszukiwanie ofert na podstawie treści.  
- **Przykład:** `"Dołącz do zespołu wolontariuszy dbających o zieleń miejską w Warszawie..."`

### 3. Tagi
- **Typ:** Multi picklist
- **Opis:** Kategorie, które opisują ofertę i umożliwiają filtrowanie.  
- **Dostępne wartości:**
  - Rynek mieszkaniowy  
  - Zieleń i klimat  
  - Jakość powietrza  
  - Potrzeby kierowców  
  - Potrzeby rowerzystów  
  - Potrzeby pieszych  
  - Komunikacja miejska  
  - Edukacja  
  - Zdrowie  
  - Oferta społeczno-kulturalna miasta  
  - Zwierzęta  
  - Seniorzy i seniorki  
  - Transparentność działań urzędów  
  - Usługi komunalne (np. woda, śmieci)  

### 4. Thumbnail
- **Typ:** string (URL)  
- **Opis:** Link do zdjęcia reprezentującego ofertę.  
- **Przykład:** `"https://example.com/images/volunteer_green_warsaw.jpg"`

### 5. Lokalizacja
- **Typ:** Single picklist 
- **Opis:** Miasto, w którym realizowany jest wolontariat. Można filtrować po wszystkich miastach Polski.  
- **Przykład:** `"Warszawa"`

### 6. Data rozpoczęcia
- **Typ:** string  
- **Format:** `dd:mm:yyyy`  
- **Opis:** Data rozpoczęcia wydarzenia wolontariackiego.  
- **Przykład:** `"06:10:2025"` (1 czerwca 2025)

### 7. Data zakończenia
- **Typ:** string  
- **Format:** `dd:mm:yyyy`  
- **Opis:** Data zakończenia wydarzenia.  
- **Przykład:** `"06:10:2025"` (30 czerwca 2025)

### 8. Wymagania nakładu pracy
- **Typ:** Multi picklist 
- **Opis:** Określa ile czasu wolontariusz powinien poświęcić na działania. Można filtrować oferty według nakładu pracy.  
- **Dostępne wartości:**
  - Mini - Zaangażowanie do 1 godziny tygodniowo
  - Lekkie - Zaangażowanie 1-4 godziny tygodniowo  
  - Umiarkowane - Zaangażowanie 4-8 godzin tygodniowo  
  - Pełne - Zaangażowanie ponad 8 godzin tygodniowo  

### 9. Preferowana forma działalności
- **Typ:** Multi picklist
- **Opis:** Określa formę aktywności wolontariusza. Można filtrować oferty według preferowanej formy.  
- **Dostępne wartości:**
  - Zostań aktywistą online  
  - Dbaj o potrzeby dzielnicy 
  - Weź udział w akcjach bezpośrednich
  - Spotkaj się z mieszkańcami
  - Zaangażuj się w obywatelską kontrolę
  - Wesprzyj pogotowie obywatelskie

### 10. Nazwa organizatora
- **Typ:** string  
- **Opis:** Nazwa organizacji, która wystawiła ogłoszenie.  
- **Przykład:** `"Fundacja Zielona Przyszłość"`

---

## Przykładowy rekord

curl --request POST \
  --url http://localhost:5000/add_opportunity \
  --header 'Content-Type: application/json' \
  --data '{
   "title": "Zielona Warszawa - wsparcie lokalnych inicjatyw",
   "description": "Dołącz do zespołu wolontariuszy dbających o zieleń miejską w Warszawie. Twoim zadaniem będzie sadzenie roślin, czyszczenie parków i edukacja mieszkańców.",
   "tags": ["Zieleń i klimat"],
   "thumbnail": "https://example.com/images/volunteer_green_warsaw.jpg",
   "location": "Warszawa",
   "start_date": "01:06:2025",
   "end_date": "30:06:2025",
   "workload": ["Mini - Zaangażowanie do 1 godziny tygodniowo", "Lekkie - Zaangażowanie 1-4 godziny tygodniowo"],
   "form": ["Dbaj o potrzeby dzielnicy", "Weź udział w akcjach bezpośrednich"],
   "organizer": "Fundacja Zielona Przyszłość"
 }'

 # Sample succesfull response

 {
	"record_id": "da0a347a-d96f-4ea2-af60-6237644d0f81",
	"status": "success"
}


## Zapytania i filtrowanie rekordów

# Filtrowanie miast

curl --request GET \
  --url 'http://localhost:5001/query?location=Ca%C5%82a%20Polska'

curl --request GET \
  --url 'http://localhost:5001/query?location=Warszawa'

# Filtrowanie na podstawie zakresu dat i organizatora

curl --request GET \
  --url 'http://localhost:5001/query?organizer=Fundacja&start_date_from=2025-09-01&end_date_to=2025-12-31'

# Filtrowanie na podstawie tagu i lokalizacji

curl --request GET \
  --url 'http://localhost:5001/query?tags=Oferta%20spo%C5%82eczno-kulturalna%20miasta&location=Ca%C5%82a%20Polska'

# Filtrowanie na podstawie lokacji i opisu tekstowego

curl --request GET \
  --url 'http://localhost:5001/query?text=opieka%20nad%20dzie%C4%87mi&location=Warszawa'

# Wszystkie możliwe parametry endpointu /query

Nazwa -> ?title=grafiki
Tags -> ?tags=Zwierzęta
Lokalizacja -> ?location=Warszawa
Data rozpoczęcia -> ?start_date_from=2025-09-01&start_date_to=2025-12-31
Data zakończenia -> ?end_date_from=2025-10-01
Wymagania nakładu pracy -> ?workload=Mini - Zaangażowanie do 1 godziny tygodniowo
Preferowana forma działalności -> ?form=Zostań aktywistą online
text -> ?text=wolontariat zdalny

# Przykładowe query

curl --request GET \
  --url https://chroma-db-api-369833237955.europe-west1.run.app/query \
  --header 'User-Agent: insomnia/11.6.1' \
  --header 'x-api-key: CHUJDUPACYCKI'

curl --request POST \
  --url https://chroma-db-api-369833237955.europe-west1.run.app/add_opportunity \
  --header 'Content-Type: application/json' \
  --header 'x-api-key: CHUJDUPACYCKI' \
  --data '{
     "title": "Sprzątanie Parku Skaryszewskiego",
     "description": "Dołącz do nas w sobotni poranek, aby wspólnie posprzątać Park Skaryszewski. Zapewniamy rękawice i worki. To świetna okazja, by zadbać o naszą wspólną zieleń.",
     "tags": [
         "Zieleń i klimat",
         "Usługi komunalne (np. woda, śmieci)"
     ],
     "thumbnail": "https://example.com/images/park_cleanup.jpg",
     "lon": 21.045,
     "lat": 52.245,
     "start_date": "2025-10-18",
     "end_date": "2025-10-18",
     "workload": [
         "Lekkie - Zaangażowanie 1-4 godziny tygodniowo"
     ],
     "form": [
         "Weź udział w akcjach bezpośrednich"
     ],
     "organizer": "Stowarzyszenie Czysta Warszawa"
 }'

