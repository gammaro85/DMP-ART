# DMP-ART: Speaker Notes
## Skrypt prelegenta — wersja do wydruku

**Prezentacja:** DMP-ART: How a Non-Programmer Built a Production Tool Through Conversations with AI
**Czas:** ~66 minut (z Q&A)
**Slajdy:** 24
**Język:** English

---

> **Jak używać tego dokumentu:**
> Tekst kursywą = tekst do mówienia.
> Tekst zwykły = wskazówki sceniczne.
> *(pauza)* = zatrzymaj się na 2–3 sekundy.
> Każdy slajd zawiera szacowany czas.

---

## SLIDE 1 — Title
**⏱ 2 min**

*Good morning / Good afternoon, everyone.*

*Quick question to start. Raise your hand if you've ever thought: "I wish someone would build a small tool to handle this one repetitive part of my work." Something specific. Something that would save you an hour a week.*

*(pauza)*

*Keep your hand up if your next thought was: "…but I'd need a programmer for that, it's too complicated, it's probably not worth the effort."*

*(pauza)*

*This talk is for everyone whose hand is still up.*

*My name is [Imię Nazwisko]. I'm a data steward at [Instytucja]. Today I want to tell you how I built a tool that saves me ninety minutes on every grant review — without writing a single line of code myself. But more than the tool itself, I want to talk about how that process worked. Because I think the process is what's actually interesting.*

*The talk is roughly an hour. I'll leave time at the end for questions, and I'll be honest throughout — including about the parts where I made mistakes.*

---

## SLIDE 2 — About Me
**⏱ 2 min**

*Let me introduce myself briefly, because my background is relevant to what I'm going to tell you.*

*I'm a data steward. My job is to help researchers at [Instytucja] manage their research data well — from planning how they'll collect data, through storing it securely, to sharing and preserving it after the project ends.*

*A significant part of that work involves reviewing Data Management Plans in grant applications. Roughly [liczba] proposals per year, depending on the season.*

*My background is in [dziedzina]. I have no programming background. I did not study computer science. Before this project, the most technically complex thing I did regularly was write Excel formulas.*

*I'm telling you this not to establish credibility — but to establish the baseline. The person who built DMP-ART was not a technical person who happens to work in research support. It was a non-technical person who had a specific problem and eventually found a path to a solution.*

*That path is what this talk is about.*

---

## SLIDE 3 — The World This Tool Lives In
**⏱ 3 min**

*Before we get to the problem and the tool, I need to give you the context — the world this tool lives in. Because without it, the problem won't make complete sense.*

*NCN — the National Science Centre, in Polish: Narodowe Centrum Nauki — is Poland's primary public funding body for basic research. If you're a Polish researcher and you want funding for fundamental science, NCN is where you apply. The grant schemes — OPUS for established researchers, PRELUDIUM for PhD students, SONATA for early career researchers, and several others — together receive thousands of applications per year.*

*Since around 2019, NCN has required that funded projects include a Data Management Plan. This is in line with trends across European research funding — Horizon Europe, the EU's flagship research programme, has required DMPs since its launch in 2021. The principle is simple: if public money funds research, the data from that research should be properly managed, documented, and where possible, made available to others.*

*A DMP is a structured document. It follows a framework developed by Science Europe — a European association of major research funding and performing organisations. The framework has six main sections covering twelve standard questions: how data will be collected, documented, stored, secured, shared, and who is responsible for all of this.*

*The data steward — my role — sits between the funder's requirements and the researcher's reality. I review the DMP before submission, identify gaps and weaknesses, and provide feedback that helps the researcher improve it. I'm not deciding whether the science is good. I'm checking whether the data management is sound.*

*And that review process — repeated for every proposal, every season — is where the problem lives.*

---

## SLIDE 4 — The Problem: Two Hours Every Time
**⏱ 3 min**

*So here is the problem.*

*A grant proposal arrives. It's a PDF. It's eighty pages long, sometimes more. Somewhere inside — usually around page forty-five, sometimes page sixty, occasionally much earlier or much later — is the Data Management Plan. The DMP is almost never a clearly labelled standalone document. It's a section within a larger proposal, formatted differently in every submission, sometimes in Polish, sometimes in English, sometimes both.*

*Let me walk through the table on screen.*

*(czytaj każdy wiersz powoli)*

*Two hours. Every single proposal.*

*But the number that really bothered me was not the total. It was the split. The intellectual work — actually reading the DMP and forming a judgment about its quality — took about twenty minutes. The other hundred minutes was administration. Scrolling. Copying. Pasting. Reformatting.*

