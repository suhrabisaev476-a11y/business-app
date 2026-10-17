import json
import os
import csv
from datetime import datetime

FILENAME = "products.json"
SALES_FILE = "sales.json"
DATE_FILE = "last_date.txt"

# --- СТАРТОВЫЙ ЭКРАН ---
def show_start_screen():
    print("\n" * 2)
    print("╔" + "═" * 48 + "╗")
    print("║" + " " * 12 + "БИЗНЕС ПРИЛОЖЕНИЕ" + " " * 15 + "║")
    print("║" + " " * 10 + "Версия 4.0 (Категории+)" + " " * 11 + "║")
    print("╚" + "═" * 48 + "╝")
    print("\nДобро пожаловать! Программа готова к работе.\n")

# --- ЗАГРУЗКА И СОХРАНЕНИЕ ---
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- АВТОМАТИЧЕСКИЙ СБРОС ОТЧЕТА ---
def auto_reset_report():
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(DATE_FILE):
        with open(DATE_FILE, "r") as f:
            last_date = f.read().strip()
        if last_date != today:
            save_data([], SALES_FILE)
            with open(DATE_FILE, "w") as f:
                f.write(today)
            print("📅 Наступил новый день! Отчет за прошлый день сброшен автоматически.")
    else:
        with open(DATE_FILE, "w") as f:
            f.write(today)

# --- ФУНКЦИИ МАГАЗИНА ---
def add_product(products):
    name = input("Введите название товара: ")
    category = input("Введите категорию (например, Еда, Техника, Одежда): ")
    try:
        price = float(input("Введите цену: "))
        quantity = int(input("Введите количество: "))
    except ValueError:
        print("❌ Ошибка: цена и количество должны быть числами!")
        return
    product = {"name": name, "category": category, "price": price, "quantity": quantity}
    products.append(product)
    save_data(products, FILENAME)
    print(f"✅ Товар '{name}' (Категория: {category}) успешно добавлен!")

def show_products(products):
    if not products:
        print("📭 Склад пуст.")
        return
    low_stock = [p for p in products if p["quantity"] < 5]
    if low_stock:
        print("\n⚠️  ВНИМАНИЕ! ТОВАРЫ С НИЗКИМ ОСТАТКОМ (меньше 5 шт):")
        for p in low_stock:
            print(f"   - {p['name']}: осталось {p['quantity']} шт.")
        print("   Пора сделать заказ поставщику!\n")

    print("\n" + "=" * 85)
    print(f"{'НАЗВАНИЕ':<18} | {'КАТЕГОРИЯ':<12} | {'ЦЕНА':<10} | {'КОЛ-ВО':<8} | {'СУММА':<10}")
    print("-" * 85)
    for p in products:
        total = p["price"] * p["quantity"]
        cat = p.get("category", "Без кат.")
        print(f"{p['name']:<18} | {cat:<12} | {p['price']:<10.2f} | {p['quantity']:<8} | {total:<10.2f}")
    print("=" * 85 + "\n")

# --- НОВАЯ ФУНКЦИЯ: ПОИСК ПО КАТЕГОРИЯМ ---
def search_by_category(products):
    if not products:
        print("📭 Склад пуст.")
        return
    
    # Собираем уникальные категории и считаем количество товаров в каждой
    categories = {}
    for p in products:
        cat = p.get("category", "Без кат.")
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    # Показываем список категорий
    print("\n=== ДОСТУПНЫЕ КАТЕГОРИИ ===")
    cat_list = list(categories.keys())
    for i, cat in enumerate(cat_list, 1):
        print(f"{i}. {cat} (товаров: {categories[cat]})")
    
    try:
        choice = int(input("Выберите номер категории: "))
        if choice < 1 or choice > len(cat_list):
            print("❌ Неверный номер.")
            return
        
        selected_cat = cat_list[choice - 1]
        
        # Фильтруем товары по категории
        filtered = [p for p in products if p.get("category", "Без кат.") == selected_cat]
        
        if not filtered:
            print(f"📭 В категории '{selected_cat}' нет товаров.")
            return
        
        print(f"\n--- Товары в категории '{selected_cat}' ({len(filtered)} шт.) ---")
        print(f"{'№':<4} | {'НАЗВАНИЕ':<20} | {'ЦЕНА':<10} | {'КОЛ-ВО':<8} | {'СУММА':<10}")
        print("-" * 75)
        for i, p in enumerate(filtered, 1):
            total = p["price"] * p["quantity"]
            print(f"{i:<4} | {p['name']:<20} | {p['price']:<10.2f} | {p['quantity']:<8} | {total:<10.2f}")
        print("-" * 75)
        
        # Предлагаем найти конкретный товар внутри категории
        search_query = input("\nХотите найти конкретный товар в этой категории? (Enter - пропустить): ").strip().lower()
        if search_query:
            # Ищем внутри уже отфильтрованного списка
            found = [p for p in filtered if search_query in p["name"].lower()]
            if found:
                print(f"\n🔍 Найдено {len(found)} товаров:")
                for p in found:
                    print(f"   {p['name']} | Цена: {p['price']:.2f} | В наличии: {p['quantity']}")
            else:
                print("🔍 Ничего не найдено.")
    
    except ValueError:
        print("❌ Ошибка: введите число.")

