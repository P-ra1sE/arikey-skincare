from django.core.management.base import BaseCommand
from store.models import Product


class Command(BaseCommand):
    help = "Load Arikey Skincare products into the database"

    def handle(self, *args, **kwargs):

        products = [
            {
                "id": 1,
                "name": "5D Whitening Molato Soap (Small)",
                "price": 12000,
                "image": "molato-small.jpg",
            },
            {
                "id": 2,
                "name": "5D Whitening Molato Soap (Medium)",
                "price": 17000,
                "image": "molato-medium.jpg",
            },
            {
                "id": 3,
                "name": "5D Whitening Molato Soap (Big)",
                "price": 28000,
                "image": "molato-big.jpg",
            },
            {
                "id": 4,
                "name": "5D Whitening Healing Black Soap (Small)",
                "price": 8500,
                "image": "healing-black-soap-small.jpg",
            },
            {
                "id": 5,
                "name": "5D Whitening Healing Black Soap (Medium)",
                "price": 14000,
                "image": "healing-black-soap-medium.jpg",
            },
            {
                "id": 6,
                "name": "5D Whitening Healing Black Soap (Big)",
                "price": 30000,
                "image": "healing-black-soap-big.jpg",
            },
            {
                "id": 7,
                "name": "Lightening Soap (Small)",
                "price": 10000,
                "image": "lightening-soap-small.jpg",
            },
            {
                "id": 8,
                "name": "Lightening Soap (Big)",
                "price": 26000,
                "image": "lightening-soap-big.jpg",
            },
            {
                "id": 9,
                "name": "Face Soap",
                "price": 6000,
                "image": "face-soap.jpg",
            },
            {
                "id": 10,
                "name": "Body Wash",
                "price": 15000,
                "image": "body-wash.jpg",
            },
            {
                "id": 11,
                "name": "Body & Face Scrub",
                "price": 15000,
                "image": "body-face-scrub.jpg",
            },
            {
                "id": 12,
                "name": "Pure Glow Oil",
                "price": 12000,
                "image": "pure-glow-oil.jpg",
            },
            {
                "id": 13,
                "name": "Rude Oil",
                "price": 5000,
                "image": "rude-oil.jpg",
            },
            {
                "id": 14,
                "name": "Whitening Face Cream",
                "price": 15000,
                "image": "whitening-face-cream.jpg",
            },
            {
                "id": 15,
                "name": "Acne & Pimples Face Cream",
                "price": 12000,
                "image": "acne-pimples-face-cream.jpg",
            },
            {
                "id": 16,
                "name": "Face Serum",
                "price": 12000,
                "image": "face-serum.jpg",
            },
            {
                "id": 17,
                "name": "Face Toner",
                "price": 8000,
                "image": "face-toner.jpg",
            },
            {
                "id": 18,
                "name": "Whitening Body Cream",
                "price": 20000,
                "image": "whitening-body-cream.jpg",
            },
            {
                "id": 19,
                "name": "Hot Chocolate Body Cream",
                "price": 17000,
                "image": "hot-chocolate-body-cream.jpg",
            },
            {
                "id": 20,
                "name": "Lip Balm",
                "price": 3000,
                "image": "lip-balm.jpg",
            },
            {
                "id": 21,
                "name": "Lip Scrub",
                "price": 3000,
                "image": "lip-scrub.jpg",
            },
            {
                "id": 22,
                "name": "Barbie Pink Gloss",
                "price": 5000,
                "image": "barbie-pink-gloss.jpg",
            },
            {
                "id": 23,
                "name": "Clear Gloss",
                "price": 5000,
                "image": "clear-gloss.jpg",
            },
            {
                "id": 24,
                "name": "Brownie Gloss",
                "price": 5000,
                "image": "brownie-gloss.jpg",
            },
            {
                "id": 25,
                "name": "Red Cherry Gloss",
                "price": 5000,
                "image": "red-cherry-gloss.jpg",
            },
            {
                "id": 26,
                "name": "Brush",
                "price": 1000,
                "image": "brush.jpg",
            },
            {
                "id": 27,
                "name": "Lip Mask",
                "price": 1000,
                "image": "mask.jpg",
            },

            # COMBO SETS

            {
                "id": 101,
                "name": "Face Set",
                "price": 47000,
                "image": "face-set.png",
            },
            {
                "id": 102,
                "name": "Student Fair Set",
                "price": 57000,
                "image": "student-fair.png",
            },
            {
                "id": 103,
                "name": "Students Dark Set",
                "price": 55000,
                "image": "students-dark.png",
            },
            {
                "id": 104,
                "name": "Full Set",
                "price": 145000,
                "image": "full-set.png",
            },
            {
                "id": 105,
                "name": "Hot Choco Set",
                "price": 85000,
                "image": "hot-choco.jpg",
            },
            {
                "id": 106,
                "name": "Caramel Set",
                "price": 100000,
                "image": "caramel-set.png",
            },
            {
                "id": 107,
                "name": "Mini Set",
                "price": 80000,
                "image": "mini-set.png",
            },
        ]

        created_count = 0
        updated_count = 0

        for product_data in products:

            product, created = Product.objects.update_or_create(
                id=product_data["id"],
                defaults={
                    "name": product_data["name"],
                    "price": product_data["price"],
                    "image": product_data["image"],
                    "is_active": True,
                },
            )

            if created:
                created_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: {product.id} - {product.name}"
                    )
                )

            else:
                updated_count += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"Updated: {product.id} - {product.name}"
                    )
                )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished! {created_count} created, "
                f"{updated_count} updated."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Total products: {Product.objects.count()}"
            )
        )