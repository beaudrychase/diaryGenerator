from datetime import date, timedelta

from diary_generator.classes.doc import Doc
from diary_generator.classes.linear_links import LinearLinks

sunday = date.fromisoformat("2021-08-01")
thisweek = f"Week {sunday.strftime('%U, %Y')}"

lastSunday = sunday + timedelta(days=-7)
lastweek = f"Week {lastSunday.strftime('%U, %Y')}"


def create_example_diary(output_file_name: str):
    doc = Doc("templates/pagetemplate.pdf")

    # links between top level weekly pages
    weekly_links = LinearLinks(
        horizontal_anchor="left",
        horizontal_anchor_offset=10,
        vertical_achor="top",
        vertical_achor_offset=110,
    )

    # links down to daily goal pages from weekly pages
    daily_goals_links = LinearLinks(
        horizontal_anchor="right",
        horizontal_anchor_offset=-10,
        vertical_achor="top",
        vertical_achor_offset=110,
    )

    # Build top level weekly pages, with templates, and give them their outbound links
    # Note the daily goal pages do not exist yet, but that's ok!
    weekly_retro = doc.add_page(
        title=f"Retro for {lastweek}",
        base_pdf_name="templates/weeklyRetroTemplate.pdf",
        toc_level=1,
    )
    weekly_retro.add_links(weekly_links, daily_goals_links)

    weekly_planner = doc.add_page(
        title=f"Planner for {thisweek}",
        base_pdf_name="templates/weeklyPlannerTemplate.pdf",
        toc_level=1,
    )
    weekly_planner.add_links(weekly_links, daily_goals_links)

    weekly_dump_1 = doc.add_page(title=f"Dump 1 for {thisweek}", toc_level=1)
    weekly_dump_1.add_links(weekly_links, daily_goals_links)

    weekly_dump_2 = doc.add_page(title=f"Dump 2 for {thisweek}", toc_level=1)
    weekly_dump_2.add_links(weekly_links, daily_goals_links)

    weekly_goals = doc.add_page(
        title=f"Goals for {thisweek}",
        base_pdf_name="templates/weeklyGoalsTemplate.pdf",
        toc_level=1,
    )
    weekly_goals.add_links(weekly_links, daily_goals_links)

    # Link top level pages to each other
    weekly_links.add_link(weekly_retro, "R")
    weekly_links.add_link(weekly_planner, "P")
    weekly_links.add_link(weekly_dump_1, "D1")
    weekly_links.add_link(weekly_dump_2, "D2")
    weekly_links.add_link(weekly_goals, "G")

    # Build one goals page and 9 notes pages for each day of the week
    days = []
    for x in range(1, 6):
        day_of_the_week_date = sunday + timedelta(days=x)
        days.append(day_of_the_week_date)

    for day_date in days:
        day = day_date.strftime("%a %-d %b %Y")
        # Each set of daily notes has links to each other
        daily_notes_links = LinearLinks(
            horizontal_anchor="right",
            horizontal_anchor_offset=-5,
            vertical_achor="bottom",
            vertical_achor_offset=-500,
            flow_direction="down",
        )

        # First page is a goals page.
        # Each of the daily pages links back up to the weekly pages, to the other days in the week, and to each other on this day
        daily_goals = doc.add_page(
            title=f"{day}: Daily Goals",
            base_pdf_name="templates/dailyGoalsTemplate.pdf",
            toc_level=1,
        )
        daily_goals.add_links(weekly_links, daily_goals_links, daily_notes_links)

        # This gets linked "down to" from the weekly pages above
        daily_goals_links.add_link(daily_goals, f"{day[0]}")

        # It is also linked by each other page on this day
        daily_notes_links.add_link(daily_goals, "G")

        # Add index page
        daily_note = doc.add_page(title=f"{day}: Notes Index")
        daily_note.add_links(weekly_links, daily_goals_links, daily_notes_links)

        daily_notes_links.add_link(daily_note, f"I")

        for pageno in range(2, 10):
            # These are the individual note pages for a given day
            daily_note = doc.add_page(title=f"{day}: Notes {pageno}")
            daily_note.add_links(weekly_links, daily_goals_links, daily_notes_links)
            daily_notes_links.add_link(daily_note, f"{pageno}")

    doc.render(output_file_name)
