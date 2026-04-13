import requests
from bs4 import BeautifulSoup
import time
import random
import re
from django.core.management.base import BaseCommand
from devices.models import Smartphone

# База AnTuTu для розрахунку логіки
ANTUTU_DB = {
                    # --- APPLE SMARTPHONES (A-Series) ---
                    'a19 pro': 2400000,'a18 pro': 1900000,'a17 pro': 1550000, 'a16 bionic': 1430000,
                    'a15 bionic': 1290000,'a18':1500000,
                    'a14 bionic': 1100000, 'a13 bionic': 850000, 'a12 bionic': 680000,
                    'a11 bionic': 520000, 'a10 fusion': 380000, 'a9': 250000, 'a8': 150000,

                    # --- APPLE TABLETS/LAPTOPS (M-Series) ---
                    'apple m5': 2800000,'apple m4': 2500000, 'apple m3': 1950000, 'apple m2': 1600000, 'apple m1': 1350000,

                    # --- APPLE WATCH (S-Series) ---
                    # Примітка: Для годинників AnTuTu не є стандартним, це приблизні еквіваленти потужності
                    'apple s9': 85000, 'apple s8': 75000, 'apple s7': 75000, 'apple s6': 70000,
                    'apple s5': 45000, 'apple s4': 45000,

                    # --- SNAPDRAGON (8-Series & Gaming) ---
                    'snapdragon 8 gen 3': 2080000, 'snapdragon 8 gen 2': 1530000,
                    'snapdragon 8+ gen 1': 1280000, 'snapdragon 8 gen 1': 1150000,
                    'snapdragon 888': 820000, 'snapdragon 870': 710000, 'snapdragon 865': 650000,
                    'snapdragon 855': 550000, 'snapdragon 845': 420000,

                    # --- SNAPDRAGON (7, 6 & 4 Series) ---
                    'snapdragon 7+ gen 3': 1450000, 'snapdragon 7+ gen 2': 1120000,
                    'snapdragon 7 gen 3': 850000, 'snapdragon 7 gen 1': 660000,
                    'snapdragon 778g': 590000, 'snapdragon 765g': 430000,
                    'snapdragon 6 gen 1': 550000, 'snapdragon 695': 440000,
                    'snapdragon 685': 340000, 'snapdragon 680': 310000,
                    'snapdragon 4 gen 2': 450000, 'snapdragon 4 gen 1': 380000,

                    # --- EXYNOS (Samsung) ---
                    'exynos 2400': 1680000, 'exynos 2200': 1140000, 'exynos 2100': 800000,
                    'exynos 1480': 720000, 'exynos 1380': 580000, 'exynos 1280': 480000,
                    'exynos 1080': 700000, 'exynos 990': 620000, 'exynos 980': 440000,
                    'exynos 850': 150000,

                    # --- DIMENSITY (MediaTek Flagship/High) ---
                    'dimensity 9300': 2050000, 'dimensity 9200': 1500000, 'dimensity 9000': 1100000,
                    'dimensity 8300': 1400000, 'dimensity 8200': 900000, 'dimensity 8100': 830000,
                    'dimensity 8020': 750000, 'dimensity 7200': 730000,

                    # --- DIMENSITY & HELIO (MediaTek Mid/Budget) ---
                    'dimensity 7050': 560000, 'dimensity 1080': 540000, 'dimensity 930': 420000,
                    'dimensity 700': 390000, 'dimensity 6080': 430000,
                    'helio g99': 415000, 'helio g96': 360000, 'helio g95': 350000,
                    'helio g88': 270000, 'helio g85': 260000, 'helio p35': 120000,

                    # --- GOOGLE TENSOR ---
                    'google tensor g3': 1100000, 'google tensor g2': 800000, 'google tensor': 720000,
                    
                    # --- UNISOC (Budget) ---
                    'unisoc t616': 280000, 'unisoc t612': 250000, 'unisoc t606': 230000
                }

