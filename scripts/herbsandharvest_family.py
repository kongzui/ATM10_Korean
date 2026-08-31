#!/usr/bin/env python3
"""Mama's Herbs and Harvest의 언어와 자체 가이드를 번역하고 검증해요."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root

FAMILY = "herbsandharvest"
MOD_ID = "herbsandharvest"
JAR_PATTERN = "herbsandharvest-*.jar"
EXPECTED_KEYS = 865
WORK_ROOT = PROJECT_ROOT / "working" / FAMILY
OUTPUT_ROOT = active_output_root() / "resourcepack/ATM10_Korean/assets/herbsandharvest"
LANG_OUTPUT = OUTPUT_ROOT / "lang/ko_kr.json"
BOOK_PREFIX = "assets/herbsandharvest/books/"
VISIBLE_BOOK_FIELD = re.compile(
    r'("(?:summary|literal_text)"\s*:\s*)("(?:\\.|[^"\\])*")'
)
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[a-zA-Z]|\{\d+\}")
FORMAT_CODE = re.compile(r"[§&][0-9A-FK-ORa-fk-or]")
NUMBER = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?")
URL = re.compile(r"https?://[^\s\"']+")
VISIBLE_DATA_KEYS = {
    "custom_name",
    "minecraft:custom_name",
    "minecraft:item_name",
    "item_name",
    "title",
    "description",
    "literal_text",
}

NAMES = {
    "Acacia": "아카시아나무",
    "Apple": "사과",
    "Asparagus": "아스파라거스",
    "Avocado": "아보카도",
    "Bacon": "베이컨",
    "Bagel": "베이글",
    "Barley": "보리",
    "Basil": "바질",
    "Bay Leaf": "월계수 잎",
    "Beef": "소고기",
    "Black Forest": "블랙 포레스트",
    "Blackberry": "블랙베리",
    "Blueberry": "블루베리",
    "Bread": "빵",
    "Broccoli": "브로콜리",
    "Butter": "버터",
    "Cabbage": "양배추",
    "Camel": "낙타",
    "Caravane": "카라반",
    "Carrot": "당근",
    "Cauliflower": "콜리플라워",
    "Celery": "셀러리",
    "Cheddar": "체더 치즈",
    "Cheese": "치즈",
    "Cherry": "체리",
    "Cherries": "체리",
    "Chicken": "닭고기",
    "Chive": "차이브",
    "Chives": "차이브",
    "Chocolate": "초콜릿",
    "Cilantro": "고수",
    "Cinnamon": "시나몬",
    "Corn": "옥수수",
    "Cream": "크림",
    "Cow": "소",
    "Cucumber": "오이",
    "Dill": "딜",
    "Egg": "달걀",
    "Eggplant": "가지",
    "Eggs": "달걀",
    "Feta": "페타 치즈",
    "Garlic": "마늘",
    "Ginger": "생강",
    "Goat": "염소",
    "Gouda": "고다 치즈",
    "Grape": "포도",
    "Grapes": "포도",
    "Grape Vine": "포도 덩굴",
    "Green Bean": "그린빈",
    "Green Beans": "그린빈",
    "Green Pepper": "피망",
    "Ham": "햄",
    "Lamb": "양고기",
    "Lemon": "레몬",
    "Lemongrass": "레몬그라스",
    "Lettuce": "상추",
    "Lime": "라임",
    "Meatloaf": "미트로프",
    "Milk": "우유",
    "Mint": "민트",
    "Mutton": "양고기",
    "Mustard": "겨자",
    "Oat": "귀리",
    "Oats": "귀리",
    "Onion": "양파",
    "Orange": "오렌지",
    "Oregano": "오레가노",
    "Parmesan": "파르메산 치즈",
    "Parsley": "파슬리",
    "Pea": "완두콩",
    "Peach": "복숭아",
    "Peanut": "땅콩",
    "Peanuts": "땅콩",
    "Pear": "배",
    "Peas": "완두콩",
    "Peppercorn": "통후추",
    "Peppercorns": "통후추",
    "Pineapple": "파인애플",
    "Pinto Beans": "핀토콩",
    "Plum": "자두",
    "Pork": "돼지고기",
    "Pork Chop": "돼지갈비",
    "Potato": "감자",
    "Pumpkin": "호박",
    "Pumpernickel": "펌퍼니켈 빵",
    "Radish": "무",
    "Raspberry": "라즈베리",
    "Rice": "쌀",
    "Ricotta": "리코타 치즈",
    "Rosemary": "로즈메리",
    "Rye": "호밀",
    "Sage": "세이지",
    "Salmon": "연어",
    "Salt": "소금",
    "Sausage": "소시지",
    "Sausages": "소시지",
    "Sheep": "양",
    "Squash": "호박",
    "Strawberry": "딸기",
    "Sugar": "설탕",
    "Sweet Berry": "달콤한 열매",
    "SweetBerry": "달콤한 열매",
    "Sweet Potato": "고구마",
    "Swiss": "스위스 치즈",
    "Thistle": "엉겅퀴",
    "Thyme": "타임",
    "Tomato": "토마토",
    "Tomatoes": "토마토",
    "Turmeric": "강황",
    "Turnip": "순무",
    "Vegetable": "채소",
    "Wheat": "밀",
    "Zucchini": "주키니",
}

EXACT_NAMES = {
    "Herbs & Harvest": "Herbs & Harvest",
    "Herbs & Harvest: Pantry": "Herbs & Harvest: 팬트리",
    "Jar": "보관 병",
    "Spice Jar": "향신료 병",
    "Ingredient Jar": "재료 보관 병",
    "Produce Basket": "농산물 바구니",
    "Butter Churn": "버터 교반기",
    "Cake Stand": "케이크 스탠드",
    "Cupcake Stand": "페이스트리 스탠드",
    "Charcuterie Board": "샤퀴테리 보드",
    "Cheesemaking Cauldron": "치즈 제조 가마솥",
    "Cheese Aging Shelf": "치즈 숙성 선반",
    "Empty Pot": "빈 수프 냄비",
    "Empty Baking Pan": "빈 베이킹 팬",
    "Salt Basin": "염전",
    "Glass Cup": "유리컵",
    "Glass Pitcher": "유리 피처",
    "Dinner Plate": "식사용 접시",
    "Delftware Dinner Plate": "델프트웨어 식사용 접시",
    "Holiday Dinner Plate": "축제용 식사용 접시",
    "Wood Board": "나무 보드",
    "Oil": "기름",
    "Rennet": "레닛",
    "Chèvre": "셰브르 치즈",
    "Chèvre Wedge": "셰브르 치즈 조각",
    "Caravane Wedge": "카라반 치즈 조각",
    "Feta Wedge": "페타 치즈 조각",
    "The Homesteader's Handbook": "자급자족 생활 안내서",
    "Pumpernickel Bread": "펌퍼니켈 빵",
    "Pumpernickel Bread Slice": "펌퍼니켈 빵 조각",
    "Monte Cristo Sandwich": "몬테크리스토 샌드위치",
    "Snickerdoodle": "스니커두들",
    "Burrito": "부리토",
    "Taco": "타코",
    "Guacamole": "과카몰리",
    "Guacamole with Chips": "칩을 곁들인 과카몰리",
    "Graham Crackers": "그레이엄 크래커",
    "Biscuits and Gravy": "비스킷과 그레이비",
    "Caesar Salad": "시저 샐러드",
    "Chef Salad": "셰프 샐러드",
    "Garden Salad": "가든 샐러드",
    "Chicken Berry Salad": "닭고기와 달콤한 열매 샐러드",
    "Avocado Toast with Tomatoes and Feta": "토마토와 페타 치즈를 곁들인 아보카도 토스트",
    "Bagel with Cream Cheese": "크림치즈 베이글",
    "Bagel with Salmon": "연어 베이글",
    "Beef and Cheddar Sandwich": "소고기 체더 치즈 샌드위치",
    "Ham and Swiss Sandwich": "햄과 스위스 치즈 샌드위치",
    "Grilled Cheese Sandwich": "구운 치즈 샌드위치",
    "Peanut Butter and Jelly Sandwich": "땅콩버터와 잼 샌드위치",
    "Garlic Chicken with Lemon": "레몬 마늘 닭고기",
    "Slices and Broccoli": "조각과 브로콜리",
    "Eggplant Parmesan with": "가지 파르메산과",
    "Caprese Salad": "카프레제 샐러드",
    "Lamb Chops with Mint": "민트 소스를 곁들인 양갈비와",
    "Sauce and Potatoes": "감자",
    "Lasagna with Caesar Salad": "시저 샐러드를 곁들인 라자냐",
    "Meatloaf with Mashed Potatoes": "으깬 감자를 곁들인 미트로프와",
    "and Green Beans": "그린빈",
    "Pork Chops with Apples": "사과를 곁들인 돼지갈비와",
    "and Cornbread Stuffing": "옥수수빵 스터핑",
    "Pot Roast with Potatoes,": "감자와",
    "Carrots, and Celery": "당근, 셀러리를 곁들인 냄비 구이",
    "Salmon Steaks with": "연어 스테이크와",
    "Asparagus and Lemon Slices": "아스파라거스, 레몬 조각",
    "Beef Wellington with Mashed": "으깬 감자와",
    "Potatoes and Vegetable Medley": "채소 모둠을 곁들인 비프 웰링턴",
    "Amount: %s": "수량: %s",
    "Contains: ": "내용물: ",
    "Can be placed": "놓을 수 있습니다",
    "Can be potted": "화분에 심을 수 있습니다",
    "Liquid Pouring": "액체 따르는 소리",
    "Cauldron is not empty. Please empty before making dairy products.": (
        "가마솥이 비어 있지 않습니다. 유제품을 만들기 전에 비워 주세요."
    ),
    "The soup pot must be heated to enjoy the soup!": (
        "수프를 먹으려면 수프 냄비를 데워야 합니다!"
    ),
    "Corn Kernels": "옥수수알",
    "Garlic Clove": "마늘 한 쪽",
    "Garlic Bulb": "마늘 한 통",
    "Ginger Root": "생강 뿌리",
    "Turmeric Root": "강황 뿌리",
    "Fruit Tree Leaves": "과일나무 잎",
    "Bay Leaves": "월계수 잎",
    "Chopped Bay Leaves": "다진 월계수 잎",
    "Chopped Herbs": "다진 허브",
    "Example: Chopped Parsley": "예: 다진 파슬리",
    "Apple Cinnamon Muffin": "사과 시나몬 머핀",
    "Avocado Toast with Feta and Tomatoes": "페타 치즈와 토마토를 곁들인 아보카도 토스트",
    "Bagel and Cream Cheese": "크림치즈 베이글",
    "Bagel and Cream Cheese with Salmon": "연어 크림치즈 베이글",
    "Beef and Cheddar": "소고기와 체더 치즈",
    "Beef Pot Pie": "소고기 포트 파이",
    "Black Forest CupcakeCake": "블랙 포레스트 컵케이크",
    "Bowl of Broccoli & Cheddar Soup": "브로콜리 체더 치즈 수프 한 그릇",
    "Broccoli and Cheddar Soup": "브로콜리 체더 치즈 수프",
    "Broccoli Cheddar Soup": "브로콜리 체더 치즈 수프",
    "Camel Milk": "낙타 우유",
    "CarrotCupcake": "당근 컵케이크",
    "Cheesecake": "치즈케이크",
    "Cheeses": "치즈",
    "Chevre": "셰브르 치즈",
    "Chicken Cutlet": "닭고기 커틀릿",
    "Chicken  and Dumplings": "닭고기와 덤플링",
    "Chicken Dumplings": "닭고기 덤플링",
    "Chicken Noodle Soup": "닭고기 국수 수프",
    "Chicken and Rice Soup": "닭고기 쌀 수프",
    "Chicken Pot Pie": "닭고기 포트 파이",
    "Chicken, Apple, and SweetBerry Salad": "닭고기, 사과와 달콤한 열매 샐러드",
    "Chips": "칩",
    "Chips and Guacamole": "칩과 과카몰리",
    "Cinnamon Roll": "시나몬 롤",
    "Corn Chowder": "옥수수 차우더",
    "Cornbread Stuffing": "옥수수빵 스터핑",
    "Cream Bucket": "크림 양동이",
    "Cream Cheese": "크림치즈",
    "Eggplant Parmesan": "가지 파르메산",
    "Garlic Lemon Chicken with Broccoli": "브로콜리를 곁들인 레몬 마늘 닭고기",
    "Goat Milk": "염소 우유",
    "Graham Cracker": "그레이엄 크래커",
    "Grilled Cheese on Rye": "호밀빵 구운 치즈 샌드위치",
    "Ham and Swiss": "햄과 스위스 치즈",
    "Ketchup": "케첩",
    "Key Lime Pie": "키 라임 파이",
    "Lamb Chops": "양갈비",
    "Lamb Shanks with Mint Sauce and Potatoes": "민트 소스와 감자를 곁들인 양고기 사태",
    "Lamb Pot Pie": "양고기 포트 파이",
    "Lamb Pot Pie Pie": "양고기 포트 파이",
    "Lasagna": "라자냐",
    "Lemon Meringue Pie": "레몬 머랭 파이",
    "Mashed Potatoes": "으깬 감자",
    "Mayonnaise": "마요네즈",
    "Meatloaf with Mashed Potatoes and Green Beans": "으깬 감자와 그린빈을 곁들인 미트로프",
    "Monte Cristo": "몬테크리스토 샌드위치",
    "Oatmeal": "오트밀",
    "Oatmeal Raisin Cookie": "오트밀 건포도 쿠키",
    "Pancakes": "팬케이크",
    "Peanut Butter": "땅콩버터",
    "Peanut Butter and Jelly": "땅콩버터와 잼",
    "Peanut Butter Cookie": "땅콩버터 쿠키",
    "Pepperoni": "페퍼로니",
    "Pineapple Upside Down Cake": "파인애플 업사이드다운 케이크",
    "Plain Dinner Plate": "일반 식사용 접시",
    "Plum Pudding": "자두 푸딩",
    "Pork Chops": "돼지갈비",
    "Pork Chops with Apples and Stuffing": "사과와 스터핑을 곁들인 돼지갈비",
    "Pork Pot Pie": "돼지고기 포트 파이",
    "Pot Roast": "냄비 구이",
    "Pot Roast with Vegetables": "채소를 곁들인 냄비 구이",
    "Pumpernickel Slice": "펌퍼니켈 빵 조각",
    "Reuben": "루벤 샌드위치",
    "Reuben Sandwich": "루벤 샌드위치",
    "Salami": "살라미",
    "Salami on Rye": "호밀빵 살라미 샌드위치",
    "Salmon Steak": "연어 스테이크",
    "Salmon Steaks": "연어 스테이크",
    "Salmon Steaks with Asparagus": "아스파라거스를 곁들인 연어 스테이크",
    "Sheep Milk": "양 우유",
    "Sour Cream": "사워크림",
    "Spiced Pears": "향신료로 조린 배",
    "Spiced Pears in Citrus Sauce": "감귤 소스로 조린 배",
    "Sweet Roll": "스위트 롤",
    "Vegetable Medley": "채소 모둠",
    "Vegetable Oil": "식용유",
    "Beef Wellington": "비프 웰링턴",
    "Beef Wellington with Mashed Potatoes and Vegetable Medley": (
        "으깬 감자와 채소 모둠을 곁들인 비프 웰링턴"
    ),
    "Whipped Cream": "휘핑크림",
    "Yellow Cake": "옐로 케이크",
    "Yellow Cupcake": "옐로 컵케이크",
    "Apple Juice": "사과 주스",
    "SweetBerry Juice": "달콤한 열매 주스",
    "Fruit Punch": "과일 펀치",
    "Grape Juice": "포도 주스",
    "Lemonade": "레모네이드",
    "Orange Juice": "오렌지 주스",
    "Water": "물",
    "Cup of Milk": "우유 한 컵",
    "Pitcher of Milk": "우유 한 피처",
    "Cup of Apple Juice": "사과 주스 한 컵",
    "Cup of SweetBerry Juice": "달콤한 열매 주스 한 컵",
    "Cup of Fruit Punch": "과일 펀치 한 컵",
    "Cup of Grape Juice": "포도 주스 한 컵",
    "Cup of Lemonade": "레모네이드 한 컵",
    "Cup of Orange Juice": "오렌지 주스 한 컵",
    "Cup of Water": "물 한 컵",
    "Pitcher of Apple Juice": "사과 주스 한 피처",
    "Pitcher of SweetBerry Juice": "달콤한 열매 주스 한 피처",
    "Pitcher of Fruit Punch": "과일 펀치 한 피처",
    "Pitcher of Grape Juice": "포도 주스 한 피처",
    "Pitcher of Lemonade": "레모네이드 한 피처",
    "Pitcher of Orange Juice": "오렌지 주스 한 피처",
    "Pitcher of Water": "물 한 피처",
    "Plants Grape Vine": "포도 덩굴을 심습니다",
    "Raw Cheddar": "숙성 전 체더 치즈",
    "Raw Gouda": "숙성 전 고다 치즈",
    "Raw Parmesan": "숙성 전 파르메산 치즈",
    "Raw Swiss": "숙성 전 스위스 치즈",
    "Ground Peppercorn": "간 후추",
    "Barley Slice": "보리빵 조각",
    "Rye Slice": "호밀빵 조각",
    "Charcuterie Foods": "샤퀴테리 음식",
    "Unbaked Chicken Meal": "굽기 전 닭고기 요리",
    "Unbaked Eggplant Parmesan": "굽기 전 가지 파르메산",
    "Unbaked Lamb Meal": "굽기 전 양고기 요리",
    "Unbaked Lasagna": "굽기 전 라자냐",
    "Unbaked Meatloaf": "굽기 전 미트로프",
    "Unbaked Spiced Pears": "굽기 전 향신료 배 요리",
    "Unbaked Pork Meal": "굽기 전 돼지고기 요리",
    "Unbaked Pot Roast": "굽기 전 냄비 구이",
    "Unbaked Salmon Meal": "굽기 전 연어 요리",
    "Unbaked Beef Wellington": "굽기 전 비프 웰링턴",
    "All About the Basket": "바구니 알아보기",
    "Basket Data Tags": "바구니 데이터 태그",
    "Glassware": "유리 식기",
    "Pantry Jars": "팬트리 보관 병",
    "Baked Pan Meals": "구운 팬 요리",
    "Pan Meal Recipes": "팬 요리 레시피",
    "Pan Meal Recipes, Cont'd": "팬 요리 레시피(계속)",
    "Making Pan Meals": "팬 요리 만들기",
    "Dinner Plates": "식사용 접시",
    "Soup Pot": "수프 냄비",
    "Crafting the Pot": "수프 냄비 제작하기",
    "Discovering Soup Recipes": "수프 레시피 찾기",
    "Making the Soup": "수프 만들기",
    "Spice Jars": "향신료 병",
    "Served Plate of Food": "접시에 담은 음식",
    "Cheese Shelf": "치즈 숙성 선반",
    "Automating Aging": "숙성 자동화",
    "Using the Cheese Shelf": "치즈 숙성 선반 사용하기",
    "Dessert Stands": "디저트 스탠드",
    "Pastry Stand": "페이스트리 스탠드",
    "Crop Basket": "농산물 바구니",
    "Pantry Blocks": "팬트리 블록",
    "Cinnamon Tree": "시나몬나무",
    "Glass Cup Recipe": "유리컵 레시피",
    "Pan Meals": "팬 요리",
    "Craft Baking Pan": "베이킹 팬 제작하기",
    "Glass Pitcher Recipe": "유리 피처 레시피",
    "Cheese-Making Guide": "치즈 제조 안내",
    "Cheese Making Guide": "치즈 제조 안내",
    "Add Milk": "우유 넣기",
    "Add Rennet": "레닛 넣기",
    "Curds and Whey": "응유와 유청",
    "Aging on the Cheese Shelf": "치즈 숙성 선반에서 숙성하기",
    "Soft Cheese": "연성 치즈",
    "Crops": "작물",
    "Foods": "음식",
    "Grape Vines": "포도 덩굴",
    "Herbs And Spices": "허브와 향신료",
    "Herbs and Harvest Herbs": "Herbs and Harvest 허브",
    "Potted Herbs": "화분에 심은 허브",
    "Introduction": "소개",
    "Herbs and Harvest Crops": "Herbs and Harvest 작물",
    "Pantry Items": "팬트리 아이템",
    "Desserts": "디저트",
    "Mama Michelle": "마마 미셸",
    "Afterword": "맺음말",
    "Fruit Trees": "과일나무",
    "Aging the Cheese": "치즈 숙성하기",
    "Automation": "자동화",
    "The Curd Stages": "응유 단계",
    "Add the Milk": "우유 넣기",
    "Cheese Recipes": "치즈 레시피",
    "Placeable Wheels": "놓을 수 있는 치즈 휠",
    "Done, or Nearly There": "완료, 또는 거의 완료",
    "Add the Rennet": "레닛 넣기",
    "Add Salt": "소금 넣기",
    "Supplies": "준비물",
    "Cheese Wheels: Soft": "치즈 휠: 연성",
    "Cheese Wheels: Hard": "치즈 휠: 경성",
    "All About Crops": "작물 알아보기",
    "List of Crops": "작물 목록",
    "Crops, A - C": "작물 A-C",
    "Crops, D - R": "작물 D-R",
    "Crops, S - Z": "작물 S-Z",
    "Tall Crops": "키 큰 작물",
    "Breakfast Foods": "아침 식사",
    "Breads": "빵",
    "Bread Slices": "빵 조각",
    "Sandwiches": "샌드위치",
    "Condiments P.1": "조미료 1",
    "Condiments P.2": "조미료 2",
    "Dairy": "유제품",
    "Obtaining Milk": "우유 얻기",
    "Cakes and Cupcakes": "케이크와 컵케이크",
    "Cheesecakes": "치즈케이크",
    "Cookies": "쿠키",
    "Desserts (Continued)": "디저트(계속)",
    "Muffins and Rolls": "머핀과 롤",
    "Pies": "파이",
    "Meats": "육류",
    "Other Dishes P.1": "기타 요리 1",
    "Other Dishes P.2": "기타 요리 2",
    "Other Dishes P.3": "기타 요리 3",
    "Salads": "샐러드",
    "Cinnamon Trees": "시나몬나무",
    "All About Herbs": "허브 알아보기",
    "List of Herbs": "허브 목록",
    "All about Spices": "향신료 알아보기",
    "Prepared Herbs & Spices": "손질한 허브와 향신료",
    "All About Fruit Trees": "과일나무 알아보기",
    "A Complete List of Trees": "전체 나무 목록",
    "The Homesteader's Handbook:": "자급자족 생활 안내서:",
}

BOOK_TEXT = {
    "The crop basket can hold up to 8 stacks of any Crop items such as fruits or vegetables.\n\nEach item displayed represents one stack.": (
        "농산물 바구니에는 과일이나 채소 같은 작물 아이템을 최대 8스택까지 "
        "보관할 수 있어요.\n\n표시되는 아이템 하나가 한 스택을 뜻해요."
    ),
    "\nTo remove an item, right-click with an empty hand. Items will add back to player inventory, starting with the most recent.": (
        "\n아이템을 꺼내려면 빈손으로 우클릭하세요. 가장 최근에 넣은 아이템부터 "
        "플레이어 인벤토리로 돌아와요."
    ),
    "The Pantry Update adds several blocks to the game. Select a topic below to learn more:": (
        "팬트리 업데이트에서는 여러 블록을 추가해요. 자세히 알아볼 주제를 아래에서 "
        "선택하세요:"
    ),
    "Right-click on a block of Sand with a shovel to create a salt basin.\n\nUse a bucket of water on it, or allow rainfall to fill it.\n\nThen, let it dry up.": (
        "삽을 들고 모래 블록을 우클릭하면 염전을 만들 수 있어요.\n\n물 양동이를 "
        "사용하거나 비가 내려 물이 차게 하세요.\n\n그다음 물이 마를 때까지 기다리세요."
    ),
    "When the Basin has dried, Salt will appear.\n\nYou can automate collection with a hopper underneath the basin.": (
        "염전이 마르면 소금이 생겨요.\n\n아래에 깔때기를 놓으면 소금 수집을 "
        "자동화할 수 있어요."
    ),
    "Pantry Jars are storage jars that will hold up to a single stack of any item.": (
        "팬트리 보관 병에는 어떤 아이템이든 한 스택까지 보관할 수 있어요."
    ),
    "Pantry Jars will only hold items, not blocks.": (
        "팬트리 보관 병에는 아이템만 보관할 수 있고 블록은 보관할 수 없어요."
    ),
    "These small storage jars will hold a single stack of seasonings.\n\nThe label will change automatically based on the ingredient inside the jar.\n\nSpice Jars hold their contents when broken and picked up.": (
        "이 작은 향신료 병에는 조미료 한 스택을 보관할 수 있어요.\n\n병 안의 "
        "재료에 따라 라벨이 자동으로 바뀌어요.\n\n향신료 병은 부숴서 회수해도 내용물을 "
        "그대로 보관해요."
    ),
    "Plates will hold and display a single item.\n\nDinner Plates are also used to retrieve servings from Pan Meals or the Charcuterie Board.": (
        "접시에는 아이템 하나를 놓아 전시할 수 있어요.\n\n식사용 접시로 팬 요리나 "
        "샤퀴테리 보드에서 1인분을 담아낼 수도 있어요."
    ),
    "There are 3 styles of dinner plates:\n": "식사용 접시는 3가지 모양이 있어요:\n",
    "The Cheese shelf is an interactive block, and has a GUI similar to a Furnace. Click on a topic below to learn more.": (
        "치즈 숙성 선반은 상호작용할 수 있는 블록이며 화로와 비슷한 GUI를 사용해요. "
        "자세히 알아볼 주제를 아래에서 선택하세요."
    ),
    "Click on the shelf to open the GUI, and add a raw wheel of cheese to the input slot. If you close the GUI, you will see the wheel appear on the shelf. The shelf holds two wheels at once.": (
        "선반을 클릭해 GUI를 열고 입력 칸에 숙성 전 치즈 휠을 넣으세요. GUI를 닫으면 "
        "선반 위에 치즈 휠이 보여요. 선반 하나에는 치즈 휠을 두 개까지 놓을 수 있어요."
    ),
    "\nAfter some time, the wheel will change to an Aged wheel. Open the block interface once more, to retrieve the aged wheel.": (
        "\n시간이 지나면 치즈 휠이 숙성돼요. 숙성된 치즈 휠을 꺼내려면 블록 화면을 "
        "다시 여세요."
    ),
    "The Aging process for cheese can be automated with Redstone. ": (
        "레드스톤으로 치즈 숙성 과정을 자동화할 수 있어요. "
    ),
    "\nThe Cheese Shelf allows Hoppers to insert raw wheels into the shelf, and Hopper output to extract aged wheels from it.": (
        "\n깔때기로 숙성 전 치즈 휠을 치즈 숙성 선반에 넣고, 숙성된 치즈 휠을 "
        "꺼낼 수 있어요."
    ),
    "The Butter Churn creates Butter using Cream. To create butter, place down the Churn Block. Use a Bucket of Cream on the Churn.": (
        "버터 교반기는 크림으로 버터를 만들어요. 교반기를 설치한 뒤 크림 양동이를 "
        "교반기에 사용하세요."
    ),
    "The Churn will animate and play sounds. When it's finished, it will drop a stick of Butter. This process can be automated with a Dispenser.": (
        "교반기가 움직이며 소리를 내다가 작업이 끝나면 버터 한 개를 떨어뜨려요. 이 "
        "과정은 발사기로 자동화할 수 있어요."
    ),
    "There are two types of dessert stands for displaying desserts. Click on a link below to learn more.": (
        "디저트를 전시하는 스탠드는 두 종류예요. 자세히 알아보려면 아래 링크를 "
        "선택하세요."
    ),
    "A Cake Stand has a large, single tiered base and will hold a single Cake, Pie, or Cheesecake, or up to 8 small pastries or desserts.": (
        "케이크 스탠드는 큰 단층 받침대예요. 케이크, 파이 또는 치즈케이크 하나를 "
        "놓거나 작은 페이스트리나 디저트를 최대 8개까지 놓을 수 있어요."
    ),
    "A Cake, Pie, or Cheesecake placed on a Cake Stand will yield its normal amount of servings.\n\nNote: Savory Pies can also be placed on a Cake Stand.": (
        "케이크 스탠드에 놓은 케이크, 파이 또는 치즈케이크는 원래 개수만큼 조각을 "
        "제공해요.\n\n참고: 짭짤한 파이도 케이크 스탠드에 놓을 수 있어요."
    ),
    "A Pastry Stand is a little smaller and has two tiers.\n\nIt will hold up to 8 of any one kind of small pastries or desserts.": (
        "페이스트리 스탠드는 조금 더 작고 2단으로 되어 있어요.\n\n같은 종류의 작은 "
        "페이스트리나 디저트를 최대 8개까지 놓을 수 있어요."
    ),
    "\n\nMuffins, Cupcakes, Cookies, or Rolls can all be placed on a Pastry Stand.": (
        "\n\n머핀, 컵케이크, 쿠키와 롤을 페이스트리 스탠드에 놓을 수 있어요."
    ),
    "A Soup Pot is a placeable food block. Click on the links below to learn more.": (
        "수프 냄비는 설치할 수 있는 음식 블록이에요. 자세히 알아보려면 아래 링크를 "
        "선택하세요."
    ),
    "An empty Soup Pot is needed for Soup. The crafting recipe for it is shown here:": (
        "수프를 만들려면 빈 수프 냄비가 필요해요. 제작법은 다음과 같아요:"
    ),
    "\n\nThe Empty Soup Pot can be placed and picked back up with an empty hand.": (
        "\n\n빈 수프 냄비는 설치할 수 있으며 빈손으로 다시 회수할 수 있어요."
    ),
    "Soups are created by combining an empty pot with ingredients. This results in a pot of soup which is a placeable block.\n\nTo heat the Soup Pot, place a heat source underneath it such as a Campfire, or fire.": (
        "빈 냄비와 재료를 조합하면 설치할 수 있는 수프 냄비가 만들어져요.\n\n수프 "
        "냄비를 데우려면 아래에 모닥불이나 불 같은 열원을 놓으세요."
    ),
    "When the Soup Pot is heated, use a bowl on it to retrieve soup.": (
        "수프 냄비가 데워지면 그릇을 사용해 수프를 담아내세요."
    ),
    "\nExample of a Soup Bowl:": "\n수프 한 그릇의 예:",
    "\nNote: ONLY heated pots will allow a bowl to be used on them to get soup. Each pot will yield 8 bowls of soup.": (
        "\n참고: 데운 냄비에만 그릇을 사용해 수프를 담을 수 있어요. 냄비 하나에서는 "
        "수프 8그릇이 나와요."
    ),
    "Soup recipes will be discovered when a player obtains their main ingredient, or meat.\n\nList of Soups and their discovery ingredient, which is in parentheses: ": (
        "플레이어가 수프의 주재료나 고기를 얻으면 해당 수프 레시피를 발견해요.\n\n"
        "수프 목록과 괄호 안에 표시된 발견 재료: "
    ),
    "Soups and their discovery ingredient, continued: ": "수프와 발견 재료(계속): ",
    "Baked Pan Meals are also placeable food blocks. Click on the links below to learn more.": (
        "구운 팬 요리도 설치할 수 있는 음식 블록이에요. 자세히 알아보려면 아래 링크를 "
        "선택하세요."
    ),
    "An empty Baking Pan is needed for a Baked Pan Meal. The crafting recipe for it is shown here:": (
        "구운 팬 요리를 만들려면 빈 베이킹 팬이 필요해요. 제작법은 다음과 같아요:"
    ),
    "\n\nThe Empty Baking Pan can be placed and picked back up with an empty hand.": (
        "\n\n빈 베이킹 팬은 설치할 수 있으며 빈손으로 다시 회수할 수 있어요."
    ),
    "Baked Pan meals are made by combining a Pan with recipe ingredients, and then 'baking' it in a furnace or a smoker.": (
        "팬과 레시피 재료를 조합한 뒤 화로나 훈연기에 구우면 구운 팬 요리가 "
        "완성돼요."
    ),
    "The Baked Pan Meal is a placeable block. To 'serve' a Pan Meal, use a plate on it. Each pan yields 8 servings.\n\nPan Meal Recipes are discovered when a player obtains their main ingredient or meat.": (
        "구운 팬 요리는 설치할 수 있는 블록이에요. 팬 요리를 담아내려면 접시를 "
        "사용하세요. 팬 하나에서 8인분이 나와요.\n\n플레이어가 주재료나 고기를 얻으면 "
        "해당 팬 요리 레시피를 발견해요."
    ),
    "Pan Recipes and Discovery Ingredients:": "팬 요리 레시피와 발견 재료:",
    "Pan Recipes and Discovery Ingredients, continued:": (
        "팬 요리 레시피와 발견 재료(계속):"
    ),
    'Using a Dinner Plate on a Baked Pan Meal will create a "Served Plate" of that particular meal.\n\nThe Served Plate of food is a placeable block which can can be "eaten" at a later time, by right-clicking on it.': (
        "구운 팬 요리에 식사용 접시를 사용하면 해당 요리를 담은 음식 접시가 "
        "만들어져요.\n\n음식 접시는 설치할 수 있는 블록이며, 나중에 우클릭해 먹을 수 "
        "있어요."
    ),
    "Or, you can eat the food while holding the plate, and it will leave the empty plate behind, when finished.": (
        "접시를 든 채로 음식을 먹을 수도 있으며, 다 먹으면 빈 접시가 남아요."
    ),
    "There are several drinks in Herbs and Harvest. To make drinks, you need glassware.\n\nClick on the links below to learn more:": (
        "Herbs and Harvest에는 여러 음료가 있어요. 음료를 만들려면 유리 식기가 "
        "필요해요.\n\n자세히 알아보려면 아래 링크를 선택하세요:"
    ),
    "Drink Pitchers are crafted with glass, and are reusable.\n\nCrafting a Glass Pitcher and combining it with different drink recipes will create a placeable Drink Pitcher.": (
        "음료 피처는 유리로 제작하며 재사용할 수 있어요.\n\n유리 피처를 제작해 여러 음료 "
        "레시피와 조합하면 설치할 수 있는 음료 피처가 만들어져요."
    ),
    "Use a Pitcher on a glass cup to 'pour' a drink. Each pitcher can pour up to 4 drinks, and will leave behind an empty Glass Pitcher in the inventory.": (
        "유리컵에 피처를 사용해 음료를 따르세요. 피처 하나로 최대 4잔을 따를 수 "
        "있으며, 다 따르면 인벤토리에 빈 유리 피처가 남아요."
    ),
    "Cups are also crafted with glass, and are reusable, as well.\n\nWhen placed, the Glass Cup can be picked back up with an empty hand.\nIf it contains a drink, it will keep the drink in inventory.": (
        "컵도 유리로 제작하며 재사용할 수 있어요.\n\n설치한 유리컵은 빈손으로 다시 "
        "회수할 수 있어요.\n음료가 들어 있다면 회수해도 내용물이 유지돼요."
    ),
    "Picking up a full cup will give an item that can be drank, and will leave behind the empty cup in the inventory, once used.": (
        "음료가 든 컵을 회수하면 마실 수 있는 아이템이 되며, 다 마시면 인벤토리에 "
        "빈 컵이 남아요."
    ),
}

BOOK_TEXT.update(
    {
        "The Homesteader's Guide to Cheese Making\n\n": "자급자족 생활자를 위한 치즈 제조 안내\n\n",
        "Cheese comes in two types: Soft Cheese, and Hard Cheese. A Soft Cheese Wheel is ready for use immediately.": (
            "치즈는 연성 치즈와 경성 치즈로 나뉘어요. 연성 치즈 휠은 만든 즉시 "
            "사용할 수 있어요."
        ),
        'A raw wheel of hard cheese must be "aged" on a Cheese Shelf before using.': (
            "숙성 전 경성 치즈 휠은 사용하기 전에 치즈 숙성 선반에서 숙성해야 해요."
        ),
        "For Cheese Making, you need the following:\n-Milk Buckets (An assortment, for different cheeses)\n-A Cauldron with a heat source below it\n-Rennet\n-Salt\n-A Cheese Aging Shelf": (
            "치즈를 만들려면 다음 준비물이 필요해요:\n-우유 양동이(치즈 종류에 맞는 "
            "조합)\n-아래에 열원이 있는 가마솥\n-레닛\n-소금\n-치즈 숙성 선반"
        ),
        "Once you have your supplies ready, you will need to decide on what cheese to make.\n\nThere are 8 total types of cheeses, and each uses a unique mixture of milks to create.\n\nMilk mixtures for Cheese recipes are as follows:": (
            "준비물을 갖췄다면 어떤 치즈를 만들지 정하세요.\n\n치즈는 모두 8종류이며, "
            "종류마다 고유한 우유 조합을 사용해요.\n\n치즈 레시피에 필요한 우유 조합은 "
            "다음과 같아요:"
        ),
        "Hard Cheeses:\n\n- Cheddar: Cow Milk\n- Gouda: Sheep Milk\n- Parmesan: Cow Milk, Goat Milk\n- Swiss: Sheep Milk, Goat Milk": (
            "경성 치즈:\n\n- 체더 치즈: 소 우유\n- 고다 치즈: 양 우유\n- 파르메산 "
            "치즈: 소 우유, 염소 우유\n- 스위스 치즈: 양 우유, 염소 우유"
        ),
        "\n\nSoft Cheeses:\n\n- Caravane: Camel Milk\n- Chevre: Goat Milk\n- Feta: Camel Milk, Goat Milk\n- Ricotta: Camel Milk, Sheep Milk": (
            "\n\n연성 치즈:\n\n- 카라반 치즈: 낙타 우유\n- 셰브르 치즈: 염소 "
            "우유\n- 페타 치즈: 낙타 우유, 염소 우유\n- 리코타 치즈: 낙타 우유, 양 "
            "우유"
        ),
        "Once you have decided on a recipe, and you have your other supplies, it's time to start creating the Cheese.": (
            "레시피를 정하고 다른 준비물도 갖췄다면 치즈를 만들 차례예요."
        ),
        "Make sure your Caluldron is heated below, and add your Milk to the Cauldron. For a mix of Milk types, add one, then quickly add the other.": (
            "가마솥 아래에 열원이 있는지 확인하고 우유를 넣으세요. 여러 종류의 우유를 "
            "섞는 레시피라면 한 종류를 넣은 뒤 다른 종류를 빠르게 넣으세요."
        ),
        "Next, QUICKLY add your Rennet. This is important, because if Rennet is not added fast enough, the Milk will change into Cream.": (
            "그다음 레닛을 곧바로 넣으세요. 레닛을 충분히 빨리 넣지 않으면 우유가 "
            "크림으로 변하므로 중요해요."
        ),
        "When Rennet is added, you will see the mixture in the cauldron immediately change.": (
            "레닛을 넣으면 가마솥 속 혼합물이 즉시 변하는 것을 볼 수 있어요."
        ),
        "The mixture will begin to move, and after some time, will change once more, into Curds and Whey.": (
            "혼합물이 움직이기 시작하고 시간이 지나면 응유와 유청으로 다시 변해요."
        ),
        "This looks like a yellow liquid with white bits that rise to the surface, as seen here in the photo. Bubbles will also be visible.": (
            "사진처럼 노란 액체 위로 흰 덩어리가 떠오르며 거품도 보여요."
        ),
        "When your Cauldron is full of Curds and Whey, the next thing to do is to use Salt on the Cauldron.": (
            "가마솥이 응유와 유청으로 가득 차면 가마솥에 소금을 사용하세요."
        ),
        "The Salt will combine with the Whey, and will solidify the cheese into a Cheese Wheel.\n\nYour Cauldron should be empty after receiving the Cheese Wheel.": (
            "소금이 유청과 결합해 치즈를 치즈 휠로 굳혀요.\n\n치즈 휠을 받으면 "
            "가마솥은 비어 있어야 해요."
        ),
        "The next part depends on what type of Cheese you have made.\n\nIf your Cheese recipe was a Soft Cheese, then there is nothing else to do; it's ready to go. ": (
            "다음 단계는 만든 치즈 종류에 따라 달라요.\n\n연성 치즈를 만들었다면 추가 "
            "과정 없이 바로 사용할 수 있어요. "
        ),
        "Place it down, and click on it to receive a wedge of Cheese.": (
            "치즈 휠을 설치하고 클릭하면 치즈 조각을 얻어요."
        ),
        'If you have crafted a Hard Cheese recipe, the Wheel you receive will be a "Raw" Wheel of that Cheese type, which will need to be aged.': (
            "경성 치즈를 만들었다면 숙성이 필요한 숙성 전 치즈 휠을 받게 돼요."
        ),
        "Add the Raw Wheel to a Cheese Shelf so that it can age. You will be able to see it change on the shelf, when it is aged.": (
            "숙성 전 치즈 휠을 치즈 숙성 선반에 넣으세요. 숙성이 끝나면 선반 위의 "
            "모습이 바뀌는 것을 볼 수 있어요."
        ),
        "A finished Wheel of Cheese is a placeable block.\n\nPlace it down, and click on it to recieve an edible Wedge of Cheese, which can be eaten or used in food recipes.": (
            "완성된 치즈 휠은 설치할 수 있는 블록이에요.\n\n설치한 뒤 클릭하면 먹거나 "
            "음식 레시피에 사용할 수 있는 치즈 조각을 얻어요."
        ),
        "Each wheel will yield 4 Wedges of Cheese.\n\nSpecial note: a cheese wheel CANNOT be picked up once it has been placed.": (
            "치즈 휠 하나에서는 치즈 조각 4개가 나와요.\n\n주의: 한 번 설치한 치즈 "
            "휠은 회수할 수 없어요."
        ),
        "Adding Rennet or Salt to the Cauldron can be automated with a Dispenser.\n\nNote: Adding the Milk mixtures to the Cauldron cannot be automated.": (
            "발사기로 가마솥에 레닛이나 소금을 넣는 과정을 자동화할 수 있어요.\n\n"
            "참고: 우유 조합을 가마솥에 넣는 과정은 자동화할 수 없어요."
        ),
        "If Milk has cooked into Cream, extraction of the Cream Bucket can also be automated.": (
            "우유가 크림으로 변했다면 크림 양동이를 꺼내는 과정도 자동화할 수 있어요."
        ),
        "Herbs and Harvest adds 32 new crops to the game.\n\nSelect a topic below to learn more:": (
            "Herbs and Harvest에는 새로운 작물 32종이 추가돼요.\n\n자세히 알아볼 주제를 "
            "아래에서 선택하세요:"
        ),
        "Herbs and Harvest Crops behave the same as Vanilla crops.\n\nThe Crops are all plantable on farmland, and they must be broken to obtain produce and seeds.": (
            "Herbs and Harvest 작물은 기본 게임의 작물과 똑같이 자라요.\n\n모든 작물은 "
            "경작지에 심을 수 있으며, 수확물과 씨앗을 얻으려면 작물을 부숴야 해요."
        ),
        "\n\nCrops can be found in village farms, and seeds can be found in chests throughout the Overworld.\n\nSeeds can also be created by crafting from produce. In a Crafting Table, one crop will yield one seed.": (
            "\n\n작물은 마을 농장에서, 씨앗은 오버월드 곳곳의 상자에서 찾을 수 "
            "있어요.\n\n수확물을 제작해 씨앗을 얻을 수도 있어요. 작업대에서 작물 하나로 "
            "씨앗 하나를 만들 수 있어요."
        ),
        "There are several tall crops available:\n\nCorn, Eggplant, Peas, and Tomatoes.": (
            "키가 크게 자라는 작물은 다음과 같아요:\n\n옥수수, 가지, 완두콩, 토마토."
        ),
        "\n\nBreaking either the top or bottom of these will break the entire crop, dropping its produce and seeds, if it is mature.\n\nOnly one seed is required to plant a tall crop, and they must be replanted.": (
            "\n\n위쪽이나 아래쪽을 부수면 작물 전체가 부서지며, 다 자랐다면 수확물과 "
            "씨앗이 나와요.\n\n키 큰 작물을 심는 데에는 씨앗 하나만 필요하며, 수확한 뒤 "
            "다시 심어야 해요."
        ),
        "Grape vines grow similarly to cave vines and produce harvestable fruit.\n\nThey are planted by placing underneath a block, and over time, will grow downward and produce fruit.": (
            "포도 덩굴은 동굴 덩굴과 비슷하게 자라며 수확할 수 있는 열매를 맺어요.\n\n"
            "블록 아래에 심으면 시간이 지나면서 아래로 자라 열매를 맺어요."
        ),
        "Like Cave Vines, they can be bonemealed.\n\nGrapes can be found growing on trellises in villages, or in Overworld chests.": (
            "동굴 덩굴처럼 뼛가루를 사용할 수 있어요.\n\n포도는 마을의 격자 울타리에서 "
            "자라는 것을 찾거나 오버월드 상자에서 얻을 수 있어요."
        ),
        "Following is a complete, alphabetized list of all Herbs & Harvest Crops.\nClick on the links below to view each section:": (
            "다음은 Herbs & Harvest의 모든 작물을 알파벳순으로 정리한 목록이에요.\n"
            "각 부분을 보려면 아래 링크를 선택하세요:"
        ),
        "\n\nGrowing Vine Crops:\n": "\n\n덩굴 작물 기르기:\n",
    }
)

BOOK_TEXT.update(
    {
        "Grape Vines grow and produce harvestable fruit similarly to Cave Vines.\n\nThey are planted by placing underneath a block, and over time, will grow downward and produce fruit.": (
            "포도 덩굴은 동굴 덩굴과 비슷하게 자라며 수확할 수 있는 열매를 맺어요.\n\n"
            "블록 아래에 심으면 시간이 지나면서 아래로 자라 열매를 맺어요."
        ),
        "Like Cave Vines, they can be bonemealed.\n\nGrapes can be found growing on a trellis in villages, or in overworld chests.": (
            "동굴 덩굴처럼 뼛가루를 사용할 수 있어요.\n\n포도는 마을의 격자 울타리에서 "
            "자라는 것을 찾거나 오버월드 상자에서 얻을 수 있어요."
        ),
        "Herbs and Harvest adds several herbs and spices. Select a topic below to learn more:": (
            "Herbs and Harvest에는 여러 허브와 향신료가 추가돼요. 자세히 알아볼 주제를 "
            "아래에서 선택하세요:"
        ),
        "Like crops, Herbs require farmland and water to grow.\n\nOnce harvested, herbs can be placed on grass or dirt for decoration.\n\nHerbs can also be potted in a Flower Pot.": (
            "허브도 작물처럼 자라려면 경작지와 물이 필요해요.\n\n수확한 허브는 잔디나 "
            "흙에 놓아 장식할 수 있어요.\n\n화분에 심을 수도 있어요."
        ),
        "\nIn the Pantry Update, Fresh herbs can be chopped or ground, then stored in Spice Jars for use in recipes.": (
            "\n팬트리 업데이트에서는 신선한 허브를 다지거나 갈아 향신료 병에 보관한 뒤 "
            "레시피에 사용할 수 있어요."
        ),
        "Like herbs, Peppercorn, Ginger, and Turmeric all require farmland to grow.\n\nPeppercorn and the Cinnamon Tree Sapling can also be potted.": (
            "통후추, 생강과 강황도 허브처럼 자라려면 경작지가 필요해요.\n\n통후추와 "
            "시나몬나무 묘목은 화분에 심을 수도 있어요."
        ),
        "\n\nList of Spices:\n": "\n\n향신료 목록:\n",
        "Thistle is a flower that can be found growing in nearly any Overworld biome.\n\nThistle is used to create Rennet, which is used to make cheese.": (
            "엉겅퀴는 오버월드의 거의 모든 생물군계에서 자라는 꽃이에요.\n\n엉겅퀴로 "
            "치즈 제조에 쓰는 레닛을 만들 수 있어요."
        ),
        "Thistle is two blocks tall, with purple/pink blooms.\n\nIt can be bonemealed and farmed the same way as tall flowers.": (
            "엉겅퀴는 높이가 2블록이고 보라색과 분홍색 꽃이 피어요.\n\n키 큰 꽃처럼 "
            "뼛가루를 사용하고 재배할 수 있어요."
        ),
        "Cinnamon Trees are two blocks tall. Their bark grows continuously and can be stripped to produce Cinnamon.\n\nCinnamon saplings grow in Tropical biomes, or can be found in Overworld chests.": (
            "시나몬나무는 높이가 2블록이에요. 나무껍질이 계속 자라며 벗기면 시나몬을 "
            "얻을 수 있어요.\n\n시나몬나무 묘목은 열대 생물군계에서 자라거나 오버월드 "
            "상자에서 찾을 수 있어요."
        ),
        "To get Cinnamon, strip the bark by right-clicking the tree with an axe.\n\nIf the bark has matured, it will yield some Cinnamon.": (
            "시나몬을 얻으려면 도끼로 나무를 우클릭해 껍질을 벗기세요.\n\n껍질이 "
            "다 자랐다면 시나몬이 나와요."
        ),
        "Mama's Herbs and Harvest is a farming mod which is also the base for the recipes in Mama's Minis such as MerryMaking and Happy Hallows. There are 32 growable crops, along with: grapes, 8 fruit-bearing trees, and 14 herbs.": (
            "Mama's Herbs and Harvest는 농사 모드이며 MerryMaking과 Happy Hallows 같은 "
            "Mama's Minis 레시피의 기반이기도 해요. 재배할 수 있는 작물 32종과 포도, "
            "열매를 맺는 나무 8종, 허브 14종이 있어요."
        ),
        "The 'Pantry Update', which adds new blocks, items, and food, was released in early February of 2026.": (
            "새 블록, 아이템과 음식을 추가하는 '팬트리 업데이트'는 2026년 2월 초에 "
            "출시됐어요."
        ),
        "The Pantry Update adds several new items to the game. Select a topic below to learn more:": (
            "팬트리 업데이트에서는 여러 아이템을 추가해요. 자세히 알아볼 주제를 아래에서 "
            "선택하세요:"
        ),
        "Rennet is crafted from Thistle, and is used in Cheese Making.": (
            "레닛은 엉겅퀴로 제작하며 치즈 제조에 사용해요."
        ),
        "\nAdd it to a cauldron IMMEDIATELY after milk has been added.\n\nWaiting too long to add Rennet will cause the Milk to turn into Cream.": (
            "\n우유를 넣은 직후 가마솥에 레닛을 곧바로 넣으세요.\n\n레닛을 너무 "
            "늦게 넣으면 우유가 크림으로 변해요."
        ),
        "Salt is created when a full Salt Basin dries up.": (
            "물이 가득 찬 염전이 마르면 소금이 만들어져요."
        ),
        "\nSalt is used in cheese-making, to finalize the process, and is also used in many of the food recipes in Herbs and Harvest.": (
            "\n소금은 치즈 제조의 마지막 단계에 사용하며 Herbs and Harvest의 여러 음식 "
            "레시피에도 사용해요."
        ),
        'All of the fresh herbs in Herbs and Harvest can be crafted into a "Chopped" herb item. Peppercorn can be crafted into a ground spice.': (
            "Herbs and Harvest의 모든 신선한 허브는 다진 허브 아이템으로 제작할 수 "
            "있어요. 통후추는 간 향신료로 만들 수 있어요."
        ),
        '\nOnions and Garlic can be made into "Minced" variants, and Cinnamon and Ginger can be crafted into "Ground" versions.\n\nThese herbs and spices, along with Salt and Sugar, can be stored in the little Spice Jars.': (
            "\n양파와 마늘은 곱게 다진 형태로, 시나몬과 생강은 간 형태로 제작할 수 "
            "있어요.\n\n이 허브와 향신료는 소금, 설탕과 함께 작은 향신료 병에 보관할 "
            "수 있어요."
        ),
        "Now you're ready to begin farming and filling your home with delicious and interactive dishes.\n\nFor questions, or immediate help, please join the discord:\n\nhttps://discord.gg/2QWyQ8fkUr": (
            "이제 농사를 시작하고 맛있고 상호작용할 수 있는 요리로 집을 채울 준비가 "
            "됐어요.\n\n질문이 있거나 바로 도움이 필요하면 Discord에 참여해 주세요:\n\n"
            "https://discord.gg/2QWyQ8fkUr"
        ),
        "\n\nI hope you enjoy this addition to my catalog of mods.\n\nMuch love,\n~ Mama Michelle": (
            "\n\n제가 만든 모드 목록에 더해진 이 모드를 즐겨 주셨으면 해요.\n\n사랑을 "
            "담아,\n~ 마마 미셸"
        ),
        "Your guide to Mama's Herbs and Harvest": "Mama's Herbs and Harvest 안내서",
        "This guide will show you...": "이 안내서에서 다음 내용을 알려 드려요...",
        "Herbs and Harvest adds 8 Fruit Trees to the game.\n\nSelect a topic below to learn more:": (
            "Herbs and Harvest에는 과일나무 8종이 추가돼요.\n\n자세히 알아볼 주제를 "
            "아래에서 선택하세요:"
        ),
        "Fruit Trees are round shaped, with dark green leaves.\n\nThey grow naturally in almost every Overworld biome.": (
            "과일나무는 둥근 모양에 짙은 녹색 잎이 있어요.\n\n오버월드의 거의 모든 "
            "생물군계에서 자연적으로 자라요."
        ),
        "The leaves of Fruit Trees continuously grow fruit, and can be bonemealed for quicker production.\n\nFruit Tree Saplings can be found in Overworld chests, and can also be potted.": (
            "과일나무 잎에는 계속 열매가 자라며 뼛가루를 사용하면 더 빨리 수확할 수 "
            "있어요.\n\n과일나무 묘목은 오버월드 상자에서 찾을 수 있으며 화분에 심을 수도 "
            "있어요."
        ),
        "Your guide to Hearth, Harvest, and Home\n\nThis book has everything you need to know about growing food, crafting essentials, and turning harvests into hearty meals.": (
            "농사와 수확, 살림을 위한 안내서\n\n이 책에는 식량을 기르고 필수품을 제작해 "
            "수확물을 든든한 식사로 만드는 데 필요한 모든 내용이 담겨 있어요."
        ),
        "Use the Table of Contents to navigate between chapters. Some chapters have sub-sections, and clicking a chapter title will return you to the chapter's main page.": (
            "목차를 사용해 장 사이를 이동하세요. 일부 장에는 하위 항목이 있으며, 장 제목을 "
            "클릭하면 해당 장의 첫 페이지로 돌아가요."
        ),
        "Select a chapter to begin.": "시작할 장을 선택하세요.",
    }
)

BOOK_TEXT.update(
    {
        "The Pantry Update adds several new foods to the game. Select a topic below to learn more:": (
            "팬트리 업데이트에서는 여러 음식을 추가해요. 자세히 알아볼 주제를 아래에서 "
            "선택하세요:"
        ),
        'Herbs and Harvest adds a few meats to the game.\n\nAll are craftable from already-existing items, and each can be smelted into a "Cooked" variant.\n\nMeats can used in recipes, or eaten as-is.': (
            "Herbs and Harvest에는 몇 가지 고기가 추가돼요.\n\n모두 기존 아이템으로 "
            "제작할 수 있으며, 구우면 익힌 형태가 돼요.\n\n고기는 레시피에 사용하거나 "
            "그대로 먹을 수 있어요."
        ),
        "There are several dairy products available. Click the links below to learn more.": (
            "여러 유제품을 만들 수 있어요. 자세히 알아보려면 아래 링크를 선택하세요."
        ),
        "Herbs and Harvest adds three new kinds of Milk to the game.\n\nMilk is used for recipes, cheese making, or can also be heated in a cauldron to make Cream.": (
            "Herbs and Harvest에는 새로운 우유 3종이 추가돼요.\n\n우유는 레시피와 치즈 "
            "제조에 사용하거나 가마솥에서 데워 크림을 만들 수 있어요."
        ),
        "The types of Milk are:\n": "우유 종류는 다음과 같아요:\n",
        "How to Obtain Milk:\n\nJust as you would a Cow, use an empty bucket on a Goat for Goat Milk, and on a Sheep for Sheep Milk. ": (
            "우유 얻는 방법:\n\n소에게 하듯이 빈 양동이를 염소에게 사용하면 염소 우유를, "
            "양에게 사용하면 양 우유를 얻어요. "
        ),
        "For Camel Milk, shift-click the bucket on a Camel.\n\nNote: This may open the Camel's inventory or mount you on the Camel, but you will still get the Milk.": (
            "낙타 우유를 얻으려면 Shift 키를 누른 채 낙타에게 양동이를 사용하세요.\n\n"
            "참고: 낙타의 인벤토리가 열리거나 낙타에 탈 수도 있지만 우유는 정상적으로 "
            "얻어요."
        ),
        "Cream is made in a heated Cauldron.": "크림은 데운 가마솥에서 만들어요.",
        "\n\nAdd any kind of milk, and it will eventually change into cream.\n\nUse a bucket to remove the cream from the Cauldron.": (
            "\n\n아무 종류의 우유나 넣으면 시간이 지나 크림으로 변해요.\n\n양동이를 "
            "사용해 가마솥에서 크림을 꺼내세요."
        ),
        "Cream is made from cooking Milk in a heated Cauldron.\n\nUse a Bucket on a Cauldron full of Cream to obtain it.": (
            "데운 가마솥에서 우유를 익히면 크림이 만들어져요.\n\n크림이 가득 찬 "
            "가마솥에 양동이를 사용해 크림을 얻으세요."
        ),
        "\n\nButter is created by using a bucket of Cream on a Butter Churn.\n\nButter will appear when the Churn has finished churning.": (
            "\n\n버터 교반기에 크림 양동이를 사용하면 버터를 만들 수 있어요.\n\n"
            "교반 작업이 끝나면 버터가 나와요."
        ),
        "There are eight types of cheese. Four are hard cheeses, and four are soft cheeses.\n\nThe Cheesemaking guide in this book provides instructions for making each type of cheese.": (
            "치즈는 8종류로, 경성 치즈 4종과 연성 치즈 4종이 있어요.\n\n이 책의 "
            "치즈 제조 안내에서 각 치즈를 만드는 방법을 확인할 수 있어요."
        ),
        "The soft cheeses are:": "연성 치즈는 다음과 같아요:",
        "\n\nThe hard cheeses are:": "\n\n경성 치즈는 다음과 같아요:",
        "There are a few Breakfast food items Herbs and Harvest.\n\nThis list will show the Breakfast foods and their recipe discovery items:": (
            "Herbs and Harvest에는 몇 가지 아침 식사 음식이 있어요.\n\n다음 목록에서 "
            "아침 식사 음식과 레시피 발견 아이템을 확인할 수 있어요:"
        ),
        "Herbs and Harvest adds several Breads for you to enjoy. Click the links below to learn more:": (
            "Herbs and Harvest에는 여러 빵이 추가돼요. 자세히 알아보려면 아래 링크를 "
            "선택하세요:"
        ),
        "The many grains in Herbs and Harvest grants a nice selection of different breads and sandwiches.\n\nThe Breads available are:": (
            "Herbs and Harvest의 여러 곡물로 다양한 빵과 샌드위치를 만들 수 있어요.\n\n"
            "만들 수 있는 빵은 다음과 같아요:"
        ),
        "Each type of Bread loaf can be crafted into 8 Slices of that kind of bread.": (
            "빵 한 덩어리를 같은 종류의 빵 조각 8개로 제작할 수 있어요."
        ),
        "\n\nMinecraft Bread can also be crafted into slices:": (
            "\n\nMinecraft 빵도 빵 조각으로 제작할 수 있어요:"
        ),
        " Sandwich recipes call for specific breads, and the bread type is also the recipe discovery item.\n\nA complete list of the sandwiches and bread type follows:": (
            " 샌드위치마다 정해진 빵이 필요하며, 그 빵이 레시피 발견 아이템이기도 "
            "해요.\n\n샌드위치와 필요한 빵의 전체 목록은 다음과 같아요:"
        ),
        "There are four types of Salad in Herbs and Harvest, and each recipe is discovered by obtaining Lettuce.\n\nSalads, once eaten, will leave behind an empty bowl.": (
            "Herbs and Harvest에는 샐러드가 4종류 있으며, 상추를 얻으면 각 레시피를 "
            "발견해요.\n\n샐러드를 먹고 나면 빈 그릇이 남아요."
        ),
        "Some other foods, along with their discovery items are:": (
            "기타 음식과 발견 아이템은 다음과 같아요:"
        ),
        "Other foods, with their discovery items, continued:": (
            "기타 음식과 발견 아이템(계속):"
        ),
        "Condiments and other ingredients require either a Bowl or a Spice jar to craft, depending on the recipe.\n\nCondiments and their recipe discovery items are listed here:": (
            "조미료와 기타 재료를 제작할 때에는 레시피에 따라 그릇이나 향신료 병이 "
            "필요해요.\n\n조미료와 레시피 발견 아이템은 다음과 같아요:"
        ),
        "Condiments and other ingredients, continued: ": "조미료와 기타 재료(계속): ",
        "Herbs and Harvest has desserts aplenty. Click the links below to learn more:": (
            "Herbs and Harvest에는 디저트가 아주 많아요. 자세히 알아보려면 아래 링크를 "
            "선택하세요:"
        ),
        "The many Desserts available include Cakes, Cheesecakes, Pies, Cookies, Cupcakes, Muffins, Cinnamon Rolls, Sweet Rolls, and Plum Pudding.": (
            "디저트에는 케이크, 치즈케이크, 파이, 쿠키, 컵케이크, 머핀, 시나몬 롤, "
            "스위트 롤과 자두 푸딩이 있어요."
        ),
        'Cakes, Cheesecakes, Pies, and Plum Pudding are all placeable blocks, and clicking on them with an open hand will give you a "slice" of that dessert.\n\nAll but the Plum Pudding will yield 8 Slices; the Plum Pudding is much smaller, so it yields 4 slices.': (
            "케이크, 치즈케이크, 파이와 자두 푸딩은 모두 설치할 수 있는 블록이며, "
            "빈손으로 클릭하면 디저트 조각을 얻어요.\n\n자두 푸딩을 제외하면 조각이 "
            "8개씩 나오고, 더 작은 자두 푸딩에서는 조각이 4개 나와요."
        ),
        "The smaller desserts and pastries are single-use, edible items.\n\nAs previously mentioned, only the smaller, single-use desserts and pastries can be placed onto the Pastry Stand.": (
            "작은 디저트와 페이스트리는 한 번 먹으면 사라지는 음식 아이템이에요.\n\n"
            "앞서 설명했듯 작은 일회용 디저트와 페이스트리만 페이스트리 스탠드에 놓을 "
            "수 있어요."
        ),
        "Dessert recipe discovery items are listed on the dessert's page.": (
            "디저트 레시피 발견 아이템은 각 디저트 페이지에 적혀 있어요."
        ),
        "Cake recipes are all discovered by looting Wheat.\n\nThe Plum Pudding recipe is discovered by obtaining a Plum.\n\nCakes and Cupcakes are shown here:": (
            "밀을 얻으면 모든 케이크 레시피를 발견해요.\n\n자두를 얻으면 자두 푸딩 "
            "레시피를 발견해요.\n\n케이크와 컵케이크는 다음과 같아요:"
        ),
        "Cheesecake recipes are all discovered by obtaining Cream Cheese.": (
            "크림치즈를 얻으면 모든 치즈케이크 레시피를 발견해요."
        ),
        "\nCheesecakes:\n": "\n치즈케이크:\n",
        "Pies require Wheat to discover the recipe.": "밀을 얻으면 파이 레시피를 발견해요.",
        "\nPies:\n": "\n파이:\n",
        "Cookies also require Wheat to discover the recipe. ": (
            "쿠키 레시피도 밀을 얻으면 발견해요. "
        ),
        "Cookies: ": "쿠키: ",
        "Muffin and Roll recipes are disocvered by obtaining Wheat.": (
            "밀을 얻으면 머핀과 롤 레시피를 발견해요."
        ),
        "\nMuffins: ": "\n머핀: ",
        "\n\nRolls: ": "\n\n롤: ",
    }
)


def find_jar() -> Path:
    """현재 설치본에서 Herbs and Harvest JAR 하나를 찾아요."""
    matches = sorted((resolve_source_root() / "mods").glob(JAR_PATTERN))
    if len(matches) != 1:
        raise FileNotFoundError(f"대상 JAR이 정확히 한 개가 아니에요: {matches}")
    return matches[0]


def read_language(jar: Path) -> dict[str, str]:
    """현재 영어 언어 파일을 읽어요."""
    with ZipFile(jar) as archive:
        value = json.loads(archive.read("assets/herbsandharvest/lang/en_us.json"))
    if not isinstance(value, dict) or len(value) != EXPECTED_KEYS:
        raise ValueError(f"영어 키 수가 달라요: {len(value)}")
    if not all(
        isinstance(key, str) and isinstance(text, str) for key, text in value.items()
    ):
        raise TypeError("언어 키 또는 값이 문자열이 아니에요")
    return value


def translate_simple_name(source: str) -> str:
    """아이템·블록·가이드 목록에 쓰이는 짧은 이름을 번역해요."""
    leading = source[: len(source) - len(source.lstrip())]
    trailing = source[len(source.rstrip()) :]
    text = source.strip()
    if text in EXACT_NAMES:
        return f"{leading}{EXACT_NAMES[text]}{trailing}"
    if text in NAMES:
        return f"{leading}{NAMES[text]}{trailing}"

    parenthetical = re.fullmatch(r"(.+?) \((.+)\)", text)
    if parenthetical:
        name = translate_simple_name(parenthetical.group(1)).strip()
        ingredient = translate_simple_name(parenthetical.group(2)).strip()
        return f"{leading}{name} (발견 재료: {ingredient}){trailing}"

    patterns = (
        (r"Dairy Type: (.+)", lambda m: f"사용 원유: {translate_list(m[1])}"),
        (r"Crop: (.+)", lambda m: f"작물: {translate_simple_name(m[1]).strip()}"),
        (r"Crop (.+)", lambda m: f"작물: {translate_simple_name(m[1]).strip()}"),
        (
            r"Herb: Fresh (.+?)(?: Herb)?",
            lambda m: f"허브: 신선한 {translate_simple_name(m[1]).strip()}",
        ),
        (r"Seed: (.+)", lambda m: f"씨앗: {translate_seed(m[1])}"),
        (r"(.+) Seeds", lambda m: f"{translate_simple_name(m[1]).strip()} 씨앗"),
        (r"(.+) Grains", lambda m: f"{translate_simple_name(m[1]).strip()} 낟알"),
        (r"(.+) Tree", lambda m: f"{translate_simple_name(m[1]).strip()}나무"),
        (r"(.+) Milk", lambda m: f"{translate_simple_name(m[1]).strip()} 우유"),
        (r"(.+) Juice", lambda m: f"{translate_simple_name(m[1]).strip()} 주스"),
        (
            r"Plants (.+)",
            lambda m: f"{translate_simple_name(m[1]).strip()}을(를) 심습니다",
        ),
        (
            r"(.+) Fruit Leaves",
            lambda m: f"{translate_simple_name(m[1]).strip()}나무 잎",
        ),
        (r"(.+) Leaves", lambda m: f"{translate_simple_name(m[1]).strip()}나무 잎"),
        (
            r"(.+) Fruit\s+Sapling",
            lambda m: f"{translate_simple_name(m[1]).strip()}나무 묘목",
        ),
        (r"(.+) Sapling", lambda m: f"{translate_simple_name(m[1]).strip()}나무 묘목"),
        (r"Aged (.+)", lambda m: f"숙성 {translate_simple_name(m[1]).strip()}"),
        (r"Raw (.+)", lambda m: f"익히지 않은 {translate_simple_name(m[1]).strip()}"),
        (r"Cooked (.+)", lambda m: f"익힌 {translate_simple_name(m[1]).strip()}"),
        (r"Chopped (.+)", lambda m: f"다진 {translate_simple_name(m[1]).strip()}"),
        (r"Ground (.+)", lambda m: f"간 {translate_simple_name(m[1]).strip()}"),
        (r"Minced (.+)", lambda m: f"곱게 다진 {translate_simple_name(m[1]).strip()}"),
        (r"Sliced (.+)", lambda m: f"얇게 썬 {translate_simple_name(m[1]).strip()}"),
        (r"(.+) Wedge", lambda m: f"{translate_simple_name(m[1]).strip()} 조각"),
        (r"(.+) Slice", lambda m: f"{translate_simple_name(m[1]).strip()} 조각"),
        (r"Pot of (.+)", lambda m: f"{translate_simple_name(m[1]).strip()} 냄비"),
        (r"Pan of (.+)", lambda m: f"{translate_simple_name(m[1]).strip()} 팬 요리"),
        (r"Bowl of (.+)", lambda m: f"{translate_simple_name(m[1]).strip()} 한 그릇"),
        (r"Cup of (.+)", lambda m: f"{translate_simple_name(m[1]).strip()} 한 컵"),
        (
            r"Pitcher of (.+)",
            lambda m: f"{translate_simple_name(m[1]).strip()} 한 피처",
        ),
        (
            r"(.+) on Delftware Plate",
            lambda m: f"델프트웨어 접시에 담은 {translate_simple_name(m[1]).strip()}",
        ),
        (
            r"(.+) on Holiday Plate",
            lambda m: f"축제용 접시에 담은 {translate_simple_name(m[1]).strip()}",
        ),
        (
            r"(.+) on Plain Plate",
            lambda m: f"일반 접시에 담은 {translate_simple_name(m[1]).strip()}",
        ),
    )
    for pattern, render in patterns:
        match = re.fullmatch(pattern, text)
        if match:
            return f"{leading}{render(match)}{trailing}"

    suffixes = {
        " Bread": " 빵",
        " Sandwich": " 샌드위치",
        " Stew": " 스튜",
        " Soup": " 수프",
        " Pie": " 파이",
        " Cake": " 케이크",
        " Cupcake": " 컵케이크",
        " Cheesecake": " 치즈케이크",
        " Muffin": " 머핀",
        " Cookie": " 쿠키",
        " Salad": " 샐러드",
        " Jam": " 잼",
        " Milk Bucket": " 우유 양동이",
    }
    for suffix, korean_suffix in suffixes.items():
        if text.endswith(suffix):
            stem = text[: -len(suffix)]
            return f"{leading}{translate_simple_name(stem).strip()}{korean_suffix}{trailing}"
    raise KeyError(source)


def translate_list(source: str) -> str:
    """쉼표로 나뉜 재료·원유 목록을 번역해요."""
    return ", ".join(
        translate_simple_name(part.strip()).strip() for part in source.split(",")
    )


def translate_seed(source: str) -> str:
    """씨앗 툴팁의 중복 Seeds 표기를 자연스럽게 정리해요."""
    for suffix in (" Seeds", " Seed", " Kernels", " Grains", " Clove"):
        if source.endswith(suffix):
            base = translate_simple_name(source[: -len(suffix)]).strip()
            noun = {
                " Kernels": "알",
                " Grains": "낟알",
                " Clove": "쪽",
            }.get(suffix, "씨앗")
            return f"{base} {noun}"
    return translate_simple_name(source).strip()


def translate_language_value(key: str, source: str) -> str:
    """현재 키의 문맥을 확인해 언어 값을 번역해요."""
    if source == "":
        return ""
    if source in EXACT_NAMES:
        return EXACT_NAMES[source]
    if key.startswith(("block.", "item.", "guide.")):
        return translate_simple_name(source)
    if key.startswith("tooltip.dairy."):
        return translate_simple_name(source)
    if key.startswith("tooltip.block.") or key.startswith("tooltip.item."):
        return translate_simple_name(source)
    if key.startswith("tooltip.herb.") or key.startswith("sounds."):
        return translate_simple_name(source)
    if key.startswith(("chat.", "container.", "creativeTab.")):
        return translate_simple_name(source)
    if (
        key.startswith("herbsandharvest.guide_book.")
        or key == "herbsandharvest.book.cover.title"
    ):
        return translate_simple_name(source)
    raise KeyError(f"{key}={source!r}")


def prepare() -> dict[str, object]:
    """현재 영어 원문과 가이드 원본을 작업 폴더에 기록해요."""
    jar = find_jar()
    english = read_language(jar)
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    (WORK_ROOT / "en_us.json").write_text(
        json.dumps(english, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with ZipFile(jar) as archive:
        books = sorted(
            name
            for name in archive.namelist()
            if name.startswith(BOOK_PREFIX) and name.endswith(".json")
        )
    report = {
        "family": FAMILY,
        "jar": jar.name,
        "jar_size": jar.stat().st_size,
        "jar_mtime_ns": jar.stat().st_mtime_ns,
        "english_keys": len(english),
        "bundled_korean_keys": 0,
        "book_files": len(books),
        "status": "prepared",
    }
    (WORK_ROOT / "inventory.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def build_language() -> dict[str, object]:
    """865개 영어 값을 모두 현재 기준으로 번역해요."""
    english = read_language(find_jar())
    korean = {}
    errors = []
    for key, source in english.items():
        try:
            korean[key] = translate_language_value(key, source)
        except (KeyError, RecursionError) as exc:
            errors.append(f"{key}={source!r}: {exc}")
    if errors:
        report = {"translated": len(korean), "errors": errors, "status": "incomplete"}
        (WORK_ROOT / "language_build.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return report
    for path in (WORK_ROOT / "ko_kr.json", LANG_OUTPUT):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(korean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    report = {"translated": len(korean), "errors": [], "status": "complete"}
    (WORK_ROOT / "language_build.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def read_book_files(jar: Path) -> dict[str, str]:
    """현재 JAR의 자체 가이드 JSON 원문을 경로별로 읽어요."""
    with ZipFile(jar) as archive:
        names = sorted(
            name
            for name in archive.namelist()
            if name.startswith(BOOK_PREFIX) and name.endswith(".json")
        )
        return {name: archive.read(name).decode("utf-8") for name in names}


def normalize_book_layout(raw: str) -> str:
    """의미 없는 줄 끝 공백과 여분의 EOF 빈 줄만 정리해요."""
    lines = raw.replace("\r\n", "\n").splitlines()
    return "\n".join(line.rstrip(" \t") for line in lines).rstrip("\n") + "\n"


def build_books() -> dict[str, object]:
    """가이드의 직접 표시 문구만 바꾸고 나머지 원문 구조는 보존해요."""
    sources = read_book_files(find_jar())
    rendered = {}
    visible_sources = []
    errors = []
    translated_occurrences = 0

    for name, raw in sources.items():

        def replace(match: re.Match[str]) -> str:
            nonlocal translated_occurrences
            source = json.loads(match.group(2))
            visible_sources.append(source)
            if not source.strip() or source == "herbsandharvest.book.cover.subtitle":
                return match.group(0)
            translated = BOOK_TEXT.get(source)
            if translated is None:
                errors.append(f"{name}: {source!r}")
                return match.group(0)
            translated_occurrences += 1
            return f"{match.group(1)}{json.dumps(translated, ensure_ascii=False)}"

        rendered[name] = normalize_book_layout(VISIBLE_BOOK_FIELD.sub(replace, raw))

    source_set = {
        source
        for source in visible_sources
        if source.strip() and source != "herbsandharvest.book.cover.subtitle"
    }
    unused = sorted(set(BOOK_TEXT) - source_set)
    if unused:
        errors.extend(f"사용하지 않은 가이드 원문: {source!r}" for source in unused)

    if not errors:
        for name, raw in rendered.items():
            relative = Path(name).relative_to("assets/herbsandharvest")
            path = OUTPUT_ROOT / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw.encode("utf-8"))

    report = {
        "book_files": len(sources),
        "visible_occurrences": len(visible_sources),
        "visible_unique_sources": len(set(visible_sources)),
        "translated_occurrences": translated_occurrences,
        "translated_unique_sources": len(source_set),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    (WORK_ROOT / "book_build.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def walk_json(value: object, path: str = "") -> list[tuple[str, str, object]]:
    """JSON 안의 모든 값을 키와 경로와 함께 펼쳐요."""
    rows = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            rows.append((key, child_path, child))
            rows.extend(walk_json(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(walk_json(child, f"{path}[{index}]"))
    return rows


def audit() -> tuple[dict[str, object], list[str]]:
    """JAR 데이터와 FTB Quests·KubeJS의 별도 표시 문구를 감사해요."""
    instance = resolve_source_root()
    jar = find_jar()
    errors = []
    data_counts: defaultdict[str, int] = defaultdict(int)
    advancement_displays = []
    visible_data_fields = []
    invalid_data_json = []
    with ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            if not name.startswith("data/herbsandharvest/") or not name.endswith(
                ".json"
            ):
                continue
            parts = name.split("/")
            if len(parts) >= 3:
                data_counts[parts[2]] += 1
            try:
                value = json.loads(archive.read(name))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                invalid_data_json.append(f"{name}: {exc}")
                continue
            if "/advancement/" in name and isinstance(value, dict):
                display = value.get("display")
                if display is not None:
                    advancement_displays.append({"path": name, "display": display})
            for key, path, child in walk_json(value):
                if key in VISIBLE_DATA_KEYS:
                    visible_data_fields.append(
                        {"file": name, "path": path, "value": child}
                    )

    references = {"ftbquests": [], "kubejs": [], "read_errors": []}
    for label, base in (
        ("ftbquests", instance / "config/ftbquests"),
        ("kubejs", instance / "kubejs"),
    ):
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {
                ".js",
                ".json",
                ".snbt",
                ".toml",
                ".txt",
            }:
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError) as exc:
                references["read_errors"].append(f"{path}: {exc}")
                continue
            namespace_count = text.count("herbsandharvest:")
            visible_candidates = []
            name_candidates = []
            for line_number, line in enumerate(text.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("//"):
                    continue
                if re.search(
                    r"Mama['’]s Herbs|\bHerbs\s+(?:and|&)\s+Harvest\b",
                    line,
                    re.IGNORECASE,
                ):
                    name_candidates.append(line_number)
                if "herbsandharvest:" in line and any(
                    marker in line
                    for marker in (
                        "custom_name",
                        "customName",
                        "displayName",
                        "title",
                        "tooltip",
                        "lore",
                    )
                ):
                    visible_candidates.append(line_number)
            if namespace_count or name_candidates:
                references[label].append(
                    {
                        "path": path.relative_to(instance).as_posix(),
                        "namespace_occurrences": namespace_count,
                        "direct_name_candidate_lines": name_candidates,
                        "visible_namespace_candidate_lines": visible_candidates,
                    }
                )

    if invalid_data_json:
        errors.extend(invalid_data_json)
    if advancement_displays:
        errors.append(f"표시형 발전 과제가 있어요: {advancement_displays}")
    if visible_data_fields:
        errors.append(f"데이터 파일에 직접 표시 문구가 있어요: {visible_data_fields}")
    errors.extend(str(value) for value in references["read_errors"])
    for label in ("ftbquests", "kubejs"):
        for row in references[label]:
            if row["direct_name_candidate_lines"]:
                errors.append(f"{label}에 직접 모드명 후보가 있어요: {row}")
            if row["visible_namespace_candidate_lines"]:
                errors.append(f"{label}에 직접 표시 후보가 있어요: {row}")

    report = {
        "family": FAMILY,
        "jar": jar.name,
        "data_json_files": sum(data_counts.values()),
        "data_counts": dict(sorted(data_counts.items())),
        "advancement_files": data_counts["advancement"],
        "advancement_displays": advancement_displays,
        "recipe_files": data_counts["recipe"],
        "visible_data_fields": visible_data_fields,
        "references": references,
        "ftbquests_display_work": "not_present",
        "kubejs_display_work": "ids_only",
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    (WORK_ROOT / "surface_audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report, errors


def preserved_errors(label: str, source: str, target: str) -> list[str]:
    """자리표시자·서식·숫자·줄바꿈·URL 보존 여부를 확인해요."""
    errors = []
    for name, pattern in (
        ("자리표시자", PLACEHOLDER),
        ("서식 코드", FORMAT_CODE),
        ("URL", URL),
    ):
        if pattern.findall(source) != pattern.findall(target):
            errors.append(
                f"{label} {name} 불일치: "
                f"{pattern.findall(source)} != {pattern.findall(target)}"
            )
    source_numbers = Counter(NUMBER.findall(source))
    target_numbers = Counter(NUMBER.findall(target))
    missing_numbers = source_numbers - target_numbers
    if missing_numbers:
        errors.append(
            f"{label} 원문 숫자 누락: {dict(missing_numbers)}; "
            f"target={NUMBER.findall(target)}"
        )
    if source.count("\n") != target.count("\n"):
        errors.append(
            f"{label} 줄바꿈 수 불일치: "
            f"{source.count(chr(10))} != {target.count(chr(10))}"
        )
    return errors


def load_json_without_duplicates(path: Path) -> tuple[object | None, list[str]]:
    """JSON을 읽으며 같은 객체 안의 중복 키를 찾아요."""
    duplicates = []

    def object_hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        value = {}
        for key, child in pairs:
            if key in value:
                duplicates.append(key)
            value[key] = child
        return value

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=object_hook
        )
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"{path}: {exc}"]
    return value, [f"{path} 중복 키: {key}" for key in duplicates]


def verify_language() -> tuple[dict[str, object], list[str]]:
    """865개 언어 키의 구조·확정값·보존 요소·영문 잔여를 검증해요."""
    errors = []
    english = read_language(find_jar())
    work_value, work_errors = load_json_without_duplicates(WORK_ROOT / "ko_kr.json")
    output_value, output_errors = load_json_without_duplicates(LANG_OUTPUT)
    errors.extend(work_errors + output_errors)
    if not isinstance(work_value, dict) or not isinstance(output_value, dict):
        report = {"errors": errors, "status": "incomplete"}
        return report, errors
    expected = {
        key: translate_language_value(key, source) for key, source in english.items()
    }
    if list(english) != list(work_value) or list(english) != list(output_value):
        errors.append("언어 키 또는 순서가 현재 영어 원문과 달라요")
    if work_value != output_value or output_value != expected:
        errors.append("작업본·산출물·확정 번역값이 서로 달라요")

    intentional_same = {"creativeTab.hh"}
    allowed_latin = {"Herbs", "and", "Harvest"}
    untranslated = []
    latin_residue = {}
    collisions: defaultdict[str, list[str]] = defaultdict(list)
    for key, source in english.items():
        target = output_value.get(key)
        if not isinstance(target, str):
            errors.append(f"문자열이 아닌 언어 값이 있어요: {key}")
            continue
        errors.extend(preserved_errors(key, source, target))
        if source == target and source and key not in intentional_same:
            untranslated.append(key)
        residue = sorted(set(LATIN_WORD.findall(target)) - allowed_latin)
        if residue:
            latin_residue[key] = residue
        if key.startswith(("block.", "item.")) and not key.endswith(".tooltip"):
            collisions[target].append(key)
    allowed_collision_sources = {
        frozenset({"Peanut", "Peanuts"}),
        frozenset({"Cooked Sausage", "Cooked Sausages"}),
    }
    unexpected_collisions = {}
    for target, keys in collisions.items():
        sources = frozenset(english[key] for key in keys)
        if len(sources) > 1 and sources not in allowed_collision_sources:
            unexpected_collisions[target] = keys
    if untranslated:
        errors.append(f"영어와 같은 번역값이 남았어요: {untranslated}")
    if latin_residue:
        errors.append(f"허용하지 않은 영문 잔여가 있어요: {latin_residue}")
    if unexpected_collisions:
        errors.append(f"서로 다른 검색명이 충돌해요: {unexpected_collisions}")
    report = {
        "keys": len(output_value),
        "expected_keys": EXPECTED_KEYS,
        "untranslated_candidates": untranslated,
        "latin_residue": latin_residue,
        "allowed_plural_collisions": 2,
        "unexpected_name_collisions": unexpected_collisions,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def visible_fields(raw: str) -> list[tuple[str, str]]:
    """가이드 원문에서 직접 표시 필드와 값을 순서대로 읽어요."""
    rows = []
    for match in VISIBLE_BOOK_FIELD.finditer(raw):
        field = re.search(r'"(summary|literal_text)"', match.group(1))
        if field is None:
            raise ValueError("직접 표시 필드 이름을 읽지 못했어요")
        rows.append((field.group(1), json.loads(match.group(2))))
    return rows


def normalized_book_structure(raw: str) -> str:
    """직접 표시 값만 표식으로 바꿔 나머지 바이트 구조를 비교해요."""
    replaced = VISIBLE_BOOK_FIELD.sub(
        lambda match: f'{match.group(1)}"__VISIBLE__"', raw
    )
    return normalize_book_layout(replaced)


def verify_books() -> tuple[dict[str, object], list[str]]:
    """가이드 16개 파일의 경로·구조·표시 문구·보존 요소를 검증해요."""
    errors = []
    sources = read_book_files(find_jar())
    expected_paths = {
        (OUTPUT_ROOT / Path(name).relative_to("assets/herbsandharvest"))
        for name in sources
    }
    actual_paths = set((OUTPUT_ROOT / "books").rglob("*.json"))
    if expected_paths != actual_paths:
        errors.append(
            "가이드 파일 경로가 달라요: "
            f"missing={sorted(str(path) for path in expected_paths - actual_paths)}, "
            f"extra={sorted(str(path) for path in actual_paths - expected_paths)}"
        )

    translated_occurrences = 0
    all_source_values = []
    source_invalid = []
    output_invalid = []
    allowed_latin = {
        "Herbs",
        "and",
        "Harvest",
        "Mama",
        "MerryMaking",
        "Happy",
        "Hallows",
        "Minis",
        "Minecraft",
        "GUI",
        "Shift",
        "Discord",
        "https",
        "discord",
        "gg",
        "QWyQ",
        "fkUr",
    }
    latin_residue = {}
    for name, source_raw in sources.items():
        output_path = OUTPUT_ROOT / Path(name).relative_to("assets/herbsandharvest")
        if not output_path.is_file():
            continue
        output_raw = output_path.read_bytes().decode("utf-8")
        try:
            json.loads(source_raw)
        except json.JSONDecodeError:
            source_invalid.append(name)
        try:
            json.loads(output_raw)
        except json.JSONDecodeError:
            output_invalid.append(name)
        if normalized_book_structure(source_raw) != normalized_book_structure(
            output_raw
        ):
            errors.append(f"직접 표시 문구 밖의 가이드 구조가 바뀌었어요: {name}")
        source_rows = visible_fields(source_raw)
        output_rows = visible_fields(output_raw)
        if len(source_rows) != len(output_rows):
            errors.append(f"직접 표시 필드 수가 달라요: {name}")
            continue
        for index, ((source_field, source), (target_field, target)) in enumerate(
            zip(source_rows, output_rows, strict=True)
        ):
            all_source_values.append(source)
            label = f"{name}#{index}"
            if source_field != target_field:
                errors.append(f"직접 표시 필드 종류가 달라요: {label}")
            if not source.strip() or source == "herbsandharvest.book.cover.subtitle":
                expected = source
            else:
                expected = BOOK_TEXT.get(source)
                translated_occurrences += 1
            if expected is None:
                errors.append(f"가이드 번역표에 원문이 없어요: {label} {source!r}")
                continue
            if target != expected:
                errors.append(f"가이드 확정 번역값이 달라요: {label}")
            errors.extend(preserved_errors(label, source, target))
            if source != target:
                residue = sorted(set(LATIN_WORD.findall(target)) - allowed_latin)
                if residue:
                    latin_residue[label] = residue
    if source_invalid != output_invalid:
        errors.append(
            f"가이드 JSON 문법 상태가 달라요: {source_invalid} != {output_invalid}"
        )
    expected_invalid = [
        "assets/herbsandharvest/books/chapters/grapes.json",
        "assets/herbsandharvest/books/chapters/herbs.json",
    ]
    if source_invalid != expected_invalid:
        errors.append(f"원본의 알려진 비표준 JSON 범위가 달라요: {source_invalid}")
    if latin_residue:
        errors.append(f"가이드에 허용하지 않은 영문 잔여가 있어요: {latin_residue}")
    source_set = {
        source
        for source in all_source_values
        if source.strip() and source != "herbsandharvest.book.cover.subtitle"
    }
    if source_set != set(BOOK_TEXT):
        errors.append("가이드 번역표와 현재 직접 표시 원문 집합이 달라요")
    report = {
        "files": len(sources),
        "visible_occurrences": len(all_source_values),
        "visible_unique_sources": len(set(all_source_values)),
        "translated_occurrences": translated_occurrences,
        "translated_unique_sources": len(source_set),
        "source_invalid_json_files": source_invalid,
        "output_invalid_json_files": output_invalid,
        "non_visible_structure_preserved": not any(
            "구조가 바뀌었어요" in error for error in errors
        ),
        "latin_residue": latin_residue,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    return report, errors


def verify() -> tuple[dict[str, object], list[str]]:
    """언어·가이드·전체 표시 표면을 함께 검증해요."""
    language, language_errors = verify_language()
    books, book_errors = verify_books()
    surface, surface_errors = audit()
    errors = language_errors + book_errors + surface_errors
    report = {
        "family": FAMILY,
        "language": language,
        "books": books,
        "surface_audit": surface["status"],
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    (WORK_ROOT / "family_validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    deployment_path = WORK_ROOT / "deployment_report.json"
    deployment = (
        json.loads(deployment_path.read_text(encoding="utf-8"))
        if deployment_path.is_file()
        else None
    )
    translation_report = {
        "family": FAMILY,
        "reviewed_language_keys": language.get("keys", 0),
        "existing_korean_reused": 0,
        "new_language_translations": language.get("keys", 0),
        "guide_direct_translations": books.get("translated_occurrences", 0),
        "ftbquests_work": "not_present",
        "kubejs_work": "ids_only",
        "status": report["status"],
    }
    (WORK_ROOT / "translation_report.json").write_text(
        json.dumps(translation_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    completion = {
        "family": FAMILY,
        "language_keys": language.get("keys", 0),
        "guide_direct_occurrences": books.get("translated_occurrences", 0),
        "surface_audit": surface["status"],
        "family_validation": report["status"],
        "deployment": deployment,
        "errors": errors,
        "status": (
            "complete"
            if not errors
            and (
                deployment is None or deployment.get("status") == "applied_and_verified"
            )
            else "incomplete"
        ),
    }
    (WORK_ROOT / "family_completion.json").write_text(
        json.dumps(completion, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report, errors


def deployment_paths() -> set[str]:
    """이 모드가 실제 인스턴스에 적용할 정확한 상대 경로를 반환해요."""
    paths = {"resourcepacks/ATM10_Korean/assets/herbsandharvest/lang/ko_kr.json"}
    paths.update(
        f"resourcepacks/ATM10_Korean/{name}" for name in read_book_files(find_jar())
    )
    return paths


def record_deployment(manifest_path: Path) -> tuple[dict[str, object], list[str]]:
    """적용 매니페스트의 대상·백업·해시 결과를 작업 기록에 연결해요."""
    errors = []
    manifest_path = manifest_path.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "applied_and_verified":
        errors.append("적용 매니페스트 상태가 완료가 아니에요")
    expected = deployment_paths()
    targets = manifest.get("targets", [])
    if not isinstance(targets, list) or not targets:
        errors.append("적용 대상 기록이 없어요")
        targets = []
    summaries = []
    for target in targets:
        records = {
            row.get("relative_path"): row
            for row in target.get("files", [])
            if isinstance(row, dict)
        }
        missing = sorted(expected - set(records))
        extra = sorted(set(records) - expected)
        if missing or extra:
            errors.append(f"적용 경로가 달라요: missing={missing}, extra={extra}")
        hash_errors = sorted(
            path
            for path in expected & set(records)
            if records[path].get("source_sha256") != records[path].get("after_sha256")
        )
        if hash_errors:
            errors.append(f"적용 후 해시가 달라요: {hash_errors}")
        if target.get("status") != "applied_and_verified":
            errors.append(
                f"대상 적용 상태가 완료가 아니에요: {target.get('target_root')}"
            )
        if target.get("unexpected_changes"):
            errors.append(f"예상 밖 적용 변경이 있어요: {target['unexpected_changes']}")
        summaries.append(
            {
                "target_type": target.get("target_type"),
                "target_root": target.get("target_root"),
                "changed_paths": target.get("changed_paths", []),
                "unexpected_changes": target.get("unexpected_changes", []),
                "hash_verified_paths": sorted(expected - set(hash_errors)),
            }
        )
    try:
        manifest_name = manifest_path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        manifest_name = str(manifest_path)
    report = {
        "status": "applied_and_verified" if not errors else "incomplete",
        "backup_manifest": manifest_name,
        "expected_paths": sorted(expected),
        "targets": summaries,
        "errors": errors,
    }
    (WORK_ROOT / "deployment_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    verification, verification_errors = verify()
    return {
        "deployment": report,
        "verification": verification["status"],
        "status": (
            "complete" if not errors and not verification_errors else "incomplete"
        ),
    }, errors + verification_errors


def main() -> int:
    """명령행 진입점이에요."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "prepare",
            "build-language",
            "build-books",
            "build-all",
            "audit",
            "verify",
            "record-deployment",
            "all",
        ),
    )
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare()
    elif args.command == "build-language":
        result = build_language()
    elif args.command == "build-books":
        result = build_books()
    elif args.command == "build-all":
        language = build_language()
        books = build_books()
        result = {
            "language": language,
            "books": books,
            "status": (
                "complete"
                if language["status"] == books["status"] == "complete"
                else "incomplete"
            ),
        }
    elif args.command == "audit":
        result, _ = audit()
    elif args.command == "verify":
        result, _ = verify()
    elif args.command == "record-deployment":
        if args.manifest is None:
            parser.error("record-deployment에는 --manifest가 필요해요")
        result, _ = record_deployment(args.manifest)
    else:
        prepared = prepare()
        language = build_language()
        books = build_books()
        surface, surface_errors = audit()
        verification, verification_errors = verify()
        result = {
            "prepare": prepared,
            "language": language,
            "books": books,
            "audit": surface,
            "verify": verification,
            "status": (
                "complete"
                if not surface_errors and not verification_errors
                else "incomplete"
            ),
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in {"prepared", "complete"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
