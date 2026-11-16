from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUTPUT = "cs654_project4_progress_report_plain.docx"
BLACK = RGBColor(0, 0, 0)


def set_run(run, size=10.5, bold=False, italic=False):
    run.font.name = "Arial"
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Arial")
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Arial")
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = BLACK


def set_cell_margins(cell, top=45, start=75, bottom=45, end=75):
    props = cell._tc.get_or_add_tcPr()
    margins = props.first_child_found_in("w:tcMar")
    if margins is None:
        margins = OxmlElement("w:tcMar")
        props.append(margins)
    for name, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = margins.find(qn("w:" + name))
        if node is None:
            node = OxmlElement("w:" + name)
            margins.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_cell_borders(cell):
    props = cell._tc.get_or_add_tcPr()
    borders = props.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        props.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = borders.find(qn("w:" + edge))
        if node is None:
            node = OxmlElement("w:" + edge)
            borders.append(node)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), "4")
        node.set(qn("w:space"), "0")
        node.set(qn("w:color"), "808080")


def repeat_header(row):
    props = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    props.append(header)


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run("Page ")
    set_run(run, size=8)
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(end)


def paragraph(doc, text, size=10.5, bold=False, italic=False, after=5):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.05
    r = p.add_run(text)
    set_run(r, size=size, bold=bold, italic=italic)
    return p


def heading(doc, text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8 if level == 1 else 4)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    set_run(r, size=14 if level == 1 else 11.5, bold=True)
    return p


def table(doc, headers, rows, widths):
    t = doc.add_table(rows=1, cols=len(headers))
    t.autofit = False
    t.style = "Table Grid"
    repeat_header(t.rows[0])
    for i, value in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.width = Inches(widths[i])
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_borders(cell)
        set_cell_margins(cell)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(value)
        set_run(r, size=9, bold=True)
    for row_index, values in enumerate(rows):
        row = t.add_row()
        for i, value in enumerate(values):
            cell = row.cells[i]
            cell.width = Inches(widths[i])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_borders(cell)
            set_cell_margins(cell)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(str(value))
            set_run(r, size=9)
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(1)
    return t


doc = Document()
section = doc.sections[0]
section.top_margin = Inches(0.65)
section.bottom_margin = Inches(0.6)
section.left_margin = Inches(0.7)
section.right_margin = Inches(0.7)

normal = doc.styles["Normal"]
normal.font.name = "Arial"
normal._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
normal.font.size = Pt(10.5)
normal.paragraph_format.space_after = Pt(5)
normal.paragraph_format.line_spacing = 1.05

add_page_number(section.footer.paragraphs[0])

# Title and current status
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(2)
r = p.add_run("Project Progress Report")
set_run(r, size=20, bold=True)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(1)
r = p.add_run("Reinforcement Learning for Flappy Bird")
set_run(r, size=13, bold=True)
for line in (
    "CS 654 Reinforcement Learning Project 4",
    "Brian Porter, Vinayaka Hegde, Sanjana Sasmal, and Preston Huynh",
    "November 16, 2026",
):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(line)
    set_run(r, size=9)

heading(doc, "Current Status")
paragraph(doc, "The project now has a working Flappy Bird environment and a working tabular Q-learning agent. The code has been split into separate files for the environment, agent, experiments, plotting, and command-line settings. The project runs in the cluster JupyterLab environment. The environment checker passed, and the full pilot experiment finished successfully.")
paragraph(doc, "The best result so far came from the sparse reward with the basic state. It averaged 27.95 pipes during testing. The expanded state averaged 0.38 pipes, and the shaped reward averaged 1.32 pipes. This shows that the state representation and reward design make a large difference in this project.")
table(doc, ["Area", "Status", "Evidence"], [
    ["Environment", "Complete", "Environment checker passed"],
    ["Q-learning agent", "Complete", "Three versions trained"],
    ["Pilot experiments", "Complete", "5,000 episodes, 3 seeds"],
    ["Video recording", "Complete", "MP4 test files created"],
    ["Final analysis", "In progress", "More analysis and writing remain"],
    ["Final submission", "Planned", "Report, code, figures, and demo"],
], [1.6, 1.15, 4.1])

heading(doc, "Project Goal")
paragraph(doc, "The goal is to test how different state and reward choices affect reinforcement learning in a simple Flappy Bird game. The bird moves forward by itself. The agent can flap or do nothing. It receives a reward for passing pipes and a penalty for crashing. The project uses numerical observations and tabular Q-learning instead of raw images and a neural network so the results are easier to study.")

