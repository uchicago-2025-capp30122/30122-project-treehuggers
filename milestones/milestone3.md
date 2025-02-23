To earn an S your team must have:

A repository with an appropriate project layout. (see Repo Layout below)

Working data import code for at least one of your sources.

An initial draft of data reconciliation/cleaning process.

An initial draft of the final visualization/simulation/etc. that may be using mock data at this point.

The beginning of a README. (see README below)

And finally, the team* will attend a meeting with course staff to discuss the state of the project.

Repo Layout

In terms of repository layout, your code should primarily be within a single package, similarly to how you've had PAs laid out this quarter:

pyproject.toml
uv.lock
README.md
myproj/__init__.py
myproj/scrapers/news.py
myproj/scrapers/federal_reserve.py
myproj/viz.py
myproj/merge.py
myproj/utils.py
tests/...
data/shapefiles/
data/...

Keep code related to specific tasks in files with helpful names, organized with directories as needed.  All code should be in .py files within the main repository.

If you have data, that can be in an external data directory or within your myproj/ whichever works better for you.  If you have data that won't fit inside your repository you'll just need to note that at this phase (see the section on the README below)

In terms of other files (.ipynb, random scraps of code you're experimenting with) please just keep those together in a directory, I tend to name these scratch/  but as long as you have them all together (& not spread everywhere throughout your project) you're fine.

README

At this point README should contain at least:

1. An abstract describing the goals of the project, this may come from M1/M2 or be modified as needed.

2. The names of all of your team members.

3. A section titled Data Sources that lists your sources and any important details about them.  For example if someone needs an API key or to download large files, mention that here, and if possible, tell them where to get a key and/or download the files.

4. Optionally, you can begin a section "How to Run" that lets someone new to the project know the commands they need to run & in what order. Make this clear for me or anyone that hasn't been working on the project to get started from a fresh clone. This might look something like:

Step 1) Run the scrapers with uv run python -m myproj.scrapers  This will take about 45 minutes.

Step 2) Once the scrapers are done, convert the data into the final JSON form with uv run. python -m myproj.merge_data --threshold 0.8 

Step 3) To run the visualization in your browser, run python -m myproj.viz and open your browser to localhost:5000.