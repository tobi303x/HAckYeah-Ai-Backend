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
  --url 'http://localhost:5000/query?text=publikacja%2520news%25C3%25B3w%2520dementowanie%2520fake-news%25C3%25B3w%2520wilki%2520szaki%2520psy&title=Wolontariat%2520dziennikarski%2520zdalny%2520-%2520%25C5%259Aledzenie%2520nowo%25C5%259Bci%252C%2520weryfikacja%2520i%2520pisanie%2520news%25C3%25B3w&location=Ca%25C5%2582a%2520Polska&tags=&form=Zosta%25C5%2584%2520aktywist%25C4%2585%2520online&workload=Pe%25C5%2582ne%2520-%2520Zaanga%25C5%25BCowanie%2520ponad%25208%2520godzin%2520tygodniowo&start_date_from=2025-10-01&start_date_to=2025-10-01&end_date_from=2025-12-31&end_date_to=2025-12-31' \
  --header 'x-api-key: CHUJDUPACYCKI'


