from sqlalchemy.orm import Session
from app.models import Category, Skill, SkillModule, TrainingCentre, Trainer, TrainingProgram, Batch

CATEGORIES_DATA = [
    {"code": "CAT-0001", "name": "Programming & IT", "icon_name": "Code", "description": "Core software development, object-oriented languages, and scripting."},
    {"code": "CAT-0002", "name": "Web Development", "icon_name": "Globe", "description": "Frontend, backend, modern full-stack web architectures and UI frameworks."},
    {"code": "CAT-0003", "name": "Data Science & AI", "icon_name": "Cpu", "description": "Data analytics, machine learning, deep learning, NLP, and GenAI."},
    {"code": "CAT-0004", "name": "Cloud & DevOps", "icon_name": "Cloud", "description": "Cloud computing, containerization, orchestration, and CI/CD pipelines."},
    {"code": "CAT-0005", "name": "Cybersecurity & Networks", "icon_name": "Shield", "description": "Information security, network engineering, ethical hacking, and SOC."},
    {"code": "CAT-0006", "name": "Software Testing & QA", "icon_name": "CheckCircle2", "description": "Manual testing, Selenium automation, API testing, and performance testing."},
    {"code": "CAT-0007", "name": "Business & Finance", "icon_name": "Briefcase", "description": "Accounting, Tally Prime, financial analysis, banking, and management."},
    {"code": "CAT-0008", "name": "Digital Marketing & Media", "icon_name": "Share2", "description": "Search engine marketing, social media strategy, content, and e-commerce."},
    {"code": "CAT-0009", "name": "Technical & Engineering Trades", "icon_name": "Wrench", "description": "Electrical wiring, solar PV installation, CNC machining, and mechatronics."},
    {"code": "CAT-0010", "name": "Healthcare & Vocational", "icon_name": "Activity", "description": "Healthcare assistance, pharmacy support, organic farming, and hospitality."},
]

CENTRES_DATA = [
    {
        "code": "CTR-0001",
        "name": "Bengaluru Central Skill Hub (Rajajinagar)",
        "location": "Dr. Rajkumar Road, Rajajinagar, Bengaluru",
        "district": "Bengaluru Urban",
        "state": "Karnataka",
        "address": "NagrikSetu Skilling Tower, 4th Block, Rajajinagar, Bengaluru - 560010",
        "contact_phone": "+91 80 2345 6789",
        "contact_email": "bengaluru.hub@nagriksetu.gov.in",
        "delivery_modes": "Classroom, Hybrid, Online",
        "facilities": "Advanced Cloud Computing Lab, Robotics & IoT Sandbox, Smart Lecture Hall, Fiber Wi-Fi, Dedicated Interview Practice Studios",
        "latitude": 12.9874184,
        "longitude": 77.5571278,
    },
    {
        "code": "CTR-0002",
        "name": "Mysuru Regional Skilling Institute",
        "location": "Vijayanagar 2nd Stage, Mysuru",
        "district": "Mysuru",
        "state": "Karnataka",
        "address": "KSSIDC Industrial Estate, Hunsur Road, Vijayanagar, Mysuru - 570017",
        "contact_phone": "+91 821 245 8890",
        "contact_email": "mysuru.centre@nagriksetu.gov.in",
        "delivery_modes": "Classroom, Hybrid, Online",
        "facilities": "Hardware Testing Benches, Full Stack Coding Suites, Placement Assistance Desk, Seminar Hall",
        "latitude": 12.3372923,
        "longitude": 76.6073668,
    },
    {
        "code": "CTR-0003",
        "name": "Hubballi-Dharwad Tech Development Centre",
        "location": "Gokul Road, Hubballi",
        "district": "Dharwad",
        "state": "Karnataka",
        "address": "Aryabhata Tech Park, Navanagar, Hubballi - 580025",
        "contact_phone": "+91 836 223 4455",
        "contact_email": "hubballi.centre@nagriksetu.gov.in",
        "delivery_modes": "Classroom, Hybrid",
        "facilities": "CNC Machine Simulators, Electronics Prototyping Lab, Multimedia Studio",
        "latitude": 15.3938408,
        "longitude": 75.0820943,
    },
    {
        "code": "CTR-0004",
        "name": "Mangaluru Coastal Skill Academy",
        "location": "Kadri Hills, Mangaluru",
        "district": "Dakshina Kannada",
        "state": "Karnataka",
        "address": "Near Circuit House, Kadri, Mangaluru - 575004",
        "contact_phone": "+91 824 221 7788",
        "contact_email": "mangaluru.centre@nagriksetu.gov.in",
        "delivery_modes": "Classroom, Hybrid, Online",
        "facilities": "High-Speed Virtual Desktop Infrastructure, Digital Media Room, Audio-Visual Conference Lab",
        "latitude": 12.8878464,
        "longitude": 74.8521921,
    },
    {
        "code": "CTR-0005",
        "name": "NagrikSetu Virtual Learning Portal",
        "location": "National Digital Platform (Online)",
        "district": "Pan-India",
        "state": "National",
        "address": "NagrikSetu Cloud Operations, New Delhi",
        "contact_phone": "1800-11-2026",
        "contact_email": "support.elearning@nagriksetu.gov.in",
        "delivery_modes": "Online Self-Paced, Online Live",
        "facilities": "24/7 Cloud Lab Environments, Interactive Doubt Clearance Forums, On-demand Coding Sandboxes",
        "latitude": None,
        "longitude": None,
    },
]

TRAINERS_DATA = [
    {
        "code": "TRN-0001",
        "name": "Dr. Rajeshwar Sharma",
        "qualification": "M.Tech in CSE, Ph.D. in Distributed Systems",
        "specialisation": "Enterprise Java, Spring Boot & Microservices",
        "experience_years": 14,
        "contact_email": "r.sharma@nagriksetu.gov.in",
        "assigned_centre_id": 1,
        "availability": "Weekdays & Weekends",
    },
    {
        "code": "TRN-0002",
        "name": "Ananya Kulkarni",
        "qualification": "B.E. in Information Science, AWS Certified Solutions Architect",
        "specialisation": "Cloud Architecture (AWS/Azure) & DevOps Pipelines",
        "experience_years": 9,
        "contact_email": "ananya.k@nagriksetu.gov.in",
        "assigned_centre_id": 1,
        "availability": "Morning Batches",
    },
    {
        "code": "TRN-0003",
        "name": "Vikramaditya Hegde",
        "qualification": "M.Sc. in Data Science, Ex-Senior ML Engineer",
        "specialisation": "Data Science, Python, Deep Learning & GenAI",
        "experience_years": 11,
        "contact_email": "vikram.hegde@nagriksetu.gov.in",
        "assigned_centre_id": 2,
        "availability": "Evening Batches & Weekends",
    },
    {
        "code": "TRN-0004",
        "name": "Pooja Venkatesh",
        "qualification": "B.Tech in Computer Science, ISTQB Certified",
        "specialisation": "Selenium Automation Testing, Cypress & QA Engineering",
        "experience_years": 8,
        "contact_email": "pooja.v@nagriksetu.gov.in",
        "assigned_centre_id": 1,
        "availability": "Weekdays",
    },
    {
        "code": "TRN-0005",
        "name": "Manjunath Gowda",
        "qualification": "Diploma in Electrical Engg, Certified Energy Auditor",
        "specialisation": "Solar PV Rooftop Installation & Industrial Electrical Systems",
        "experience_years": 16,
        "contact_email": "manju.gowda@nagriksetu.gov.in",
        "assigned_centre_id": 3,
        "availability": "Full Time",
    },
    {
        "code": "TRN-0006",
        "name": "Farhana Banu",
        "qualification": "MBA in Finance, Tally Certified Professional",
        "specialisation": "Tally Prime, GST Accounting & Corporate Taxation",
        "experience_years": 10,
        "contact_email": "farhana.b@nagriksetu.gov.in",
        "assigned_centre_id": 4,
        "availability": "Morning & Afternoon",
    },
]

