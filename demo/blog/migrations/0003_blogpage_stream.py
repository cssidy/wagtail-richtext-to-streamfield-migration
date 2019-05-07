# Generated by Django 2.2.1 on 2019-05-03 19:25

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_blogpage'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpage',
            name='stream',
            field=wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.CharBlock(classname='full title')), ('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock())], blank=True),
        ),
    ]