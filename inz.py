import binascii
import os
import sys

from serial import Serial

# Predefinicje zmiennych globalnych
menu_actions = {}
verified_port = ""
PDU = ""
TYPE = ""


def dziel_co(n, s):
    return [s[i:i + n] for i in xrange(0, len(s), n)]


def napraw_i_wyslij(data):
    dataB = []
    data = data.split(' ')
    for i in range(len(data)):
        dataB.insert(i, int(data[i], 16))
    ser.write("".join(chr(i) for i in dataB))


output = os.popen("ls /dev/ttyUSB*").read().splitlines()
print "Trwa testowanie niezawodnosci transmisji..."
print "Wszystkie znalezione serial porty: ", output
print "Testowanie, ktory port odpowiada za komunikacje..."
for x in output:
    ser = Serial(x, timeout=1, baudrate=1000000)
    napraw_i_wyslij("FF FF 80 00 00 00 AA AA")  # komenda NOP
    data_raw = ser.readline()
    if data_raw:
        print "Wykryto odpowiadajacy port:", x
        print "Surowa odpowiedz na NOP:"
        print(data_raw.encode("hex"))
        print "Parsowanie odpowiedzi na format human readable..."
        data_raw = binascii.hexlify(data_raw)
        print dziel_co(2, data_raw)
        print "Wybieranie ", x, "jako port komunikacyjny (Baud 1 Mb)"
        verified_port = x
    else:
        print "Nie znaleziono plytki na porcie", x, "lub jest ona niedostepna"
ser = Serial(verified_port, timeout=1, baudrate=1000000)


# =======================
#     FUNKCJE MENU
# =======================

# Menu glowne
def main_menu():
    print "Akwizycja sygnalow biomedycznych wersja alpha. Aplikacje CLI w jezyku Python wykonal i zaprojektowal Pior Sienkiewicz\n"
    print "Zaimplementowane w protokole polecenia i funkcje aplikacji (Wprowadz odpowiadajacy numer):  "
    print "1. GET_ID"
    print "2. GET_SERIAL_NUM"
    print "3. test"
    print "\n0. Quit"
    choice = raw_input(" >>  ")
    exec_menu(choice)

    return


# Trigger
def exec_menu(choice):
    os.system('clear')
    ch = choice.lower()
    if ch == '':
        menu_actions['main_menu']()
    else:
        try:
            menu_actions[ch]()
        except KeyError:
            print "Invalid selection, please try again.\n"
            menu_actions['main_menu']()
    return


def extract_pdu(data_raw):  # eksport pola PDU ze sparsowanej hex ramki. Najpierw nalezy wyslac do Device komende i zbuforowac odpowiedz
    print "Surowa odpowiedz z portu w formacie ASCII: ", data_raw
    print "Odpowiedz w systemie heksadecymalnym: ", data_raw.encode("hex")
    data_raw = binascii.hexlify(data_raw)
    sparsowana_ramka = dziel_co(2, data_raw)
    print "Sparsowana ramka (odpowiedz): ", sparsowana_ramka  # PDU znajduje sie pomiedzy 5 bajtem, a wartoscia data_size
    data_size = sparsowana_ramka[4]  # parsowanie rozmiaru PDU
    data_size_int = int(data_size, 16)
    global PDU
    PDU = sparsowana_ramka[6:data_size_int + 5]
    print "Rozmiar pola PDU: ", data_size_int, "bajtow"  # rozmiar PDU


def extract_type(data_raw): # analogicznie jak do PDU export pola TYPE. Zwraca TYPE rozpisany na poszczegolny bity.
    # print "Surowa odpowiedz z portu w formacie ASCII: ", data_raw
    # print "Odpowiedz w systemie heksadecymalnym: ", data_raw.encode("hex")
    data_raw = binascii.hexlify(data_raw)
    sparsowana_ramka = dziel_co(2, data_raw)
    print "Sparsowana ramka (odpowiedz): ", sparsowana_ramka # TYPE ma stala pozycje znajduje sie na 3 bajcie
    global TYPE
    TYPE = sparsowana_ramka[2]
    print "Pole type: ", TYPE
    TYPE = bin(int(TYPE, 16))[2:].zfill(8)
    print "Postac binarna (na osmiu bitach): ", TYPE
    print type(TYPE)





# TO DO: EXTRACT COMMAND BASED ON TEST3



# Menu 1
def menu1():
    print "Trwa wysylanie zadania o podanie ID urzadzenia...\n"
    napraw_i_wyslij("FF FF 80 01 00 00 AA AA")  # komenda GET ID
    data_raw = ser.readline()
    extract_pdu(data_raw)
    global PDU
    print "Pole PDU (ID urzadzenia -hex): ", PDU
    PDU = binascii.unhexlify(''.join(PDU))  # konwersja na ASCII
    print "Pole PDU (ID urzadzenia): ", PDU
    print "9. Cofnij"
    print "0. Wyjdz"
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return


# Menu 2
def menu2():
    napraw_i_wyslij("FF FF 80 02 00 00 AA AA") # komenda GET_SERIAL_NUM
    data_raw = ser.readline()
    extract_pdu(data_raw)
    global PDU
    print "Pole PDU (Serial number -hex): ", PDU
    PDU = binascii.unhexlify(''.join(PDU))  # konwersja na ASCII
    print "Pole PDU (Serial number): ", PDU

    choice = raw_input(" >>  ")
    exec_menu(choice)
    return


#Menu 3
def menu3():
    napraw_i_wyslij("FF FF 80 00 00 00 AA AA")  # komenda NOP
    data_raw = ser.readline()



    choice = raw_input(" >>  ")
    exec_menu(choice)
    return


# Powrot do menu glownego
def back():
    menu_actions['main_menu']()


# Wyjscie
def exit():
    sys.exit()


# =======================
#    DEFINICJE MENU
# =======================


menu_actions = {
    'main_menu': main_menu,
    '1': menu1,
    '2': menu2,
    '3': menu3,
    '9': back,
    '0': exit,
}

# =======================
#      FUNKCJA MAIN
# =======================


if __name__ == "__main__":
    # Wlaczenie menu glownego
    main_menu()