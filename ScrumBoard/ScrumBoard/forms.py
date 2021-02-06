from bootstrap_datepicker_plus import DatePickerInput
from django import forms

from ScrumBoard.models import *


class ScrumForm(forms.Form):

    def salva(self):
        """Salva i dati contenuti nel form all'interno del database"""
        pass


class BoardForm(ScrumForm):
    """Creazione del form per le board. Funziona solo per la creazione"""

    def __init__(self, utente_loggato=None, data=None):
        super().__init__(data)
        self.proprietario = utente_loggato
        self.fields['membri'].queryset = User.objects.exclude(id=utente_loggato.id)

    nome = forms.CharField(
        label="Nome board",
        max_length=24,
        min_length=3
    )

    membri = forms.ModelMultipleChoiceField(
        queryset=None,
        to_field_name='username',
        label='membri',
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )

    def salva(self):
        self.board = Board(
            nome=self.cleaned_data['nome'],
            proprietario=self.proprietario
        )
        self.board.save()
        self.board.partecipanti.set(self.cleaned_data['membri'])
        self.board.partecipanti.add(self.proprietario)
        return self.board


class ColumnForm(ScrumForm):

    def __init__(self, colonna=None, data=None):
        if colonna:
            self.colonna = colonna
            if not data:
                data = {'nome': colonna.nome}
        else:
            self.colonna = None
        super().__init__(data)

    nome = forms.CharField(
        label="Nome colonna",
        max_length=16,
        min_length=3
    )

    def salva(self, board=None):
        if not self.colonna:
            self.colonna = self.crea_colonna(board)
        else:
            self.colonna.nome = self.cleaned_data['nome']
        self.colonna.save()
        return self.colonna

    def crea_colonna(self, board):
        if board:
            colonna = Colonna(
                nome=self.cleaned_data['nome'],
                board=board
            )
        else:
            raise TypeError('stai cercando di creare una colonna senza fornire una board')

        return colonna


class UserForm(ScrumForm):

    def __init__(self, board, data=None):
        super().__init__(data)
        self.board = board
        self.fields['membri'].queryset = User.objects.exclude(id=board.proprietario.id)

    membri = forms.ModelMultipleChoiceField(
        queryset=None,
        to_field_name='username',
        label='membri',
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )

    def salva(self):
        self.board.partecipanti.set(self.cleaned_data['membri'])
        self.board.partecipanti.add(self.board.proprietario)


class CardForm(ScrumForm):

    def __init__(self, board=None, card=None, data=None):
        if card:
            board = card.colonna.board
            self.card = card
            if not data:
                data = self.estrai_dati_card(card)
        else:
            self.card = None

        if not board:
            raise TypeError('non è stata fornita né una board né una card')

        super().__init__(data)
        self.fields['colonna'].queryset = Colonna.objects.filter(board=board)
        self.fields['membri'].queryset = User.objects.all()

    nome = forms.CharField(
        label="Nome card",
        max_length=24,
        min_length=3
    )
    descrizione = forms.CharField(
        label="Descrizione",
        widget=forms.Textarea(attrs={"rows": 5, "cols": 20}),
        max_length=500,
        required=False
    )
    data_scadenza = forms.DateField(label="Scadenza",
                                    widget=DatePickerInput(format='%d-%m-%Y'),
                                    required=False
                                    )
    story_points = forms.IntegerField(
        label="Story points",
        max_value=20,
        required=False,
        initial=0
    )

    colonna = forms.ModelChoiceField(
        queryset=None,
        to_field_name='nome',
        label='colonna'
    )
    membri = forms.ModelMultipleChoiceField(
        queryset=None,
        to_field_name='username',
        label='membri',
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )

    def estrai_dati_card(self, card):
        data = {'nome': card.nome,
                'descrizione': card.descrizione,
                'data_scadenza': card.data_scadenza,
                'story_points': card.story_points,
                'colonna': card.colonna,
                'membri': card.membri.all()
                }
        return data

    def salva(self):
        if not self.card:
            self.card = Card()
        self.card.nome = self.cleaned_data['nome']
        self.card.descrizione = self.cleaned_data['descrizione']
        self.card.data_scadenza = self.cleaned_data['data_scadenza']
        self.card.colonna = self.cleaned_data['colonna']
        self.card.story_points = self.cleaned_data['story_points']

        self.card.save()
        self.card.membri.set(self.cleaned_data['membri'])
        return self.card