# Definition of 105 distinct, realistic, high-value skills across all 10 categories
SKILL_DEFINITIONS = [
    # 1. Programming & IT
    ("Python Programming", "CAT-0001", "Beginner", 6, 40, "Master core Python syntax, OOP, exception handling, data structures, and script automation.", ["Syntax & Flow Control", "Data Structures & Functions", "Object-Oriented Programming", "File I/O & Modules", "Capstone Automation Script"]),
    ("Advanced Python & Concurrency", "CAT-0001", "Advanced", 8, 50, "Asynchronous programming, multithreading, generators, metaclasses, and high-performance algorithms.", ["Generators & Iterators", "Decorators & Metaprogramming", "AsyncIO & Concurrency", "Memory Management & Profiling", "Distributed Task Queues"]),
    ("Java Development Fundamentals", "CAT-0001", "Beginner", 8, 60, "Foundational Java syntax, JVM architecture, classes, collections framework, and clean code principles.", ["Java Basics & JVM Internals", "OOPs & Interfaces", "Collections & Generics", "Exception Handling & Streams", "Mini Library Management System"]),
    ("Enterprise Java & Spring Boot", "CAT-0001", "Intermediate", 10, 75, "Production-grade microservices with Spring Boot, Spring Data JPA, security, and RESTful APIs.", ["Spring Core & DI", "Spring Boot Architecture", "Spring Data JPA & Hibernate", "Spring Security & JWT", "Microservices Project"]),
    ("C Programming Foundations", "CAT-0001", "Beginner", 6, 45, "Memory management, pointers, dynamic memory allocation, structs, and low-level system interactions.", ["Variables & Control Flow", "Functions & Arrays", "Pointers & Dynamic Memory", "File Operations & Preprocessors", "Memory Profiling Project"]),
    ("Modern C++ & STL", "CAT-0001", "Intermediate", 8, 55, "Object-oriented design in modern C++20, templates, standard template library, and smart pointers.", ["OOP in C++", "Templates & Metaprogramming", "STL Containers & Algorithms", "Smart Pointers & RAII", "High Performance Cache App"]),
    ("C# and .NET Core Development", "CAT-0001", "Intermediate", 8, 60, "Enterprise application engineering using C#, ASP.NET Core Web APIs, Entity Framework, and LINQ.", ["C# Syntax & OOP", "LINQ & Collections", "ASP.NET Core Web API", "Entity Framework Core", "Clean Architecture Web Service"]),
    ("Go (Golang) Microservices", "CAT-0001", "Intermediate", 7, 50, "Build lightweight, concurrency-driven cloud microservices with Goroutines, channels, and Gin framework.", ["Go Fundamentals", "Goroutines & Channels", "HTTP Servers with Gin", "gRPC & Protobuf", "Resilient Payment Microservice"]),
    ("Rust Systems Programming", "CAT-0001", "Advanced", 9, 65, "Memory safety without garbage collection, borrow checker, concurrency, and robust CLI tooling.", ["Rust Basics & Ownership", "Borrowing & Lifetimes", "Traits & Pattern Matching", "Concurrency & Fearless Multithreading", "Fast File Indexer CLI"]),
    ("Bash Shell Scripting & Linux Command Line", "CAT-0001", "Beginner", 4, 30, "System administration scripts, process automation, grep/sed/awk pipelines, and server provisioning.", ["Linux File Hierarchy", "Permissions & Process Control", "Pipes, Sed & Awk", "Bash Logic & Cron Automation", "Automated Server Backup Script"]),
    ("Kotlin for Android & Backend", "CAT-0001", "Intermediate", 7, 50, "Coroutines, null safety, Android Jetpack, and modern server-side development with Ktor.", ["Kotlin Core & Idioms", "Coroutines & Flow", "Android UI with Jetpack Compose", "Networking & Persistence", "Mobile Civic Reporter App"]),

    # 2. Web Development
    ("HTML5 & Modern CSS3", "CAT-0002", "Beginner", 4, 30, "Semantic markup, Flexbox, CSS Grid, media queries, animations, and accessible web standards.", ["Semantic HTML & Forms", "CSS Fundamentals & Box Model", "Flexbox & CSS Grid Layouts", "Responsive Design & Transitions", "Accessible Government Portal Replica"]),
    ("JavaScript Deep Dive (ES6+)", "CAT-0002", "Intermediate", 6, 45, "Closures, event loops, promises, async/await, DOM manipulation, and modern modular architecture.", ["Data Types & Scopes", "DOM & Event Handling", "Asynchronous JS & Fetch API", "Prototypes, Classes & ES Modules", "Interactive Dashboard Widget"]),
    ("TypeScript for Modern Applications", "CAT-0002", "Intermediate", 6, 40, "Static typing, interfaces, generics, utility types, and strict mode integration with frontends.", ["Type Annotations & Unions", "Interfaces & Type Aliases", "Generics & Constraints", "Advanced Utility Types", "Type-Safe Application Core"]),
    ("React.js Frontend Development", "CAT-0002", "Intermediate", 8, 60, "Component lifecycles, hooks, context API, state management, and reusable UI architecture.", ["JSX & Functional Components", "State, Props & Hooks", "Custom Hooks & Context", "Routing & Form Handling", "Full Citizen Services Dashboard"]),
    ("Next.js & Server-Side Rendering", "CAT-0002", "Advanced", 8, 55, "App router, SSR, SSG, server actions, route handlers, and performance optimization.", ["App Router Architecture", "SSR vs SSG vs ISR", "Server Actions & Mutations", "Authentication & Middleware", "Production-Ready Public Portal"]),
    ("Node.js & Express API Engineering", "CAT-0002", "Intermediate", 7, 50, "Event-driven architecture, middleware design, JWT auth, database connectivity, and REST endpoints.", ["Node.js Runtime & Event Loop", "Express Routing & Middleware", "RESTful Architecture & Validation", "Database Integration (MongoDB/Postgres)", "Production API with Rate Limiting"]),
    ("FastAPI Python Backend Development", "CAT-0002", "Intermediate", 6, 45, "Asynchronous endpoints, Pydantic data schemas, SQLAlchemy ORM, automatic OpenAPI, and auth.", ["FastAPI Core & Type Hints", "Pydantic Models & Validation", "SQLAlchemy 2.0 & DB Sessions", "Security, OAuth2 & JWT", "Citizen Verification Microservice"]),
    ("Django Enterprise Web Framework", "CAT-0002", "Intermediate", 8, 60, "MVT architecture, Django ORM, admin dashboard, authentication, migrations, and template engines.", ["Django Architecture & Routing", "Models, Migrations & Queries", "Django Forms & Class-Based Views", "Django REST Framework (DRF)", "Multi-Tenant Welfare Portal"]),
    ("Full Stack MERN Development", "CAT-0002", "Advanced", 12, 90, "End-to-end web engineering combining MongoDB, Express, React, and Node.js with secure auth.", ["Database Design in MongoDB", "Express API Architecture", "React State & Integration", "JWT Authentication & RBAC", "End-to-End Enterprise Web Application"]),
    ("Tailwind CSS & Design Systems", "CAT-0002", "Beginner", 4, 30, "Utility-first styling, component composition, responsive tokens, dark mode, and themes.", ["Tailwind Core Principles", "Layouts, Flex & Grid", "Component Composition & Variants", "Dark Mode & Theme Configuration", "Accessible Component Library"]),

    # 3. Data Science & AI
    ("Data Analysis with Python (Pandas/NumPy)", "CAT-0003", "Beginner", 6, 45, "Tabular data wrangling, cleaning missing values, NumPy matrix calculations, and aggregations.", ["NumPy Arrays & Vectorization", "Pandas Series & DataFrames", "Data Cleaning & Imputation", "Time Series & GroupBy Analysis", "State Demographics Analytics"]),
    ("Data Visualisation (Matplotlib & Seaborn)", "CAT-0003", "Beginner", 4, 30, "Statistical charting, colour theory, exploratory data analysis dashboards, and reports.", ["Plotting Fundamentals", "Statistical Visuals with Seaborn", "Interactive Visuals with Plotly", "Storytelling with Data", "Citizen Welfare Insights Report"]),
    ("Applied Machine Learning with Scikit-Learn", "CAT-0003", "Intermediate", 8, 60, "Supervised & unsupervised learning, regression, classification, clustering, cross-validation.", ["Data Preprocessing & Splitting", "Classification Algorithms", "Regression & Tree-Based Models", "Clustering & Dimensionality Reduction", "Predictive Employment Matcher"]),
    ("Deep Learning & Neural Networks with PyTorch", "CAT-0003", "Advanced", 10, 75, "Tensors, backpropagation, CNNs for computer vision, RNNs, and custom model training pipelines.", ["PyTorch Tensors & Autograd", "Building Dense Neural Networks", "Convolutional Neural Networks (CNNs)", "Transfer Learning & Optimization", "Medical Image Screening Prototype"]),
    ("Natural Language Processing (NLP)", "CAT-0003", "Intermediate", 8, 55, "Tokenization, embeddings, sentiment analysis, TF-IDF, Word2Vec, and sequence models.", ["Text Preprocessing & Regex", "Feature Extraction & Embeddings", "Sentiment Classification", "Named Entity Recognition (NER)", "Citizen Grievance Classifier"]),
    ("Generative AI & LLM Prompt Engineering", "CAT-0003", "Beginner", 6, 40, "Prompt patterns, system prompts, retrieval-augmented generation (RAG), and API integrations.", ["Foundations of LLMs", "Prompt Engineering Frameworks", "Vector Databases & Embeddings", "Building RAG Applications", "Multilingual Citizen Chat Assistant"]),
    ("Computer Vision with OpenCV", "CAT-0003", "Intermediate", 7, 50, "Image filtering, edge detection, object tracking, face recognition, and optical character recognition.", ["Image Transformations & Filtering", "Contour Detection & Thresholding", "Object Tracking & Video Feeds", "OCR for Government Document Verification", "Real-Time ID Verification Pipeline"]),
    ("Time Series Forecasting", "CAT-0003", "Intermediate", 6, 40, "ARIMA, SARIMA, Prophet, trend decomposition, seasonality analysis, and demand forecasting.", ["Stationarity & Autocorrelation", "ARIMA & SARIMAX Modeling", "Facebook Prophet Implementation", "Evaluation Metrics & Forecasting", "Crop Yield & Employment Forecaster"]),
    ("Big Data Processing with Apache Spark", "CAT-0003", "Advanced", 8, 60, "PySpark, RDDs, DataFrames, Spark SQL, and distributed data transformations on large clusters.", ["Spark Architecture & Clustered Compute", "PySpark DataFrames & Transformations", "Spark SQL & Window Functions", "Streaming Data Pipelines", "Large-Scale Welfare Disbursement Engine"]),
    ("Business Intelligence with Power BI", "CAT-0003", "Beginner", 6, 40, "Data modelling, DAX formulas, interactive reports, visual KPIs, and scheduled dataset refreshes.", ["Data Connection & Power Query", "Star Schema Data Modeling", "DAX Measures & Calculated Columns", "Report Design & Drill-Downs", "Executive Skilling Metrics Dashboard"]),
    ("Data Storytelling with Tableau", "CAT-0003", "Beginner", 6, 40, "Calculated fields, parameters, dashboard design, geocoding maps, and business storyboards.", ["Tableau Architecture & Connectors", "Charts, Dual-Axis & Trendlines", "LOD Expressions & Filters", "Storyboards & Public Deployment", "District Skilling Heatmap"]),

    # 4. Cloud & DevOps
    ("AWS Cloud Practitioner Essentials", "CAT-0004", "Beginner", 6, 40, "Global infrastructure, IAM, EC2, S3, RDS, VPC basics, cloud economics, and billing.", ["Cloud Computing Fundamentals", "AWS Identity & Access Management (IAM)", "Compute (EC2) & Storage (S3)", "Databases (RDS/DynamoDB) & Security", "Deploying a Secure Multi-Tier App"]),
    ("AWS Solutions Architect Associate Track", "CAT-0004", "Advanced", 10, 75, "High-availability architectures, VPC peering, auto-scaling, load balancing, Route 53, and cost.", ["VPC Design & Subnet Routing", "High Availability & Elastic Load Balancing", "Serverless with Lambda & API Gateway", "Disaster Recovery & Cost Optimization", "Resilient State Government Portal on AWS"]),
    ("Microsoft Azure Fundamentals (AZ-900)", "CAT-0004", "Beginner", 5, 35, "Azure core services, resource groups, storage accounts, virtual networks, and governance.", ["Azure Architecture & SLAs", "Compute, Network & Storage Services", "Azure Active Directory / Entra ID", "Security, Privacy & Compliance", "Cloud Migration Business Case"]),
    ("Google Cloud Platform (GCP) Fundamentals", "CAT-0004", "Beginner", 5, 35, "Compute Engine, Cloud Storage, BigQuery, IAM roles, and serverless Cloud Run deployments.", ["GCP Infrastructure Overview", "Compute Engine & GKE Basics", "BigQuery Analytics & Cloud Storage", "IAM & Service Accounts", "Deploying Containerized Web Service"]),
    ("Docker & Containerization", "CAT-0004", "Intermediate", 5, 35, "Dockerfiles, multi-stage builds, volume mounts, networking, and Docker Compose orchestration.", ["Container Concepts vs VMs", "Writing Efficient Dockerfiles", "Storage Volumes & Host Bindings", "Docker Networking & Multi-Container Apps", "Dockerized Microservice Environment"]),
    ("Kubernetes Administration (CKA Prep)", "CAT-0004", "Advanced", 10, 75, "Pods, Deployments, Services, ConfigMaps, Ingress controllers, StatefulSets, and Helm charts.", ["K8s Architecture & Control Plane", "Pods, ReplicaSets & Deployments", "Cluster Networking & Ingress Controllers", "Persistent Volumes & Storage Classes", "Deploying Zero-Downtime Microservice Cluster"]),
    ("CI/CD Automation with GitHub Actions", "CAT-0004", "Intermediate", 5, 35, "Automated test pipelines, matrix testing, Docker publishing, and automated releases.", ["Workflow YAML Syntax", "Testing & Linting Automations", "Secrets Management & Environments", "Building & Pushing Containers to Registry", "Automated End-to-End Release Pipeline"]),
    ("Infrastructure as Code with Terraform", "CAT-0004", "Intermediate", 7, 50, "HCL syntax, state management, modules, remote backends, and multi-cloud provisioning.", ["Terraform Basics & State Files", "Resource Declarations & Variables", "Terraform Modules & Reusability", "Remote State Locking with S3/DynamoDB", "Automated Cloud Infrastructure Setup"]),
    ("DevOps Monitoring with Prometheus & Grafana", "CAT-0004", "Intermediate", 5, 35, "Metric scraping, PromQL queries, alertmanager configurations, and visual performance dashboards.", ["Observability Concepts (Metrics, Logs, Traces)", "Prometheus Node Exporter & Scraping", "Grafana Dashboard Construction", "Alertmanager & Slack/Email Alerts", "Full Microservice Health Dashboard"]),
    ("Site Reliability Engineering (SRE) Principles", "CAT-0004", "Advanced", 6, 45, "SLIs, SLOs, error budgets, incident post-mortems, chaos engineering, and blameless culture.", ["SRE Core Philosophy & Error Budgets", "Defining Actionable SLIs and SLOs", "On-Call, Incident Management & Runbooks", "Capacity Planning & Chaos Experiments", "Resilience Review for Mission-Critical Service"]),

    # 5. Cybersecurity & Networks
    ("Cybersecurity Fundamentals", "CAT-0005", "Beginner", 6, 40, "Threat landscape, CIA triad, phishing prevention, encryption principles, and digital hygiene.", ["Information Security Principles", "Malware Types & Threat Vectors", "Cryptography (Symmetric vs Asymmetric)", "Network Defense & Perimeter Security", "Organizational Security Assessment"]),
    ("Ethical Hacking & Penetration Testing", "CAT-0005", "Advanced", 10, 75, "Reconnaissance, Nmap, Metasploit, web vulnerability exploitation, privilege escalation, and reports.", ["Reconnaissance & Footprinting", "Vulnerability Scanning with Nmap/OpenVAS", "Exploitation Techniques & Payloads", "Post-Exploitation & Reporting", "Simulated Vulnerability Audit"]),
    ("Web Application Security (OWASP Top 10)", "CAT-0005", "Intermediate", 7, 50, "SQL injection, XSS, CSRF, broken access control, security headers, and secure coding.", ["OWASP Top 10 Breakdown", "Injection Vulnerabilities & Mitigation", "Broken Authentication & Session Hijacking", "Security Headers & CSP", "Securing Vulnerable Public Portal"]),
    ("CompTIA Network+ / Computer Networking", "CAT-0005", "Beginner", 6, 45, "OSI model, TCP/IP, IP subnetting, DNS, DHCP, routing protocols, VLANs, and cabling.", ["OSI & TCP/IP Layer Model", "IPv4 Addressing & Subnet Calculation", "Routing, Switching & VLANs", "Core Protocols (DNS, DHCP, HTTPS)", "Network Topology Simulation"]),
    ("Cisco CCNA Routing & Switching", "CAT-0005", "Intermediate", 10, 80, "Cisco IOS configuration, OSPF, STP, Access Control Lists (ACLs), NAT, and wireless LANs.", ["Cisco CLI & Router Setup", "VLANs & Inter-VLAN Routing", "OSPF Routing Protocol", "ACL Security & NAT Configuration", "Enterprise Branch Network Architecture"]),
    ("SOC Analyst & Incident Response", "CAT-0005", "Intermediate", 8, 60, "Log analysis, SIEM tools (Splunk/Wazuh), threat hunting, IoCs, and incident containment.", ["SOC Architecture & Roles", "SIEM Fundamentals & Log Parsing", "Detecting Attacks & Analyzing IoCs", "Incident Response Playbooks", "Simulated Ransomware Incident Response"]),
    ("Information Security Auditing (ISO 27001)", "CAT-0005", "Intermediate", 6, 40, "ISMS policies, risk assessments, security controls, compliance frameworks, and internal audit.", ["ISO 27001 Standards & Scope", "Risk Assessment Methodologies", "Statement of Applicability (SoA)", "Audit Checklists & Evidence Gathering", "Mock Governance Audit Documentation"]),

    # 6. Software Testing & QA
    ("Manual Software Testing Foundations", "CAT-0006", "Beginner", 6, 40, "SDLC/STLC models, test case writing, bug life cycles, exploratory testing, and Jira.", ["Software Quality Fundamentals", "Test Design Techniques (BVA, ECP)", "Writing Effective Test Cases", "Defect Logging & Severity/Priority", "Complete Test Suite for Citizen Registration"]),
    ("Selenium WebDriver with Java", "CAT-0006", "Intermediate", 8, 60, "Locators, Page Object Model (POM), TestNG, handling dynamic elements, and extent reports.", ["Selenium Architecture & Browser Setup", "Locator Strategies (XPath, CSS)", "Page Object Model Framework", "TestNG Annotations & Assertions", "Automated E2E Regression Suite"]),
    ("Selenium WebDriver with Python", "CAT-0006", "Intermediate", 7, 50, "PyTest test runner, browser automation, waits, actions chains, and HTML reporting.", ["Browser Automation with PyTest", "Explicit & Implicit Waits", "POM Pattern in Python", "Data-Driven Testing with Excel/CSV", "Automated Portal Smoke Test Suite"]),
    ("API Testing with Postman & Newman", "CAT-0006", "Beginner", 5, 35, "REST API verification, assertions, variables, environment scripts, collections, and CLI runners.", ["HTTP Protocol & REST Verification", "Writing JavaScript Test Assertions", "Environment & Global Variables", "Data-Driven Collections", "Automated Newman CI Execution"]),
    ("Performance Testing with Apache JMeter", "CAT-0006", "Intermediate", 6, 45, "Thread groups, samplers, listeners, timers, non-GUI executions, load and stress test reports.", ["Performance Testing Concepts", "JMeter Test Plan Architecture", "Samplers, Assertions & Timers", "Load, Stress & Spike Testing", "High-Volume Citizen Portal Load Test"]),
    ("Cypress Modern Web Automation", "CAT-0006", "Intermediate", 7, 50, "Fast, developer-friendly end-to-end testing, fixtures, intercepting network calls, and CI.", ["Cypress Installation & Architecture", "Writing Tests & Selectors", "Network Intercepts & Mocking", "Custom Commands & Plugins", "Modern UI Automation Pipeline"]),
    ("Mobile App Testing with Appium", "CAT-0006", "Intermediate", 7, 50, "Android/iOS app automation, appium inspector, gestures, and test runner integration.", ["Mobile Testing Ecosystem", "Appium Server & Client Setup", "Locating Mobile UI Elements", "Touch Actions & Gestures", "Automated Mobile Citizen App Suite"]),

    # 7. Business & Finance
    ("Tally Prime with GST & E-Way Bills", "CAT-0007", "Beginner", 6, 45, "Company creation, ledger posting, GST invoicing, input tax credit, and financial reporting.", ["Accounting Foundations & Double Entry", "Tally Prime Company Setup & Ledgers", "Voucher Entries & Inventory Setup", "GST Rates, HSN Codes & Invoicing", "Real Business Financial Audit Project"]),
    ("Advanced Excel for Business Analytics", "CAT-0007", "Beginner", 5, 35, "VLOOKUP/XLOOKUP, Pivot Tables, conditional formatting, what-if analysis, and basic macros.", ["Formulas & Logical Functions", "XLOOKUP, INDEX & MATCH", "Pivot Tables & Pivot Charts", "Data Validation & Conditional Formatting", "Business Financial Modeling Sheet"]),
    ("Financial Accounting & Bookkeeping", "CAT-0007", "Beginner", 6, 40, "Trial balance, profit & loss statement, balance sheet, bank reconciliation, and cash flow.", ["Accounting Principles & Standards", "Journalizing & Ledger Postings", "Bank Reconciliation Statements", "Final Accounts (P&L, Balance Sheet)", "Annual Financial Statement Compilation"]),
    ("Banking Operations & Retail Services", "CAT-0007", "Beginner", 6, 40, "KYC guidelines, retail lending, deposit products, digital payments (UPI/NEFT), and fraud.", ["Indian Banking Structure & RBI Norms", "KYC & Anti-Money Laundering Checks", "Retail Credit & Loan Appraisals", "Digital Banking & Cybersecurity in Banking", "Customer Case Study & Audit"]),
    ("Corporate Financial Modeling", "CAT-0007", "Advanced", 8, 55, "Discounted cash flows (DCF), 3-statement models, valuation metrics, and sensitivity tables.", ["3-Statement Financial Modeling", "Forecasting Revenue & Working Capital", "DCF Valuation & WACC Calculation", "Scenario & Sensitivity Analysis", "Full Company Valuation Deck"]),
    ("Entrepreneurship & Small Business Setup", "CAT-0007", "Beginner", 6, 40, "Business ideation, MSME registration, business model canvas, government loan schemes (PMEGP).", ["Ideation & Market Opportunity", "Business Model Canvas (BMC)", "MSME Schemes & Financial Aid", "Compliance, Licensing & Operations", "Ready-to-Pitch Small Business Plan"]),
    ("Agile & Scrum Project Management", "CAT-0007", "Beginner", 5, 35, "Scrum framework, sprint planning, backlog refinement, user stories, retrospectives, and Jira.", ["Agile Manifesto & Scrum Principles", "Roles: Scrum Master, Product Owner, Devs", "Sprint Ceremonies & Estimation", "Jira Software Setup & Burndown Charts", "Sprint Simulation Project"]),
    ("Business Analysis Fundamentals", "CAT-0007", "Intermediate", 6, 45, "Requirements gathering, BRD/FRD preparation, process modeling with BPMN, and user acceptance.", ["Business Analyst Role & Lifecycle", "Requirements Elicitation Techniques", "Writing BRD, FRD & Use Cases", "BPMN Flowcharts & Wireframes", "Citizen Portal Workflow Modernization Case"]),

    # 8. Digital Marketing & Media
    ("Digital Marketing Fundamentals", "CAT-0008", "Beginner", 6, 40, "Digital marketing channels, customer personas, conversion funnels, and marketing metrics.", ["Digital Landscape & Audience Personas", "Content Marketing Strategy", "Social Media Marketing Foundations", "Email Marketing & Newsletters", "Comprehensive Digital Strategy Pitch"]),
    ("Search Engine Optimization (SEO)", "CAT-0008", "Intermediate", 6, 40, "Keyword research, on-page optimization, technical SEO, link building, and Google Search Console.", ["Keyword Research & Search Intent", "On-Page SEO & Content Strategy", "Technical SEO (Crawlability, Core Web Vitals)", "Backlink Strategies & Analytics", "Complete Organic Growth Audit"]),
    ("Google Ads & Performance Marketing", "CAT-0008", "Intermediate", 6, 40, "Search ads, display networks, YouTube campaigns, keyword bidding, quality score, and ROAS.", ["Google Ads Account Architecture", "Search Campaign Setup & Ad Copy", "Bidding Strategies & Quality Score", "Display & Video Campaigns", "High-ROI Paid Advertising Campaign"]),
    ("Social Media Marketing & Brand Building", "CAT-0008", "Beginner", 5, 35, "Instagram, LinkedIn, Facebook marketing, content calendars, engagement strategies, and ads.", ["Platform Demographics & Algorithms", "Content Creation & Scheduling", "Paid Social Ads & Audience Targeting", "Influencer Collaboration Basics", "Community Building & Crisis Handling"]),
    ("UI/UX Design with Figma", "CAT-0008", "Beginner", 7, 50, "User research, wireframing, component design systems, auto-layout, prototyping, and usability.", ["Design Thinking & User Research", "Wireframing & Information Architecture", "Figma Components, Variants & Auto-Layout", "Interactive Prototyping & Micro-Interactions", "Citizen-Centric Mobile App Redesign"]),
    ("Graphic Design for Public Communication", "CAT-0008", "Beginner", 6, 40, "Typography, colour psychology, Canva and Photoshop basics, infographics, and awareness posters.", ["Visual Hierarchy & Layout Principles", "Color Theory & Typography", "Banner & Poster Design in Canva/Photoshop", "Designing Data-Dense Infographics", "Public Health & Skilling Poster Campaign"]),
    ("Video Editing & Mobile Content Creation", "CAT-0008", "Beginner", 5, 35, "Shot composition, DaVinci Resolve basics, audio leveling, pacing, and short-form video reels.", ["Storyboarding & Video Composition", "Timeline Editing & Transitions", "Audio Cleanup & Background Music", "Color Grading & Export Settings", "Skill Development Awareness Video"]),

    # 9. Technical & Engineering Trades
    ("Domestic Electrician & Home Wiring", "CAT-0009", "Beginner", 8, 60, "Electrical safety, single-phase wiring, MCB/ELCB installation, earthing, and fault diagnosis.", ["Electrical Safety Norms & PPE", "Single Phase & Three Phase Circuits", "Switchboards, MCB & Inverter Wiring", "Earthing Systems & Maintenance", "Residential Wiring Demonstration"]),
    ("Solar PV Rooftop System Installation", "CAT-0009", "Intermediate", 8, 60, "Solar panel types, on-grid/off-grid inverters, battery banks, net metering, and installation.", ["Solar Physics & Irradiation Data", "PV Module Types & Array Layouts", "Inverter Sizing & Battery Storage", "Safety, Mounting & Grid Synchronization", "5kW Rooftop Solar Installation Plan"]),
    ("CNC Machine Operation & Programming", "CAT-0009", "Intermediate", 10, 80, "G-codes, M-codes, CNC lathe/milling operations, cutting parameters, and safety standards.", ["Engineering Drawings & Dimensions", "G & M Codes Programming", "Machine Setup, Tool Offsets & Fixtures", "Dry Run & Live Machining", "Machining Precision Component"]),
    ("Manual Metal Arc & TIG Welding", "CAT-0009", "Beginner", 8, 60, "Arc welding techniques, joint preparation, welding positions, safety gear, and weld inspection.", ["Welding Safety & Equipment", "Joint Types (Lap, Butt, T-Joint)", "Electrode Selection & Arc Control", "TIG/MIG Welding Introduction", "Fabrication of Standard Steel Frame"]),
    ("Automotive Two-Wheeler Technician", "CAT-0009", "Beginner", 8, 60, "Engine mechanics, carburetors, fuel injection (FI), braking systems, electrical, and servicing.", ["Two-Wheeler Engine Cycles", "Fuel Systems & EFI Diagnostics", "Braking, Suspension & Transmission", "Electrical Wiring & Battery Maintenance", "Full Periodic Two-Wheeler Service"]),
    ("Automotive Four-Wheeler Maintenance", "CAT-0009", "Intermediate", 10, 80, "IC engines, clutch/gearbox, disc/drum brakes, OBD-II scanner diagnostics, and wheel alignment.", ["Internal Combustion Engines & Fluids", "Transmission & Drivetrain Operations", "Hydraulic Brakes & ABS Diagnostics", "OBD-II Fault Code Scans", "Scheduled Vehicle Service Procedure"]),
    ("Refrigeration & Air Conditioning (HVAC)", "CAT-0009", "Intermediate", 8, 60, "Vapor compression cycle, refrigerant gas recovery, leak testing, split AC install, and repair.", ["Refrigeration Thermodynamics", "Compressors, Condensers & Capillaries", "Gas Charging, Vacuum & Flaring", "Split AC Installation & Troubleshooting", "Comprehensive AC Overhaul Project"]),
    ("Plumbing Technician & Pipe Fitting", "CAT-0009", "Beginner", 6, 45, "PVC/CPVC piping, sanitary fixtures, drain slope calculation, pump setup, and water harvesting.", ["Plumbing Tools & Safety Norms", "Pipe Cutting, Threading & Solvent Welding", "Sanitary Fittings & Valve Assemblies", "Water Tank & Pump Hookup", "Modern Bathroom Plumbing Layout"]),
    ("Mechatronics & Industrial Automation", "CAT-0009", "Advanced", 10, 80, "PLCs, sensors, pneumatic actuators, ladder logic programming, and automated assembly line.", ["Sensors & Transducers", "Pneumatics & Electro-Pneumatics", "PLC Architecture & Wiring", "Ladder Logic Programming", "Automated Conveyor Sorting Machine"]),

    # 10. Healthcare & Vocational
    ("General Duty Assistant (Healthcare)", "CAT-0010", "Beginner", 8, 60, "Patient hygiene, vital signs recording, bed-making, infection control, and first aid.", ["Hospital Setup & Ethics", "Measuring Vital Signs (BP, Temp, Pulse)", "Infection Prevention & Bio-Waste Management", "Patient Mobilization & Nutrition", "Clinical Ward Care Simulation"]),
    ("Pharmacy Assistant Training", "CAT-0010", "Intermediate", 8, 60, "Drug categories, prescription interpretation, cold storage management, inventory, and ethics.", ["Pharmacology Basics & Drug Forms", "Reading Prescriptions & Dispensing Rules", "Inventory Control & Expiry Tracking", "First Aid & Patient Counseling", "Retail Pharmacy Operation Drill"]),
    ("Emergency Medical Technician (EMT Basic)", "CAT-0010", "Intermediate", 10, 80, "BLS certification, CPR, trauma management, splinting, oxygen therapy, and triage.", ["Human Anatomy & Vital Systems", "Cardiopulmonary Resuscitation (CPR/AED)", "Airway Management & Oxygen Delivery", "Trauma Assessment & Bandaging", "Ambulance Drill & Mock Mass Casualty"]),
    ("Organic Farming & Soil Health Management", "CAT-0010", "Beginner", 6, 45, "Composting, vermicompost, bio-fertilizers, natural pest repellents, and organic certification.", ["Soil Chemistry & Microorganisms", "Composting, Jeevamrutha & Bio-Inputs", "Natural Pest & Weed Control", "Water Conservation & Mulching", "Model Organic Farm Blueprint"]),
    ("Micro-Irrigation & Drip Irrigation Systems", "CAT-0010", "Intermediate", 6, 45, "Drip design, fertigation units, filtration systems, water calculation, and maintenance.", ["Water Requirements of Crops", "Drip System Components & Layout", "Venturi Injectors & Fertigation", "Clog Prevention & Flushing", "Field Drip Installation Exercise"]),
    ("Dairy Farming & Livestock Management", "CAT-0010", "Beginner", 6, 45, "Cattle breeds, silage preparation, milking hygiene, disease prevention, and dairy economics.", ["High-Yield Cattle Breeds", "Fodder Production & Nutrition", "Hygienic Milking & Chilling", "Vaccination Schedules & Health Checks", "Profitable 10-Cow Dairy Unit Plan"]),
    ("Hospitality Front Office Operations", "CAT-0010", "Beginner", 6, 40, "Check-in/check-out procedures, guest communication, billing systems, and telephone etiquette.", ["Hospitality Industry Overview", "Reservation Systems & Front Desk Check-in", "Professional Communication & Etiquette", "Billing, Currency & Key Handling", "Front Desk Roleplay Simulation"]),
    ("Food Safety, Hygiene & FSSAI Standards", "CAT-0010", "Beginner", 4, 30, "Food contamination hazards, HACCP basics, personal hygiene, and FSSAI licensing rules.", ["Food Borne Pathogens & Cross Contamination", "Personal Cleanliness & Kitchen Sanity", "HACCP Principles in Practice", "FSSAI Food Safety Documentation", "Commercial Kitchen Safety Audit"]),
    ("Commercial Baking & Confectionery", "CAT-0010", "Beginner", 6, 45, "Dough chemistry, bread making, pastry decoration, cookies, oven calibration, and costing.", ["Baking Ingredients & Yeast Science", "Artisan Bread & Bun Preparation", "Cakes, Sponge & Icing Techniques", "Safety, Packaging & Product Shelf-Life", "Bakery Showcase Product Batch"]),
    ("Apparel Manufacturing & Industrial Tailoring", "CAT-0010", "Beginner", 8, 60, "Industrial sewing machine operation, pattern drafting, garment assembly, and finishing.", ["Machine Safety & Threading", "Stitch Types & Tension Calibration", "Pattern Making & Fabric Cutting", "Garment Assembly (Shirts/Kurta)", "Full Garment Sewing Project"]),
    ("Beauty & Wellness Professional", "CAT-0010", "Beginner", 6, 45, "Skin analysis, facial treatments, hair styling basics, hygiene protocols, and salon management.", ["Skin Physiology & Consultations", "Facial Treatments & Bleach Safety", "Hair Styling & Conditioning", "Sterilization of Instruments", "Salon Service Session"]),
    ("Supply Chain & Warehouse Operations", "CAT-0010", "Intermediate", 6, 45, "Inbound receiving, barcode scanning, inventory counting, dispatch, and forklift safety.", ["Warehouse Logistics Concepts", "Receiving & Quality Inspection", "Inventory Audits (FIFO/LIFO)", "Picking, Packing & Dispatch Procedures", "Warehouse Management System (WMS) Drill"]),
    ("Commercial Vehicle Driving & Fleet Safety", "CAT-0010", "Beginner", 6, 45, "Traffic laws, defensive driving, route navigation, basic mechanical checks, and emergency care.", ["Motor Vehicle Act & Road Signs", "Defensive Driving Techniques", "Pre-Trip Inspection Checklist", "Fuel Efficiency & Emergency Braking", "Fleet Road Safety Simulation"]),
    ("Drone Pilot Operations (DGCA Compliant)", "CAT-0010", "Intermediate", 7, 50, "Drone physics, airspace regulations (Digital Sky), flight planning, mapping, and safety.", ["Drone Aerodynamics & Components", "Airspace Rules & DGCA Guidelines", "Flight Simulator Practice", "Agricultural & Survey Payload Basics", "Field Drone Flight Exercise"]),
    ("3D Printing & Additive Manufacturing", "CAT-0010", "Intermediate", 6, 40, "CAD modeling, slicing software (Cura), FDM 3D printer calibration, and prototyping.", ["Additive Manufacturing Overview", "3D CAD Modeling for Printability", "Slicing Settings, Infill & Supports", "Printer Bed Leveling & Material Selection", "Functional Engineering Prototype Print"]),
    ("Spoken English for Professional Careers", "CAT-0010", "Beginner", 6, 40, "Everyday conversation, workplace vocabulary, email drafting, presentations, and self-confidence.", ["Pronunciation & Common Expressions", "Sentence Structure & Conversational Drills", "Workplace Meetings & Etiquette", "Drafting Professional Emails", "5-Minute Formal Career Presentation"]),
    ("Spoken Kannada for Workplace & Community", "CAT-0010", "Beginner", 5, 30, "Day-to-day conversational Kannada, polite phrases, civic office interactions, and market vocabulary.", ["Basic Kannada Alphabet & Sounds", "Greeting & Polite Forms of Address", "Asking for Directions & Prices", "Workplace Conversations & Civic Interactions", "Interactive Speaking Simulation"]),
    ("Hindi for Workplace Communication", "CAT-0010", "Beginner", 5, 30, "Conversational Hindi, business vocabulary, polite interactions, and telephonic etiquette.", ["Phonetics & Everyday Phrases", "Office & Technical Hindi Vocabulary", "Client Interactions & Politeness", "Drafting Simple Notifications", "Workplace Roleplay Drill"]),
    ("Carpentry & Architectural Woodwork", "CAT-0009", "Beginner", 6, 45, "Wood cutting, joinery techniques, furniture assembly, surface finishing, and hand tool safety.", ["Wood Types & Timber Selection", "Measuring, Marking & Hand Tools", "Mortise, Tenon & Dovetail Joints", "Sanding, Polishing & Finishing", "Modular Furniture Unit Construction"]),
    ("Masonry & Construction Fundamentals", "CAT-0009", "Beginner", 6, 45, "Brick laying, mortar ratios, plastering, plumb line alignment, and building safety standards.", ["Masonry Tools & Mortar Chemistry", "Brick Bonding (English/Flemish)", "Plastering Techniques & Curing", "Foundation Layout & Leveling", "Structural Brick Wall Construction"]),
    ("Retail Store Operations & Inventory", "CAT-0007", "Beginner", 5, 35, "Visual merchandising, POS billing, stock replenishment, barcode management, and customer care.", ["Retail Formats & Customer Flow", "Point of Sale (POS) Billing", "Inventory Replenishment & Stock Audits", "Customer Grievance Resolution", "Supermarket Floor Simulation"]),
    ("Medical Records & Billing Specialist", "CAT-0010", "Intermediate", 6, 40, "ICD-10 coding, electronic health records (EHR), patient data confidentiality, and insurance claims.", ["Healthcare Information Systems", "ICD-10 Diagnostic Coding", "Health Insurance Claims Processing", "Patient Data Privacy & Ethics", "Hospital Patient Billing Audit"]),
    ("Drip Irrigation Installation & Maintenance", "CAT-0010", "Intermediate", 6, 40, "Water budget estimation, emitter spacing, drip lateral layout, pump selection, and acid treatment.", ["Soil Moisture & Crop Water Need", "Drip System Components & Layout", "Filtration & Fertigation Setup", "Flushing & System Maintenance", "1-Acre Drip Network Commissioning"]),
    ("Industrial Safety & OSHA Standards", "CAT-0009", "Beginner", 4, 30, "Hazard identification, personal protective equipment (PPE), fire drills, and incident investigation.", ["Industrial Hazards (Chemical, Electrical)", "PPE Selection & Maintenance", "Fire Prevention & Emergency Evacuation", "Accident Reporting & Root Cause", "Mock Factory Safety Inspection Report"]),
]

