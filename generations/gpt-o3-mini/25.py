plik = open("dane_obrazki.txt")
maxbitybledne = 0
bityBledne = list()

def czyPoprawny(obrazek): # obrazek zawiera liste łancuchów znaków i można korzystać z operatora indeksowania
                           # obrazek[i][j]
    for wiersz in obrazek[:-1]:  # nie liczymy z ostaniego wiersza tam są bity parzystosci
        if wiersz[:-1].count('1') % 2 != int(wiersz[-1]):
            return False
    for i in range(20):  # i = 0,1,2,...,19
        kolumna = ""
        for j in range(21):  # j = 0,1,2,...,20
            kolumna += obrazek[j][i]
        if kolumna[:-1].count('1') % 2 != int(kolumna[-1]):
            return False
    return True

def czyNaprawialny(obrazek):
    bityKolBleden = 0
    bityWierBledne = 0
    for wiersz in obrazek[:-1]:  # nie liczymy z ostaniego wiersza tam są bity parzystosci
        if wiersz[:-1].count('1') % 2 != int(wiersz[-1]):
            bityWierBledne += 1
    for i in range(20):  # i = 0,1,...,19
        kolumna = ""
        for j in range(21):  # j = 0,1,...,20
            kolumna += obrazek[j][i]
        if kolumna[:-1].count('1') % 2 != int(kolumna[-1]):
            bityKolBleden += 1
    global maxbitybledne
    if maxbitybledne < (bityKolBleden + bityWierBledne):
        maxbitybledne = bityKolBleden + bityWierBledne
    bityBledne.append(bityKolBleden + bityWierBledne)

    if bityWierBledne > 1:
        return False
    if bityKolBleden > 1:
        return False

    return True

def napraw(obrazek):
    """Wejście stanowi plik tekstowy zawierający dane czarnobiałego obrazka zakodowane jako piksele.
0 - piksel biały, 1 - piksel czarny.
Każdy wiersz oraz kolumna zawiera na swoim końcu bit parzystości.
Bit parzystości jest równy 0, jeśli ilość jedynek w wierszu (lub w kolumnie dla kolumn) jest parzysta,
a 1 jeśli jest nieparzysta.
Np.
0 1 1 0 1 1   <- bit parzystości wiersza (błędny – należy zmienić go na przeciwny)
1 1 1 0 1 0
1 1 1 1 1 1
0 1 1 0 0 0
1 1 0 1 1 0
1 1 0 0 0   <- bity parzystości kolumny 
              ^        
              |-- bity parzystości wiersza

Napisz funkcję, która znajdzie uszkodzone obrazki oraz je naprawi,
tzn. obrazek naprawialny (posiada co najwyżej jeden bit parzystości wiersza i co najwyżej jeden bit parzystości kolumny niepoprawny)
a następnie naprawi te obrazy.
Wynik ma zawierać obrazek błędny (naprawialny) oraz obrazek poprawiony.
    """
    # Zachowujemy kopię oryginalnego (błędnego) obrazka jako listę stringów
    bledny = obrazek.copy()
    
    # Tworzymy zmienną 'poprawiony' jako macierz (lista list znaków), aby móc modyfikować konkretne bity
    poprawiony = [list(wiersz) for wiersz in obrazek]
    
    error_row = None
    error_col = None

    # Sprawdzenie błędów w wierszach (tylko dla wierszy zawierających dane, czyli 0-19)
    for i in range(len(poprawiony) - 1):  # pomijamy ostatni wiersz, który zawiera bity parzystości kolumn
        data = poprawiony[i][:-1]
        parity_bit = int(poprawiony[i][-1])
        if data.count('1') % 2 != parity_bit:
            error_row = i
            break

    # Sprawdzenie błędów w kolumnach (dla kolumn 0-19; ostatni element w kolumnie jest bitem parzystości)
    for j in range(20):
        col_data = [poprawiony[i][j] for i in range(len(poprawiony))]
        data = col_data[:-1]  # dane z 20 pierwszych wierszy
        parity_bit = int(col_data[-1])  # ostatni wiersz - bit parzystości kolumny
        if data.count('1') % 2 != parity_bit:
            error_col = j
            break

    # Naprawa wykrytego błędu:
    if error_row is not None and error_col is not None:
        # Błąd znajduje się w pikselu danych w przecięciu błędnego wiersza i kolumny.
        current = poprawiony[error_row][error_col]
        poprawiony[error_row][error_col] = '0' if current == '1' else '1'
    elif error_row is not None:
        # Błąd dotyczy bitu parzystości wiersza; naprawiamy ostatni bit w tym wierszu.
        current = poprawiony[error_row][-1]
        poprawiony[error_row][-1] = '0' if current == '1' else '1'
    elif error_col is not None:
        # Błąd dotyczy bitu parzystości kolumny; naprawiamy bit w ostatnim wierszu, w danej kolumnie.
        current = poprawiony[-1][error_col]
        poprawiony[-1][error_col] = '0' if current == '1' else '1'
    # Jeśli nie znaleziono błędu, obrazek pozostaje niezmieniony.

    # Konwertujemy poprawioną macierz z powrotem na listę stringów
    poprawiony = [''.join(rzad) for rzad in poprawiony]
    
    # Wynik zawiera oryginalny (błędny) obrazek i obrazek naprawiony
    wynik = [bledny, poprawiony]
    return wynik

poprawne = 0
naprawialne = 0
obrazek = list()
for linia in plik:
    wiersz = linia.strip()  # odcinamy białe znaki np. enter
    # wiersz = wiersz[:-1]  # tylko dane obrazka bez bitu parzystości, teraz czytamy cały wiersz danych
    obrazek.append(wiersz)
    if len(obrazek) == 21:  # mamy 21 linii czyli cały obrazek razem z wierszami bitów parzystości
        if czyPoprawny(obrazek):
            poprawne += 1
        elif czyNaprawialny(obrazek):
            naprawialne += 1
            naprawiony = napraw(obrazek)
    if len(obrazek) == 22:  # po 22 liniach czyścimy obrazek, by czytać kolejne
        obrazek = list()

print(poprawne, naprawialne, 200 - poprawne - naprawialne)
print(maxbitybledne, max(bityBledne))
