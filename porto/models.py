from django.db import models
from wagtail.search import index
from django import forms
from wagtail.core.models import Page
from wagtail.snippets.models import register_snippet
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel

from wagtail.core.fields import RichTextField, StreamField
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.tags import ClusterTaggableManager

from taggit.models import TaggedItemBase, Tag as TaggitTag

# Create your models here.


class PortoIndexPage(RoutablePageMixin, Page):
    description = models.CharField(max_length=255, blank=True,)

    content_panels = Page.content_panels + [
        FieldPanel('description', classname="full")
    ]

    def get_context(self, request, *args, **kwargs):
        context = super(PortoIndexPage, self).get_context(
            request, *args, **kwargs)
        postpages = self.get_children().live().order_by('-first_published_at')
        context['posts'] = self.posts
        context['blog_page'] = self
        return context
    
    def get_posts(self):
        return PostPage.objects.descendant_of(self).live()

    @route(r'^tag/(?P<tag>[-\w]+)/$')
    def post_by_tag(self, request, tag, *args, **kwargs):
        self.search_type = 'tag'
        self.search_term = tag
        self.posts = self.get_posts().filter(tags__slug=tag)
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^category/(?P<category>[-\w]+)/$')
    def post_by_category(self, request, category, *args, **kwargs):
        self.search_type = 'category'
        self.search_term = category
        self.posts = self.get_posts().filter(categories__slug=category)
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^$')
    def post_list(self, request, *args, **kwargs):
        self.posts = self.get_posts()
        return Page.serve(self, request, *args, **kwargs)


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

    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('body'),
    ]

    @property
    def blog_page(self):
        return self.get_parent().specific

    def get_context(self, request, *args, **kwargs):
        context = super(PostPage, self).get_context(request, *args, **kwargs)
        context['blog_page'] = self.blog_page
        context['post'] = self
        return context


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