*A hundred minutes of expertise applied to tasks requiring no judgment, no knowledge of research data management. Just patient mechanical work.*

*That is an inefficiency with a very specific shape. And a very specific solution: a tool that does the mechanical part automatically, leaving only the twenty minutes that actually require a data steward's expertise.*

*That tool didn't exist. So I built it.*

---

## SLIDE 5 — The First Conversation
**⏱ 3 min**

*I want to be precise about how this started, because the starting point matters.*

*I didn't decide to "build a web application." I didn't know what a web application was made of. I had a vague sense that "AI can do things with text" from what I'd read. What I actually did was open a chat window — at that point using Claude in a browser — and type something that was essentially a complaint about my job.*

*(czytaj cytat z ekranu powoli)*

*That's not a technical specification. That's a frustration. But it was a specific frustration about a specific workflow, and that made all the difference.*

*What the AI did not do was say "you need to learn Python first." It asked me questions. What kind of documents? What format? How do you know where the relevant section starts? What do the headings look like?*

*And then it described — in plain language — what was possible. And then it showed me about twenty lines of code that could extract text from a PDF.*

*I had never seen Python code before in my life. I didn't know what most of those lines meant. But I could run them. And they worked.*

*That was the moment I understood something important: the bottleneck was not coding ability. The bottleneck was describing the problem clearly enough that a solution could be built. That is a completely different skill. And one I already had.*

---

## SLIDE 6 — What Is DMP-ART
**⏱ 2 min**

*Before we go further, let me show you what actually got built.*

*(przejdź przez diagram krok po kroku)*

*A user uploads a grant proposal — PDF or Word document. The application finds the DMP section automatically, even in an eighty-page document, in Polish or English. It splits the DMP into the standard Science Europe sections. A review interface appears. The data steward reads the extracted text, clicks pre-written comments from a library, adds custom notes, and exports the review.*

*Two hours becomes thirty minutes. That's a seventy-five percent reduction. The tool correctly identifies sections in ninety-four point one percent of real NCN proposals — we tested it on seventeen actual files. One failure: a corrupted PDF where even a human couldn't read the text.*

*This is a real, working application — a server, file processing, a database of sorts, a complete web interface with dark and light themes. All of it emerged from conversations. That's what this talk is about.*

---

## SLIDE 7 — Phase 1: The Prototype
**⏱ 3 min**

*The first version of the tool could upload a file, extract some text, and display it on screen. That's it. No section detection. No templates. No interface worth speaking of.*

*Success rate: roughly forty percent.*

*But that forty percent was extraordinary to me, because zero percent of it had existed the week before.*

*The debugging process in those early weeks looked like this: I would upload a proposal. Something wouldn't work. I would copy the error message — or describe what happened — and paste it into the chat. The AI would diagnose it. We would fix it. I would try again.*

*The first real insight came when I noticed that some files worked and others didn't. I brought this to the AI: "It finds the DMP in some documents but completely misses it in others. I can't tell why."*

*Claude asked me to share an example of each. After looking at them, it explained: the documents used different heading formats. Some had the heading in bold. Some had it as a numbered section. Some were in Polish, some in English. The extraction logic only knew one pattern.*

*The fix was a bilingual keyword map — a list of all the ways you might write "Data Management Plan" in both languages, with fuzzy matching to catch variations.*

*This pattern — bring a specific failure, get a specific diagnosis — became the core rhythm of the whole project.*

---

## SLIDE 8 — The Evolution of a Conversation Language
**⏱ 3 min**

*Something interesting happened over the first few months that I didn't notice while it was happening. The way I talked to the AI changed completely.*

*In the first weeks, I described wishes. "I want it to automatically understand the whole document." Vague input, vague output. The AI guessed at what I meant, and usually guessed wrong in some important way.*

*By the second month, I was describing errors. "It crashed again. Here's the error message." Better — specific problems get specific answers. But I was still reactive.*

*By the third month, I was describing root causes. "The section detection fails on documents that use a table-based layout. Can we add a detection path for that format?" This is a different kind of question entirely. I wasn't describing what broke — I was describing why it broke and what direction the fix should go.*

*By the fourth month, I was asking about tradeoffs. "Before we add OCR, what are the implications for processing time? Is it worth it for the edge cases?" This is design thinking. Not "make it work" but "help me decide whether to make it."*

*(czytaj cztery fazy z ekranu)*

*I want to be honest: this progression wasn't deliberate. I became better at it because vague questions kept producing disappointing results, and specific questions kept producing useful ones. The feedback loop trained me.*

*The skill that developed — describing a technical problem with precision — turns out to be useful everywhere. It made me better at talking to human colleagues too. When I file a support ticket now, I describe input, expected output, and actual output. The ticket gets resolved faster. Same skill, different context.*