def search_product(products):
    query = input("Введите название или категорию для поиска: ").lower()
    found = [p for p in products if query in p["name"].lower() or query in p.get("category", "").lower()]
    if not found:
        print("🔍 Товар не найден.")
        return
    print("\n--- Результаты поиска ---")
    for p in found:
        print(f"{p['name']} | Категория: {p.get('category', 'Без кат.')} | Цена: {p['price']:.2f} | В наличии: {p['quantity']}")
    print("-------------------------\n")

def edit_product(products):
    name = input("Введите название товара для редактирования: ").lower()
    for p in products:
        if p["name"].lower() == name:
            print(f"Текущая цена: {p['price']:.2f}, Текущее количество: {p['quantity']}")
            try:
                new_price = float(input("Введите новую цену (или 0, чтобы оставить старую): "))
                if new_price > 0:
                    p["price"] = new_price
                new_quantity = int(input("Введите новое количество (или -1, чтобы оставить старое): "))
                if new_quantity >= 0:
                    p["quantity"] = new_quantity
                save_data(products, FILENAME)
                print("✅ Товар успешно отредактирован!")
                return
            except ValueError:
                print("❌ Ошибка: введите числа!")
                return
    print("❌ Товар не найден.")

def delete_product(products):
    name = input("Введите название товара для удаления: ").lower()
    for i, p in enumerate(products):
        if p["name"].lower() == name:
            deleted = products.pop(i)
            save_data(products, FILENAME)
            print(f"🗑️ Товар '{deleted['name']}' удален со склада.")
            return
    print("❌ Товар не найден.")

def sell_product(products):
    name = input("Введите название товара для продажи: ").lower()
    for p in products:
        if p["name"].lower() == name:
            try:
                amount = int(input(f"Сколько продаем? (в наличии {p['quantity']}): "))
                if amount > p["quantity"]:
                    print("❌ Недостаточно товара на складе!")
                    return
                p["quantity"] -= amount
                save_data(products, FILENAME)
                sales = load_data(SALES_FILE)
                sales.append({
                    "name": p["name"], 
                    "category": p.get("category", "Без кат."),
                    "amount": amount, 
                    "total": p["price"] * amount
                })
                save_data(sales, SALES_FILE)
                print(f"💰 Продажа успешна! Выручка: {p['price'] * amount:.2f}")
                return
            except ValueError:
                print("❌ Ошибка: введите число!")
                return
    print("❌ Товар не найден.")

def daily_report():
    sales = load_data(SALES_FILE)
    if not sales:
        print("📊 Сегодня продаж еще не было.")
        return
    total_revenue = sum(s["total"] for s in sales)
    print("\n" + "=" * 65)
    print("📊 ОТЧЕТ О ПРОДАЖАХ ЗА СЕГОДНЯ")
    print("=" * 65)
    for s in sales:
        cat = s.get("category", "Без кат.")
        print(f"Продано: {s['name']:<15} | Кат: {cat:<10} | Кол-во: {s['amount']:<5} | Сумма: {s['total']:.2f}")
    print("-" * 65)
    print(f"💰 ОБЩАЯ ВЫРУЧКА: {total_revenue:.2f}")
    print("=" * 65 + "\n")

# --- ЭКСПОРТ В CSV ---
def export_to_csv():
    sales = load_data(SALES_FILE)
    if not sales:
        print("📊 Нет данных для экспорта. Сначала сделайте продажи.")
        return
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"report_{date_str}.csv"
    try:
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(["Товар", "Категория", "Количество", "Сумма"])
            for s in sales:
                writer.writerow([s["name"], s.get("category", "Без кат."), s["amount"], f"{s['total']:.2f}"])
        print(f"✅ Отчет сохранен в файл: {filename}")
    except Exception as e:
        print(f"❌ Ошибка при экспорте: {e}")

def manual_reset():
    confirm = input("⚠️ Вы уверены, что хотите сбросить отчет за день? (да/нет): ").lower()
    if confirm == "да":
        save_data([], SALES_FILE)
        print("✅ Отчет за день успешно сброшен.")
    else:
        print("❌ Сброс отменен.")

# --- ГЛАВНОЕ МЕНЮ ---
def main():
    auto_reset_report()
    show_start_screen()
    products = load_data(FILENAME)
    while True:
        print("\n=== БИЗНЕС ПРИЛОЖЕНИЕ v4.0 ===")
        print("1. Добавить товар")
        print("2. Показать все товары")
        print("3. Найти товар (по названию/категории)")
        print("4. Показать по категориям (с фильтром)") # НОВЫЙ ПУНКТ
        print("5. Продать товар")
        print("6. Редактировать товар")
        print("7. Удалить товар")
        print("8. Отчет за день")
        print("9. Экспорт отчета в CSV (Excel)")
        print("10. Сбросить отчет вручную")
        print("11. Выход")
        
        choice = input("Выберите действие: ")
        
        if choice == "1":
            add_product(products)
        elif choice == "2":
            show_products(products)
        elif choice == "3":
            search_product(products)
        elif choice == "4":
            search_by_category(products)  # Вызов новой функции
        elif choice == "5":
            sell_product(products)
        elif choice == "6":
            edit_product(products)
        elif choice == "7":
            delete_product(products)
        elif choice == "8":
            daily_report()
        elif choice == "9":
            export_to_csv()
        elif choice == "10":
            manual_reset()
        elif choice == "11":
            print("До свидания! Хорошего дня!")
            break
        else:
            print("❌ Неверный выбор, попробуйте снова.")

if __name__ == "__main__":
    main()
