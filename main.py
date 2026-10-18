import sqlite3
import json
import os
import csv
from datetime import datetime

DB_FILE = "shop.db"
SALES_FILE = "sales.json" # Продажи пока оставим в JSON, чтобы не усложнять
DATE_FILE = "last_date.txt"

# --- ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Создаем таблицу товаров, если ее нет
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            quantity INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# --- СТАРТОВЫЙ ЭКРАН ---
def show_start_screen():
    print("\n" * 2)
    print("╔" + "═" * 48 + "╗")
    print("║" + " " * 12 + "БИЗНЕС ПРИЛОЖЕНИЕ" + " " * 15 + "║")
    print("║" + " " * 10 + "Версия 5.0 (SQLite)" + " " * 13 + "║")
    print("╚" + "═" * 48 + "╝")
    print("\nДобро пожаловать! База данных готова к работе.\n")

# --- АВТОМАТИЧЕСКИЙ СБРОС ОТЧЕТА ---
def auto_reset_report():
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(DATE_FILE):
        with open(DATE_FILE, "r") as f:
            last_date = f.read().strip()
        if last_date != today:
            with open(SALES_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
            with open(DATE_FILE, "w") as f:
                f.write(today)
            print("📅 Наступил новый день! Отчет за прошлый день сброшен.")
    else:
        with open(DATE_FILE, "w") as f:
            f.write(today)

# --- ФУНКЦИИ МАГАЗИНА ---
def add_product():
    name = input("Введите название товара: ")
    category = input("Введите категорию: ")
    try:
        price = float(input("Ведите цену: "))
        quantity = int(input("Введите количество: "))
    except ValueError:
        print("❌ Ошибка: цена и количество должны быть числами!")
        return
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, category, price, quantity) VALUES (?, ?, ?, ?)", 
                   (name, category, price, quantity))
    conn.commit()
    conn.close()
    print(f"✅ Товар '{name}' успешно добавлен в базу!")

def show_products():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, price, quantity FROM products")
    products = cursor.fetchall()
    conn.close()

    if not products:
        print("📭 Склад пуст.")
        return

    # Проверка на низкий остаток
    low_stock = [p for p in products if p[4] < 5]
    if low_stock:
        print("\n⚠  ВНИМАНИЕ! ТОВАРЫ С НИЗКИМ ОСТАТКОМ:")
        for p in low_stock:
            print(f"   - {p[1]}: осталось {p[4]} шт.")
        print("   Пора сделать заказ поставщику!\n")

    print("\n" + "=" * 95)
    print(f"{'ID':<4} | {'НАЗВАНИЕ':<18} | {'КАТЕГОРИЯ':<12} | {'ЦЕНА':<10} | {'КОЛ-ВО':<8} | {'СУММА':<10}")
    print("-" * 95)
    for p in products:
        total = p[3] * p[4]
        cat = p[2] if p[2] else "Без кат."
        print(f"{p[0]:<4} | {p[1]:<18} | {cat:<12} | {p[3]:<10.2f} | {p[4]:<8} | {total:<10.2f}")
    print("=" * 95 + "\n")

def search_product():
    query = input("Введите название или категорию для поиска: ").lower()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Используем LIKE для поиска частичного совпадения
    cursor.execute("SELECT id, name, category, price, quantity FROM products WHERE LOWER(name) LIKE ? OR LOWER(category) LIKE ?", 
                   (f'%{query}%', f'%{query}%'))
    results = cursor.fetchall()
    conn.close()

    if not results:
        print("🔍 Товар не найден.")
        return
    
    print("\n--- Результаты поиска ---")
    for p in results:
        cat = p[2] if p[2] else "Без кат."
        print(f"ID: {p[0]} | {p[1]} | Категория: {cat} | Цена: {p[3]:.2f} | В наличии: {p[4]}")
    print("-------------------------\n")
