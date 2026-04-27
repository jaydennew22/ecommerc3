from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_emailotp_alter_customer_name_alter_customer_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='out_of_order',
            field=models.BooleanField(default=False),
        ),
    ]
