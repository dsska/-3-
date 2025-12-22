# Отчёт по проекту «Блогикум» — Часть 3 (адаптация к проекту)

Дата: 22.12.2025
Автор: ds_iva (адаптация под текущий проект)

---

## Описание

Документ подготовлен по образцу файла, который вы предоставили, и адаптирован к коду вашего проекта. Здесь для каждого пункта приводятся выдержки кода, пояснения и указания на файлы, в которых реализована требуемая функциональность.

---

## Раздел 1

1. Модели `Category`, `Location`, `Post`, `Comment` должны быть представлены в админке — `admin.py`.

- Файл: `blog/admin.py`
- Показ реализации:
```py
@admin.register(Post)
class PostAdmin(BlogAdmin):
    ...

@admin.register(Category)
class CategoryAdmin(BlogAdmin):
    ...

@admin.register(Location)
class LocationAdmin(BlogAdmin):
    ...

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    ...
```

2. В моделях у всех полей-связей `ForeignKey` заданы `on_delete` (CASCADE / SET_NULL):

- Файл: `blog/models.py`
- Показ реализации:
```py
author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='posts')
category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
```

3. В форме поста `PostForm` поля `is_published` и `pub_date` доступны для редактирования.

- Файл: `blog/forms.py`
- Показ реализации:
```py
class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=True,
    )
    class Meta:
        model = Post
        exclude = ['author']  # is_published и pub_date доступны
```

4. Содержательные ключи в URL (не `pk`/`id`):

- Файл: `blog/urls.py`
- Примеры:
```py
path('posts/<int:post_id>/', views.post_detail, name='post_detail')
path('category/<slug:category_slug>/', views.category_posts, name='category_posts')
path('profile/<str:username>/', views.profile, name='profile')
```

5. Для ника пользователя используется параметр `str`, а не `slug` (корректно):

- Файл: `blog/urls.py` (см. выше).

6. Во всех местах, кроме `path()`, URL формируются по имени маршрута через `redirect` / `reverse` / `{% url %}`:

- Шаблон: `templates/includes/header.html`
```django
<a href="{% url 'blog:create_post' %}">Добавить публикацию</a>
```
- Контроллеры: примеры `redirect('blog:profile', username=...)` в `blog/views.py`.

7. Извлечение объектов выполняется через `get_object_or_404()`:

- Примеры в `blog/views.py`:
```py
post = get_object_or_404(Post.objects.select_related(...), pk=post_id)
category = get_object_or_404(query_category(), slug=category_slug)
user = get_object_or_404(User, username=username)
```

8–9. Все наборы постов для страниц (главная, категория, профиль) аннотируются количеством комментариев и это централизовано:

- Файл: `blog/utils.py` — функция `filter_and_annotate_posts()` выполняет фильтрацию и аннотацию:
```py
def filter_and_annotate_posts(qs=None, include_published=True, author=None, order_by='-pub_date'):
    if qs is None:
        qs = base_post_queryset()
    if include_published:
        now = timezone.now()
        qs = qs.filter(pub_date__lte=now, is_published=True, category__is_published=True)
    qs = qs.annotate(comments_count=Count('comments'))
    if order_by:
        qs = qs.order_by(order_by)
    return qs
```
- В шаблонах используется `{{ post.comments_count }}` (см. `templates/includes/post_card.html`).

10. После `annotate()` вызывается сортировка — реализовано (см. `order_by(order_by)`).

11. Пагинация вынесена в отдельную функцию — `paginate_queryset` в `blog/utils.py`:
```py
def paginate_queryset(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
```

12. Набор постов на странице автора зависит от посетителя — только автор видит свои неопубликованные посты:

- `blog/views.py` — `profile`:
```py
if request.user.is_authenticated and request.user == user:
    posts = filter_and_annotate_posts(qs=user.posts.all(), include_published=False, order_by='-pub_date')
else:
    posts = filter_and_annotate_posts(author=user, include_published=True, order_by='-pub_date')
```

13. Фильтрация по опубликованности вынесена в функцию — параметр `include_published` в `filter_and_annotate_posts`.

14. Контроллеры создания/редактирования/удаления защищены `@login_required` — в `blog/views.py`:
```py
@login_required
def create_post(request): ...
@login_required
def edit_post(request, post_id): ...
@login_required
def delete_post(request, post_id): ...
```

15. `redirect()` используется с именами маршрутов (без явного `reverse()`) — примеры в `views.py`.

16. `post_detail()` анализирует автора поста и запрещает показ неопубликованного не-авторам (два `get_object_or_404`):

- `blog/views.py` — `post_detail`:
```py
post = get_object_or_404(Post.objects.select_related('author', 'category', 'location'), pk=post_id)
if not (request.user.is_authenticated and request.user == post.author):
    published_qs = filter_and_annotate_posts(qs=Post.objects.filter(pk=post_id), include_published=True)
    post = get_object_or_404(published_qs)
```

---

## Раздел 2 (дополнительно)

1. Папки `static`, `static-dev`, `html` есть в `.gitignore` — не хранятся в репозитории.

2. Форма поста настроена через `exclude` — `created_at` не попадёт в форму (`auto_now_add`).

3–4. Функция `filter_and_annotate_posts` объединяет фильтрацию по опубликованности и аннотацию, принимает `qs` по умолчанию — соответствует требованиям.

5. В `post_detail` используются два `get_object_or_404`, как рекомендовано.

6. Извлечения через связанные поля (`category.posts.all()`, `user.posts.all()`) используются в контроллерах — шаблоны и виды.

7. Сортировка: в проекте используется явное `order_by='-pub_date'`. Рекомендация: можно заменить на `order_by(*Post._meta.ordering)` для точного соответствия модели.

8. Обработка GET/POST: в проекте пока реализована через ветвление по `request.method`; можно перейти на `form = PostForm(request.POST or None, ...)` при желании.

9. Админ-класс для `User` с `UserAdmin` не найден — рекомендуется добавить регистрацию `get_user_model()` с `django.contrib.auth.admin.UserAdmin`.

---

## Выявленные несоответствия и предложения по исправлению

1. Не найдено: регистрация `UserAdmin` для модели пользователя (по требованию раздела 2.9).
   - Предложение: создать `users/admin.py` и зарегистрировать пользовательскую модель через `UserAdmin`.

2. Можно улучшить: заменить явное `order_by='-pub_date'` на `order_by(*Post._meta.ordering)` для соответствия рекомендациям и уменьшения дублирования кода.

3. Можно опционально унифицировать обработку форм: `form = PostForm(request.POST or None, request.FILES or None, instance=...)`.

---

## Приложения

- Ссылки на файлы с примерами в репозитории:
  - `blog/models.py`
  - `blog/admin.py`
  - `blog/forms.py`
  - `blog/urls.py`
  - `blog/views.py`
  - `blog/utils.py`
  - `templates/includes/post_card.html`

---

Если хотите, я могу:
- Сгенерировать PDF на основе этого Markdown (и добавить в репозиторий),
- Добавить номера строк или прямые ссылки (file:line) рядом с каждым фрагментом,
- Внести предложенные исправления (зарегистрировать `UserAdmin`, заменить порядок сортировки, унифицировать формы).

Скажите, какой следующий шаг предпочитаете — экспорт в PDF, добавление ссылок на строки или правки кода? 