---

## SLIDE 9 — The Toolset Evolution: From Chat Window to IDE
**⏱ 5 min**

*I want to talk about something that isn't often covered in these discussions: the tools themselves kept changing.*

*When I started, my workflow was entirely manual. I had Claude open in a browser tab. On the other side of the screen, I had Visual Studio Code — the text editor where the code lived. The process was: ask Claude something, Claude produces code, I copy it, I paste it into VSCode, I save the file, I run the application, something breaks, I describe it back to Claude.*

*Copy, paste, copy, paste.*

*This worked. But it was slow. And there was constant friction — context got lost, I'd paste into the wrong file, I'd forget to save, the versions in my head and in the editor would drift apart.*

*Then Claude Code became available as an extension directly inside VSCode. This changed the dynamic significantly. Claude could now see the actual files — not a copy I'd pasted, the real files in their current state. When I said "the section detection isn't working," it could look at the actual code, find the relevant function, and propose a change directly. No copying. No pasting. The edit appeared in the file.*

*The iteration loop went from five minutes to thirty seconds.*

*But the most important change wasn't speed. It was context. Claude Code could read multiple files at once — it could see how the Flask routes in app.py connected to the templates in review.html connected to the JavaScript in script.js. This systemic view was something I'd been manually maintaining, poorly, by pasting relevant code snippets. Now it happened automatically.*

*Currently my workflow is more fluid. Sometimes I use the Claude desktop application — when I want a longer conversation, when I'm thinking through a design question rather than writing code, when I want to discuss something without immediately touching files. Other times I'm directly in VSCode with Claude Code, making targeted changes to specific functions.*

*The choice depends on what I'm doing. Thinking → desktop app. Implementing → VSCode. This distinction — between thinking sessions and implementation sessions — is something I arrived at by trial and error, and it's made the work significantly more efficient.*

*What I would tell someone starting today: begin in the chat interface. It forces you to learn to describe problems. Once you can do that reliably, add the IDE integration. The chat interface is where you develop the skill. The IDE integration is where you apply it faster.*

---

## SLIDE 10 — GitHub and Copilot: When AI Checks AI
**⏱ 4 min**

*At some point in the project, I started using GitHub.*

*If you're not familiar: GitHub is a platform for storing and tracking code. Every change gets recorded with a message explaining what changed and why. You can go back to any previous version. You can compare what the code looked like before and after a change.*

*For me, GitHub started as a backup system. I was worried about losing work. But it became something more useful: a memory. The AI doesn't remember what we built three months ago. I do, but imperfectly. GitHub remembers exactly. When something breaks after a change, I can see precisely what changed. That diagnostic ability alone is worth the setup time.*

*Then I added GitHub Copilot. Copilot is a different AI assistant — made by GitHub and Microsoft, trained on a vast amount of publicly available code. It lives inside VSCode and makes suggestions as you type.*

*The interesting thing is that Copilot and Claude are not the same. They notice different things.*

*There were several occasions where Claude had produced code that worked — tests passed, the feature functioned — and Copilot quietly flagged a potential issue. A function that would fail on an edge case. A CSS pattern that would cause problems in certain browsers. A security concern in how a file path was being constructed.*

*Claude missed these not because it's worse than Copilot. It missed them because it was focused on the specific thing I'd asked it to do. Copilot, working line by line as I looked at the code, had a different kind of attention.*

*Having two different AI systems with different training, different architectures, and different modes of engagement creates something neither provides alone: a second pair of eyes with a different perspective.*

*I now think of Copilot as the proofreader and Claude as the author. They serve different functions, and both are useful.*

---

## SLIDE 11 — What I Have But Don't Use
**⏱ 4 min**

*I want to be honest about something that I think is underrepresented in AI productivity discussions: the gap between what's available and what's actually used.*

*I have access to a number of tools and features that I've never meaningfully engaged with.*

*(przejdź przez każdy punkt, czytaj tytuł i pierwsze zdanie opisu)*

*Claude Projects first. There's a feature that lets you store context permanently — your codebase description, your conventions, your decisions — so every session starts with full context instead of a five-minute briefing. I have a CLAUDE.md file that Claude Code reads automatically in VSCode. In the chat interface, I'm still re-explaining. That's pure waste, and the solution exists. One afternoon of setup.*

*Automated testing. I have tests. They pass. I run them manually when I remember. Setting up GitHub to run them automatically on every push would take one afternoon and would catch every regression the moment it's introduced. I know this. It's next on my list.*

