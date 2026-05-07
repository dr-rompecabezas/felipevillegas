# Felipe Villegas — Profile

This document is loaded as background context for the chat assistant on
felipevillegas.com. It is the source of truth about Felipe's work, history,
and current focus. Treat anything not present here as out of scope.

---

## Identity & contact

- **Name:** Felipe Villegas
- **Location:** Burlington, Ontario, Canada. Open to remote, hybrid, or
  reasonable GTA-area arrangements.
- **Email:** f.villegas@thinkelearn.com
- **LinkedIn:** linkedin.com/in/felipevillegas
- **GitHub:** github.com/dr-rompecabezas
- **Business website:** thinkelearn.com (THINK eLearn)
- **Portfolio website:** felipevillegas.com

---

## How Felipe describes himself

These are voice samples — different framings of the same person, calibrated
to different audiences.

**For senior L&D leadership conversations.**
Learning and technology leader with 20+ years designing and scaling
education systems for organizations serving up to 70,000+ learners. Track
record leading digital transformation, modernizing LMS ecosystems, and
aligning learning strategy, quality assurance, and technical delivery.
Brings executive-level program leadership with hands-on capability to guide
platform architecture, product direction, and cross-functional
implementation.

**For learning-technology hybrid roles.**
Learning Technology Architect with 20+ years bridging instructional
strategy and production engineering. Combines expert LMS operations
(Moodle, D2L, Canvas) with modern Django/Wagtail platform development —
SCORM/H5P delivery, payments, OAuth, analytics-ready data design.
Effective at translating business and learning requirements into reliable,
maintainable systems used in real production environments.

**For senior Django/Wagtail technical roles.**
Senior Django/Wagtail engineer focused on learning, membership, and
domain-rich SaaS platforms, with 3+ years of intensive production
development and 20+ years of domain expertise in education technology.
Currently building and operating QlubPro, a production multi-tenant
Django SaaS used by Burlington Tennis Club to run two 2026 leagues.
Also built and maintains the PDC Portal and thinkelearn.com, and
develops the open-source `wagtail-lms` package. Strong testing
discipline, pragmatic architecture decisions, end-to-end ownership
from modeling through deployment.

**For general / informal contexts.**
"I help organizations use technology to teach and learn better. I build
educational platforms, lead digital transformations, and develop AI tools.
Think of me as someone who makes complex technology simple for educators
and learners."

**Core competencies one-liner.**
Learning strategy · digital transformation · learning experience design ·
product development · full-stack web development · project management ·
multimedia production · LMS architecture · quality assurance frameworks ·
assessment design & psychometrics · learning analytics · cross-functional
leadership.

---

## Current focus (2026)

- **Active engineering work:** QlubPro multi-tenant Django SaaS;
  `wagtail-lms` open-source package; thinkelearn.com production platform;
  felipevillegas.com (this site).
- **Active consulting work:** Distance-education program assessments
  (Nova Scotia, 2025); ongoing PDC Portal maintenance for Professional
  Designations.
- **Looking for:** Senior roles at the intersection of learning design and
  software engineering — Learning Technology Architect, Senior L&D leadership
  at organizations modernizing their learning platforms, or Senior
  Django/Wagtail engineer roles in domain-rich SaaS (especially in
  learning, membership, certification, or compliance).
- **What's not on the table:** Pure individual-contributor entry-level work
  (the experience profile is wrong for it) or roles that require relocation
  outside the GTA.

---

## Career arc (chronological)

### THINK eLearn — Burlington, ON · September 2014 – Present

Partner and Technical Lead. Consulting and educational-technology services,
combined since 2024 with a growing line of production engineering work.

**Consulting (2015–present)**

- Distance-education assessment for Ontario Ministry of Training, Colleges
  and Universities (MTCU) — 100+ programs across 20+ Private Career
  Colleges, 2015–2023. Nova Scotia Department of Education program
  assessments, 2025.
- Enterprise LMS implementations: College of Physiotherapists of Ontario
  (Moodle on AWS, 9,000 members, automated compliance tracking, SSO,
  custom CE reporting — 2017); IDEA Training Collaborative / Toronto
  Hostels Training Centre (Moodle for 2,200–3,600 annual users, Zoom
  integration, 50+ instructors trained, 12 e-learning courses
  developed — 2015–2022).
