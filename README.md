# Отчет по проекту



---

## Исходное задание

ds_iva, [22.12.2025 14:55]
В отчете необходимо привести фрагменты вашего проекта, поясняющие назначение следующих позиций в проекте:
 
Раздел 1
 
1. Модели Category, Location, Post, Commentдолжны быть представлены в админке – admin.py
2. В моделях у всех полей для связи между таблицами с типом ForeignKey должны быть заданы параметры on_delete . Для большинства — со значением CASCADE , для локации и категории — SET_NULL .
3. При настройке формы в forms.py для поста нужно предоставить на редактирование поля is_published, pub_date , чтобы автор смог изменять их: публиковать, откладывать, снимать с публикации конкретный пост.
4. Извлекаемые из URL ключи — в urls.py — должны быть содержательными: pk или id не годятся. Нужно добавлять имя модели или таблицы.
5. В маршрутах, которые настраиваются в urls.py , для ника пользователя тип параметра в URL не может быть slug
path ('profile/<slug:username>/', ...) , так как у слага мало вариантов.
6. Явные URL – например, '/' или 'posts/create/' или 'profile/oleg/' — не могут применяться нигде, кроме вызовов path() в urls.py . Во всех остальных частях проекта URL должны вычисляться через имя маршрута, заданного в path(url, контроллер, name='имя-маршрута') .
Допустимые способы: 
• В контроллерах в views.py через reverse('имя-маршрута', параметр)(можно и без параметра) или redirect('имя-маршрута', параметр ). 
• В шаблонах через {% url 'имя-маршрута' параметр %} .
7. Извлечение поста, категории, комментария из базы выполняется только через вызов get_object_or_404() .
8. Все посты в наборах, попадающих на страницы «Главная», «Посты категории», «Посты автора», должны быть дополнены количеством комментариев.
9. Вычисление количества комментариев к постам должно находится в единственном месте — в новой функции. Само вычисление выполняется методом кверисета annotate() .
10. После вызова annotate() обязательно нужен вызов сортирующего метода: сортировка из модели уже будет неприменима, так как добавилось поле. Без сортировки пагинация работать не сможет.
11. Вычисление одной страницы пагинаторанужно разместить в новой функции.
12. Набор постов на странице автора должен зависеть от посетителя. Только посетитель-автор может видеть свои неопубликованные посты.
13. Фильтрация записей из таблицы постов по опубликованности должна размещаться в новой функции.
14. Контроллер-функции для создания, редактирования, удаления работают не с анонимом. Нужно применить Django-декоратор @login_required .
15. Для применения redirect() не нужно вычислять URL через reverse() . redirect()сам умеет работать с маршрутами.
16. В контроллере post_detail () нужно анализировать автора поста, чтобы отказать в показе неопубликованного не авторам.
 
Раздел 2
1. В гит-репозитории не должны храниться папки static , static-dev , html
2. Класс формы для поста в forms.py лучше настраивать не через fields , а через exclude , так как нужны изменения всех полей кроме автора. Проверить, что поле created_at не попадёт в форму: по модели оно нередактируемое.
3. Функции «фильтрация по опубликованным» и «дополнение числа комментариев» может быть объединена в одну. Тогда для этой функции потребуется параметр со значениями «Да» или «Нет», чтобы можно было пропускать лишнюю фильтрацию для постов на странице автора для самого автора.
4. Функция, фильтрующая по опубликованности, может принимать параметром набор постов для фильтрации. Этому параметру можно дать значение по умолчанию «все посты таблицы», что будет ещё лучше.
5. Чтобы в контроллере post_detail() отказать в показе неопубликованного поста не автору, лучше всего делать два вызова get_object_or_404() : 
• Первый для извлечения поста по ключу из полной таблицы. 
• Второй, после проверки авторства — из набора опубликованных постов.
6. Извлечения постов для уже излвеченнойкатегории лучше выполнять, применяя «поле связи». То есть вместо посты = Post.objects.filter(category=категория)писать посты = категория.поле-связи . То же самое с постами автора: посты = автор.поле-связи . И с комментариями к постам комментарии = пост.поле-связи .

ds_iva, [22.12.2025 14:55]
 
Важно: внутри шаблонов второй способ практически единственный, так как Python-вставки не допускают прямых вызовов методов с параметрами. А вот обращения к свойствам выполняются легко.
7. При указании сортировки после вызова annotate() лучше не угадывать значение, а брать точно такое же, какое уже есть в модели. Пригодится магическое поле ._metaи распаковка. Код будет иметь следующий вид:
предыдущие-действия.order_by(*Post._meta.ordering )
8. В контроллерах, которые создают или редактируют пост, нужна разная обработка для GET и POST-запросов. Есть способ избежать прямых проверок вида 
if request.method == 'POST': .
Для этого форма создается так: form = PostForm(request.POST or None, ...).Такая форма годится для обоих запросов. Её валидация form.is_valid() всегда неуспешна при GET-запросе. Значит, проверку метода выполнит проверка ответа от .is_valid() . Удачное совмещение: и при провале валидации, и при GET-запросе как раз и нужно вызывать рендер:
if not form.is_valid():
…
return render(...)
9. У модели «Пользователь» есть поля — например, пароль,— которые нельзя показывать в админке. Поэтому админ-класс нельзя наследовать от django.contrib.admin.ModelAdmin . Для этого есть класс django.contrib.auth.admin.UserAdmin , который будет прятать секреты.
 