def seed_database(db: Session):
    # 1. Seed Categories
    for c_data in CATEGORIES_DATA:
        existing = db.query(Category).filter(Category.code == c_data["code"]).first()
        if not existing:
            cat = Category(**c_data)
            db.add(cat)
    db.commit()

    cat_map = {c.code: c.id for c in db.query(Category).all()}

    # 2. Seed Training Centres
    for ctr_data in CENTRES_DATA:
        existing = db.query(TrainingCentre).filter(TrainingCentre.code == ctr_data["code"]).first()
        if not existing:
            ctr = TrainingCentre(**ctr_data)
            db.add(ctr)
        else:
            if existing.latitude is None and ctr_data.get("latitude") is not None:
                existing.latitude = ctr_data.get("latitude")
                existing.longitude = ctr_data.get("longitude")
    db.commit()

    centre_list = db.query(TrainingCentre).all()

    # 3. Seed Trainers
    for trn_data in TRAINERS_DATA:
        existing = db.query(Trainer).filter(Trainer.code == trn_data["code"]).first()
        if not existing:
            trn = Trainer(**trn_data)
            db.add(trn)
    db.commit()

    trainers_list = db.query(Trainer).all()

    # 4. Seed Skills and Modules
    for i, s_def in enumerate(SKILL_DEFINITIONS, start=1):
        name, cat_code, level, weeks, hours, summary, module_titles = s_def
        code = f"SKL-{i:04d}"
        existing = db.query(Skill).filter(Skill.code == code).first()
        if not existing:
            skill = Skill(
                code=code,
                name=name,
                category_id=cat_map.get(cat_code),
                category_name=next((c["name"] for c in CATEGORIES_DATA if c["code"] == cat_code), "General"),
                level=level,
                duration_weeks=weeks,
                duration_hours=hours,
                summary=summary,
                details=f"The {name} course delivers an industry-aligned syllabus aligned with national skilling frameworks. Participants gain hands-on practice, real-world case studies, and mentorship from experienced domain specialists.",
                prerequisites="Basic computer literacy and enthusiasm to learn.",
                learning_objectives=f"Gain competency in {name}; build practical project portfolio; prepare for recognized certification.",
                learning_outcomes=f"Develop end-to-end practical ability; solve real industry challenges; earn an official NSQF-aligned certificate.",
                relevant_industries="Information Technology, Services, Governance, Engineering, Manufacturing",
                career_opportunities=f"{name} Specialist, Associate Engineer, Technical Consultant, Analyst",
                cert_info="NagrikSetu Skill Development Certificate of Competency (NSQF Level 5/6 Aligned)",
                rating=4.7 + ((i % 4) * 0.1),
                enrolled_count=45 + (i * 3),
                active=True
            )
            db.add(skill)
            db.flush()

            for order, m_title in enumerate(module_titles, start=1):
                mod = SkillModule(
                    skill_id=skill.id,
                    module_order=order,
                    title=f"Module {order}: {m_title}",
                    description=f"Detailed study and practical lab exercise covering {m_title}.",
                    topics=f"Core concepts, hands-on lab, code walkthroughs, diagnostic troubleshooting, assessment.",
                    practical_assignments=f"Hands-on lab exercise for {m_title} with verified code submission.",
                    projects=f"Guided milestone component for the {name} final portfolio project."
                )
                db.add(mod)

            # Create a corresponding training program for skills
            prog_code = f"PRG-{i:04d}"
            existing_prog = db.query(TrainingProgram).filter(TrainingProgram.code == prog_code).first()
            if not existing_prog:
                trainer_idx = (i - 1) % len(trainers_list)
                centre_idx = (i - 1) % len(centre_list)
                mode_choice = "Online" if (i % 3 == 0) else ("Hybrid" if (i % 3 == 1) else "Classroom")
                prog = TrainingProgram(
                    code=prog_code,
                    skill_id=skill.id,
                    title=f"National Skilling Mission: {name}",
                    description=f"Government-supported structured training programme in {name} with industry certification and placement support.",
                    provider_name="NagrikSetu National Skill Academy",
                    trainer_id=trainers_list[trainer_idx].id,
                    centre_id=centre_list[centre_idx].id,
                    mode=mode_choice,
                    duration_hours=hours,
                    fee=0.0 if (i % 2 == 0) else 1500.0, # Many free government courses
                    scholarship_available=True,
                    eligibility_criteria="Age 18-35 years; 10th/12th/Diploma/Graduate eligible",
                    start_date="2026-12-01",
                    end_date="2027-01-15",
                    status="PUBLISHED"
                )
                db.add(prog)
                db.flush()

                # Create 2 batches per program
                batch1 = Batch(
                    code=f"BAT-{((i-1)*2)+1:04d}",
                    program_id=prog.id,
                    batch_name=f"{name} - Regular Morning Batch",
                    timings="08:30 AM - 10:30 AM",
                    training_schedule="Monday to Friday",
                    mode=mode_choice,
                    total_seats=30,
                    available_seats=28,
                    start_date="2026-12-01",
                    end_date="2027-01-15",
                    application_deadline="2026-11-28",
                    status="ADMISSIONS_OPEN"
                )
                batch2 = Batch(
                    code=f"BAT-{((i-1)*2)+2:04d}",
                    program_id=prog.id,
                    batch_name=f"{name} - Weekend Professional Batch",
                    timings="10:00 AM - 02:00 PM",
                    training_schedule="Saturday & Sunday",
                    mode="Hybrid",
                    total_seats=25,
                    available_seats=22,
                    start_date="2026-12-06",
                    end_date="2027-01-24",
                    application_deadline="2026-12-02",
                    status="ADMISSIONS_OPEN"
                )
                db.add_all([batch1, batch2])

    db.commit()