heading(doc, "Background Work and Setup")
paragraph(doc, "The team reviewed Q-learning, epsilon-greedy exploration, discounting, state discretization, and reward design. We also reviewed how to build a custom Gymnasium environment, including reset, step, action spaces, observation spaces, and random seeds. Pygame is used for the game display. Matplotlib is used for result figures.")
paragraph(doc, "The cluster uses Python 3.13.14. NumPy, Matplotlib, Gymnasium, Pygame, MoviePy, and FFmpeg were installed or available. Import tests passed for the Python packages, and FFmpeg was found at /opt/conda/bin/ffmpeg.")

heading(doc, "System Design")
heading(doc, "Environment", level=2)
paragraph(doc, "The game screen is 288 by 400 pixels. The bird has a vertical position and velocity. Gravity pulls the bird down, and the flap action gives it an upward velocity. Pipes move from right to left. The gap in each pipe is randomly placed. The episode ends when the bird hits a pipe, hits a boundary, or reaches the step limit.")
heading(doc, "State and Actions", level=2)
paragraph(doc, "The observation includes the bird's height, vertical velocity, distance to the next pipe, the next gap height, and the following gap height. The basic state groups these values into bins. The expanded state also includes the difference between the next two gaps. The agent has two actions: 0 means do nothing and 1 means flap.")
heading(doc, "Rewards", level=2)
paragraph(doc, "The sparse reward gives +1 for passing a pipe and -1 for crashing. The shaped reward also gives a small positive value when the bird is near the center of a pipe gap. The experiment tests whether this extra feedback helps learning.")

heading(doc, "Learning Method and Experiments")
paragraph(doc, "The agent uses tabular Q-learning with an epsilon-greedy policy. The learning rate is 0.1, the discount factor is 0.99, and epsilon starts at 0.1 and decreases during training. The study trained three versions for 5,000 episodes each with seeds 0, 1, and 2. Each learned policy was then tested on 20 new levels. A random policy and a hand-coded controller were also used as comparison points.")

heading(doc, "Pilot Results")
paragraph(doc, "These numbers came from the completed full run in JupyterLab. The test score is the average number of pipes passed. The state count is the number of different table states visited during training.")
table(doc, ["Configuration", "Test mean", "Scores by seed", "States"], [
    ["Random policy", "0.00", "0.00", "-"],
    ["Sparse reward, basic state", "27.95", "29.30, 36.65, 17.90", "12,237-12,259"],
    ["Sparse reward, expanded state", "0.38", "0.45, 0.45, 0.25", "57,126-57,477"],
    ["Shaped reward, basic state", "1.32", "1.20, 1.25, 1.50", "11,202-11,290"],
    ["Hand-coded controller", "45.40", "Sanity check", "Not used"],
], [2.3, 1.0, 2.0, 1.55])

heading(doc, "What the Results Mean")
paragraph(doc, "The sparse basic-state version performed much better than the other learned versions. The expanded state visited about 57,000 states instead of about 12,000. That makes the table much larger, so the agent has fewer chances to visit the same states and improve them during 5,000 episodes. The extra information may still help if the agent is trained longer.")
paragraph(doc, "The shaped reward also performed poorly. The agent received local feedback for being near a gap, but that did not teach it the correct time to flap. This result only applies to the reward rule used here. A different shaping rule could work better.")

heading(doc, "Implementation and Testing")
paragraph(doc, "The original prototype used one large file. It is now divided into modules. The environment module handles game physics and rendering. The agent module handles state bins and Q-learning. The experiment module handles training and testing. The plotting module writes JSON results and a PDF learning curve. The main module handles command-line options.")
paragraph(doc, "The following tests passed in JupyterLab: the Gymnasium environment checker, Python compilation with python -m py_compile, package imports, a short smoke test, a full pilot run, and a video smoke test. The video test created three MP4 files. FFmpeg confirmed H.264 video at 288 by 440 pixels with 44 frames in the selected test video.")

heading(doc, "Reproducibility")
paragraph(doc, "The full pilot can be repeated from the project folder with the command below. It trains the three selected versions, tests them with three seeds, and saves a JSON summary and a PDF learning curve in the output folder.")
paragraph(doc, "python main.py --workers 3 --output-dir progress_run", size=9.5, after=4)
paragraph(doc, "The video test uses the same program with the recording options below. It records one evaluation episode for each configuration and saves the MP4 files in the video folder.")
paragraph(doc, "python main.py --episodes 2 --eval-episodes 2 --seeds 0 --workers 1 --record-video --video-episodes 1 --video-dir video_smoke/videos --output-dir video_smoke", size=9.5, after=4)
paragraph(doc, "This organization makes it possible to rerun the project without changing the source files. The main result files are progress_run/results/pilot.json and progress_run/figures/learning_curve.pdf.")

