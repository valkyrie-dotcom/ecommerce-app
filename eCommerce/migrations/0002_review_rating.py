from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("eCommerce", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="rating",
            # Reviews written before ratings existed are given 5
            field=models.PositiveSmallIntegerField(
                choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
                default=5,
                validators=[MinValueValidator(1), MaxValueValidator(5)],
            ),
            preserve_default=False,
        ),
    ]