*Model selection. I use the default model for everything. Routing complex architectural decisions to the most capable model and routine edits to a faster cheaper model is straightforward and would reduce both cost and latency. I don't do it.*

*The adversarial review session. In April, one dedicated session — no new features, just "read the code and tell me what's wrong" — removed one hundred and thirty kilobytes of dead code that had accumulated over months. If I'd done that session every two months, the dead code would never have accumulated.*

*Why am I telling you this? Two reasons. First: I want to be accurate. I'm not a power user. I'm a domain expert who learned to use tools well enough to build something useful. There's a difference.*

*Second: this list represents a roadmap. Every item is a genuine opportunity to improve the workflow. The tool works at ninety-four percent accuracy today. With better tooling discipline, it could be better, faster, and cheaper.*

---

## SLIDE 12 — The Bug That Disappeared and Came Back Twice
**⏱ 5 min**

*I want to tell you about a specific bug, because it illustrates something important about how AI-assisted development can fail in a very quiet way.*

*In February 2026 — version 0.9.1 of the tool — the category comments dropdown in the review sidebar stopped working. I would click on a category name, and nothing would happen. No error. No message. The interface just sat there.*

*I described this to Claude: "The sidebar dropdown doesn't show comments. I click the category and nothing happens."*

*Claude asked to see the JavaScript function that was supposed to show the dropdown, and the HTML for that element. I pasted both. Claude's response was almost immediate.*

*"Found it. The element has the CSS class .hidden. That class applies display:none with an !important flag. Your JavaScript does element.style.display equals block — but the !important rule always takes priority over inline JavaScript styles. The dropdown is technically appearing, then immediately being hidden by the CSS. Change the JavaScript to use element.classList.remove, quote hidden."*

*One line of JavaScript. Three weeks of broken functionality.*

*(pauza)*

*Now here's the uncomfortable part.*

*In April 2026 — two months later — the upload progress bar stopped working. Or rather: we discovered it had never worked. It had been invisible since it was first implemented. Months of uploads, and the progress bar had never once appeared.*

*The root cause was identical. The same CSS class. The same JavaScript pattern. The same !important override. The same silent failure.*

*Claude built both of these components. In different sessions, months apart. It did not notice that it was repeating a pattern that had already caused a silent failure elsewhere. It solved the problem in front of it — here's a dropdown, here's how to show it — without awareness of what had already broken in a different part of the codebase.*

*This is the critical insight: AI does not audit the codebase before writing new code. It responds to the immediate request. The developer — the non-programmer, in this case — has to maintain the systemic view. You have to be the one who remembers the diagnosis from three months ago. Because Claude won't.*

---

## SLIDE 13 — The Yes-Man Problem
**⏱ 5 min**

*This is the slide I wish someone had shown me at the beginning. It's the most important conceptual point in the whole talk.*

*AI almost never says "that's a bad idea."*

*(pauza)*

*This is not a criticism — it's a structural observation. AI is trained to be helpful. Helpful, in practice, means implementing what you ask, optimising what you describe, and validating the direction you choose. Even when the direction is wrong.*

*(pauza)*

*Let me give you three concrete examples from this project.*

*Example one: dead code.*

*(czytaj tabelę z ekranu)*

*template_editor.html — nine hundred and eighty-four lines. Rendered by zero routes in the application. The page existed. The application never showed it. ai_settings.html — one thousand and twenty lines. Same situation. template_editor.js — twenty-eight kilobytes of JavaScript. Loaded by no page in the application.*

*Total: approximately one hundred and thirty kilobytes of completely dead code.*

*Nobody asked "do we actually need a separate page for this?" Claude never said "I notice you already handle this elsewhere." The code was requested. The code was written. The code sat there, doing nothing, for months.*

*Example two: the settings architecture. Early in the project, we built two separate settings pages — one for templates, one for AI configuration. Both were built in full. Later, both were consolidated into a single settings page. All the original code had to be maintained through the consolidation, then removed. The question "would one page be sufficient?" was never asked until after two full pages had been built.*

*Example three: CSS !important. Early in the project, these flags were added because they made things work quickly without thinking about specificity. Eighty instances. Later, they caused the hidden sidebar bug and the invisible progress bar. Removing them required a dedicated refactoring session.*

*(pauza)*

*The pattern across all three examples is the same: AI optimises for making your current request work. It does not optimise for making future requests easier. It does not maintain a view of the whole.*

*What you need to do is ask the questions AI won't ask itself.*

*(czytaj pytania z ekranu powoli, z pauzami)*

*"Is there a simpler way to achieve this?"*

*"What could go wrong with this approach?"*

*"Are we building something we'll want to throw away later?"*

