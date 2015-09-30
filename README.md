# wagtail-jinja2
Jinja2 extensions to support the main django tags on wagtail.
This won't make wagtail use jinja as a template backend (cms admin) but allow you to use jinja in your CMS pages.

## Setup the extensions
Example of settings.py:

```python
# Wagtail is still using django template as to 1.1
JINJA_EXCLUDE_TEMPLATE_PATHS = (
    ...
    "wagtailcore",
    "wagtailadmin",
    "wagtaildocs",
    "wagtailsnippets",
    "wagtailusers",
    "wagtailsites",
    "wagtailimages",
    "wagtailembeds",
    "wagtailsearch",
    "wagtailredirects",
    "wagtailforms",
    "wagtailstyleguide",
    ...
)
JINJA_EXCLUDE_REGEX = r'^(?!{}/).*'.format(
    '/|'.join(JINJA_EXCLUDE_TEMPLATE_PATHS))
    
TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'APP_DIRS': True,
        'DIRS': (os.path.join(ROOT_PATH, 'templates'), ),
        'NAME': 'jinja2',
        'OPTIONS': {
            'environment': 'config.jinja.Environment',
            'extensions': [
                'wagtail_jinja2.extensions.WagtailUserBarExtension',
                'wagtail_jinja2.extensions.WagtailImagesExtension',
            ],
            'match_extension': None,
            'trim_blocks': True,
            'lstrip_blocks': True,
            'match_regex': JINJA_EXCLUDE_REGEX,
            'context_processors': (
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dealer.contrib.django.staff.context_processor',
            ),
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (os.path.join(ROOT_PATH, 'templates'), ),
        'NAME': 'django',
        'OPTIONS': {
            'context_processors': (
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dealer.contrib.django.staff.context_processor',
            ),
            'loaders': (
                ('django.template.loaders.cached.Loader', (
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                )),
            )
        },
    },
]
```

## Use the tags in your templates
```html
<html>
    <head></head>
    <body>
    {% wagtailuserbar %}
    
    <h1>An image</h1>
    {% image page.image "width-720" %} <!-- Note that the filter_spec has to be between quotes -->
    
    <h1>A div with a background image</h1>
    {% image page.image "width-1440" as background_image %}
    <div style="background-image: url({{ background_image.url }});"></div>
    
    </body>
</html>
```

## Render rich text
The only approach I could think of for now is to create a render_html global_function (we are using django_jinja).

In ```myapp.templatetags.jinja_tags.py```:

```python
from jinja2 import Markup
from django_jinja import library

@library.global_function
def render_html(html):
    return jinja2.Markup(html)
```

In your template:

```html
    <p>{{ render_html(page.body) }}</p>
```

## Render blocks of a StreamField with original context
In ```myapp.templatetags.jinja_tags.py```:

```python
@library.global_function
@jinja2.contextfunction
def render_stream_child(context, stream_child):
    # Use the django_jinja to get the template content based on its name
    template = get_template(stream_child.block.meta.template)
    # Create a new context based on the current one as we can't edit it directly
    new_context = context.get_all()
    # Add the value on the context (value is the keyword chosen by wagtail for the blocks context)
    new_context['value'] = stream_child.value
    # Render the template with the context
    html = template.render(context=new_context)
    # Return the rendered template as safe html
    return jinja2.Markup(html)
```

In your template:

```html
{% for stream_child in page.body %} {# body is a StreamField #}
    {{ render_stream_child(stream_child) }}
{% endfor %}
```
