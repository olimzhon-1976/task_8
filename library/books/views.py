from django.shortcuts import render, redirect, get_object_or_404
from .forms import BookForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Book
from django.contrib.auth.models import User


def index(request):
    return render(request, 'books/index.html')


def is_librarian(user):
    return user.groups.filter(name='Librarians').exists()


@login_required
@user_passes_test(is_librarian)
def book_list(request):
    # books = Book.objects.all()
    query = request.GET.get('q', '')
    author = request.GET.get('author', None)
    genre = request.GET.get('genre', None)
    year = request.GET.get('year', None)
    books = Book.objects.filter(is_deleted=False)

    if query:
        books = books.filter(title__icontains=query)

    if author:
        books = books.filter(author__id=author)

    if genre:
        books = books.filter(genre__id=genre)

    if year:
        books = books.filter(publication_date__year=year)

    return render(request, 'books/book_list.html', {'books': books})


@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/add_book.html', {'form': form})


@login_required
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form})


@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})


# def delete_book(request, book_id):
#     book = Book.objects.get(id=book_id)
#     book.is_deleted = True
#     book.save()
#     return redirect('book_list')



def log_user_action(user, action_type, action_description):
    UserAction.objects.create(user=user, action_type=action_type, action_description=action_description)


def delete_book(request, book_id):
    book = Book.objects.get(id=book_id)
    book.is_deleted = True
    book.save()
    log_user_action(request.user, 'delete', f'Deleted book with id: {book_id}')
    return redirect('book_list')

def user_action_history(request):
    actions = UserAction.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'history/action_history.html', {'actions': actions})