heading(doc, "Next Experiments")
paragraph(doc, "The first next experiment will use a longer training run for the expanded state. This will show whether its poor score is caused by the larger table or by a problem with the state itself. The second experiment will change the bin sizes and compare a smaller and a larger table. The third possible experiment is SARSA, which will provide a second learning algorithm for comparison.")
paragraph(doc, "For each extra experiment, the team will keep the number of evaluation levels and random seeds the same. This will make the comparisons fair. If time becomes limited, the final study will focus on the sparse basic-state version, the expanded-state version, and one improved setting instead of adding too many new algorithms.")

heading(doc, "Recorded Video Evidence")
paragraph(doc, "The project can record a short evaluation episode after training. I reviewed the recorded shaped-reward evaluation video and extracted the three frames below. The frames show the bird moving toward the next pipe. The video was 1.47 seconds long and contained 44 frames. This is an evaluation recording, not a screen recording of every training episode.")
doc.add_picture("video_frames_montage.png", width=Inches(5.55))
p = doc.paragraphs[-1]
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(1)
paragraph(doc, "Figure 1. Three frames from one recorded evaluation episode after training.", size=8.5, italic=True, after=3)

heading(doc, "Problems and Limitations")
paragraph(doc, "The continuous game state had to be changed into bins so that it could be used as a table key. The bin sizes affect both learning speed and performance. The expanded state is larger and was harder to learn in the current training budget. The shaped reward also did not help in the pilot run. The current study uses numerical observations, only three learned configurations, and average pipe score as its main measure.")

heading(doc, "Remaining Work and Schedule")
paragraph(doc, "The main system is complete. The remaining work is to confirm the results, finish the analysis, and prepare the final report and demonstration.")
table(doc, ["Dates", "Task", "Output"], [
    ["Nov. 16-20", "Repeat the pilot and organize files", "Reproducible results"],
    ["Nov. 21-25", "Test another training length or bin setting", "Extra comparison"],
    ["Nov. 26-29", "Run SARSA if time permits", "Optional comparison"],
    ["Nov. 30-Dec. 2", "Run final experiments with several seeds", "Final scores and curves"],
    ["Dec. 3-5", "Analyze results and prepare video", "Final figures and demo"],
    ["Dec. 6-7", "Finish report and presentation", "Submission draft"],
    ["Dec. 8", "Submit the project", "Code, report, figures, instructions"],
], [1.25, 3.7, 1.9])

heading(doc, "How the Remaining Work Will Be Judged")
paragraph(doc, "The repeated pilot will be compared with the current numbers instead of being judged by one unusually good or bad run. The team will report the average test score, the scores for each seed, the last part of the training curve, and the number of visited states. These values will show both performance and learning stability.")
paragraph(doc, "The extra state and bin experiments will be useful only if they improve the test score without making the table too large to learn. The SARSA experiment is optional because the main research question can be answered with Q-learning. If SARSA is completed, it will use the same environment, seeds, episode count, and test levels so the comparison is fair.")
paragraph(doc, "The final demonstration will show the program starting, the output files being written, and a recorded evaluation episode. The report will explain that the video is an evaluation after training, while the JSON file and learning curve are the main evidence about the training process.")

doc.add_page_break()
heading(doc, "Risk and Backup Plan")
paragraph(doc, "The main risk is that longer experiments may take too much time in the shared cluster. If that happens, the team will keep the completed pilot as the main result and run only one additional setting. Another risk is that a new reward or state will perform worse. That result is still useful because it shows which design choices did not work under the current training budget.")

heading(doc, "Final Deliverables")
paragraph(doc, "The final submission will include the modular source code, the Flappy Bird environment, the Q-learning agent, experiment results, learning curves, the README, recorded evaluation video, final report, and presentation materials.")

heading(doc, "Conclusion")
paragraph(doc, "The project has reached the main progress goal: the complete system runs in the cluster environment and produces repeatable results. The sparse basic state is currently the strongest learned version. The next step is to confirm this result with a small number of extra experiments and clearly explain the limitations.")

heading(doc, "References")
for ref in (
    "Sutton and Barto, Reinforcement Learning: An Introduction, 2nd edition, MIT Press, 2018.",
    "Watkins and Dayan, Q-learning, Machine Learning, 1992.",
    "Farama Foundation, Gymnasium documentation for creating custom environments.",
    "Pygame documentation.",
    "CS 654 lectures on Q-learning, exploration, and reward design.",
):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Inches(0.18)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(ref)
    set_run(r, size=8.5)

doc.save(OUTPUT)
print(OUTPUT)