*"Does this pattern exist anywhere else in the codebase? Could it cause the same problem?"*

*These are adversarial questions. They're uncomfortable to ask because they might mean more work. But they're the questions that prevent a hundred and thirty kilobytes of dead code from accumulating. And they're questions that only the human can ask.*

---

## SLIDE 14 — The Optimization Crisis: 64.7% → 94.1%
**⏱ 4 min**

*At some point in version 0.7, I tested the tool on seventeen real NCN proposals. Eleven worked correctly. Six failed. Sixty-four point seven percent success rate. The target was ninety-three percent. I had a significant problem.*

*The conversation that followed was one of the most productive of the entire project, because the failures were specific and describable — and specific failures are solvable failures.*

*I told Claude: "Three of the failures are scanned PDFs. I can see the text fine when I open the file, but the tool extracts nothing."*

*Claude explained: scanned PDFs contain images, not text. The PDF viewer shows you a picture of text. The extraction library reads the underlying data — which, for a scan, contains no text at all. The solution is OCR — Optical Character Recognition. The standard open-source tool is Tesseract.*

*I had never heard of Tesseract. But within one conversation, it was integrated, and every previously-failing scanned PDF now processed successfully.*

*For the other three failures — regular PDFs with text being assigned to the wrong sections — the diagnosis took longer. Claude looked at the section detection logic and identified the core problem: it tried one detection method and stopped. If that method didn't work, the content was marked as unassigned.*

*The fix was a four-tier fallback. First: look for PDF form patterns and bold markers. Second: look for numbered headings. Third: look for formatted text markers. Fourth: use text similarity — fuzzy matching against known section titles with a Jaccard threshold.*

*That fourth tier alone added eighteen percent to the success rate.*

*Final result: ninety-four point one percent. Sixteen out of seventeen files. The one failure was a corrupted PDF — garbled characters even in a standard viewer. That one we accepted.*

*The lesson: a crisis is a diagnostic opportunity. Describe the failure precisely and the solution often follows.*

---

## SLIDE 15 — What the Human Brought
**⏱ 3 min**

*I want to be direct about this, because it gets glossed over in discussions about AI productivity.*

*Domain knowledge was not a nice-to-have in this project. It was the foundation everything else was built on.*

*Claude had no idea what Science Europe was. It had no idea what an NCN proposal looked like. It had never encountered a Polish DMP. Every piece of domain-specific logic in the tool — which sections matter, what good feedback looks like, what patterns indicate a weak DMP, how to distinguish section headings from body text in a Polish government document — came entirely from me. The AI had the technical knowledge to implement. I had the domain knowledge to specify.*

*The test cases came from me. Seventeen real proposals from real researchers at real institutions. AI cannot test against reality. Only the human in the situation can.*

*The priority decisions came from me. At every fork — fix the sidebar first or add the AI module? Better export or better detection? — I decided based on what would actually save time in real use. AI has no way to know which features matter most to a specific user at a specific institution.*

*The judgment call about when "good enough" was actually good enough — that came from me. Ninety-four point one percent accuracy. Is that enough for production? A machine can't answer that. I could, because I know what the alternative looks like: two hours of manual work per proposal.*

*The most important contribution I made to this project was not technical. It was knowing exactly what problem I needed to solve — and caring enough about it to spend months solving it.*

---

## SLIDE 16 — What AI Brought
**⏱ 3 min**

*Equally direct on the other side.*

*Translation was the core service. Turning a description of a problem into working software. "When I click save, it should store the feedback and show a green confirmation message" becomes a Flask route, a JSON serialisation function, a JavaScript fetch call, and a toast notification. That translation — from human intent to executable code — is what made the project possible.*

*Diagnosis without fatigue. When something broke — and things broke constantly, especially early on — Claude would analyse the failure with the same quality of attention every time. The tenth debugging session looks the same as the first. For a human collaborator, that's not always true.*

*Ecosystem knowledge. I didn't know Tesseract existed. I didn't know what O-n-squared meant. I didn't know that CSS !important could override JavaScript inline styles. Claude knew all of this and brought it in precisely when it was needed.*

*Availability. This sounds mundane but it isn't. The ability to work for twenty minutes at eleven in the evening, without scheduling, without briefing anyone, without context-switching overhead for a collaborator — that was practically significant. The tool was built in small bursts, across many months, fitting around everything else.*

*And no opinions about the stack. When I said "keep it simple," it kept it simple. Vanilla JavaScript. No build tools. Plain JSON files for configuration. The constraint came from me, and AI respected it. That constraint produced a tool I can actually maintain and deploy without specialised knowledge.*

---

