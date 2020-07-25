import unittest
import datetime
from django.test import TestCase, Client, LiveServerTestCase
from ScrumBoard.models import *
from django.contrib.auth.models import User
from utils import get_project_root
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys


class ModelTest(TestCase):
    def setUp(self):
        # inizializzazione client
        self.client = Client()

        # inizializzazione degli utenti
        self.utenti = []
        self.utenti.append(User(username="Utente1", password="admin"))
        self.utenti.append(User(username="Utente2", password="admin"))
        self.utenti.append(User(username="Utente3", password="admin"))
        for utente in self.utenti:
            utente.save()

        # inizializzazione delle boards
        self.boards = []
        self.boards.append(Board(nome='Board1', proprietario=self.utenti[0]))
        self.boards.append(Board(nome='Board2', proprietario=self.utenti[1]))
        self.boards.append(Board(nome='Board3', proprietario=self.utenti[2]))
        for board in self.boards:
            board.save()

        # inizializzazione delle colonne
        self.colonne = []
        self.colonne.append(Colonna(nome='Colonna1', board=self.boards[0]))
        self.colonne.append(Colonna(nome='Colonna2', board=self.boards[0]))
        self.colonne.append(Colonna(nome='Colonna3', board=self.boards[0]))
        self.colonne.append(Colonna(nome='Colonna4', board=self.boards[2]))
        for colonna in self.colonne:
            colonna.save()

        # inizializzazione delle carte
        self.cards = []
        self.cards.append(Card(nome="Prova",
                               descrizione="Carta di prova",
                               story_points="5",
                               data_scadenza=datetime.date.today() - datetime.timedelta(days=3),
                               colonna=self.colonne[0]))
        self.cards.append(Card(nome="Prova2",
                               descrizione="Carta di prova2",
                               story_points="3",
                               data_scadenza=datetime.date.today() + datetime.timedelta(days=3),
                               colonna=self.colonne[1]))
        self.cards.append(Card(nome="Prova3",
                               descrizione="Carta di prova3",
                               story_points="5",
                               data_scadenza=datetime.date.today(),
                               colonna=self.colonne[1]))
        self.cards.append(Card(nome="Completed Card",
                               descrizione="Una carta che ha completato il suo ciclo",
                               story_points=10,
                               data_scadenza=datetime.date.today() + datetime.timedelta(days=5),
                               colonna=self.boards[0].get_ultima_colonna()))
        for card in self.cards:
            card.save()

        # aggiunta dei partecipanti
        self.boards[0].partecipanti.add(self.utenti[1], self.utenti[2])

    def testFindUtenti(self):
        # test sugli utenti
        self.assertEqual(User.objects.all().count(), len(self.utenti))
        for utente in self.utenti:
            self.assertIn(utente, User.objects.all())

    def testFindBoards(self):
        # test sulle board
        self.assertEqual(len(Board.objects.all()), len(self.boards))
        for board in self.boards:
            self.assertIn(board, Board.objects.all())
        # self.assertEqual(Board.objects.get(proprietario=self.utente).proprietario, self.utente)

    def testFindColonne(self):
        # test sulle colonne
        self.assertEqual(len(Colonna.objects.all()), len(self.colonne))
        for colonna in self.colonne:
            self.assertIn(colonna, Colonna.objects.all())

    def testFindCards(self):
        # test sulle card
        self.assertEqual(len(Card.objects.all()), len(self.cards))
        for card in self.cards:
            self.assertIn(card, Card.objects.all())

        # si può pensare di usare questo test per eliminare tutti i successivi
        self.assertEqual(self.cards, list(Card.objects.all()))

        self.assertEqual(Card.objects.get(nome='Prova'), self.cards[0])
        self.assertEqual(Card.objects.get(nome='Prova2'), self.cards[1])
        # self.assertEqual(len(Card.objects.all().filter(nome__contains="Prova")), 3)
        # self.assertEqual(len(Card.objects.all().filter(nome__contains="Prova2")), 1)
        # self.assertEqual(len(Card.objects.all().filter(nome__contains="Prova3")), 1)
        # self.assertEqual(len(Card.objects.all().filter(descrizione__contains="Carta di prova")), 3)
        # self.assertEqual(len(Card.objects.all().filter(descrizione__contains="Carta di prova2")), 1)
        # self.assertEqual(len(Card.objects.all().filter(story_points="5")), 2)
        self.assertIn(self.cards[0], self.colonne[0].card_set.all())
        self.assertIn(self.cards[1], self.colonne[1].card_set.all())

    def testPartecipanti(self):
        self.assertIn(self.utenti[1], User.objects.filter(partecipanti=self.boards[0]))
        self.assertIn(self.utenti[2], User.objects.filter(partecipanti=self.boards[0]))

    def testNumeroColonne(self):
        self.assertEqual(self.boards[0].num_colonne(), self.contaColonne(self.boards[0]))
        self.assertEqual(self.boards[2].num_colonne(), self.contaColonne(self.boards[2]))

    def contaColonne(self, board):
        count = 0
        for colonna in self.colonne:
            if colonna.board == board:
                count += 1
        return count

    def testNumeroCarteInColonna(self):
        self.assertEqual(self.colonne[0].num_carte(), self.contaCarteColonna(self.colonne[0]))
        self.assertEqual(self.colonne[1].num_carte(), self.contaCarteColonna(self.colonne[1]))

    def contaCarteColonna(self, colonna):
        count = 0
        for card in self.cards:
            if card.colonna == colonna:
                count += 1
        return count

    def testNumeroCarteInBoard(self):
        self.assertEqual(self.boards[0].num_carte(), self.contaCarteBoard(self.boards[0]))

    def contaCarteBoard(self, board):
        count = 0
        for colonna in self.colonne:
            if colonna.board == board:
                count += self.contaCarteColonna(colonna)
        return count

    def testIsScaduta(self):
        self.assertTrue(self.cards[0].is_scaduta())
        self.assertFalse(self.cards[1].is_scaduta())
        self.assertFalse(self.cards[2].is_scaduta())

        # una card nell'ultima colonna non può essere scaduta
        self.assertFalse(self.cards[3].is_scaduta())

    def testContaScadute(self):
        self.assertEqual(self.boards[0].conta_scadute(), self.contaScadute(self.boards[0]))

    def contaScadute(self, board):
        count = 0
        for card in self.cards:
            if (card.colonna.board == board and card.is_scaduta()):
                count += 1
        return count;

    def testContaStorypointsUsati(self):
        self.assertEqual(self.boards[0].conta_storypoints_usati(), self.contaStorypointsUsati(self.boards[0]))

    def contaStorypoints(self, colonna):
        totale = 0
        for card in self.cards:
            if (card.colonna == colonna):
                totale += card.story_points
        return totale

    def contaStorypointsUsati(self, board):
        return self.contaStorypoints(board.get_ultima_colonna())

    def testDashboardView(self):
        # self.assertTrue(self.client.login(username=self.utenti[0].username, password='admin'))
        self.client.force_login(self.utenti[0])
        response = self.client.get('/dashboard/')
        for board in self.boards:
            if (board.partecipanti == self.utenti[0]):
                self.assertContains(response, board.nome)
