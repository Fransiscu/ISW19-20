from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect

from ScrumBoard.forms import *
from ScrumBoard.models import *


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')


@login_required(login_url='/login')
def dashboard(request):
    return render(request, "dashboard.html", {'board': Board.objects.filter(partecipanti=request.user)})


@login_required(login_url='/login')
def showboard(request, board_id):
    board = Board.objects.get(pk=board_id)
    if request.user not in board.partecipanti.all():
        raise Http404
    else:
        return render(request, "showboard.html", {'board': board, 'board_id': board_id})


@login_required(login_url='/login')
def showcard(request, card_id):
    card = Card.objects.get(id=card_id)
    board = Board.objects.get(pk=card.colonna.board.id)

    if request.user not in board.partecipanti.all():
        raise Http404
    else:
        try:
            card = Card.objects.get(pk=card_id)
        except Card.DoesNotExist:
            card = None
    return render(request, "showcard.html", {'card': card, 'card_id': card_id})


@login_required(login_url='/login')
def crea_board(request):
    if request.method == "POST":
        board_form = BoardForm(request.user, request.POST)
        if board_form.is_valid():
            new_board = board_form.salva()

            redirect_to = Board.objects.get(pk=new_board.pk)
            return redirect(redirect_to)
    else:
        board_form = BoardForm(request.user)
    return render(request, "crea_board.html", {"form": board_form})


@login_required(login_url='/login')
def aggiungi_card(request, board_id):
    board = Board.objects.get(pk=board_id)

    if request.user not in board.partecipanti.all():
        raise Http404

    if request.method == "POST":
        card_form = CardForm(board=board, data=request.POST)
        if card_form.is_valid():
            card_form.salva()

            redirect_to = Board.objects.get(pk=board_id)
            return redirect(redirect_to)
    else:
        card_form = CardForm(board=board_id)
    return render(request, "aggiungi_card.html", {"board": board, "form": card_form})


@login_required(login_url='/login')
def aggiungi_colonna(request, board_id):
    board = Board.objects.get(pk=board_id)

    if request.user not in board.partecipanti.all():
        raise Http404

    if request.method == "POST":
        column_form = ColumnForm(data=request.POST)
        if column_form.is_valid():
            board = Board.objects.get(id=board_id)
            column_form.salva(board)

            return redirect(board)
    else:
        column_form = ColumnForm()
    return render(request, "aggiungi_colonna.html",
                  {"form": column_form, "board": board})


@login_required(login_url='/login')
def aggiungi_utente(request, board_id):
    board = Board.objects.get(pk=board_id)

    if request.user not in board.partecipanti.all():
        raise Http404

    if request.method == "POST":
        user_form = UserForm(board, data=request.POST)
        if user_form.is_valid():
            user_form.salva()

            return redirect(board)
    else:
        user_form = UserForm(board, data={'membri': board.partecipanti.all()})
    return render(request, "aggiungi_utente.html", {"board": board, "form": user_form})


@login_required(login_url='/login')
def modifica_colonna(request, column_id):
    colonna = Colonna.objects.get(id=column_id)
    board = Board.objects.get(pk=colonna.board_id)

    if request.user not in board.partecipanti.all():
        raise Http404

    if request.method == "POST":
        column_form = ColumnForm(colonna=colonna, data=request.POST)
        if column_form.is_valid():
            column_form.salva()

            return redirect(board)
        elif 'cancella_colonna' in request.POST:
            return cancella_colonna(request, column_id)
    else:
        column_form = ColumnForm(colonna=colonna)
    return render(request, "modifica_colonna.html",
                  {'form': column_form, 'column': colonna})


@login_required(login_url='/login')
def modifica_card(request, card_id):
    card = Card.objects.get(id=card_id)
    board = Board.objects.get(pk=card.colonna.board.id)

    if request.user not in board.partecipanti.all():
        raise Http404

    if request.method == "POST":
        card_form = CardForm(card=card, data=request.POST)

        if card_form.is_valid():
            card_form.salva()

            return redirect(board)
    else:
        card_form = CardForm(card=card)
    return render(request, "modifica_card.html", {"form": card_form, "card": card})


@login_required(login_url='/login')
def burndown(request, board_id):
    board = Board.objects.get(pk=board_id)

    if request.user not in board.partecipanti.all():
        raise Http404

    context = {
        'board': board
    }
    return render(request, "burndown.html", context)


@login_required(login_url='/login')
def cancella_board(request, board_id):
    """Elimina la board indicata"""
    Board.objects.get(id=board_id).delete()
    return HttpResponseRedirect('dashboard/')


@login_required(login_url='/login')
def cancella_colonna(request, column_id):
    """Elimina la colonna indicata"""
    colonna = Colonna.objects.get(id=column_id)
    board = Board.objects.get(pk=colonna.board_id)

    if request.user not in board.partecipanti.all():
        raise Http404
    else:
        colonna.delete()
        return redirect(board)


@login_required(login_url='/login')
def cancella_card(request, card_id):
    """Elimina la card indicata"""
    card = Card.objects.get(id=card_id)
    board = Board.objects.get(pk=card.colonna.board.id)

    if request.user not in board.partecipanti.all():
        raise Http404
    else:
        card.delete()
        column = Colonna.objects.get(id=card.colonna_id)
        return redirect(column)