def edit_product():
    try:
        prod_id = int(input("Введите ID товара для редактирования: "))
    except ValueError:
        print("❌ Ошибка: ID должен быть числом.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT price, quantity FROM products WHERE id = ?", (prod_id,))
    product = cursor.fetchone()

    if not product:
        print("❌ Товар с таким ID не найден.")
        conn.close()
        return

    print(f"Текущая цена: {product[0]:.2f}, Текущее количество: {product[1]}")
    try:
        new_price = float(input("Введите новую цену (или 0, чтобы оставить старую): "))
        new_quantity = int(input("Введите новое количество (или -1, чтобы оставить старое): "))
        
        # Обновляем только то, что нужно
        if new_price > 0:
            cursor.execute("UPDATE products SET price = ? WHERE id = ?", (new_price, prod_id))
        if new_quantity >= 0:
            cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, prod_id))
            
        conn.commit()
        print("✅ Товар успешно отредактирован!")
    except ValueError:
        print("❌ Ошибка: введите числа!")
    finally:
        conn.close()

def delete_product():
    try:
        prod_id = int(input("Введите ID товара для удаления: "))
    except ValueError:
        print("❌ Ошибка: ID должен быть числом.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (prod_id,))
    conn.commit()
    
    if cursor.rowcount > 0:
        print(f"🗑 Товар с ID {prod_id} удален.")
    else:
        print("❌ Товар с таким ID не найден.")
    conn.close()

def sell_product():
    try:
        prod_id = int(input("Введите ID товара для продажи: "))
    except ValueError:
        print("❌ Ошибка: ID должен быть числом.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, category, price, quantity FROM products WHERE id = ?", (prod_id,))
    product = cursor.fetchone()

    if not product:
        print("❌ Товар не найден.")
        conn.close()
        return

    name, category, price, current_qty = product
    
    try:
        amount = int(input(f"Сколько продаем? (в наличии {current_qty}): "))
        if amount > current_qty:
            print("❌ Недостаточно товара на складе!")
            conn.close()
            return
        
        # Обновляем остаток в базе
        cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (amount, prod_id))
        conn.commit()
        conn.close()

        # Записываем продажу в JSON
        with open(SALES_FILE, "r", encoding="utf-8") as f:
            sales = json.load(f)
        
        sales.append({
            "name": name, 
            "category": category if category else "Без кат.",
            "amount": amount, 
            "total": price * amount
        })
        
        with open(SALES_FILE, "w", encoding="utf-8") as f:
            json.dump(sales, f, ensure_ascii=False, indent=4)
            
        print(f"💰 Продажа успешна! Выручка: {price * amount:.2f}")
        
    except ValueError:
        print("❌ Ошибка: введите число!")
        conn.close()

def daily_report():
    with open(SALES_FILE, "r", encoding="utf-8") as f:
        sales = json.load(f)
        
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
    with open(SALES_FILE, "r", encoding="utf-8") as f:
        sales = json.load(f)
        
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
    confirm = input("⚠ Вы уверены, что хотите сбросить отчет за день? (да/нет): ").lower()
    if confirm == "да":
        with open(SALES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        print("✅ Отчет за день успешно сброшен.")
    else:
        print("❌ Сброс отменен.")

# --- ГЛАВНОЕ МЕНЮ ---
def main():
    init_db() # Создаем базу при запуске
    auto_reset_report()
    show_start_screen()
    
    while True:
        print("\n=== БИЗНЕС ПРИЛОЖЕНИЕ v5.0 (SQLite) ===")
        print("1. Добавить товар")
        print("2. Показать все товары")
        print("3. Найти товар")
        print("4. Продать товар (по ID)")
        print("5. Редактировать товар (по ID)")
        print("6. Удалить товар (по ID)")
        print("7. Отчет за день")
        print("8. Экспорт отчета в CSV (Excel)")
        print("9. Сбросить отчет вручную")
        print("10. Выход")
        
        choice = input("Выберите действие: ")
        
        if choice == "1":
            add_product()
        elif choice == "2":
            show_products()
        elif choice == "3":
            search_product()
        elif choice == "4":
            sell_product()
        elif choice == "5":
            edit_product()
        elif choice == "6":
            delete_product()
        elif choice == "7":
            daily_report()
        elif choice == "8":
            export_to_csv()
        elif choice == "9":
            manual_reset()
        elif choice == "10":
            print("До свидания! Хорошего дня!")
            break
        else:
            print("❌ Неверный выбор, попробуйте снова.")

if __name__ == "__main__":
    main()