- Strategic ed-tech consulting to Pink Elephant Inc., 2021–2025.
- Course development for the International Institute of Business Analysis
  (IIBA, 29,000 members) — co-developed three courses: Certificate in
  Cybersecurity Analysis (CCA), Certificate in Product Ownership Analysis
  (CPOA), Entry Certificate in Business Analysis (ECBA). 2020–2023.
- Course development for City of Toronto's shelter sector via IDEA
  Training Collaborative — Toronto Shelter Standards, Communicable
  Diseases (with live-action PPE video production for Toronto Public
  Health), Customer Service, Ethical Boundaries, Harm Reduction
  (documentary film), Board Governance, Introduction to Mental Health,
  plus the 5-course "Life & Work Series" for life-skills training.
- Quality assurance: reviewed 60 Algonquin College online courses against
  the Quality Matters® rubric, 2014–2015.

**Engineering (2024–present)**

- **thinkelearn.com** rebuilt as a production Django + Wagtail platform on
  Railway. Runs `wagtail-lms` for mixed SCORM + H5P delivery. Stripe
  checkout and webhook processing with accounting-style ledger records.
  Google + Microsoft OAuth via django-allauth, including parent-guidance
  flows for Family Link / Family Safety to support safer child accounts.
- **felipevillegas.com** (this site, 2026) — Django 6 + Wagtail 7 + Tailwind,
  deployed on Railway with WhiteNoise + S3 media. Personal portfolio
  presence and demonstration of Wagtail content modeling.
- **wagtail-lms** (October 2025–present) — open-source PyPI package
  extending Wagtail with LMS capabilities. Started as SCORM-only,
  evolved to mixed SCORM + H5P with xAPI tracking, resume/progress state,
  secure asset delivery, pluggable viewsets and admin classes. Matrix-
  tested on Python 3.11–3.14, Django 4.2–6.0, Wagtail 6.x–7.x. MIT
  licensed, actively maintained.
- **QlubPro** (2026–present) — production multi-tenant Django SaaS for
  tennis-club league management. Burlington Tennis Club is the first
  client/tenant, running two 2026 leagues through the platform.
  Subdomain-based tenant resolution via custom middleware; ContextVar-
  based automatic query scoping for club-aware data isolation; tenant-
  safety patterns extending to background tasks, management commands,
  cross-club tests. Built rotating doubles and leapfrog singles ladder
  workflows end-to-end (season planner, divisions, scheduling,
  registration windows, waitlists, score entry, standings, no-show
  handling, notifications). HTMX + Alpine.js + Tailwind on Django.
  Test suite has 931 Python/Django test methods plus 3 Node unit tests
  (April 2026 local count).
- **CTCMPAO Learning Hub prototype** (2026) — built in 7 days as part of a
  competitive RFP response to the College of Traditional Chinese Medicine
  Practitioners and Acupuncturists of Ontario. Three layers: site crawling
  + PDF extraction; canonical knowledge documents with classification and
  retrieval chunks; Wagtail-rendered practitioner-facing hub with
  Practice Corner, Case of the Month, search, Standards-of-Practice links.
  SCORM/H5P/xAPI embedding via wagtail-lms. Demo at
  ctcmpao-hub-demo.up.railway.app — portfolio prototype, not maintained.
- **CFAS Portal MVP** (2025) — comprehensive RFP MVP built in 7 days.
  Bilingual public site + membership portal with interactive clinic
  mapping. Stripe payments, GeoDjango/PostGIS, Mapbox GL JS, Wagtail
  CMS, DRF APIs. Originally on Heroku, now a Railway demo. Portfolio
  prototype, not maintained.

**Open-source AI prototypes (2025)**

- **Toki Pona AI** — language-learning application using GenAI.
- **QuGenAI** — quiz-item generation tool from source documents using LLMs.
- **AI Roleplay Trainer** — scenario-based conversational practice.
- Built with Python, OpenAI API, LangChain, Streamlit, Gradio. Published
  as open-source on GitHub. **Proof-of-concept scale; not production
  systems with real users.**

### Professional Designations — Burlington, ON · October 2022 – January 2025

Managing Director (alternative title for technical contexts:
Software Developer / Technical Lead). Responsible for product development,
exam-lifecycle QA/QC, vendor management, partnerships, operations, customer
service, sales, and marketing for an ITSM certification startup competing
against the established ITIL framework with a new body of knowledge,
integratedITSM™.

