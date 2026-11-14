#!/usr/bin/env python3

import argparse
from pathlib import Path
from datetime import datetime, date
from icalendar import Calendar


def format_date(value):
    """Форматирует дату или дату со временем."""
    if isinstance(value, datetime):
        return value.strftime("%d.%m.%Y %H:%M")

    if isinstance(value, date):
        return value.strftime("%d.%m.%Y")

    return str(value)


def parse_event(event):
    """Извлекает информацию о событии."""

    summary = str(event.get("SUMMARY", "Без названия"))

    start = event.get("DTSTART")
    end = event.get("DTEND")

    start = start.dt if start else None
    end = end.dt if end else None

    description = str(event.get("DESCRIPTION", "")).strip()
    location = str(event.get("LOCATION", "")).strip()
    organizer = str(event.get("ORGANIZER", "")).strip()

    return {
        "title": summary,
        "start": start,
        "end": end,
        "description": description,
        "location": location,
        "organizer": organizer,
    }


def load_events(path):
    """Загружает события из ICS-файла."""

    with path.open("rb") as file:
        calendar = Calendar.from_ical(file.read())

    events = []

    for component in calendar.walk():
        if component.name != "VEVENT":
            continue

        events.append(parse_event(component))

    events.sort(
        key=lambda event: (
            event["start"] is None,
            event["start"] or date.min,
        )
    )

    return events


def to_markdown(events):
    """Преобразует события в Markdown."""

    lines = ["# 📅 Календарь событий", ""]

    if not events:
        return "# 📅 Календарь событий\n\nСобытий не найдено.\n"

    for event in events:
        lines.append(f"## {event['title']}")
        lines.append("")

        if event["start"]:
            lines.append(f"**Начало:** {format_date(event['start'])}")

        if event["end"]:
            lines.append(f"**Окончание:** {format_date(event['end'])}")

        if event["location"]:
            lines.append(f"**Место:** {event['location']}")

        if event["organizer"]:
            lines.append(f"**Организатор:** {event['organizer']}")

        if event["description"]:
            lines.append("")
            lines.append("### Описание")
            lines.append("")
            lines.append(event["description"])

        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def to_text(events):
    """Преобразует события в обычный текст."""

    lines = ["КАЛЕНДАРЬ СОБЫТИЙ", "=" * 40, ""]

    for index, event in enumerate(events, 1):
        lines.append(f"{index}. {event['title']}")

        if event["start"]:
            lines.append(f"   Начало: {format_date(event['start'])}")

        if event["end"]:
            lines.append(f"   Окончание: {format_date(event['end'])}")

        if event["location"]:
            lines.append(f"   Место: {event['location']}")

        if event["organizer"]:
            lines.append(f"   Организатор: {event['organizer']}")

        if event["description"]:
            lines.append(f"   Описание: {event['description']}")

        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Конвертер календарей ICS в Markdown или TXT."
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Путь к ICS-файлу",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Путь к выходному файлу",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["md", "txt"],
        default="md",
        help="Формат результата: md или txt (по умолчанию md)",
    )

    args = parser.parse_args()

    if not args.input.exists():
        parser.error(f"Файл не найден: {args.input}")

    if args.input.suffix.lower() != ".ics":
        parser.error("Входной файл должен иметь расширение .ics")

    output = args.output or args.input.with_suffix(f".{args.format}")

    if output.resolve() == args.input.resolve():
        parser.error("Входной и выходной файлы не должны совпадать")

    events = load_events(args.input)

    if args.format == "md":
        result = to_markdown(events)
    else:
        result = to_text(events)

    output.write_text(result, encoding="utf-8")

    print(f"✅ Готово!")
    print(f"📅 Событий: {len(events)}")
    print(f"📄 Результат: {output.resolve()}")


if __name__ == "__main__":
    main()