class Command(BaseCommand):
    help = 'Парсинг телефонів з GSMArena'

    def safe_get(self, soup, data_spec):
        element = soup.find('td', {'data-spec': data_spec})
        return element.text.strip() if element else ""

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Запуск супер-парсера (GSMArena + Logic)...'))
        
        session = requests.Session()
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]

        urls = [
            {'brand': 'Samsung', 'url': 'https://www.gsmarena.com/samsung_galaxy_s24_ultra-12771.php'},
            {'brand': 'Samsung', 'url': 'https://www.gsmarena.com/samsung-phones-9.php'},
            # Можеш додавати інші посилання сюди
        ]

        for item in urls:
            brand = item['brand']
            headers = {'User-Agent': random.choice(user_agents)}
            
            try:
                res = session.get(item['url'], headers=headers, timeout=15)
                if res.status_code != 200:
                    self.stdout.write(self.style.ERROR(f"❌ Помилка доступу до {item['url']}"))
                    continue

                soup = BeautifulSoup(res.text, 'html.parser')
                phones_to_parse = []

                # Спершу шукаємо десктопну версію
                makers = soup.find('div', class_='makers')
                
                # Якщо не знайшли, шукаємо мобільну верстку (клас 'phone-results' або просто посилання в 'general-menu')
                if not makers:
                    makers = soup.find('div', class_='phone-results') or soup.find('div', id='general-menu')

                if makers:
                    self.stdout.write("📋 Знайдено список телефонів...")
                    for a in makers.find_all('a'):
                        # У мобільній версії назва може бути просто в тексті посилання або в strong
                        name_tag = a.find('span') or a.find('strong')
                        name = name_tag.get_text().strip() if name_tag else a.text.strip()
                        
                        if name and 'href' in a.attrs:
                            url = a['href']
                            if not url.startswith('http'):
                                url = 'https://www.gsmarena.com/' + url.lstrip('/')
                            
                            phones_to_parse.append({'name': name, 'url': url})
                else:
                    # Перевірка на один телефон (якщо це пряме посилання)
                    model_name = soup.find('h1', {'data-spec': 'modelname'})
                    if model_name:
                        phones_to_parse.append({'name': model_name.get_text().strip(), 'url': item['url']})

                # 4. Перевірка результату пошуку
                if not phones_to_parse:
                    self.stdout.write(self.style.WARNING("⚠️ Помилка: Не вдалося знайти ні список 'makers', ні назву моделі 'h1'."))
                    # Роздрукуємо шматок коду сторінки, щоб зрозуміти, що бачить скрипт
                    self.stdout.write(f"Код сторінки (перші 500 символів): {res.text[:500]}")
                    continue

                # 5. ГОЛОВНИЙ ЦИКЛ ОБРОБКИ
                for phone in phones_to_parse:
                    wait_time = random.uniform(7, 10) # Випадкова пауза від 2 до 5 секунд
                    self.stdout.write(f"⏳ Чекaю {wait_time:.1f} сек, щоб не забанили...")
                    time.sleep(wait_time)
                    
                    self.stdout.write(f"🔎 Обробка: {phone['name']}...")
                    
                    # Твій існуючий запит до сторінки телефону
                    p_res = session.get(phone['url'], headers=headers, timeout=15)
                    
                    
                    p_res = session.get(phone['url'], headers=headers, timeout=15)
                    if p_res.status_code != 200:
                        continue
                        
                    p_soup = BeautifulSoup(p_res.text, 'html.parser')

                    # 1. Назва та Процесор
                    clean_name = phone['name']
                    cpu_name = "Unknown"
                    chipset_tag = p_soup.find('td', {'data-spec': 'chipset'})
                    if chipset_tag:
                        cpu_name = chipset_tag.text.split('(')[0].split(',')[0].strip()
                    
                    if "Exynos/Snapdragon" in cpu_name or cpu_name == "Unknown":
                        cpu_tag = p_soup.find('td', {'data-spec': 'cpu'})
                        if cpu_tag:
                            cpu_name = cpu_tag.text.split(' ')[0] + " Chipset"

                    # 2. Пам'ять
                    mem_text = self.safe_get(p_soup, 'internalmemory')
                    mem_nums = re.findall(r'(\d+)\s*(?:GB|MB)', mem_text)
                    storage_gb = int(mem_nums[0]) if len(mem_nums) >= 1 else 128
                    ram_gb = int(mem_nums[1]) if len(mem_nums) >= 2 else 8

                    # 3. Камера та Батарея
                    cam_text = self.safe_get(p_soup, 'cam1modules')
                    cam_match = re.search(r'(\d+)\s*MP', cam_text)
                    main_camera_mp = int(cam_match.group(1)) if cam_match else 50

                    battery_mah = 0

                    # 1. Пріоритет: Шукаємо в спеціальному тегу (швидкий доступ)
                    batt_hl = self.safe_get(p_soup, 'batsize-hl')
                    if batt_hl:
                        batt_match = re.search(r'(\d{3,5})', batt_hl)
                        if batt_match:
                            battery_mah = int(batt_match.group(1))

                    # 2. РЕЗЕРВ: Якщо в HL порожньо, шукаємо в таблиці специфікацій (рядок Battery -> Type)
                    if battery_mah < 1000:
                        batt_row = p_soup.find('td', {'data-spec': 'batdescription'})
                        if batt_row:
                            batt_match = re.search(r'(\d{3,5})\s*mAh', batt_row.text)
                            if batt_match:
                                battery_mah = int(batt_match.group(1))

                    # 3. ГЛИБОКИЙ ПОШУК: Якщо все ще 0, шукаємо слово "mAh" по всьому тексту сторінки
                    if battery_mah < 1000:
                        page_text = p_soup.get_text()
                        # Шукаємо цифри перед mAh, наприклад "Li-Po 4500 mAh"
                        all_batt_matches = re.findall(r'(\d{3,5})\s*mAh', page_text)
                        if all_batt_matches:
                            # Беремо найбільше число (зазвичай це і є основна батарея)
                            battery_mah = int(max(all_batt_matches, key=int))

                    # 4. ФІНАЛЬНИЙ ЛОГІЧНИЙ ПЛАН "Б" (Тільки якщо реально нічого не знайшли)
                    if battery_mah < 1000:
                        if brand == "Apple":
                            # Для iPhone ставимо реалістичніші середні значення, якщо парсинг впав
                            if release_year >= 2023: battery_mah = 4422 # 15 Pro Max style
                            elif release_year >= 2021: battery_mah = 3200
                            else: battery_mah = 2800
                        else:
                            battery_mah = 5000 if release_year >= 2022 else 4000

                    # 4. Рік та Екран
                    year_text = self.safe_get(p_soup, 'year-hl')

                    # 2. Якщо порожньо, шукаємо в полі "Status" (там пише Released 2023, September)
                    if not year_text:
                        year_text = self.safe_get(p_soup, 'status-hl')

                    # 3. Якщо і там немає, шукаємо в офіційній таблиці анонсів
                    if not year_text:
                        year_text = self.safe_get(p_soup, 'announced-hl')

                    # Витягуємо саме 4 цифри року за допомогою регулярного виразу
                    year_match = re.search(r'\d{4}', year_text)

                    if year_match:
                        release_year = int(year_match.group(0))
                    else:
                        # Останній шанс: шукаємо будь-які 4 цифри в тексті всієї сторінки, 
                        # які схожі на рік (від 2010 до 2026)
                        page_text = p_soup.get_text()
                        years_found = re.findall(r'20[12]\d', page_text)
                        release_year = int(years_found[0]) if years_found else 2024

                    display_info = self.safe_get(p_soup, 'displaytype')
                    hz_match = re.search(r'(\d+)\s*Hz', display_info)
                    screen_hz = int(hz_match.group(1)) if hz_match else 60

                    # 5. Antutu
                    antutu_score = 0
                    cpu_lower = cpu_name.lower()

                    # Шукаємо в нашій базі ANTUTU_DB
                    for cpu_key, score in ANTUTU_DB.items():
                        if cpu_key in cpu_lower:
                            antutu_score = score
                            break

                    # Якщо в базі не знайшли, пробуємо витягнути з самої сторінки (якщо там є блок тестів)
                    if antutu_score == 0:
                        perf_td = p_soup.find('td', {'data-spec': 'tbench'})
                        if perf_td and 'AnTuTu' in perf_td.text:
                            at_match = re.search(r'AnTuTu:\s*(\d+)', perf_td.text)
                            if at_match:
                                antutu_score = int(at_match.group(1))

                    # План "В" - якщо всюди порожньо (дуже рідкісні чипи)
                    if antutu_score == 0:
                        antutu_score = (release_year - 2018) * 110000 + random.randint(30000, 100000)

                    # 6. Фото
                    image_url = ""

                    # 1. Шукаємо в основному контейнері
                    img_div = p_soup.find('div', class_='specs-photo-main')
                    if img_div:
                        img_tag = img_div.find('img')
                        if img_tag:
                            # Перевіряємо src або data-src (якщо фото завантажується пізніше)
                            image_url = img_tag.get('src') or img_tag.get('data-src')

                    # 2. РЕЗЕРВ: Шукаємо посилання в мета-тегах (воно там майже завжди є для соцмереж)
                    if not image_url:
                        og_image = p_soup.find('meta', property='og:image')
                        if og_image:
                            image_url = og_image.get('content')

                    # 3. ВИПРАВЛЕННЯ ПОСИЛАННЯ (якщо воно неповне)
                    if image_url and not image_url.startswith('http'):
                        if image_url.startswith('//'):
                            image_url = 'https:' + image_url
                        else:
                            image_url = 'https://www.gsmarena.com/' + image_url.lstrip('/')

                    charge_score = 0
                    # Шукаємо в тій же таблиці, де батарея, або через загальний пошук тексту
                    charging_text = self.safe_get(p_soup, 'charging-hl') # Спроба №1: швидкий доступ
                    
                    if not charging_text:
                        # Спроба №2: Шукаємо в таблиці специфікацій
                        charging_row = p_soup.find('td', {'data-spec': 'charging'})
                        if charging_row:
                            charging_text = charging_row.get_text()

                    if charging_text:
                        # Шукаємо число перед 'W' (наприклад, 45W, 120W)
                        watt_match = re.search(r'(\d+)\s*W', charging_text)
                        if watt_match:
                            charging_text = int(watt_match.group(1))
                    
                    # Якщо нічого не знайшли, ставимо стандарт (наприклад, 25 для Samsung, якщо не вказано)
                    if charge_score == 0:
                        if brand == 'Apple': charge_score = 20
                        elif brand == 'Samsung': charge_score = 25
                        else: charging_watts = 18
                    
                    self.stdout.write(f"⚡️ Зарядка: {charge_score}W")

                    # Збереження
                    Smartphone.objects.update_or_create(
                        name=clean_name,
                        defaults={
                            'brand': brand,
                            'release_year': release_year,
                            'cpu_name': cpu_name,
                            'storage_gb': storage_gb,
                            'ram_gb': ram_gb,
                            'main_camera_mp': main_camera_mp,
                            'battery_mah': battery_mah,
                            'screen_hz': screen_hz,
                            'antutu_score': antutu_score,
                            'image_url': image_url,
                            'charge_score': charge_score,
                            
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f" ✅ {clean_name} збережено!"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f" ❌ Помилка: {e}"))

        self.stdout.write(self.style.SUCCESS('🏁 ГОТОВО!'))