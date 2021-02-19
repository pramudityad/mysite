from django.db import models
from django import forms
from wagtail.core.models import Page
from wagtail.snippets.models import register_snippet

from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel

from wagtail.core.fields import RichTextField, StreamField
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.tags import ClusterTaggableManager

from taggit.models import TaggedItemBase, Tag as TaggitTag

# Create your models here.


class PortoIndexPage(Page):
    description = models.CharField(max_length=255, blank=True,)

    content_panels = Page.content_panels + [
        FieldPanel('description', classname="full")
    ]

    def get_context(self, request, *args, **kwargs):
        context = super(PortoIndexPage, self).get_context(
            request, *args, **kwargs)
        postpages = self.get_children().live().order_by('-first_published_at')
        context['postpages'] = postpages
        context['menuitems'] = self.get_children().filter(
            live=True, show_in_menus=True)
        return context


class PostPage(Page):
    header_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    overview = models.CharField(max_length=250, blank=True,)
    body = RichTextField(blank=True)
    # carousel_image = models.ForeignKey(
    #     "wagtailimages.Image",
    #     null=True,
    #     blank=False,
    #     on_delete=models.SET_NULL,
    #     related_name="+",
    # )
    categories = ParentalManyToManyField('porto.PortoCategory', blank=True)
    link_url = models.URLField(max_length=250, blank=True,)
    tags = ClusterTaggableManager(through='porto.PortoPageTag', blank=True)
    date = models.DateField("Post date")

    content_panels = Page.content_panels + [
        ImageChooserPanel("header_image"),
        FieldPanel('overview'),
        FieldPanel('body', classname="full"),
        FieldPanel('link_url'),
        FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        FieldPanel('tags'),
        FieldPanel('date'),
        # MultiFieldPanel(
        #     [InlinePanel("carousel_image", max_num=5,
        #                  min_num=1, label="Image")],
        #     heading="Carousel Images",
        # ),
    ]


@register_snippet
class PortoCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=80)
    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class PortoPageTag(TaggedItemBase):
    content_object = ParentalKey('PostPage', related_name='post_tags')


@register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy = True
