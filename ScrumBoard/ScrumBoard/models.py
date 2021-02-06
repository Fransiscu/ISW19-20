from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Board(models.Model):
    """La rappresentazione di una board"""
    nome = models.CharField(max_length=50)
    proprietario = models.ForeignKey(User, on_delete=models.CASCADE)
    partecipanti = models.ManyToManyField(User, related_name='partecipanti')

    def get_absolute_url(self):
        return reverse('show-board', args=[str(self.id)])

    def num_colonne(self):
        """Restituisce il numero di colonne di questa board"""
        return Colonna.objects.filter(board=self).count()

    def conta_storypoints_usati(self):
        """Conta il totale dei punti storia utilizzati"""
        return self.get_ultima_colonna().conta_storypoints()

    def num_carte(self):
        """Conta il numero totatle di cards nella board"""
        totale = 0
        for colonna in Colonna.objects.filter(board=self):
            totale += colonna.num_carte()
        return totale

    def conta_scadute(self):
        """Conta le cards scaduta nella board"""
        count = 0
        colonne = list(Colonna.objects.filter(board=self).order_by('pk'))
        for colonna in colonne[:-1]:
            count += colonna.conta_scadute()
        return count

    def conta_storypoints(self):
        totale = 0
        for colonna in Colonna.objects.all().filter(board=self):
            totale += colonna.conta_storypoints()
        return totale

    def get_colonne(self):
        return Colonna.objects.all().filter(board=self)

    def get_ultima_colonna(self):
        return Colonna.objects.filter(board=self).last()

    def __str__(self):
        return self.nome

class Colonna(models.Model):
    """La rappresentazione di una colonna"""
    nome = models.CharField(max_length=50)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)

    def num_carte(self):
        """Conta il numero totale di cards nella colonna"""
        return Card.objects.filter(colonna=self).count()

    def conta_storypoints(self):
        """Conta il numero di punti storia totali nella colonna"""
        totale = 0
        for card in Card.objects.filter(colonna=self):
            totale += card.story_points
        return totale

    def conta_scadute(self):
        count = 0
        for card in Card.objects.filter(colonna=self):
            if (card.is_scaduta()):
                count += 1
        return count

    def get_cards(self):
        return Card.objects.all().filter(colonna=self)

    def get_absolute_url(self):
        return reverse('modifica-colonna', args=[str(self.id)])

    def is_ultima_colonna(self):
        """Restituisce true se questa colonna è l'ultima colonna della board"""
        return self == self.board.get_ultima_colonna()

    def __str__(self):
        return self.nome


class Card(models.Model):
    nome = models.CharField(max_length=50)
    descrizione = models.TextField(blank=True, default="")
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_scadenza = models.DateField(null=True)
    story_points = models.IntegerField(null=False, blank=True, default=0)
    colonna = models.ForeignKey(Colonna, on_delete=models.CASCADE)
    membri = models.ManyToManyField(User, related_name='membri')

    def is_scaduta(self):
        """Restituisce true se la card è scaduta"""
        if self.colonna.is_ultima_colonna():    #una card non può essere scaduta se è completata
            return False
        if self.data_scadenza is None:
            return False
        return date.today() > self.data_scadenza

    def get_users(self):
        return self.membri.all()


    def get_absolute_url(self):
        return reverse('show-card', args=[str(self.id)])

    def __str__(self):
        return self.nome
