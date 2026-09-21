from django.core.management.base import BaseCommand

from store.models import DeliveryLocation


class Command(BaseCommand):

    help = "Seed delivery locations for Arikey Skincare"

    def handle(self, *args, **kwargs):

        locations = [

            # =================================================
            # NIGERIA — LAGOS
            # =================================================

            ("Nigeria", "Lagos", "Ikeja", ""),
            ("Nigeria", "Lagos", "Maryland", ""),
            ("Nigeria", "Lagos", "Ojota", ""),
            ("Nigeria", "Lagos", "Ketu", ""),
            ("Nigeria", "Lagos", "Alapere", ""),
            ("Nigeria", "Lagos", "Ogba", ""),
            ("Nigeria", "Lagos", "Agege", ""),
            ("Nigeria", "Lagos", "Abule Egba", ""),
            ("Nigeria", "Lagos", "Alimosho", ""),
            ("Nigeria", "Lagos", "Egbeda", ""),
            ("Nigeria", "Lagos", "Idimu", ""),
            ("Nigeria", "Lagos", "Ipaja", ""),
            ("Nigeria", "Lagos", "Ayobo", ""),

            ("Nigeria", "Lagos", "Yaba", ""),
            ("Nigeria", "Lagos", "Surulere", ""),
            ("Nigeria", "Lagos", "Mushin", ""),
            ("Nigeria", "Lagos", "Oshodi", ""),
            ("Nigeria", "Lagos", "Isolo", ""),
            ("Nigeria", "Lagos", "Ilupeju", ""),
            ("Nigeria", "Lagos", "Gbagada", ""),
            ("Nigeria", "Lagos", "Bariga", ""),

            ("Nigeria", "Lagos", "Victoria Island", ""),
            ("Nigeria", "Lagos", "Ikoyi", ""),
            ("Nigeria", "Lagos", "Lekki Phase 1", ""),
            ("Nigeria", "Lagos", "Lekki Phase 2", ""),
            ("Nigeria", "Lagos", "Chevron", ""),
            ("Nigeria", "Lagos", "Ajah", ""),
            ("Nigeria", "Lagos", "Sangotedo", ""),
            ("Nigeria", "Lagos", "Awoyaya", ""),
            ("Nigeria", "Lagos", "Ibeju-Lekki", ""),

            ("Nigeria", "Lagos", "Lagos Island", ""),
            ("Nigeria", "Lagos", "Marina", ""),
            ("Nigeria", "Lagos", "CMS", ""),

            ("Nigeria", "Lagos", "Festac", ""),
            ("Nigeria", "Lagos", "Amuwo Odofin", ""),
            ("Nigeria", "Lagos", "Mile 2", ""),
            ("Nigeria", "Lagos", "Satellite Town", ""),

            ("Nigeria", "Lagos", "Ikorodu", ""),
            ("Nigeria", "Lagos", "Igbogbo", ""),
            ("Nigeria", "Lagos", "Agric Ikorodu", ""),
            ("Nigeria", "Lagos", "Epe", ""),
            ("Nigeria", "Lagos", "Badagry", ""),

            # =================================================
            # NIGERIA — KWARA
            # =================================================

            ("Nigeria", "Kwara", "Tanke", ""),
            ("Nigeria", "Kwara", "Fate", ""),
            ("Nigeria", "Kwara", "GRA Ilorin", ""),
            ("Nigeria", "Kwara", "Taiwo", ""),
            ("Nigeria", "Kwara", "Challenge", ""),
            ("Nigeria", "Kwara", "Sango", ""),
            ("Nigeria", "Kwara", "Oke Odo", ""),
            ("Nigeria", "Kwara", "Pipeline", ""),
            ("Nigeria", "Kwara", "Oloje", ""),
            ("Nigeria", "Kwara", "Adewole", ""),
            ("Nigeria", "Kwara", "Asa Dam", ""),
            ("Nigeria", "Kwara", "Offa", ""),
            ("Nigeria", "Kwara", "Omu-Aran", ""),
            ("Nigeria", "Kwara", "Jebba", ""),

            # =================================================
            # NIGERIA — ABUJA
            # =================================================

            ("Nigeria", "FCT", "Central Area", ""),
            ("Nigeria", "FCT", "Wuse", ""),
            ("Nigeria", "FCT", "Wuse 2", ""),
            ("Nigeria", "FCT", "Garki", ""),
            ("Nigeria", "FCT", "Maitama", ""),
            ("Nigeria", "FCT", "Asokoro", ""),
            ("Nigeria", "FCT", "Jabi", ""),
            ("Nigeria", "FCT", "Gwarinpa", ""),
            ("Nigeria", "FCT", "Kubwa", ""),
            ("Nigeria", "FCT", "Lugbe", ""),

            # =================================================
            # NIGERIA — OTHER MAJOR CITIES
            # =================================================

            ("Nigeria", "Oyo", "Ibadan", ""),
            ("Nigeria", "Oyo", "Bodija", ""),
            ("Nigeria", "Oyo", "Ring Road", ""),
            ("Nigeria", "Oyo", "Challenge", ""),

            ("Nigeria", "Ogun", "Abeokuta", ""),
            ("Nigeria", "Ogun", "Ota", ""),
            ("Nigeria", "Ogun", "Mowe", ""),
            ("Nigeria", "Ogun", "Ibafo", ""),

            ("Nigeria", "Osun", "Osogbo", ""),
            ("Nigeria", "Osun", "Ile-Ife", ""),
            ("Nigeria", "Osun", "Ilesa", ""),

            ("Nigeria", "Ondo", "Akure", ""),
            ("Nigeria", "Ondo", "Ondo City", ""),

            ("Nigeria", "Edo", "Benin City", ""),
            ("Nigeria", "Delta", "Asaba", ""),
            ("Nigeria", "Delta", "Warri", ""),

            ("Nigeria", "Rivers", "Port Harcourt", ""),
            ("Nigeria", "Rivers", "GRA Port Harcourt", ""),

            ("Nigeria", "Enugu", "Enugu", ""),
            ("Nigeria", "Anambra", "Awka", ""),
            ("Nigeria", "Anambra", "Onitsha", ""),

            ("Nigeria", "Kano", "Kano", ""),
            ("Nigeria", "Kaduna", "Kaduna", ""),
            ("Nigeria", "Plateau", "Jos", ""),

            # =================================================
            # GHANA
            # =================================================

            ("Ghana", "Greater Accra", "Accra", ""),
            ("Ghana", "Greater Accra", "East Legon", ""),
            ("Ghana", "Greater Accra", "Tema", ""),
            ("Ghana", "Ashanti", "Kumasi", ""),

            # =================================================
            # KENYA
            # =================================================

            ("Kenya", "Nairobi County", "Nairobi", ""),
            ("Kenya", "Nairobi County", "Westlands", ""),
            ("Kenya", "Nairobi County", "Kilimani", ""),
            ("Kenya", "Mombasa County", "Mombasa", ""),
            ("Kenya", "Kisumu County", "Kisumu", ""),

            # =================================================
            # SOUTH AFRICA
            # =================================================

            ("South Africa", "Gauteng", "Johannesburg", ""),
            ("South Africa", "Gauteng", "Pretoria", ""),
            ("South Africa", "Gauteng", "Sandton", ""),
            ("South Africa", "Western Cape", "Cape Town", ""),
            ("South Africa", "KwaZulu-Natal", "Durban", ""),

            # =================================================
            # UNITED KINGDOM
            # =================================================

            ("United Kingdom", "England", "London", ""),
            ("United Kingdom", "England", "Manchester", ""),
            ("United Kingdom", "England", "Birmingham", ""),
            ("United Kingdom", "England", "Leeds", ""),
            ("United Kingdom", "Scotland", "Edinburgh", ""),
            ("United Kingdom", "Scotland", "Glasgow", ""),

            # =================================================
            # UNITED STATES
            # =================================================

            ("United States", "New York", "New York City", ""),
            ("United States", "New York", "Buffalo", ""),

            ("United States", "Texas", "Houston", ""),
            ("United States", "Texas", "Dallas", ""),
            ("United States", "Texas", "Austin", ""),

            ("United States", "California", "Los Angeles", ""),
            ("United States", "California", "San Francisco", ""),
            ("United States", "California", "San Diego", ""),

            ("United States", "Florida", "Miami", ""),
            ("United States", "Florida", "Orlando", ""),

            ("United States", "Georgia", "Atlanta", ""),

            ("United States", "Illinois", "Chicago", ""),

            ("United States", "Maryland", "Baltimore", ""),

            ("United States", "New Jersey", "Newark", ""),

            # =================================================
            # CANADA
            # =================================================

            ("Canada", "Ontario", "Toronto", ""),
            ("Canada", "Ontario", "Ottawa", ""),
            ("Canada", "British Columbia", "Vancouver", ""),
            ("Canada", "Alberta", "Calgary", ""),
            ("Canada", "Quebec", "Montreal", ""),
        ]

        created_count = 0
        updated_count = 0


        for (
            country,
            state_region,
            city_area,
            landmark
        ) in locations:

            location, created = (
                DeliveryLocation.objects.update_or_create(

                    country=country,

                    state_region=state_region,

                    city_area=city_area,

                    landmark=landmark,

                    defaults={

                        # We start with quote because
                        # actual delivery prices have
                        # not been supplied yet.

                        "delivery_type": "quote",

                        "fee": None,

                        "is_active": True,
                    }
                )
            )


            if created:

                created_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: {location}"
                    )
                )

            else:

                updated_count += 1

                self.stdout.write(
                    f"Already exists: {location}"
                )


        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                (
                    f"Finished! "
                    f"{created_count} created, "
                    f"{updated_count} already existed."
                )
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                (
                    "Total delivery locations: "
                    f"{DeliveryLocation.objects.count()}"
                )
            )
        )