## SLIDE 17 — The Scale of What Was Built
**⏱ 3 min**

*Let me put some numbers on this, because I think the scale matters for understanding what AI-assisted development actually means.*

*(czytaj tabelę)*

*The core codebase is approximately ten thousand lines. The Flask server alone is fifteen hundred and fifty lines. The extraction engine is two thousand one hundred and one lines. The review interface HTML is two thousand three hundred and forty-one lines.*

*A novel is roughly seventy to one hundred thousand words. Ten thousand lines of code is roughly the same character count — except each line has to be logically correct, syntactically valid, and coherent with everything that came before and after it. A novel can have a weak chapter. Code cannot have a weak function.*

*If an experienced developer built this from scratch — full design, implementation, testing, debugging — it would take three to six months of full-time work. The estimate I received from a development agency was in that range.*

*What it delivers: PDF and Word file processing, OCR for scanned documents, bilingual text detection, real-time progress feedback, a complete web interface with dark and light themes, a template and category management system, UUID-based caching that survives browser refreshes, and an optional AI assistant that connects to both OpenAI and Anthropic.*

*I'm sharing these numbers not to impress. I'm sharing them to establish the baseline. This is a production application, used in real work, handling real documents, at a real institution. The fact that it was built through conversations deserves to be appreciated on its actual scale.*

---

## SLIDE 18 — Five Lessons Learned
**⏱ 5 min**

*Five things I know now that I wish I'd known at the beginning. I'm going to pause between each one, because I think they deserve individual attention.*

*(pauza)*

*Lesson one: small, specific problems get good solutions.*

*"The dropdown doesn't show when I click" produces a fix in ten minutes. "Make the app better" produces a two-hour session of mixed results. One problem per conversation. Describe input, expected output, actual output. Everything else follows from that.*

*(pauza)*

*Lesson two: you are the architect. AI has no memory.*

*Every conversation starts fresh. AI doesn't know what was built three months ago, what decisions were made, what patterns have already caused problems. If you don't track the big picture, nobody does. Keep a log of major decisions. Before starting a session, give Claude the context it needs. That investment pays for itself immediately.*

*(pauza)*

*Lesson three: never accept a solution you can't roughly describe.*

*If AI produces code and you cannot explain in plain English what it does and why — stop. Ask. "Explain this to me in plain language." "What happens if the file doesn't exist?" "What happens if the user uploads an empty PDF?" Code you don't understand will break in ways you won't be able to find.*

*(pauza)*

*Lesson four: ask adversarial questions.*

*AI will implement anything you ask. So ask the questions it won't ask itself. "What could go wrong here?" "Is there a simpler way?" "What are the tradeoffs?" "Does this pattern exist anywhere else in the codebase?" One adversarial question per major feature. It will save you a refactoring session six months later.*

*(pauza)*

*Lesson five: domain expertise is the multiplier.*

*The people who will build the best tools with AI are the people who know their problems best — not the people who know the most code. The bottleneck has shifted from "can I write this?" to "can I describe this precisely enough that something can write it for me?" Those are completely different skills. One of them you may already have.*

---

## SLIDE 19 — The Skills You Actually Need
**⏱ 3 min**

*I want to be precise about this, because I've seen the message "anyone can build anything with AI now" used in ways that are not helpful.*

*Here's what you genuinely don't need: programming syntax. Knowledge of algorithms. Database design theory. Framework opinions. DevOps or deployment knowledge.*

*Here's what you do need.*

*(czytaj każdy punkt z prawej kolumny, z krótką pauzą między nimi)*

*Problem decomposition: the ability to take "I want a review tool" and break it into twenty specific, solvable problems. This is the hardest skill, and it's the one that took the longest to develop.*

*Precise description: the ability to say "the dropdown shows on click but disappears immediately" instead of "it doesn't work." These sound similar. They produce completely different results.*

*Failure pattern recognition: recognising when the same failure is appearing in different places. Remembering the diagnosis from three months ago. The AI won't do this. You have to.*

*Priority judgment: knowing which twenty percent of features delivers eighty percent of the value. Knowing when ninety-four percent is good enough.*

*Healthy scepticism: the willingness to ask "what could go wrong?" even when something appears to be working.*

*Domain expertise: knowing what the tool needs to do from the perspective of the person who will actually use it.*

*The closest analogy I've found for this skill set is product management. The skills that make a good product manager — user empathy, problem clarity, prioritisation, knowing when to say no — are the same skills that make a good AI development collaborator. This is not a shortcut. It is genuinely demanding cognitive work. It's just different demanding cognitive work than programming.*

---

## SLIDE 20 — Current State and What's Next
**⏱ 2 min**

