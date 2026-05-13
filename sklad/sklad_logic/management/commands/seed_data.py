from django.core.management.base import BaseCommand
from django.db import connection, transaction
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = "Заполняет БД тестовыми данными"

    def handle(self, *args, **options):
        with transaction.atomic():
            with connection.cursor() as cursor:
                # === Склады ===
                self.stdout.write("Склады...")
                warehouses = [
                    ("Основной склад", "г. Минск, ул. Промышленная, 15", 5000),
                    ("Дополнительный склад", "г. Минск, ул. Логойский тракт, 25", 3000),
                    ("Склад-магазин", "г. Минск, ул. Независимости, 100", 1000),
                ]
                for name, addr, cap in warehouses:
                    cursor.execute(
                        "INSERT INTO sklad_logic_warehouses (name, address, capacity) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                        [name, addr, cap],
                    )

                # === Поставщики ===
                self.stdout.write("Поставщики...")
                suppliers = [
                    ("ООО «ПродуктСервис»", "+375291234501", "info@produkt.by"),
                    ("ИП Иванов А.П.", "+375291234502", "ivanov@tut.by"),
                    ("ЗАО «БелТорг»", "+375291234503", "zakaz@beltorg.by"),
                    ("ООО «ЕвроПродукт»", "+375291234504", "sales@europrod.by"),
                    ("ЧУП «СкладЛайн»", "+375291234505", "info@skladline.by"),
                ]
                for name, phone, email in suppliers:
                    cursor.execute(
                        "INSERT INTO sklad_logic_suppliers (name, contact_phone, email) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                        [name, phone, email],
                    )

                # === Категории (с вложенностью) ===
                self.stdout.write("Категории...")
                categories_data = [
                    (None, "Напитки"),
                    (None, "Продукты питания"),
                    (None, "Бытовая химия"),
                    (1, "Газированные напитки"),
                    (1, "Соки"),
                    (1, "Вода"),
                    (2, "Бакалея"),
                    (2, "Консервы"),
                    (2, "Молочные продукты"),
                    (2, "Замороженные продукты"),
                    (3, "Моющие средства"),
                    (3, "Чистящие средства"),
                    (4, "Кола"),
                    (4, "Лимонады"),
                    (4, "Энергетики"),
                    (5, "Фруктовые соки"),
                    (5, "Овощные соки"),
                    (7, "Макаронные изделия"),
                    (7, "Крупы"),
                    (7, "Масло"),
                    (8, "Мясные консервы"),
                    (8, "Рыбные консервы"),
                    (9, "Йогурты"),
                    (9, "Молоко"),
                    (9, "Сыры"),
                    (10, "Пельмени"),
                    (10, "Овощные смеси"),
                ]
                cat_id_map = {}
                for i, (parent_idx, name) in enumerate(categories_data, start=1):
                    parent = cat_id_map.get(parent_idx) if parent_idx else None
                    cursor.execute(
                        "INSERT INTO sklad_logic_categories (name, parent_id) VALUES (%s, %s) RETURNING id",
                        [name, parent],
                    )
                    cat_id_map[i] = cursor.fetchone()[0]

                # === Товары ===
                self.stdout.write("Товары...")
                products_data = [
                    ("Coca-Cola 0.5л", "COLA-05", 13, "шт"),
                    ("Coca-Cola 1л", "COLA-10", 13, "шт"),
                    ("Sprite 0.5л", "SPR-05", 14, "шт"),
                    ("Fanta 0.5л", "FAN-05", 14, "шт"),
                    ("Burn Energy 0.33л", "BURN-033", 15, "шт"),
                    ("Добрый Сок яблочный 1л", "JUS-APL-10", 16, "шт"),
                    ("Добрый Сок апельсиновый 1л", "JUS-ORN-10", 16, "шт"),
                    ("Вода «Калипсо» негаз. 1.5л", "WAT-15", 6, "шт"),
                    ("Вода «Калипсо» газ. 1.5л", "WAT-GAS-15", 6, "шт"),
                    ("Макароны «Макфа» 400г", "PASTA-400", 18, "шт"),
                    ("Макароны «Макфа» 900г", "PASTA-900", 18, "шт"),
                    ("Гречка «Национальная» 800г", "BUK-800", 19, "шт"),
                    ("Рис «Национальный» 900г", "RICE-900", 19, "шт"),
                    ("Масло подсолнечное «Золотая Семечка» 1л", "OIL-1L", 20, "шт"),
                    ("Тушёнка говяжья «Гродфуд» 325г", "MEAT-325", 21, "шт"),
                    ("Сайра тихоокеанская 250г", "FISH-250", 22, "шт"),
                    ("Йогурт «Савушкин» клубничный 125г", "YOG-125", 23, "шт"),
                    ("Йогурт «Актуаль» вишня 260г", "YOG-260", 23, "шт"),
                    ("Молоко «Брест-Литовск» 3.2% 1л", "MILK-32", 24, "шт"),
                    ("Сыр «Российский» 200г", "CHEESE-200", 25, "шт"),
                    ("Пельмени «Домашние» 500г", "PEL-500", 26, "шт"),
                    ("Смесь овощная «Мексиканская» 400г", "VEG-400", 27, "шт"),
                    ("Порошок стиральный «Tide» 2кг", "TIDE-2K", 11, "шт"),
                    ("Средство для мытья посуды «Fairy» 500мл", "FAIRY-500", 11, "шт"),
                    ("Чистящее средство «Cif» 450мл", "CIF-450", 12, "шт"),
                ]
                for name, sku, cat_idx, unit in products_data:
                    cat_id = cat_id_map.get(cat_idx)
                    cursor.execute(
                        "INSERT INTO sklad_logic_products (name, sku, category_id, unit) VALUES (%s, %s, %s, %s) ON CONFLICT (sku) DO NOTHING",
                        [name, sku, cat_id, unit],
                    )

                # === Партии и транзакции ===
                self.stdout.write("Партии и транзакции...")
                cursor.execute("SELECT id, sku FROM sklad_logic_products")
                all_products = cursor.fetchall()

                cursor.execute("SELECT id FROM sklad_logic_warehouses")
                all_warehouses = [r[0] for r in cursor.fetchall()]

                cursor.execute("SELECT id FROM sklad_logic_suppliers")
                all_suppliers = [r[0] for r in cursor.fetchall()]

                today = date.today()

                for prod_id, sku in all_products:
                    # 1-3 партии на каждый товар
                    num_batches = random.randint(1, 3)
                    for _ in range(num_batches):
                        wh_id = random.choice(all_warehouses)
                        sup_id = random.choice(all_suppliers)
                        qty = random.randint(10, 500)
                        price = round(random.uniform(0.5, 50), 2)
                        days_to_expire = random.randint(-60, 365)  # некоторые просроченные
                        exp_date = today + timedelta(days=days_to_expire)
                        days_ago = random.randint(1, 120)
                        created = today - timedelta(days=days_ago)

                        cursor.execute(
                            """
                            INSERT INTO sklad_logic_batches
                                (product_id, warehouse_id, supplier_id, quantity, purchase_price, expire_date, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """,
                            [prod_id, wh_id, sup_id, qty, price, exp_date, created],
                        )

                        cursor.execute(
                            "SELECT currval(pg_get_serial_sequence('sklad_logic_batches', 'id'))"
                        )
                        batch_id = cursor.fetchone()[0]

                        cursor.execute(
                            """
                            INSERT INTO sklad_logic_transactions
                                (batch_id, type, quantity, timestamp, user_id, comment)
                            VALUES (%s, 'IN', %s, %s, NULL, 'Начальные остатки')
                            """,
                            [batch_id, qty, created],
                        )

                        # Иногда часть партии уже списана
                        if qty > 50 and random.random() < 0.3:
                            out_qty = random.randint(5, qty // 2)
                            out_date = created + timedelta(days=random.randint(1, (today - created).days or 1))
                            cursor.execute(
                                "UPDATE sklad_logic_batches SET quantity = quantity - %s WHERE id = %s",
                                [out_qty, batch_id],
                            )
                            cursor.execute(
                                """
                                INSERT INTO sklad_logic_transactions
                                    (batch_id, type, quantity, timestamp, user_id, comment)
                                VALUES (%s, 'OUT', %s, %s, NULL, 'Тестовое списание')
                                """,
                                [batch_id, out_qty, out_date],
                            )

                # === Заказы ===
                self.stdout.write("Заказы...")
                cursor.execute("SELECT id FROM sklad_logic_products")
                all_product_ids = [r[0] for r in cursor.fetchall()]

                orders_data = [
                    ("Иван Петров", "NEW", today - timedelta(days=2), None),
                    ("ООО «Магазин №1»", "SHIPPED", today - timedelta(days=10), today - timedelta(days=8)),
                    ("ИП Сидоров", "NEW", today - timedelta(days=1), None),
                    ("ЧУП «Продукты»", "SHIPPED", today - timedelta(days=15), today - timedelta(days=12)),
                    ("Петр Иванов", "CANCELLED", today - timedelta(days=20), None),
                    ("ООО «Торговый дом»", "SHIPPED", today - timedelta(days=7), today - timedelta(days=5)),
                    ("ИП Кузнецов", "NEW", today, None),
                ]

                for customer, status, created, shipped in orders_data:
                    cursor.execute(
                        """
                        INSERT INTO sklad_logic_orders (customer_name, status, created_at, shipped_at)
                        VALUES (%s, %s, %s, %s)
                        """,
                        [customer, status, created, shipped],
                    )
                    cursor.execute(
                        "SELECT currval(pg_get_serial_sequence('sklad_logic_orders', 'id'))"
                    )
                    order_id = cursor.fetchone()[0]

                    # 1-4 позиции в заказе
                    num_items = random.randint(1, 4)
                    selected_products = random.sample(all_product_ids, min(num_items, len(all_product_ids)))
                    for prod_id in selected_products:
                        requested = random.randint(1, 50)
                        if status == "SHIPPED":
                            fulfilled = requested
                        elif status == "CANCELLED":
                            fulfilled = 0
                        else:
                            fulfilled = random.randint(0, requested)
                        cursor.execute(
                            """
                            INSERT INTO sklad_logic_orderitems
                                (order_id, product_id, quantity_requested, quantity_fullfilled)
                            VALUES (%s, %s, %s, %s)
                            """,
                            [order_id, prod_id, requested, fulfilled],
                        )

        self.stdout.write(self.style.SUCCESS("База данных заполнена тестовыми данными!"))
