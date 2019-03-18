from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from cloudinary.models import CloudinaryField

from authors.apps.authentication.models import User


# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=225)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    description = models.TextField()
    body = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    favourited = models.BooleanField(default=False)
    author = models.ForeignKey(User, related_name="articles", on_delete=models.CASCADE)


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("articles:articles", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            """
            creating slug
            """
            a_slug = slugify(self.title)
            origin = 1
            unique_slug = a_slug
            while Article.objects.filter(slug=unique_slug).exists():
                unique_slug = '{}-{}'.format(a_slug, origin)
                origin += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('created_at',)


class ArticleImage(models.Model):
    article = models.ForeignKey(
        Article,
        related_name='article_images',
        on_delete=models.CASCADE,
        verbose_name='Image associated with the article'
    )
    image = CloudinaryField('image', default="image/upload/v1551960935/books.png")
    created = models.DateTimeField(
        auto_now=True,
        verbose_name='When was this image saved'
    )
    description = models.CharField(db_index=True, max_length=255)

    class Meta:
        ordering = ('created',)
class Rate(models.Model):
    """
        Rate model schema
    """
    user = models.ForeignKey(
        User,
        related_name="rater",
        on_delete=models.CASCADE)

    article = models.ForeignKey(
        Article,
        related_name='rated_article',
        on_delete=models.CASCADE
    )

    your_rating = models.FloatField(null=False)
