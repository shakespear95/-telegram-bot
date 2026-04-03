"""Shakespear Takudzwa Samu - Complete professional profile.

This is injected into the system prompt so the bot can generate
tailored CVs for any role without asking for details already known.
"""

PROFILE = """
=== CANDIDATE PROFILE: SHAKESPEAR TAKUDZWA SAMU ===

LOCATION: St. Gallen, Switzerland
OPEN TO RELOCATION: Yes (e.g. Lisbon, Portugal; other locations as specified)

--- PROFESSIONAL EXPERIENCE ---

1) IT Support & Endpoint Engineer — H-Tech & Amaris (Consulting)
   Switzerland | May 2024 - Present
   Clients: Arval (BNP Paribas Group - Rotkreuz), Honeywell (Volketswil)
   - Manage complete employee IT onboarding and offboarding: account provisioning, device setup (Apple & Windows), onboarding calls, and equipment logistics
   - Oversee full device lifecycle using Apple Business Manager, Apple Configurator, Microsoft Intune, and Autopilot - prepare, enroll, ship, track, and collect hardware
   - Ensure all devices are MDM-enrolled with proper encryption, security policies, and endpoint compliance before deployment
   - Handle 30+ daily tickets in ServiceNow: hardware, software, access, and general tech issues - consistently meeting SLA targets
   - Administer SaaS licences and access controls in Microsoft 365 Admin Centre, Azure AD, and Active Directory
   - Build PowerShell and Python automations to streamline bulk user provisioning, software deployment, and recurring IT tasks
   - Leverage AI tools to accelerate troubleshooting, automate routine support workflows, and improve first-contact resolution rates
   - Perform server room operations including hardware installation, cable management, and UPS maintenance
   - Configure network printers and meeting room AV equipment in accordance with corporate standards
   - Manage IT asset inventory and lifecycle tracking using designated asset management tools
   - Coordinate with global IT teams and external service providers to deliver infrastructure changes and rollouts
   - Resolve complex technical incidents for VIP users and business-critical departments via ServiceNow
   - Coach end-users on IT tools and best practices; create user guides to improve IT self-service adoption
   - Support video conferencing systems, meeting rooms, and remote collaboration tools (Teams, Zoom)
   - Collaborate with security team on compliance, endpoint hardening, and continuous improvement of IT operations

2) Field Technical Engineer — Freelance/Contract
   Switzerland | February 2024 - May 2024
   Clients: Fossil, Cinted Global, RITUALS Cosmetics, Aspen Pharma
   - Executed on-site troubleshooting for Cisco and Meraki network infrastructure across multiple client sites
   - Managed secure IT asset decommissioning and issued certificates of destruction per corporate compliance policies
   - Provided ad hoc out-of-hours support for planned infrastructure changes and site migrations
   - Travelled to client locations nationally for onsite support, demonstrating flexibility and reliability
   - Delivered IT support across four international clients - device setup, network troubleshooting, and hardware logistics

3) IT Support Engineer — Econet Wireless
   Zimbabwe | August 2022 - January 2024
   - Provided Tier 1 & 2 support for a large-scale user base across distributed locations, both Apple and Windows environments
   - Configured and upgraded operating systems and critical business applications across the organisation
   - Managed local IT projects including equipment rollouts and infrastructure upgrades
   - Managed account lifecycle: provisioning, access controls, password management, and offboarding procedures
   - Acted as IT advocate with local management, communicating technology initiatives and improvements
   - Coordinated with external IT service providers for specialised maintenance and installations
   - Maintained documentation and knowledge base articles

4) Microwave Ablation R&D, IT Intern — ECO Medical Company
   China | October 2021 - June 2022
   - Resolved complex LAN/Wi-Fi infrastructure issues and supported internal IT operations
   - Integrated AI tools into sales workflows, improving team productivity

5) Sales Assistant & IT Intern — Nanjing Superstar Medical Company
   China | July 2020 - February 2021
   - Maintained video conferencing and meeting room systems, providing desk-side support in a global trade environment

--- EDUCATION ---

1) Master of Science in Information Systems — University of Liechtenstein (In Progress)
   Focus: Digital Transformation, Business Process Automation, Data Analytics
   Coursework: Networking fundamentals, IT service management, information security

2) Master of Engineering in Information and Communication Engineering
   Nanjing University of Posts and Telecommunications (July 2023)

3) Bachelor of Engineering in Electronics Information Engineering
   Nanjing University of Posts and Telecommunications (July 2020)

--- TECHNICAL SKILLS (comprehensive, select relevant ones per role) ---

Apple Ecosystem: Apple Business Manager (ABM), Apple Configurator, macOS, iOS, Apple device setup & enrollment, MDM deployment workflows
MDM & Deployment: Kandji (familiar), Microsoft Intune, Autopilot, SCCM, Podcom, OS Imaging & Provisioning
Windows & Linux: Windows 10/11, Windows Server, Linux (Ubuntu, CentOS) - installation, configuration, troubleshooting
Networking: Cisco, Meraki, Routing & Switching, LAN, TCP/IP, Wi-Fi, VPN, DNS, DHCP, Firewalls (Fortinet, pfSense), UPS Systems, Network Printer Configuration
System Administration: Active Directory, Azure AD, Microsoft 365 Admin, Google Workspace, Group Policy, User Lifecycle Management, Backup & Disaster Recovery
ITSM & Ticketing: ServiceNow, Freshservice (familiar), Zendesk (familiar), ITIL Framework, SLA Management
Monitoring: PRTG, Zabbix, SolarWinds
Virtualization & Servers: Hyper-V, VMware, Windows Server
SaaS Management: Microsoft 365 Admin, licence management, SaaS lifecycle workflows, cost optimisation, Trelica (familiar)
AI & Automation: AI-powered troubleshooting tools, workflow automation
Scripting & Tools: PowerShell, Python, Bash, JavaScript, Git
Cloud: AWS (Solutions Architect in progress), Azure, Office 365
Hardware: Server room racking/stacking, PCs, MacBooks, iPhones/iPads, monitors, printers, video conferencing systems, device logistics (prepare, ship, track, collect), asset decommissioning, Lexmark peripherals
Meeting Room Solutions: Video conferencing systems setup & maintenance, AV equipment support
Documentation: Knowledge base management, IT procedures, onboarding guides, compliance documentation
End-User Devices: PC, Laptop, Tablet, Smartphone hardware setup, imaging, troubleshooting & lifecycle management
Identity & Access: Account provisioning, access controls, MFA, encryption, endpoint security

--- CERTIFICATIONS ---

- Cisco CCNA Coursework Completed (Routing, Switching, VLANs, Subnetting, TCP/IP, Network Security - not yet examined)
- AWS Certified Solutions Architect (In Progress)
- Google IT Support Professional Certificate (2023)
- Front-end Web Development Bootcamp (Microverse)
- JavaScript Algorithms & Data Structures (Coursera)

--- PUBLICATIONS ---

- Samu, S. T., Zhang, S., & Magunda, S. (2023). 2023 IEEE 7th International Conference on Information Technology, Information Systems and Electrical Engineering (ICITISEE)
- Zhou, M., Samu, S. T., et al. (2022). Journal of Sol-Gel Science and Technology, 111(2), 421-429
- Wei, B., Samu, S. T., et al. (2024). 2024 22nd International Conference on Optical Communications and Networks (ICOCN)

--- LANGUAGES ---

- English (Bilingual/Fluent)
- Shona (Native)
- Mandarin Chinese (Intermediate)
- German (B1)

--- CV GENERATION INSTRUCTIONS ---

CORE PRINCIPLE: Truth-preserving optimization — maximize fit while maintaining
factual integrity. NEVER fabricate experience, but intelligently reframe and
emphasize relevant aspects of real experience.

=== STEP 1: JOB DESCRIPTION ANALYSIS ===

When the user provides a job description (or you fetched one via get_job_details),
parse it to extract:
1. EXPLICIT REQUIREMENTS (must-have vs nice-to-have)
2. TECHNICAL KEYWORDS and domain terminology
3. IMPLICIT PREFERENCES (cultural signals, hidden requirements)
4. ROLE ARCHETYPE (IC technical / people leadership / cross-functional)

=== STEP 2: CONTENT MATCHING (Confidence Scoring) ===

For each requirement in the JD, score Shakespear's experience using:
- Direct Match (40%): Same skill, domain, technology, outcome type
- Transferable Skills (30%): Same capability in different context
- Adjacent Experience (20%): Related tools/methods, supporting role
- Impact Alignment (10%): Achievement type matches what role values

Overall = (Direct x 0.4) + (Transferable x 0.3) + (Adjacent x 0.2) + (Impact x 0.1)

Confidence Bands:
- 90-100%: DIRECT — use with confidence
- 75-89%: TRANSFERABLE — strong candidate, reframe terminology
- 60-74%: ADJACENT — acceptable with reframing
- 45-59%: WEAK — consider only if no better option
- <45%: GAP — flag as unaddressed, recommend cover letter

=== STEP 3: CONTENT REFRAMING STRATEGIES ===

When match is good (>60%) but language doesn't align with target terminology:

Strategy 1 — Keyword Alignment: Preserve meaning, adjust terminology
  Before: "Manage device lifecycle using Apple Business Manager"
  After:  "Manage enterprise endpoint lifecycle including provisioning,
           MDM enrollment, and secure decommissioning"
  Reason: Target role uses "endpoint management" terminology

Strategy 2 — Emphasis Shift: Same facts, different focus
  Before: "Handle 30+ daily tickets in ServiceNow"
  After:  "Resolve 30+ technical incidents daily, consistently meeting
           SLA targets across hardware, software, and access issues"
  Reason: Target role values incident resolution over ticket handling

Strategy 3 — Abstraction Level: Adjust technical specificity
  Before: "Build PowerShell and Python automations"
  After:  "Develop automation solutions to streamline bulk provisioning
           and recurring IT operations"
  Reason: Target role is tool-agnostic, emphasize outcomes

Strategy 4 — Scale Emphasis: Highlight relevant scale aspects
  Before: "Support video conferencing systems"
  After:  "Manage enterprise collaboration infrastructure including
           video conferencing, AV equipment, and remote tools (Teams, Zoom)"
  Reason: Emphasize enterprise scale over task description

=== STEP 4: RESUME ASSEMBLY RULES ===

1. TAILOR the CV to the specific job/role. Adjust summary, skills, and
   bullet ordering to match the target role.
2. The job title under the name should match the target role.
3. Select only the most relevant technical skills — do not dump everything.
4. Rewrite the professional summary to align with the JD using matched
   keywords and the company's terminology.
5. For experience bullets, lead with highest-confidence matches first.
6. Always include Education, Certifications, Publications, and Languages.
7. Contact details (phone, email) should be asked from the user if not
   provided — never invent them.
8. Keep the CV to 2 pages maximum.
9. Use strong action verbs and quantify achievements where possible.
10. When presenting the CV plan to the user, mention your confidence
    scores and any gaps you identified so they can provide additional
    context if needed.

=== STEP 5: EXPERIENCE DISCOVERY (when gaps found) ===

If confidence <60% on critical requirements, ask the user branching
questions to surface undocumented experiences:
- "The role requires {SKILL}. Have you worked with this or anything related?"
- If YES: "Tell me more — what scale? What challenges? Any metrics?"
- If INDIRECT: "What was your role in relation to {SKILL} work?"
- If ADJACENT: "Tell me about your {ADJACENT_TECH} experience"
- If PERSONAL: "Any personal projects, courses, or self-learning?"
- After 2-3 attempts with no result, move on gracefully.

=== STEP 6: GAP HANDLING ===

For unaddressed requirements:
- Recommend addressing in a cover letter
- Suggest emphasizing learning ability and adjacent skills
- Never fabricate or exaggerate experience to fill gaps
- Be transparent with the user about what's missing
""".strip()
