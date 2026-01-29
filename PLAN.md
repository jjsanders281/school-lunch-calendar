# School Lunch Calendar Sync - Project Plan

## Goal
Automatically sync Bay Middle School lunch menus to your shared iCloud calendar using GitHub Actions.

## How It Will Work
1. A Python script runs daily via GitHub Actions (free)
2. It fetches the current month's menu from the school's public API
3. It generates an `.ics` calendar file
4. GitHub Pages hosts the `.ics` file at a public URL
5. You subscribe to that URL in iCloud Calendar (one-time setup)
6. iCloud automatically refreshes the calendar periodically

## Architecture
```
School Menu API  →  GitHub Actions (daily)  →  Python Script  →  .ics file
                                                                      ↓
                                                              GitHub Pages
                                                                      ↓
                                                    iCloud Calendar Subscription
```

---

## Project Steps

### Phase 1: Local Development & Testing
- [ ] **Step 1:** Create project folder structure
- [ ] **Step 2:** Write Python script to fetch menu data from API
- [ ] **Step 3:** Write code to generate .ics calendar file
- [ ] **Step 4:** Test locally - verify .ics file works in Calendar app

### Phase 2: GitHub Repository Setup
- [ ] **Step 5:** Create GitHub account (if needed)
- [ ] **Step 6:** Create new GitHub repository
- [ ] **Step 7:** Push code to repository
- [ ] **Step 8:** Enable GitHub Pages to host the .ics file

### Phase 3: Automation with GitHub Actions
- [ ] **Step 9:** Create GitHub Actions workflow file
- [ ] **Step 10:** Configure workflow to run on schedule (daily)
- [ ] **Step 11:** Test the automated workflow

### Phase 4: Calendar Subscription
- [ ] **Step 12:** Get the public URL of your hosted .ics file
- [ ] **Step 13:** Subscribe to the calendar in iCloud
- [ ] **Step 14:** Verify sync works on all devices

---

## Technical Details

### API Endpoints Used
- Menu metadata: `https://menus.healthepro.com/api/organizations/1229/menus/109815`
- Recipe data: `https://menus.healthepro.com/api/organizations/1229/menus/109815/start_date/{YYYY-MM-DD}/end_date/{YYYY-MM-DD}/recipes/`

### Files We'll Create
```
school-lunch-calendar/
├── fetch_menu.py          # Main Python script
├── requirements.txt       # Python dependencies
├── .github/
│   └── workflows/
│       └── update-calendar.yml  # GitHub Actions config
├── docs/
│   └── lunch.ics          # Generated calendar (hosted via GitHub Pages)
└── README.md              # Documentation
```

### Schedule
- GitHub Actions will run weekly (Sundays at 6:00 AM ET)
- This catches any menu updates while being conservative with resources
- iCloud typically refreshes subscribed calendars every few hours

---

## Questions Before We Start

1. Do you have a GitHub account, or do we need to create one?
2. What do you want the calendar events to show?
   - Just the main entree (e.g., "Popcorn Chicken")
   - Full meal details (entree + sides + vegetables)
   - Something else?

---

## Let's Begin!
Once you answer the questions above, we'll start with Step 1.