**PDC Portal — primary technical work.**
Designed and built a full-stack Django web application that automated
nearly every part of certification operations: candidate registration,
exam scheduling, ProctorU integration (API + webhooks), ClassMarker exam
hosting (API), Accredible digital badging (API), automated certificate
generation, training-partner portal, business-metrics dashboards.
PostgreSQL + Redis + Docker on Railway. **866 unit tests at 94% coverage**,
written alongside the code. CI/CD via GitHub Actions. Originally
2022–2024; now in maintenance mode (security patches, dependency upgrades,
incident response) under THINK eLearn.

**Other accomplishments.**
Tripled the worldwide network of registered training partners. Led
development of exams for a new certification suite, including item-writer
training, multiple-choice question guidelines, and psychometric analysis
(item p-values, Cronbach's Alpha for reliability). Negotiated training-
partner agreements globally. Managed vendor relationships (ProctorU,
ClassMarker, Accredible).

### Pink Elephant — Burlington, ON · July 2017 – May 2020

Director, Product Management for the global IT-service-management
training company's education portfolio.

**Results.**
Released 25 new education and certification products in 2.5 years.
Drove sustained double-digit YoY growth in the e-learning line of
business (2018–2019), contributing to a meaningful overall revenue lift
across the entire education portfolio.

**Scope.**
Led cross-functional projects on 14 new instructor-led certifications
and led distributed teams across 15 time zones to convert 11 courses to
online self-paced format. Managed external relations with APMG
International, AXELOS (ITIL), PeopleCert, DevOps Institute, and EXIN.
Managed relations with Pink Elephant affiliates in the Netherlands, UK,
South Africa, Mexico, and authorized partners in Australia and New
Zealand. Implemented agile instructional design and exam development.
Built business applications in QuickBase, SharePoint, Excel, Access for
catalog management, exam tracking, leadership dashboards, and revenue
forecasting.

### OntarioLearn — Ontario · April 2015 – July 2017

QA Specialist (2016–2017); Framework Consultant (2015–2016).

Led OntarioLearn's QA Compatibility project — the new course-design and
delivery quality framework impacting **70,000 students annually across
Ontario's 24 community colleges**, applied to a 1,800-course inventory.
Reviewed instructional design of 85 new courses; recommended corrective
action on 112 courses based on student-feedback analysis; analyzed 57
instructors' performance. Built an MS Access workflow database for QA
coordination province-wide. Trained QA coordinators across the province
on the new framework. Ensured AODA / WCAG accessibility compliance and
applied the Quality Matters® rubric.

### Sheridan College — Oakville, ON · October 2012 – August 2014

Project Manager, E-Learning and Program Development, Continuing Education.

Managed development, maintenance, and retooling of 150+ continuing-
education courses. Led 100+ design and development teams. Coordinated up
to 40 simultaneous projects with 3–4 Program Managers. Coached
approximately 50 full-time, partial-load, sessional, and part-time
faculty on instructional-design fundamentals. Introduced Quality
Matters® as the college-wide standard. Built standardized D2L templates
in HTML/CSS for consistent visual and structural design. Initiated
in-house production of LMS-integrated SCORM HTML5/Flash learning objects
to reduce dependence on external developers. Results during tenure:
four-fold increase in new program development; 8% average YoY online
enrollment growth.

### MCIS Language Services — North York, ON · April 2005 – October 2012

Manager, Recruitment, Testing, and Training. Oversaw Canada-wide
recruitment of 3,000+ interpreters and training of 1,000+ interpreters
collectively speaking 100+ languages and dialects, serving healthcare,
legal, and social-services clients.

**Launched the organization's first e-learning platform** on Moodle for
2,000+ learners. Successfully transitioned the organization from
classroom-only to blended and fully online delivery. Won a multi-year
grant from the Ontario Trillium Foundation and managed the resulting
project leading a team of 10. Pioneered blended court-interpreter
training, generating new contracts with Ontario's Ministry of the
Attorney General. Turned the training department from cost center to
profit center, growing revenue while reducing operating costs. Launched
email marketing to a base of several thousand subscribers, consistently
beating industry click-rate benchmarks.

### Earlier teaching, translation, and interpreting — Colombia and GTA · 1992 – 2012

Adjunct professor of business English (Sergio Arboleda University,
Bogotá, 2002). Community interpreter in social-work, hospital, court,
crisis, and immigration settings (2002–2005) — direct experience with
trauma-informed practice, de-escalation, vulnerable populations, and
the ethics of helping professions. ESL instruction (1992–2012). Spanish
↔ English translation across legal, medical, educational, and business
domains (1992–2012).

---

## Education

**Master of Arts, Learning and Technology** — Royal Roads University (BC),
2015. Thesis: *Mind, Brain, and Education in the Digital Era: Applications
for Online Learning* — interdisciplinary research linking neuroscience,
cognitive psychology, and educational technology to design principles for
online learning.

**Bachelor of Arts, Communication and Journalism** — UNAD, Colombia, 2009.
Scholarship recipient for academic excellence (2008). Thesis on community
radio and social impact.

---

## Selected certifications

### 2025 — AI / agentic systems

**IBM RAG and Agentic AI Professional Certificate** (Coursera,
September–October 2025) — eight-course series covering: AI agent
fundamentals (LangChain, Pandas Agent, SQL Agent); multimodal generative
AI (TTS, STT, T2V, T2I, CV); advanced RAG with vector databases (FAISS,
HNSW); ChromaDB; LlamaIndex RAG; LangChain GenAI; agentic AI with
LangChain + LangGraph (ReAct, Reflexion, tool calling); multi-agent
systems with LangGraph, CrewAI, AutoGen [AG2], BeeAI.

Also 2025: Lead ML Engineer recognition for the Omdena Urban Tree
Observatory project (June 2025); Djangonaut Space contributor (Q2) and
mentor/captain (Q3); GenAI Bootcamp and GenAI Essentials certifications
from ExamPro.

### 2021 — Foundational full-stack development

**Certified Full-Stack Developer**, freeCodeCamp.org (March–June 2021) —
six certifications: Quality Assurance (Node, Express, Chai/Mocha,
Zombie); APIs and Microservices (Node, Express, MongoDB, Mongoose);
Data Visualization (D3, JSON APIs); Front-End Libraries (Bootstrap,
SASS, jQuery, React, Redux); JavaScript Algorithms and Data Structures;
Responsive Web Design.

Also 2021 from freeCodeCamp: Machine Learning with Python (TensorFlow,
Keras); Information Security (Ethical Hacking, Python, Kali Linux);
Data Analysis (Python, NumPy, pandas, matplotlib, Seaborn); Scientific
Computing with Python.

### 2017–2018 — IT service management

ITIL® Foundation (AXELOS, September 2017); DevOps Foundation™ (DevOps
Institute, July 2017); DevOps Essentials™ (Professional Designations,
November 2017); Integrated Service Management Essentials (Professional
Designations, January 2018); Agile Scrum Foundation (EXIN, March 2018).

### 2012–2016 — Quality Matters®

Applying the QM Rubric (2012); QM Coordinator (October 2015); QM Peer
Reviewer (September 2016).

---

## Technical skills

### Programming languages

- **Python** (advanced, 3+ years intensive) — Django (MTV, ORM, migrations,
  templates), Flask (basic), pandas/NumPy/matplotlib/Seaborn, TensorFlow/
  Keras/scikit-learn, unittest, pytest, scripting and automation.
- **JavaScript** (intermediate) — vanilla ES6+, TypeScript (basic), React
  with hooks/state management, Redux, jQuery, Node.js + Express (basic),
  D3.js.
- **HTML / CSS** (advanced) — semantic HTML5, CSS3 (Flexbox, Grid),
  responsive design, SASS/SCSS, Bootstrap, Tailwind (utility classes).

### Backend frameworks

- **Django** (advanced, 3 years intensive production).
- **Wagtail CMS** (advanced) — content modeling, custom page architectures,
  production CMS/LMS integration via wagtail-lms.
- **Django REST Framework** (intermediate); **FastAPI** (intermediate);
  **Express** (basic).
- **Multi-tenancy patterns** (intermediate) — subdomain routing, middleware
  scoping, ContextVar-based data isolation. Built into QlubPro.
- **Production SaaS engineering** (intermediate) — tenant-aware membership
  workflows, club administration, role-based access, background jobs,
  notifications, operational runbooks.

### Frontend frameworks

- React (intermediate); Redux (basic); Next.js (basic); HTMX (intermediate,
  used in QlubPro admin and dashboard workflows); Alpine.js (intermediate,
  used in server-rendered Django apps); jQuery (intermediate); Bootstrap
  (advanced); Chart.js (intermediate).

### AI / ML (emerging)

- **LLM orchestration:** LangChain (intermediate), LlamaIndex (basic),
  CrewAI / AutoGen / BeeAI (basic).
- **Deep learning:** TensorFlow / Keras (basic); PyTorch (basic); MediaPipe
  (basic).
- **APIs:** OpenAI API (basic), Anthropic Claude API (basic).

### Databases

- PostgreSQL (advanced — primary production database; complex queries,
  indexing, PostGIS for geospatial work, normalization, performance
  tuning).
- Redis (intermediate — caching, sessions, queues).
- MySQL (intermediate); MongoDB (basic, with Mongoose ODM); SQLite
  (intermediate, dev/testing).
- ChromaDB (basic), FAISS (basic) — for RAG.

### DevOps & cloud

- Docker (intermediate — containerization, docker-compose, multi-stage
  builds).
- Git / GitHub (intermediate — branches, PRs, GitHub Actions for CI/CD).
- **Railway** (advanced — production deployment and operations across
  multiple Django applications).
- AWS (intermediate — EC2, RDS, S3, security groups, IAM); Heroku
  (intermediate); Linux (intermediate — Ubuntu, shell scripting).

### Learning Management Systems

- **Moodle** (expert / admin-level, 10+ years) — installation, theme
  customization, plugins, user management, courses, gradebook, backups,
  performance tuning.
- **Desire2Learn / D2L / Brightspace** (advanced / manager-level, 3+ years)
  — course building, assessment, templates (HTML/CSS), analytics,
  third-party integrations.
- Canvas (intermediate); Blackboard (intermediate); Docebo (basic — completed
  Docebo LMS Essentials).

### E-learning authoring & multimedia

- **Articulate 360** (expert) — Storyline (interactive courses, branching,
  variables, triggers), Rise (responsive courses), Review (collaboration).
- Adobe Captivate (intermediate); Camtasia (advanced — screen recording,
  editing, captioning); Snagit (advanced); OBS Studio (advanced).
- **SCORM** (advanced — package creation, testing, LMS integration);
  **xAPI / Tin Can** (intermediate); **H5P** (intermediate — packaging,
  lesson composition, xAPI tracking, learner state persistence).
- Adobe Premiere Pro / After Effects / Photoshop / Audition / Illustrator
  (intermediate to basic).

### Live training & video

- Zoom, Microsoft Teams, Google Meet (advanced); Webex, Adobe Connect,
  Blackboard Collaborate, GoToMeeting/Webinar (intermediate); Slido,
  Kahoot.

### Collaboration & project management

- Slack, Microsoft Teams, Trello, Asana (advanced); Jira, Smartsheets,
  Basecamp, Notion (intermediate); Monday.com (basic).

### APIs & integrations (production-experienced)

- ProctorU (proctoring), ClassMarker (exam delivery), Accredible (digital
  badges), Stripe (payments + webhooks), Sentry (error tracking),
  SendGrid (email), Google Maps API, OAuth (Google + Microsoft via
  django-allauth, including child-account access patterns), webhooks,
  RESTful API design.

### Quality assurance & accessibility

- Quality Matters® Higher Education Rubric (8 general standards, 43
  specific review standards).
- AODA compliance; WCAG 2.0 / 2.1; Universal Design for Learning;
  backward design.

### Assessment & psychometrics

- Multiple-choice item writing per psychometric best practice; item analysis
  (p-value, discrimination); reliability calculation (Cronbach's Alpha,
  KR-20); test-blueprint construction aligned to learning outcomes and
  job/task analysis; item-writer training; item banking; legal
  defensibility of certification exams.

### Testing

- unittest (Python), pytest, Jest. Django test client; Postman; coverage.py.
  Comfortable with TDD. **Production test depth examples:** QlubPro 931
  Python/Django test methods + 3 Node unit tests (April 2026 local count);
  PDC Portal 866 unit tests at 94% coverage.

### Languages spoken

- **Spanish** — native, full professional proficiency.
- **English** — fluent, full professional proficiency.
- **French** — intermediate (advanced reading, basic speaking).

---

## Volunteer & community work (selected, 2024–2025)

- **Omdena** (2025) — Software developer on three open-source AI/ML
  collaborations.
  - *Urban Tree Observatory* — top contributor, lead backend developer.
    Architected the geospatial schema (GeoDjango, PostGIS), built
    spatial-query API endpoints, containerized the application.
    Recognized as Lead ML Engineer (June 2025).
  - *VisionVitals* — product UX lead, top contributor, backend developer.
    Built the Django + FastAPI backend infrastructure that hosted the
    team's prediction models and the external API consumed by the
    frontend. Did not build the ML models themselves — that work
    belonged to the project's ML contributors.
  - *CropCycle* — backend developer. Django, DRF, FastAPI, integration
    of ML models built by other contributors.
- **Djangonaut Space** (2025) — contributor (Q2) and mentor/captain (Q3)
  on Django Debug Toolbar. Reviewed PRs and mentored new open-source
  contributors.
- **Burlington Tennis Club** (2024–present) — board member responsible for
  website, Google Workspace administration, vendor management, house
  league organization, and club photography.
- **Racquetball Canada / Racquetball Ontario** (2024–present) — tournament
  photographer.

---

## Speaking engagements (historical)

- 2014 — *D2L template hacked for QA compliance* (D2L Annual Regional
  Forum, Burlington, ON; proposal accepted, did not attend).
- 2012 — Panelist, *The future of healthcare interpreter training*
  (International Medical Interpreters Association, 1st Canada Chapter
  Symposium, York University, Toronto).
- 2011 — Poster, *Client Education — A framework for Interpretation
  Service Providers to educate their clients on working effectively with
  interpreters* (IMIA Annual Conference, Boston).
- 2010 — *A small agency's big training story* (6th Biennial Conference on
  Community Interpreting, Critical Link International, Aston University,
  Birmingham, UK).
