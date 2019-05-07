I was able to migrate a RichTextField to StreamField with a RichTextBlock with this script (this assumes a schema that looks like the first 3 chapters of the Wagtail Getting Started tutorial). I found that it was easier to think about this process by breaking it into distinct steps: fresh db from backup/make backup, schema migration, data migration, and admin/template alterations. I found that I needed to loop through each BlogPost and all of its associated PageRevision. Editing the live published data was straightforward, but the drafts are stored as serialized JSON two levels deep, which was tricky to figure out how to interact with. Hopefully this script helps others. Note: this script doesn't migrate in reverse.

0004_convert_data.py
```
import json
from django.db import migrations
import wagtail.core.fields
from wagtail.core.rich_text import RichText


def convert_data(apps, schema_editor):
    blog_page = apps.get_model('blog', 'BlogPage')
    for post in blog_page.objects.all():
        print('\n', post.title)
        # edit the live post
        if post.body.raw_text and not post.body:
            post.body = [('paragraph', RichText(post.body.raw_text))]
            print('Updated ' + post.title)
            post.save()

        # edit drafts associated with post
        if post.has_unpublished_changes:
            print(post.title + ' has drafts...')
            for rev in post.revisions.all():
                data = json.loads(rev.content_json)
                body = data['body']
                print(body)

                print('This is current JSON:', data, '\n')
                data['body'] = json.dumps([{
                    "type": "paragraph",
                    "value": body
                }])
                rev.content_json = json.dumps(data)
                print('This is updated JSON:', rev.content_json, '\n')

                rev.save()

        print('Completed ' + post.title + '.' + '\n')


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_blogpage_stream'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpage',
            name='body',
            field=wagtail.core.fields.StreamField([('paragraph', wagtail.core.blocks.RichTextBlock())], blank=True),
        ),

        migrations.RunPython(convert_data),
    ]
```

models.py

```
from django.db import models

from wagtail.core.models import Page
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.search import index


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]


class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    # body = RichTextField(blank=True)
    body = StreamField([
        ('paragraph', blocks.RichTextBlock()),
    ], blank=True)
    stream = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
    ], blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        StreamFieldPanel('body'),
        StreamFieldPanel('stream'),
    ]


```

templates/blog/blog_page.html

```
{% extends "base.html" %}

{% load wagtailcore_tags %}

{% block body_class %}template-blogpage{% endblock %}

{% block content %}
    <h1>{{ page.title }}</h1>
    <p class="meta">{{ page.date }}</p>

    <div class="intro">{{ page.intro }}</div>

    {{ page.body }}

    <p><a href="{{ page.get_parent.url }}">Return to blog</a></p>

{% endblock %}
```
