import pandas as pd

# Generowanie przykładowych pytań (50 sztuk)
questions = [
    "Jaka jest nazwa kierunku studiów opisanych w programie?",
    "Na jakim poziomie Polskiej Ramy Kwalifikacji znajduje się ten kierunek?",
    "Ile semestrów trwają studia stacjonarne na kierunku zarządzanie i inżynieria produkcji?",
    "Jaki tytuł zawodowy otrzymuje absolwent tego kierunku?",
    "Ile punktów ECTS trzeba zdobyć, aby ukończyć studia stacjonarne?",
    "Ile godzin zajęć obejmuje program studiów stacjonarnych?",
    "Ile godzin praktyk przewidziano w programie dla studiów stacjonarnych?",
    "W jakim języku prowadzone są zajęcia?",
    "Jakie są kluczowe efekty uczenia się w zakresie wiedzy?",
    "Jakie umiejętności praktyczne powinien zdobyć absolwent kierunku?",
    "Jakie kompetencje społeczne są wymagane od absolwenta?",
    "Na którym semestrze realizowana jest obowiązkowa praktyka zawodowa?",
    "Ile punktów ECTS przypisano do praktyki zawodowej?",
    "Czy praktyka zawodowa jest oceniana stopniem?",
    "Jakie są zasady zaliczenia praktyki zawodowej?",
    "Jakie są przedmioty obieralne dostępne na 5 semestrze studiów stacjonarnych?",
    "Jakie są przykłady zajęć z obszaru humanistycznego lub społecznego?",
    "Jakie przedmioty obieralne dotyczą sztucznej inteligencji i uczenia maszynowego?",
    "Na którym semestrze realizowane są zajęcia z wychowania fizycznego?",
    "Czy wychowanie fizyczne ma przypisane punkty ECTS?",
    "Jakie szkolenia obowiązują studentów w pierwszym semestrze?",
    "Ile godzin języka obcego przewidziano w formie stacjonarnej?",
    "Na jakim poziomie językowym student powinien posługiwać się językiem obcym po ukończeniu kursu?",
    "Jakie są sposoby weryfikacji efektów uczenia się?",
    "Jak wygląda proces przygotowania pracy dyplomowej?",
    "Ile punktów ECTS przypisano do przygotowania pracy dyplomowej?",
    "W jakim semestrze realizowane jest seminarium dyplomowe?",
    "Jakie są kryteria zaliczenia semestru?",
    "Jakie są stopnie w skali ocen stosowanej na studiach?",
    "Czy student może zaproponować własny temat pracy dyplomowej?",
    "Jakie warunki trzeba spełnić, aby móc kontynuować studia mimo niezaliczenia przedmiotu?",
    "Ile razy student może podejść do egzaminu poprawkowego?",
    "Jakie są kluczowe obszary wiedzy technicznej wymagane od absolwenta?",
    "Czym różni się liczba godzin zajęć między studiami stacjonarnymi a niestacjonarnymi?",
    "Jakie są zasady zaliczania przedmiotów obieralnych?",
    "Jakie są przykłady przedmiotów z zakresu automatyzacji i robotyzacji produkcji?",
    "Które przedmioty rozwijają kompetencje związane z metrologią i systemami pomiarowymi?",
    "Na którym semestrze realizowane jest seminarium przeddyplomowe?",
    "Ile punktów ECTS przypisano do seminarium przeddyplomowego?",
    "Jakie są przykłady zajęć związanych z prowadzoną działalnością naukową uczelni?",
    "Jakie efekty uczenia się związane są z projektowaniem wyrobów?",
    "Jakie efekty uczenia się odnoszą się do zarządzania jakością?",
    "Jakie efekty uczenia się dotyczą znajomości prawa gospodarczego i etyki?",
    "Jakie kompetencje zdobywa absolwent w zakresie pracy zespołowej?",
    "Czy student może zaliczyć praktykę zawodową na podstawie doświadczenia zawodowego?",
    "Jakie są obowiązki studenta podczas praktyki zawodowej?",
    "Które zajęcia umożliwiają zdobycie kompetencji inżynierskich?",
    "Jakie znaczenie mają przedmioty obieralne w całkowitej liczbie punktów ECTS?",
    "Jakie elementy obejmuje proces dyplomowania na tym kierunku?",
    "Jak monitorowane są losy absolwentów kierunku?"
]

# Tworzenie DataFrame
df = pd.DataFrame({
    "id": range(1, len(questions) + 1),
    "question": questions
})

# Zapis do CSV
output_path = "notebooks/sample_questions.csv"
df.to_csv(output_path, index=False, encoding="utf-8")