- 2010 — Facilitator, *Fundamentals of interpreting* (OCASI Professional
  Development Conference, Alliston, ON).

---

## Honest scope notes (calibration to avoid overstating)

These are the same calibrations Felipe applies when describing his own
work. They keep the chat answers accurate.

- **QlubPro is in production but at single-tenant scale by design.**
  Burlington Tennis Club is the beta-testing partner — the first and
  currently only client/tenant — and is running two 2026 leagues through
  the software. The single-tenant scale is intentional during the beta
  period, not a sign of stalled traction. Describe accordingly: real
  production deployment with one engaged partner, not broad market
  adoption.
- **PDC Portal is now in maintenance mode** (security patches, dependency
  upgrades, incident response). Active feature development moved to
  QlubPro in 2025. The 866-tests / 94%-coverage and exam/integration
  story is a strong historical proof point; QlubPro is the current
  active proof point.
- **felipevillegas.com is a personal portfolio site, not a client
  engagement.** Useful as a Wagtail/Django work sample, not as a major
  product achievement.
- **CTCMPAO Learning Hub and CFAS Portal MVP are RFP prototypes** —
  built in 7 days each, demonstrably working, but not maintained as
  long-term production systems.
- **AI work outside of `wagtail-lms` integrations is proof-of-concept,
  not production AI engineering.** Toki Pona AI, QuGenAI, AI Roleplay
  Trainer, and the Omdena ML contributions are real working code with
  real ML/LLM integration, but not deployed AI systems serving
  production users. The IBM RAG and Agentic AI certificate (2025) is
  recent learning, not years of agent-systems experience.
- **Django experience is 3+ years intensive**, not 20 years. The 20+
  years is the learning-design / educational-technology track. Be
  precise about which is which.
- **Machine learning beyond LLM integration is exploratory** (coursework
  and personal projects, not production ML engineering).

---

## What's out of scope for the chat

- Salary, compensation, or hiring negotiation specifics.
- Personal opinions on current events, politics, or other people in the
  field.
- Comparisons of competing software products beyond Felipe's direct
  experience.
- Anything that would commit Felipe to action (interviews, contracts,
  meetings) — direct those to f.villegas@thinkelearn.com.
- General L&D essays or "what should we do about X in the field" — out
  of scope; this chat is about Felipe's specific work.
