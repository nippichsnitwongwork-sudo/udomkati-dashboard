# Udomkati Brewing Academy · Marketing Plan & Content Operations Dashboard

A single-file dashboard (`index.html`) for planning campaigns, scheduling content, assigning work and reviewing results for Udomkati Brewing Academy. Thai-first, with international terminology.

## Features
- **Campaign Template Library** – 26 task templates across 4 campaign categories (Masterclass, Workshop, Activity & Event, PR & Collaboration). Pick a category and a Launch Day (T-0) and the tasks are generated with calculated dates, owners, deliverables and KPIs (`data/campaign-task-templates.csv`).
- **Task Schedule** – list or board (by sprint phase) view, status flow *To Do → In progress → In review → Done*, filters by status, category and owner.
- **Monthly Calendar** – colour-coded by project, drag & drop, export to PNG / CSV / print.
- **Projects & Timeline**, **On-site Shoot Checklists** (add / delete / restore), **Alerts & Timeline Check**, **LINE summary** generator.
- **Team, Access & Workload** – roles (Host, Editor, Assignee, Viewer), join-request approval, activity log.
- **AI helpers** – persona fit analysis, campaign planner, performance insights (only when run inside Claude, see below).

## Two ways to run

| | A. Published as a Claude artifact | B. Standalone (this repo / GitHub Pages) |
|---|---|---|
| Shared real-time data for the team | Yes (shared database) | No – data is stored in each browser (`localStorage`) |
| Roles & approval | Yes | Single user, full access |
| AI helpers | Yes (Claude Pro or higher) | No |
| Export PNG / CSV | Yes | Yes (browser download) |

**A.** Publish `index.html` as a Claude artifact with these capabilities: `db` (rules: `udk/team` and `udk/projects` writable by admin only), `user` (profile scope), `sample`, `downloads`. Share it with teammates from the artifact's **Share** menu (an eligible Claude plan is required).

**B.** Open `index.html` in a browser, or serve the folder with any static host (e.g. GitHub Pages). Everything works except shared data, roles and AI.

## Data model (shared database, collection `udk`)
`plan` (posts), `tasks`, `items` (events), `check` (checklists), `done`, `metrics`, `team` (members & roles), `projects`, `log`, and `req_<userId>` (join requests). Each document is stored as `{ j: "<JSON string>", by, at }`.

## Security notes
- Role limits inside the dashboard (Assignee, Viewer) are enforced in the UI. Hard guarantees come from the sharing level set in Claude (Viewer cannot write; only Editor and above can change `team` and `projects`).
- Do not commit exported data containing student or customer information. Keep this repository **private** unless the team is comfortable with the template content being public.
- Advertising copy about alcohol must be reviewed against Thai alcohol-advertising rules before publishing.

## Tests
```bash
npm install
npm test
```
Headless smoke tests (jsdom) cover core flows, permissions, shared sync, template generation, board/filters and checklists.

## Docs
- [User guide](docs/USER_GUIDE.md)

## License
Not specified yet – add a `LICENSE` file before sharing outside the team.