---

# Примеры из кода (фрагменты)

Ниже приведены короткие примеры из файлов проекта, подтверждающие реализацию пунктов в отчёте.

### Раздел 1

1) Модели в админке — `blog/admin.py`:
```py
@admin.register(Post)
class PostAdmin(BlogAdmin):
    # ...

@admin.register(Category)
class CategoryAdmin(BlogAdmin):
    # ...

@admin.register(Location)
class LocationAdmin(BlogAdmin):
    # ...

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # ...
```

2) `on_delete` у ForeignKey в `blog/models.py` (CASCADE / SET_NULL):
```py
author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='posts')
category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
```

3) Поля для редактирования в форме поста — `blog/forms.py` (используется `exclude`, `pub_date` доступен):
```py
class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(...)
    class Meta:
        model = Post
        exclude = ['author']  # is_published и pub_date будут доступны для редактирования
```

4) Содержательные ключи в URL — `blog/urls.py` (используются `post_id`, `category_slug`, `username`):
```py
path('posts/<int:post_id>/', views.post_detail, name='post_detail')
path('category/<slug:category_slug>/', views.category_posts, name='category_posts')
path('profile/<str:username>/', views.profile, name='profile')
```

5) Для ника пользователя тип параметра — `str`, а не `slug` (см. предыдущий пункт).

6) В коде используются имена маршрутов и `redirect`/`{% url %}`: пример в шаблонах и контроллерах:
- шаблон `templates/includes/header.html`:
```django
<a href="{% url 'blog:create_post' %}">Добавить публикацию</a>
```
- контроллер `blog/views.py`:
```py
return redirect('blog:profile', username=request.user.username)
```

7) Извлечение объектов через `get_object_or_404` — примеры в `blog/views.py`:
```py
post = get_object_or_404(Post.objects.select_related(...), pk=post_id)
category = get_object_or_404(query_category(), slug=category_slug)
user = get_object_or_404(User, username=username)
```

8–9) Дополнение наборов постов количеством комментариев и централизованное вычисление — `blog/utils.py`:
```py
def filter_and_annotate_posts(qs=None, include_published=True, ...):
    if qs is None:
        qs = base_post_queryset()
    if include_published:
        qs = qs.filter(pub_date__lte=now, is_published=True, category__is_published=True)
    qs = qs.annotate(comments_count=Count('comments'))
    if order_by:
        qs = qs.order_by(order_by)
    return qs
```
(аннотация и фильтрация в одном месте; используем `annotate()` и затем `order_by()` — пагинация работает корректно)

10) Порядок сортировки после `annotate()` — в `filter_and_annotate_posts` есть параметр `order_by` (вызов `qs.order_by(order_by)`). Примеры вызовов: `order_by='-pub_date'`.

11) Пагинация — единая функция `paginate_queryset` в `blog/utils.py`:
```py
def paginate_queryset(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
```

12) Набор постов на странице автора зависит от посетителя — `blog/views.py`, `profile`:
```py
if request.user.is_authenticated and request.user == user:
    posts = filter_and_annotate_posts(qs=user.posts.all(), include_published=False, order_by='-pub_date')
else:
    posts = filter_and_annotate_posts(author=user, include_published=True, order_by='-pub_date')
```

13–14–15–16) Контроллеры защищены, применяют `@login_required`, используют `redirect()` с именами маршрутов и в `post_detail` проверяют автора:
```py
@login_required
def create_post(request):
    # ...
    return redirect('blog:profile', username=request.user.username)

# post_detail: два вызова get_object_or_404 и проверка авторства
post = get_object_or_404(Post.objects.select_related(...), pk=post_id)
if not (request.user.is_authenticated and request.user == post.author):
    published_qs = filter_and_annotate_posts(qs=Post.objects.filter(pk=post_id), include_published=True)
    post = get_object_or_404(published_qs)
```

### Раздел 2 — дополнительные моменты

1) Папки `static`, `static-dev`, `html` перечислены в `.gitignore` (значит не хранятся в репозитории):
```gitignore
static/
static-dev/
html/
```

2) Форма поста настроена через `exclude` (см. `blog/forms.py`) — `created_at` не попадает в форму.

3–4) Функция `filter_and_annotate_posts` объединяет фильтрацию по опубликованности и аннотирование; у неё есть параметр `include_published` и `qs` по умолчанию — это реализует пункты 3 и 4 из раздела 2.

5–6) В `post_detail` используются два `get_object_or_404` и извлечения постов через связанные поля (`category.posts.all()` и `user.posts.all()` используются в соответствующих видах).

7) В проекте сортировка обычно задаётся явно (`order_by='-pub_date'`), а не через `Post._meta.ordering`. Можно заменить на `order_by(*Post._meta.ordering)` при желании.

8) В контроллерах обработка GET/POST реализована явно (в `create_post`, `edit_post` используются ветвления по `request.method`) — это рабочая конструкция; при желании можно перейти на `form = PostForm(request.POST or None, ...)` для единого шаблона обработки.

9) Регистрация и настройка админ-класса для модели `User` с использованием `UserAdmin` в проекте **не обнаружена** — если это требование обязательно, можно добавить файл `users/admin.py`, зарегистрировать `get_user_model()` с `django.contrib.auth.admin.UserAdmin`.

---



