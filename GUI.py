"""
COMP.CS.100 Ohjelmointi 1 / Programming 1

Ohjelma on korttipeli nimeltä Blackjack. Siinä pelataan jakajaa vastaan ja
yritetään voittaa jakajan käsi saamalla suurempi korttien yhteenlaskettu summa.
Toisin sanoen pelaaja yrittää saada korttien summasta mahdollisimman suur1,
korttien yhteenlaskettu summa ei saa kuitenkaan ylittää lukua 21. Tällöin
häviää automaattisesti.

Jokaiselle pelaajalle ja jakajalle jaetaan aluksi 2 korttia. Kun on pelaajan
vuoro, hän voi valita ottaako uuden kortin vai antaako vuoron seuraavalle
pelaajalle tai jakajalle jos on viimeinen pelaaja. Pelin voittaa se pelaaja,
jolla on suurin käsi, joka on suurempi kuin jakallla, ja se on alle 21.

Korttien arvo niiden nimellis arvo tai kuvakorttien suhteen 10. Ässä voi olla
joko 1 tai 11 riippuen tilanteesta. Ässän arvo valiutuu sen mukaan kaatuisiko
käsi, jos ässän arvo olisi 11. Tällöin se on 1.

"""
import random
from tkinter import *


class GUI:
    def __init__(self):
        self.__main = Tk()
        self.__main.title("Blackjack")
        self.__main.geometry("500x450")

        # Luo kuvan menuruutuun ja asettaa sen paikan.
        bg = PhotoImage(file="Hearts 1.gif")
        self.__backgroud = Label(self.__main, image=bg)
        self.__backgroud.place(x=0, y=0, relwidth=1, relheight=1)

        # Pelin otsikko
        self.__headline = Label(self.__main, text="Blackjack",
                                font=("Helvetica", 46))
        self.__headline.pack()
        self.__mb = Label(self.__main, text="How many players?\n(max 7)")
        self.__mb.pack(fill=BOTH)

        self.__player_count = Entry()
        self.__player_count.pack()

        self.__player_points = {"dealer": []}

        menu = Menu(self.__main)
        self.__main.config(menu=menu)

        filemenu = Menu(menu)

        # Luo pelin oikeaan ylälaitaan valikot joista löytyy uusi peli ja
        # lopetusnappi.
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New", command=self.reset2)
        filemenu.add_command(label="Exit", command=self.stop)

        # Luo menun ohjeille jos haluaa kesken pelin lukea niitä.
        helpmenu = Menu(menu)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="Rules", command=help_tab)

        # Tässä kohtaan luodaan pelissä tarvittavat painikkeet ja muut
        # tarvittavat muuttujat.
        self.__Ready = Button(self.__main, text="Ready!", font=50,
                              command=self.card_reveal)

        self.__error = Label(self.__main, text="")

        self.__next = Button(self.__main, text="Start",
                             command=self.remove_menu)
        self.__next.pack()

        self.__deal = Button(self.__main, text="Hit", command=self.deal,
                             state=DISABLED)
        self.__next_turn = Button(self.__main, text="Stand",
                                  command=self.change_turn, state=DISABLED)
        self.__whos_turn = 0
        self.__row_of_the_card = 0
        self.__card_reveal_check = 0

        self.__player_cards = []
        self.__point_labels = []
        self.__how_many_aces = {}
        self.__starting_hand_aces = {}

        self.__main.mainloop()

    def get_player_count_as_integer(self):
        """
        Hakee Entrystä pelaajien lukumäärän ja muuttaa sen kokonaisluvuksi.
        Pitää myös huolen, että pelaajien lukumäärä ei ylitä maksimia.
        :return: Pelaajien määrän
        """
        self.__player_count_int = int(self.__player_count.get())
        if self.__player_count_int > 7:
            self.__player_count_int = 7

    def stop(self):
        """
        Pysäyttää ohjelman
        :return:
        """
        self.__main.destroy()

    def reset(self):
        """
        Alustaa Entryn, eli poistaa tämän arvon
        :return:
        """
        self.__player_count.delete(0, END)

    def create_menu(self):
        """
        Luo aloitusvalikon, josta valitaan pelaajien määrä
        :return:
        """

        # Lisätään kaikki tarvittavat painikkeet, tekstit ja kuvat menuun.
        self.__headline.pack()
        self.__mb.pack()
        self.__player_count.pack()
        self.__next.pack()
        self.__main.geometry("500x450")
        self.__backgroud.place(x=0, y=0, relwidth=1, relheight=1)

        # Alustetaan anettu pelaajien lukumäärä.
        self.reset()

    def reset2(self):
        """
        Pyyhkii pöydän tyhjäksi ja luo menun uudelleen.
        :return:
        """
        # Unohdetaan järjestyksessä kaikki mainissä olevat kuvakkeet, jolloin
        # ne poistuvat näkyvistä.
        for i in self.__main.grid_slaves():
            i.grid_forget()

        # Alustetaan tarvittavat muuttuvat.
        self.__whos_turn = 0
        self.__row_of_the_card = 0
        self.__card_reveal_check = 0
        self.__player_points.clear()
        self.__player_points = {"dealer": []}
        self.__player_cards.clear()
        self.__point_labels.clear()
        self.__backgroud.place_forget()

        # Luodaan menu
        self.create_menu()

    def reset3(self):
        """
        Pyyhkii myös pöydön tyhjäksi, mutta ei luo uutta menua. Pelaajien määrä
        ei muutu, mutta pöytään jaetaan uudet kortit. Sama toimintaperiaate
        kuin reset2, mutta eri tilanteeseen.
        :return:
        """

        for i in self.__main.grid_slaves():
            i.grid_forget()

        self.__whos_turn = 0
        self.__row_of_the_card = 0
        self.__card_reveal_check = 0
        self.__player_points.clear()
        self.__player_points = {"dealer": []}
        self.__player_cards.clear()
        self.__point_labels.clear()

    def player_and_dealer_points(self, player, amount):
        """
        Laskee pelaajien ja jakajan korttien summan
        :param player: Kyseinen pelaaja
        :param amount: Uuden kortin arvo
        :return: Palauttaa päivitetyn pistemäärän
        """
        # Tarkistetaan onko pelaajalla vielä pisteit, jos ei ole asetetaan
        # tämän hetkiset pisteet nollaksi.
        if len(self.__player_points[player]) != 0:
            exsiting_points = self.__player_points[player][0]
        else:
            exsiting_points = 0

        # Muodostetaan uudet pisteet lisäämällä uuden kortin arvo olemassa
        # oleviin pisteisiin ja muutetaan peelajan pistemäärä.
        new_points = exsiting_points + amount
        self.__player_points[player] = [new_points]

    def remove_menu(self):
        """
        Poistaa menun ja kutsuu create_table metodia, jotta pelipöytä luodaan.
        Tarkistaa myös onko annetu pelaajien määrä hyväksyttävä luku. Eli
        pelaajien määrä ei saa olla negatiivinen tai jokin muu kuin luku.
        :return:
        """

        # Testataan onko luku kelvollinen, muuten annetaan virhe ilmoitus ja
        # pelaajan pitää yrittää uudelleen.
        try:
            self.get_player_count_as_integer()
            if self.__player_count_int > 0:
                # Poistetaan menussa sijaitsevat kuvat ja painikkeet
                for i in self.__main.pack_slaves():
                    i.pack_forget()

                # Luku oli kelvollinen luodaan pelipöytä
                self.create_table()
            else:
                self.__error.configure(
                    text="Values must be greater than 0")
                self.__error.pack()
                self.reset()
        except ValueError:
            self.__error.configure(text="Values must be integer")
            self.__error.pack()
            self.reset()

    def create_table(self):
        """
        Luo pelipöydän. Lisää kaikki tarvittavat painikkeet ja kuvat pöydälle.
        Tässä metodissa myös luodaan alun kortit jakajalle.
        :return:
        """

        # Luodaan pelipöydän koko ja tar
        self.__main.geometry("750x800")
        arvo = random_card()[1]
        card = f"{random_card()[0]} {arvo}.gif"

        # Tilasto jakajan ässille ja aloituksessa oleville ässille.
        self.__how_many_aces["dealer"] = [0]
        self.__starting_hand_aces["dealer"] = [0]

        # Koska kuvakortit ovat arvoltaan 10 niin asetetaan niiden arvoksi 10
        if arvo > 10:
            arvo = 10
        # Ässä on arvoltaan 11
        elif arvo == 1:
            arvo = 11
            self.__how_many_aces["dealer"] = [1]
            self.__starting_hand_aces["dealer"] = [1]
        if self.__how_many_aces["dealer"][0] > 1:
            self.player_and_dealer_points("dealer", 1)
        else:
            self.player_and_dealer_points("dealer", arvo)

        # Luodaan jokaiselle pelaajalle sanakirja, johon voidaan lisätä pisteet
        # myöhemmin.
        for player in range(self.__player_count_int):
            self.__player_points[player] = []

        # Lisätään pelipöydälle kaikki tarvittavat kohdat.
        # Aluksi kortit ovat kuvapuoli alaspäin, joten valitaan se kuvaksi.
        self.__kuva = PhotoImage(file=card)
        self.__back_side = PhotoImage(file="Back.gif")

        # Lisätään Dealer pelipöydälle
        sarake = self.__player_count_int // 2 + 1
        self.__dealer = Label(self.__main, text="Dealer")
        self.__dealer.grid(row=1, column=sarake)

        # Lisätään yksi kuvapuoli ylöspäin ja yksi kuvapuoli alaspäin oleva
        # kortti jakajalle ja loput kortit kuvakuoli alaspäin pelaajille
        self.__kuva_implement = Label(self.__main, image=self.__kuva)
        self.__kuva_implement.grid(row=2, column=sarake)

        self.__back_side_implement = Label(self.__main, image=self.__back_side)
        self.__back_side_implement.grid(row=2, column=sarake + 1)

        self.__turn = Label(self.__main,
                            text=f"Pelaajan {self.__whos_turn + 1} vuoro")
        self.__turn.grid(row=3, column=1)

        self.__deal.grid(row=3, column=2)
        self.__next_turn.grid(row=3, column=3)
        self.__Ready.grid(row=2, column=6)

        column = 1
        cards = 2

        # Tässä lisätään itse kortit pelipöydälle
        for i in range(self.__player_count_int):
            row = 0
            for number in range(cards):
                self.__kortti = PhotoImage(file="Back.gif")
                self.__player_cards.append(self.__kortti)
                self.__kuvat = Label(self.__main, image=self.__kortti)
                self.__kuvat.grid(row=7 + row, column=column)
                row += 1
            column += 1

        # Poistetaan menun taustalla ollut kortti.
        self.__backgroud.place_forget()

    def card_reveal(self):
        """
        Ennen pelin aloittamista ei vielä näe kortteja. Tämä metodi paljastaa
        kaikkien pelaajien kortit, kun peli halutaan aloittaa.
        :return:
        """

        column = 1
        cards = 2

        # Arpoo jokaiselle pelaajalle kaksi korttia ja lisää ne pelipöydälle
        # kuvapuoli ylöspäin
        for i in range(self.__player_count_int):
            aces = 0
            row = 0

            # Tilasto jakajan ässille ja aloituksessa oleville ässille.
            self.__how_many_aces[i] = [0]
            self.__starting_hand_aces[i] = [0]

            for number in range(cards):
                arvo = random_card()[1]
                card = f"{random_card()[0]} {arvo}.gif"

                if arvo > 10:
                    arvo = 10
                elif arvo == 1:
                    arvo = 11
                    aces += 1
                    # Lisää tilastoon aloitusässän
                    self.__starting_hand_aces[self.__whos_turn] = [1]

                # Tarkastaa ässien määrän.
                if aces < 2:
                    self.player_and_dealer_points(i, arvo)
                    if aces == 1:
                        self.__how_many_aces[i] = [1]
                elif aces == 2:
                    self.player_and_dealer_points(i, 1)
                    self.__how_many_aces[i] = [0]

                # Lisää kortit esille pelipöydälle
                self.__kortti = PhotoImage(file=card)
                self.__player_cards.append(self.__kortti)
                self.__kuvat = Label(self.__main, image=self.__kortti)
                self.__kuvat.grid(row=7 + row, column=column)
                row += 1
            column += 1

        # Jokaisen pelaajan yläpuolella lukee heidän pistemääränsä eli
        # tässä lisätään pisteet pelaajien yläpuolelle.
        for i in range(self.__player_count_int):
            point_label = Label(self.__main)
            point_label.grid(row=6, column=i + 1)
            self.__point_labels.append(point_label)

            Label(self.__main, text="Player " + str(i + 1)) \
                .grid(row=5, column=i + 1, sticky=E)

        self.update()
        self.__Ready.grid_forget()
        self.__deal.configure(state=NORMAL)
        self.__next_turn.configure(state=NORMAL)

    def deal(self):
        """
        Tämä metodi vastaa korttien jakamisesta, kun pelaaja haluaa lisää
        kortteja. Joka kerta kun pelaaja haluaa uuden kortin deal valitsee ja
        lisää sen pelipöydälle. Metodi kutsuu myös automaattisesti chage_turn
        metodia ja vaihtaa pelaajien vuoroa jos korttien lukumäärä menee yli 21.
        :return:
        """
        arvo = random_card()[1]
        card = f"{random_card()[0]} {arvo}.gif"

        if arvo > 10:
            arvo = 10
        elif arvo == 1:
            arvo = 11
            self.__starting_hand_aces[self.__whos_turn] = [1]

        # Jos korttien summa ei ylitä 11 niin ässän arvo on 1. Muulloin sen
        # on oltava 1
        if self.__player_points[self.__whos_turn][0] < 11:
            self.player_and_dealer_points(self.__whos_turn, arvo)
            if arvo == 11:
                self.__how_many_aces[self.__whos_turn] = [1]
        # Koska korttien summa ylittää luvun 11 niin pitää tarkistella
        # tilannetta tarkemmin
        elif self.__player_points[self.__whos_turn][0] >= 11:
            # Jos kortti on ässä muutetaan sen arvo 1
            if arvo == 11:
                self.player_and_dealer_points(self.__whos_turn, 1)
            # Jos ässiä on yksi ja arvo on ylittämässä 21 niin
            # olemassa olevan ässän arvo muutetaan 1
            elif self.__player_points[self.__whos_turn][0] + arvo > 21 and \
                    self.__how_many_aces[self.__whos_turn][0] == 1:
                self.player_and_dealer_points(self.__whos_turn, arvo - 10)
                self.__how_many_aces[self.__whos_turn] = [0]
            else:
                self.player_and_dealer_points(self.__whos_turn, arvo)

        # Lisätään pelipöydälle tarvittavat kuvakkeet
        self.__card_ready = PhotoImage(file=card)
        self.__player_cards.append(self.__card_ready)

        self.__new_image = Label(self.__main, image=self.__card_ready)

        self.__new_image.grid(row=9 + self.__row_of_the_card,
                              column=self.__whos_turn + 1)
        self.__row_of_the_card += 1
        if self.__player_points[self.__whos_turn][0] > 21:
            self.change_turn()
        self.update()

    def change_turn(self):
        """
        Vaihtaa pelaajien vuoroa aina seuraavaan pelaajaan ja viimeisen
        pelaajan jälkeen kutsuu metodia dealer_hit, jossa jakajalle jaetaan
        kortit.
        :return:
        """

        # Muutta kortin rivin takaisin alkuun
        self.__row_of_the_card = 0
        # Jos pelaajien määrä ja kenen vuoro ovat samat niin silloin siirrytään
        # jakajan vuoroon
        if self.__whos_turn < self.__player_count_int - 1:
            self.__whos_turn += 1
        elif self.__whos_turn == self.__player_count_int - 1:
            self.dealer_hit()
        self.update()

    def dealer_hit(self):
        """
        Kun kaikki pelaajat ovat päättäneet vuoronsa jakajalle jaetaan tämän
        kortit.
        :return:
        """
        check = 0
        largest_number = 0
        who = 0

        # Tarkastetaan kenen pelaajan korttien summa oli suurin. Jos kahdella
        # pelaajalla oli yhtäsuuri summa niin silloin check arvoksi muutetaan
        # yksi
        for i in range(self.__player_count_int):
            if i < self.__player_count_int:
                if self.__player_points[i][0] <= 21:
                    if self.__player_points[i][0] == largest_number:
                        check = 1
                    elif self.__player_points[i][0] > largest_number:
                        largest_number = self.__player_points[i][0]
                        who = i
                        check = 0

        column = 2

        # Silmukassa jakajalle jaetaan kortteja kunnes tämän käsi on suurempi,
        # kuin pelaajan tai se ylittään 21. Jakaja ei ota kortteja jos summa
        # on 17 tai suurempi.
        while True:
            # Tarkistaa onko arvo suurempi kuin 17
            if self.__player_points["dealer"][0] < 17 and \
                    self.__player_points["dealer"][0] <= largest_number:
                arvo = random_card()[1]
                card = f"{random_card()[0]} {arvo}.gif"

                if arvo > 10:
                    arvo = 10
                elif arvo == 1:
                    arvo = 11
                # Jos korttien summa ei ylitä 11 niin ässän arvo on 1. Muulloin sen
                # on oltava 1
                if self.__player_points["dealer"][0] < 11:
                    self.player_and_dealer_points("dealer", arvo)
                    if arvo == 11:
                        self.__how_many_aces["dealer"] = [1]
                # Koska korttien summa ylittää luvun 11 niin pitää tarkistella
                # tilannetta tarkemmin
                elif self.__player_points["dealer"][0] >= 11:
                    if arvo == 11:
                        # Jos kortti on ässä muutetaan sen arvo 1
                        self.player_and_dealer_points("dealer", 1)
                    # Jos ässiä on yksi ja arvo on ylittämässä 21 niin
                    # olemassa olevan ässän arvo muutetaan 1
                    elif self.__player_points["dealer"][0] + arvo > 21 and \
                            self.__how_many_aces["dealer"][0] == 1:
                        self.player_and_dealer_points("dealer", arvo - 10)
                        self.__how_many_aces["dealer"] = [0]

                    else:
                        self.player_and_dealer_points("dealer", arvo)
                # Liätään tarvittavat kuvakkeet pelipöydälle
                self.__new_photo = PhotoImage(file=card)
                self.__player_cards.append(self.__new_photo)
                self.__back_side_implement = Label(self.__main,
                                                   image=self.__new_photo)
                self.__back_side_implement.grid(row=2,
                                                column=self.__player_count_int // 2 + column)
                column += 1
            else:
                break
        self.update()

        # Kutsutaan end_screen jotta saadaan pelin tulos selville
        self.end_screen(largest_number, who, check)

    def end_screen(self, largest_number, who, check):
        """
        Kun kaikki vuorot ovat ohi tämä metodi tarkastaa pistetilanteen ja
        tulostaa lopputuloksen pelipöydälle.

        :param largest_number: Suurin tietyn pelaajan yhteenlaskettujen
        korttien summa.

        :param who: Kenen pelaajista korttien summa on suurin
        :param check: Tarkistaa onko kahdella pelaajalla jaettu suurin summa.
        :return:
        """

        # Tulostetaan voittaja
        result = Label(self.__main)
        if self.__player_points["dealer"][0] > 21:
            if check == 1:
                result.configure(text="Draw", font=36)
            else:
                result.configure(text=f"Player {who + 1} wins", font=36)
        elif self.__player_points["dealer"][0] == largest_number:
            # Jos pelaajan ja jakanan summa on yhtä suuri, jakaja
            # voitaa aina paitsi jos summa on 21.
            if largest_number == 21:
                # Tarkastetaan onko kahdella pelaajalla sama korttien summa
                # jos on niin tulee tasapeli muuten ilmoitetaan voittaja.
                if check == 0:
                    result.configure(text=f"Player {who + 1} wins", font=36)
                else:
                    result.configure(text="Draw", font=36)
            else:
                result.configure(text="Dealer wins", font=36)
        elif self.__player_points["dealer"][0] > largest_number:
            result.configure(text="Dealer wins", font=36)
        else:
            # Tarkastetaan onko kahdella pelaajalla sama korttien summa
            # jos on niin tulee tasapeli muuten ilmoitetaan voittaja.
            if check == 1:
                result.configure(text="Draw", font=36)
            else:
                result.configure(text=f"Player {who + 1} wins", font=36)

        # Lisätään pelipöydälle halutut painikkeet ja tekstit, jotta voidaan
        # jatkaa.
        result.grid(row=15, column=1)

        quit_game = Button(self.__main, text="Exit", command=self.stop)
        quit_game.grid(row=15, column=4)
        reset = Button(self.__main, text="Reset players", command=self.reset2)
        reset.grid(row=15, column=2)
        new = Button(self.__main, text="New game", command=self.new_game)
        new.grid(row=15, column=3)

        # Sammutetaan hit ja stand ominaisuudet.
        self.__deal.configure(state=DISABLED)
        self.__next_turn.configure(state=DISABLED)
        self.__turn.grid_forget()

    def new_game(self):
        """
        Aloittaa uuden pelin siten, että pelaajamäärä ei muutu.
        :return:
        """
        self.reset3()
        self.create_table()

    def update(self):
        """
        Päivittää pelaajien ja jakajan korttien summan sekä kenen vuoro on
        pelipöydälle.
        :return:
        """
        # Jakana pisteet
        self.__dealer.configure(
            text=f"Dealer \nPoints {self.__player_points['dealer'][0]}")

        #Pelaajien pisteet
        for i in range(self.__player_count_int):
            self.__point_labels[i].configure(
                text=f"Points {self.__player_points[i][0]}")
        self.__turn.configure(text=f"Pelaajan {self.__whos_turn + 1} vuoro")


def help_tab():
    """
    Avaa Ohjeet pelaajalle
    :return:Nothing
    """
    # Luodaan uusi ikkun josta voidaan lukea ohjeet
    top = Toplevel()
    top.title("Rules")

    text_file = open("Rules", mode="r", encoding="utf-8")
    stuff = text_file.read()

    teksti = Text(top, width=70, height=15, font=("Helvetica", 16))
    teksti.insert(END, stuff)
    text_file.close()
    teksti.pack()

    top.mainloop()


def random_card():
    """
    Arpoo satunnaisen kortin ja palauttaa sen listan sisällä vastaavat kuvan
    tiedot.
    :return: Satunnainen kortti.
    """
    chosen_card = []

    # Arvotaan rivi 1-4 väliltä ja sen mukaan asetetaan maa.
    row_number = random.randrange(1, 5, 1)
    if row_number == 1:
        chosen_card.append("Clubs")
    elif row_number == 2:
        chosen_card.append("Diamonds")
    elif row_number == 3:
        chosen_card.append("Hearts")
    else:
        chosen_card.append("Spades")

    # Valitaan 1-13 väliltä kortti
    column_number = random.randrange(1, 14, 1)
    chosen_card.append(column_number)

    return chosen_card


def main():
    GUI()


if __name__ == "__main__":
    main()