"""
    def testShowBoard(self):
        # self.assertTrue(self.client.login(username='Utente1', password='admin'))

        response = self.client.get(self.boards[0].get_absolute_url())
        for colonna in Colonna.objects.filter(board=self.boards[0]):
            self.assertContains(response, colonna.nome)
            for card in Card.objects.filter(colonna=colonna):
                self.assertContains(response, card.nome)

    def testCreaBoardViewGet(self):
        response = self.client.get('/dashboard/crea_board')
        self.assertIsInstance(response.context['fo  rm'], BoardForm)

    def testCreaBoardPost(self):
        response = self.client.post('/dashboard/crea_board', {'nome':'testpipo'})
        print(response.context['nome'])"""


class ViewsTest(LiveServerTestCase):
    def setUp(self):
        #dovete scaricare il driver del browser corrispondente (chrome in questo caso)
        #da https://sites.google.com/a/chromium.org/chromedriver/downloads
        #metterlo in venv nel percorso qua sotto
        #ho cercato di fare in modo che il percorso che ho messo valesse per tutti,
        # ma potrebbe non funzionare a seconda della struttura del vostro progetto...
        self.selenium = webdriver.Chrome(str(get_project_root()) + r"\venv\Lib\site-packages\selenium\webdriver\chrome\chromedriver.exe")

        #inizializza qui tutto il test database
        super(ViewsTest, self).setUp()

    #questo metodo chiude il server quando finiscono i test
    def tearDown(self):
        self.selenium.quit()
        super(ViewsTest, self).tearDown()

    def testRegisterLogin(self):
        selenium = self.selenium

        # apre la pagina register
        selenium.get(self.live_server_url + '/register')

        # aspetta che gli elementi vengano caricati prima di cercarli, se ci mette più
        # di 5 secondi lancia un'eccezione
        timeout = 5
        try:
            WebDriverWait(selenium, timeout).until(EC.presence_of_element_located((By.ID, 'username')))
            WebDriverWait(selenium, timeout).until(EC.presence_of_element_located((By.ID, 'password1')))
            WebDriverWait(selenium, timeout).until(EC.presence_of_element_located((By.ID, 'password2')))
            WebDriverWait(selenium, timeout).until(EC.element_to_be_clickable((By.ID, 'submit')))
        except TimeoutException:
            print("Page took too long to load!")

        assert 'Registrati' in selenium.title
        assert 'scrumboard' in selenium.page_source

        # cerca gli elementi nella pagina
        username = selenium.find_element(By.NAME, 'username')
        password1 = selenium.find_element(By.NAME, 'password1')
        password2 = selenium.find_element(By.NAME, 'password2')
        submit = selenium.find_element(By.ID, 'submit')

        # inserisce le credenziali
        username.send_keys('Utente1')
        password1.send_keys('Admin1')
        password2.send_keys('Admin1')
        submit.click()

        #aspetta che la pagina cambi
        try:
            WebDriverWait(selenium, timeout).until(EC.url_contains('login'))
        except TimeoutException:
            print("Page took too long to load!")
        assert "Login" in selenium.title
        assert "successo" in selenium.page_source

        try:
            WebDriverWait(selenium, timeout).until(EC.presence_of_element_located((By.ID, 'username')))
            WebDriverWait(selenium, timeout).until(EC.presence_of_element_located((By.ID, 'password')))
            WebDriverWait(selenium, timeout).until(EC.element_to_be_clickable((By.ID, 'submit')))
        except TimeoutException:
            print("Page took too long to load!")

        assert 'Login' in selenium.title
        assert 'scrumboard' in selenium.page_source

        username = selenium.find_element(By.ID, 'username')
        password = selenium.find_element(By.ID, 'password')
        submit = selenium.find_element(By.ID, 'submit')

        username.send_keys('Utente1')
        password.send_keys('Admin1')
        submit.click()

        # controlla che siamo in dashboard
        try:
            WebDriverWait(selenium, timeout).until(EC.url_contains('dashboard'))
        except TimeoutException:
            print("Page took too long to load!")

        assert "Le mie board" in selenium.title


if __name__ == '__main__':
    unittest.main()
