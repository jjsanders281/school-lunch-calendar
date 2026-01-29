#!/usr/bin/env python3
"""
Fetch Bay Middle School lunch menus and generate an iCal file.
"""

import requests
from datetime import datetime, timedelta
from icalendar import Calendar, Event
from pathlib import Path
import hashlib
import json

# API Configuration
ORG_ID = "1229"
MENU_ID = "109815"
BASE_URL = "https://menus.healthepro.com/api"

# Output configuration
OUTPUT_DIR = Path(__file__).parent / "docs"
OUTPUT_FILE = OUTPUT_DIR / "lunch.ics"


def get_published_months():
    """Get list of months that have published menu data."""
    url = f"{BASE_URL}/organizations/{ORG_ID}/menus/{MENU_ID}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data.get("data", {}).get("published_months", [])


def get_menu_for_month(year: int, month: int):
    """Fetch menu data for a specific month using date_overwrites endpoint."""
    url = f"{BASE_URL}/organizations/{ORG_ID}/menus/{MENU_ID}/year/{year}/month/{month}/date_overwrites"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def parse_menu_data(raw_data):
    """
    Parse the raw API data into a structured format.
    Returns dict: {date_str: {"entree": str, "sides": [str], "is_off": bool, "off_reason": str}}
    """
    menus = {}

    for day_data in raw_data.get("data", []):
        date_str = day_data.get("day")
        if not date_str:
            continue

        # Parse the setting JSON
        setting_str = day_data.get("setting", "{}")
        try:
            setting = json.loads(setting_str)
        except json.JSONDecodeError:
            continue

        # Check if it's a day off (holiday, break, etc.)
        days_off = setting.get("days_off", {})
        # days_off can be a dict or empty list
        if isinstance(days_off, dict) and days_off.get("status") == 1:
            menus[date_str] = {
                "is_off": True,
                "off_reason": days_off.get("description", "No School"),
                "entree": None,
                "sides": [],
                "vegetables": [],
                "fruit": [],
                "milk": []
            }
            continue

        # Parse current_display for menu items
        current_display = setting.get("current_display", [])
        if not current_display:
            continue

        menu_entry = {
            "is_off": False,
            "off_reason": None,
            "entree": None,
            "sides": [],
            "vegetables": [],
            "fruit": [],
            "milk": []
        }

        current_category = None
        in_with_section = False

        for item in current_display:
            item_type = item.get("type")
            item_name = item.get("name", "")

            if item_type == "category":
                current_category = item_name.lower()
                in_with_section = False
            elif item_type == "text" and "with" in item_name.lower():
                in_with_section = True
            elif item_type == "recipe":
                # Categorize the recipe
                if current_category and "entree" in current_category:
                    if not in_with_section and menu_entry["entree"] is None:
                        menu_entry["entree"] = item_name
                    else:
                        menu_entry["sides"].append(item_name)
                elif current_category and "vegetable" in current_category:
                    menu_entry["vegetables"].append(item_name)
                elif current_category and "fruit" in current_category:
                    menu_entry["fruit"].append(item_name)
                elif current_category and "milk" in current_category:
                    menu_entry["milk"].append(item_name)
                else:
                    menu_entry["sides"].append(item_name)

        # Only add if we have an entree
        if menu_entry["entree"]:
            menus[date_str] = menu_entry

    return menus


def create_calendar(menus):
    """Create an iCal calendar from the parsed menu data."""
    cal = Calendar()
    cal.add("prodid", "-//Bay Middle School Lunch Menu//")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")
    cal.add("x-wr-calname", "Bay MS Lunch")
    cal.add("x-wr-timezone", "America/New_York")

    for date_str, meal_data in sorted(menus.items()):
        # Parse date
        try:
            event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        # Skip days off (no school)
        if meal_data.get("is_off"):
            continue

        # Skip if no entree
        if not meal_data.get("entree"):
            continue

        # Create event
        event = Event()

        # Title is the main entree
        title = meal_data["entree"]
        event.add("summary", f"{title}")

        # Description has full details
        description_parts = []
        description_parts.append(f"Entree: {meal_data['entree']}")

        if meal_data["sides"]:
            description_parts.append(f"With: {', '.join(meal_data['sides'])}")
        if meal_data["vegetables"]:
            description_parts.append(f"Vegetables: {', '.join(meal_data['vegetables'])}")
        if meal_data["fruit"]:
            description_parts.append(f"Fruit: {', '.join(meal_data['fruit'])}")
        if meal_data["milk"]:
            description_parts.append(f"Milk: {', '.join(meal_data['milk'])}")

        event.add("description", "\n".join(description_parts))

        # All-day event
        event.add("dtstart", event_date)
        event.add("dtend", event_date + timedelta(days=1))

        # Generate unique ID based on date and content
        uid_source = f"{date_str}-{title}"
        uid = hashlib.md5(uid_source.encode()).hexdigest()
        event.add("uid", f"{uid}@bayms-lunch")

        # Timestamp
        event.add("dtstamp", datetime.now())

        cal.add_component(event)

    return cal


def main():
    print("Fetching Bay Middle School lunch menus...")

    # Get available months
    published_months = get_published_months()
    print(f"Published months: {published_months}")

    if not published_months:
        print("No published months found!")
        return

    # Fetch all published months
    all_menus = {}
    for month_str in published_months:
        try:
            year, month, _ = month_str.split("-")
            year, month = int(year), int(month)
            print(f"Fetching {year}-{month:02d}...")

            raw_data = get_menu_for_month(year, month)
            month_menus = parse_menu_data(raw_data)
            all_menus.update(month_menus)
            print(f"  Found {len(month_menus)} days with menus")

        except Exception as e:
            print(f"Error fetching {month_str}: {e}")

    # Count actual menu days (not days off)
    menu_days = sum(1 for m in all_menus.values() if not m.get("is_off") and m.get("entree"))
    print(f"Total days with lunch menus: {menu_days}")

    # Create calendar
    cal = create_calendar(all_menus)

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Write calendar file
    with open(OUTPUT_FILE, "wb") as f:
        f.write(cal.to_ical())

    print(f"Calendar saved to {OUTPUT_FILE}")
    print(f"Total events: {len([c for c in cal.walk() if c.name == 'VEVENT'])}")


if __name__ == "__main__":
    main()