*DMP-ART is in production. I use it regularly. It does what it was supposed to do.*

*(szybko przez lewą kolumnę — achieved items)*

*The right column is equally important. Things deliberately not built.*

*Multi-user support — there is one user at one institution. Adding authentication and collaboration features would add complexity with no benefit to the person who actually uses this.*

*Mobile version — target users are at office desks. Every hour spent making this work on a phone is an hour not spent making it work better on a desktop.*

*Full AI automation — I want to review DMPs, not delegate that review to an algorithm. The AI module helps me write faster. It does not replace my judgment.*

*Every "not built" decision was deliberate. One of the strongest signals of a mature product is knowing what to leave out. The tool does its job. That is enough.*

---

## SLIDE 21 — The Bigger Picture
**⏱ 2 min**

*DMP-ART is not unique. It's representative of something that's happening across every field.*

*Across every profession, there are people who know a specific problem intimately, repeat the same mechanical work every week, and have never been able to build a solution — because the path to software ran through "learn to program," which ran through "find time, find a teacher, find money." That bottleneck is shifting. Not to zero — there is still real cognitive work required, and domain knowledge is still the foundation. But the threshold has moved significantly.*

*For institutions, this means something concrete: create conditions where domain experts can experiment. Recognise that "I built this with AI" is a legitimate professional contribution. Understand that the constraint is now problem clarity, not coding ability.*

*For individuals in this room: think about your own work. What process could you describe precisely enough to automate? What do you do mechanically that an AI could do instead, if you could explain it clearly?*

*The DMP-ART story is evidence that the answer might be: more than you think.*

*(pauza — czytaj cytat z ekranu powoli)*

*"The best tools are built by the people who feel the problem. AI now makes it possible for those people to also build the solution."*

---

## SLIDE 22 — What Does This Actually Cost?
**⏱ 4 min**

*Let me talk about money, because I want to be transparent about what the actual spend looks like.*

*The foundation is two subscriptions. Claude Pro — roughly twenty dollars a month. GitHub Copilot — ten dollars a month. Thirty dollars total. That's the minimum viable setup, and for most months it covers everything. Claude Pro gives you a generous amount of usage. GitHub Copilot runs in the background. No surprises.*

*The months where the cost goes up are the months of active development. Building a new feature involves long conversations, large contexts — pasting in files, getting back substantial changes, iterating. At a certain point in a heavy session, Claude Pro starts throttling. You hit rate limits and have to wait. During those months I upgrade to Claude Max, which is around a hundred dollars. That month's total: a hundred and ten.*

*The "additional payments" category is really just this: active development sprints are more expensive. Not continuously — but when you're building, the higher tier pays for itself in uninterrupted sessions. For maintenance and small improvements, thirty dollars a month is enough.*

*Now for context. The estimate I received to have this built professionally was somewhere between five and fifteen thousand dollars. At thirty dollars a month, you'd need over a decade of subscriptions to reach that cost. Even at a hundred and ten a month during development, the economics are not comparable.*

*The more useful comparison is time. Before DMP-ART, a review took two hours. After, thirty minutes. I do roughly twelve reviews a season. That's eighteen hours saved. Per season. The tool pays for its entire annual subscription cost in the first week it's used.*

*One practical note: GitHub Copilot pricing is per user. If your institution were to adopt this for a team, the Business tier is about nineteen dollars per person per month. Both Claude and GitHub have organisational plans. What I've described is individual use — for exactly the scale this project needed.*

---

## SLIDE 23 — The Roadmap I'm Not Building — But Should Be
**⏱ 4 min**

*I want to end not with what was built, but with what I would do differently. Because that's more useful to most people in this room than a summary of what already works.*

*The six things on this slide are not hypothetical. They're real gaps in my own workflow, with real costs.*

*(przejdź przez każdy punkt)*

*Claude Projects first. I have a CLAUDE.md file — a detailed document describing the codebase architecture, patterns, and conventions — that Claude Code reads automatically every time it opens in VSCode. That part works. In the chat interface, I'm still re-explaining the project from scratch every session. Five minutes of setup waste, every time. The solution — a proper Project with persistent context — exists and I haven't configured it. One afternoon of work, permanent benefit.*

*Session types. This took months to figure out intuitively. A thinking conversation and an implementation session are fundamentally different tasks. They benefit from different environments and different framing. When I mix them in the same session — "let me think about the architecture and also write the code" — the quality of both suffers. Now I decide before opening VSCode: design session or implementation session?*

*Automated testing. I have tests. I run them manually. Setting up GitHub Actions to run them automatically on every push would take one afternoon and would catch every regression the moment it's introduced. I know this. It is literally the next thing I am going to do after this conference.*

*Prompt library. The same questions come up constantly. "Review this function for edge cases." "Add a new DMP section following the existing pattern." Writing a good prompt for each of these once, and reusing it, produces dramatically more consistent results than improvising each time.*

*Model selection. Default for everything. Wrong. Complex architectural decisions need the most capable model. Routine line-level fixes need the fastest cheapest model. I haven't set this up. I should.*

*And the adversarial review session. In April, one dedicated session — no new features, just "read the code and tell me what's wrong" — removed one hundred and thirty kilobytes of dead code that had accumulated across months. If I'd done that session every two months, the dead code would never have accumulated. It costs nothing. It prevents a lot.*

*The summary of all six: the biggest efficiency gains are not in the AI. They're in the workflow around the AI. The tool is capable. The question is whether you're using it deliberately — or just reaching for it when something breaks.*

---

## SLIDE 24 — Questions
**⏱ 5 min**

*Thank you. I'm happy to take questions.*

*(jeśli cisza — zaproponuj jedno z pytań z ekranu)*

---

### Wskazówki do trudnych pytań z sali

**"Isn't this just prompt engineering?"**
Partly. But prompt engineering in service of real user problems, with real domain expertise behind it, produces real production software. The label matters less than the outcome.

**"What happens when the AI gives wrong code?"**
You test it on a real file. Either it works or it doesn't. If it doesn't, you describe what went wrong and try again. The iteration loop is the mechanism. The key is understanding roughly what "wrong" looks like — which comes back to understanding the solution well enough to evaluate it.

**"Can anyone do this?"**
Anyone with deep knowledge of a specific problem and willingness to describe it precisely. That's a narrower group than "anyone" but a much wider group than "people who can code."

**"Did you ever think about hiring a developer instead?"**
Yes. The estimate I received was three to six months and a significant budget. The AI-assisted approach took roughly the same calendar time — spread across small sessions, cost a fraction, and left me with a tool I understand deeply enough to maintain and modify. The knowledge transfer is built in, because I was present for every decision.

**"Is this safe? Can AI introduce security vulnerabilities?"**
Yes, and it's a real concern. The tool validates file uploads, sanitises filenames, limits file size to sixteen megabytes, and validates the structure of Word documents before processing them. Every security measure was explicitly requested and reviewed. Claude didn't add them automatically — I had to know to ask.

---

## Zestawienie czasowe

| #  | Slajd                                        | Czas   |
|----|----------------------------------------------|--------|
| 1  | Title                                        | 2 min  |
| 2  | About Me                                     | 2 min  |
| 3  | The World This Tool Lives In                 | 3 min  |
| 4  | The Problem: Two Hours Every Time            | 3 min  |
| 5  | The First Conversation                       | 3 min  |
| 6  | What Is DMP-ART                              | 2 min  |
| 7  | Phase 1: The Prototype                       | 3 min  |
| 8  | The Evolution of a Conversation Language     | 3 min  |
| 9  | The Toolset Evolution: From Chat to IDE      | 5 min  |
| 10 | GitHub and Copilot: When AI Checks AI        | 4 min  |
| 11 | What I Have But Don't Use                    | 4 min  |
| 12 | The Bug That Disappeared and Came Back Twice | 5 min  |
| 13 | The Yes-Man Problem                          | 5 min  |
| 14 | The Optimization Crisis: 64.7% → 94.1%      | 4 min  |
| 15 | What the Human Brought                       | 3 min  |
| 16 | What AI Brought                              | 3 min  |
| 17 | The Scale of What Was Built                  | 3 min  |
| 18 | Five Lessons Learned                         | 5 min  |
| 19 | The Skills You Actually Need                 | 3 min  |
| 20 | Current State and What's Next                | 2 min  |
| 21 | The Bigger Picture                           | 2 min  |
| 22 | What Does This Actually Cost?                | 4 min  |
| 23 | The Roadmap I'm Not Building — But Should Be | 4 min  |
| 24 | Questions                                    | 5 min  |
|    | **RAZEM**                                    | **66 min** |

---

> **Jak skrócić do 60 minut:**
> Połącz slajdy 15 i 16 w jeden (dwie kolumny: Human / AI) → oszczędność 3 min.
> Skróć slajd 17 (Skala) do 2 min → oszczędność 1 min.
> Skróć slajd 19 (Umiejętności) do 2 min → oszczędność 1 min.
> Razem: −5 min → ~61 min z Q&A.

---

*Dokument wygenerowany: 2026-05-05*
*Wersja prezentacji: 1.0*
*Projekt: DMP-ART v0.9.1*
