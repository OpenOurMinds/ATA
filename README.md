# ATA - Agent To Agent
## Digital Soul Generator & Virtual City Simulator

A framework for generating synthetic populations with memories, emotions, and unique identities to simulate democratic resilience and population collapse risks in a virtual city environment.

### 🎯 Purpose

This project addresses the risk of demographic collapse and democratic erosion by creating a "Synthetic Population" that isn't just numbers, but possesses high-fidelity human traits like memories and emotional logic. The simulation explores how humanoid robots might bridge physical and digital worlds to manage insurance risk and social credit systems.

### 🧬 Core Components

#### 1. Digital Soul Generator (`digital_soul_generator.py`)
Generates synthetic citizens with:
- **Digital Soul Hash (DSH)**: Unique cryptographic ID based on birth date, core memory, and biometric seed
- **Memory Anchors**: High-emotion root events that dictate worldview (e.g., childhood triumph, early loss)
- **Emotional Resonance Vectors**: Mathematical representation of trust, fear, altruism, ambition, and curiosity
- **Archetypes**: 6 personality types (Stoic Engineer, Disillusioned Artist, Community Builder, etc.)
- **Census Weighting**: Statistically accurate age/gender distributions based on real-world data

#### 2. Virtual City Simulator (`virtual_city_simulator.py`)
Simulates city-wide interactions:
- **Robot Observations**: Humanoid robots detect physical behaviors (eating, driving, exercise, social interaction)
- **Automated Internet Tasks**: Robots perform tasks (YouTube research, SNS posting, smart home triggers)
- **Ethical Guardrails**: Human-in-the-loop approval, data encryption, manual overrides
- **Democratic Health Monitor**: Tracks social credit scores and city-wide democratic index

#### 3. Democratic Voting System (`democratic_voting_system.py`)
Implements democratic infrastructure for digital souls:
- **Age-Group Voting Behaviors**: 7 age groups with unique turnout rates and issue sensitivities
- **Proposal System**: Create and vote on policies, resource allocations, and constitutional amendments
- **AI-Generated Reasoning**: Votes include reasoning based on memory anchors and emotional state
- **Lazarus Clause**: Activates proxy voting when democratic index falls below threshold (population collapse scenario)
- **Vote Confidence Tracking**: Measures decision confidence based on issue alignment

#### 4. Age-Group Workflows (`age_group_workflows.py`)
Defines age-specific robot-to-internet interactions:
- **Youth (16-24)**: Educational content, social learning, skill building with parental safeguards
- **Young Adult (25-34)**: Career development, financial management, housing search
- **Mid Adult (35-44)**: Family coordination, investment management, health monitoring
- **Late Adult (45-54)**: Retirement planning, elder care coordination, continuing education
- **Pre-Retirement (55-64)**: Healthcare enrollment, downsizing assistance, estate planning
- **Retiree (65-74)**: Medication management, social engagement, fraud protection
- **Elderly (75-85)**: Emergency response, cognitive stimulation, legacy preservation

#### 5. Decentralized Storage (`decentralized_storage.py`)
Implements data air-gapping and distributed storage:
- **Data Sharding**: Splits citizen data across multiple shards for redundancy
- **Replication Factor**: Configurable replication across storage nodes
- **Air-Gapped Vaults**: Encrypts and isolates sensitive data from external networks
- **Data Classification**: PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED levels
- **Node Failure Simulation**: Tests redundancy by simulating node failures
- **Integrity Checking**: Monitors replication health and data availability

#### 6. Robot-to-Internet Workflow (`robot_internet_workflow.py`)
Complete pipeline from physical perception to internet content generation:
- **Camera Perception**: Action recognition, skeletal tracking (pose estimation), object metadata
- **Life Log Database**: Temporal storage with identity tagging and environmental context
- **Imitation Learning**: Inverse Reinforcement Learning (IRL), behavioral cloning, morphology adaptation
- **Agent Proxy**: Digital persona calibration based on physical activities (mood, energy level)
- **YouTube Enrichment**: Spatial-temporal data extraction (keypoints, velocity vectors), contextual search, technique learning
- **Archetype-Specific SNS**: 6 unique posting styles (Stoic Engineer, Disillusioned Artist, Community Builder, etc.)
- **Insurance Impact**: Archetype-based premium adjustments (Reliability Score, Social Contribution Score, etc.)
- **Safety Safeguards**: Digital signatures, privacy masks, source verification

#### 7. Virtual City Integration (`virtual_city_integration.py`)
Analyzes SNS activity for democratic health and economic flow:
- **Sentiment Analysis**: Keyword extraction, sentiment scoring, democratic contribution calculation
- **Economic Flow**: Collective insurance impact by archetype, economic activity scoring
- **Democratic Health**: Overall index calculation, collapse risk assessment
- **Population Collapse Hedge**: Internet space maintenance during demographic collapse
- **Social Cohesion**: Community-focused activity tracking and scoring

#### 8. Global Hierarchical Architecture (`global_architecture.py`)
Distributed system with central Global Soul Ledger and distributed City Nodes:
- **Global Soul Ledger**: Identity Vault (DSH storage), Global Insurance Engine, Democratic Health Monitor
- **City Nodes**: New York (high-density vertical), Beijing (large-scale infrastructure), Tokyo (high-tech elderly)
- **Data Sharding**: NY-SHARD (30k), BJ-SHARD (30k), TK-SHARD (30k), GLOBAL-VIRTUAL (10k)
- **City Adapters**: Localization layers (NY: side hustles, BJ: social harmony, TK: omotenashi)
- **API Communication**: Life Update packets (learning, social, migration, insurance)
- **Cross-City Migration**: Digital Soul Hash preservation with behavioral adaptation
- **Global Resilience Index**: Aggregated sentiment tracking across all cities

#### 9. Agent-to-Agent Communication Protocol (`agent_communication_protocol.py`)
Three-layer communication system enabling agents to exchange information like humans:
- **Layer 1 (Opened Information)**: Public conversation tracking, attendance logging, information flow analysis, consequence recording
- **Layer 2 (Semi-Opened Information)**: Deep feeling exchange, truth sharing, private conversations, trust-based access, emotional synchronization
- **Layer 3 (Real-time Signals)**: Motor coordination signals, sensor data sharing, task priority updates, emergency signals, low-latency communication
- **Message Router**: Broadcast and direct message routing, agent connection management, message queue processing
- **Trust Relationships**: Dynamic trust scoring between agents, truth sharing impact on trust levels
- **Conversation Tracking**: Public and private conversation management, participant tracking, message history

#### 10. ATA Integrated Dashboard (`dashboard.py`)
Web-based dashboard integrating all ATA components with real-time monitoring:
- **Real-time Status Monitoring**: Live status of all components (digital souls, workflows, city analysis, global architecture, agent communication)
- **Interactive Controls**: One-click generation, execution, and analysis of all components
- **Data Visualization**: Chart.js-powered visualizations for archetype distribution, statistics, and metrics
- **System Logging**: Real-time log streaming with INFO, SUCCESS, and ERROR levels
- **Quick Simulation**: One-click full simulation running all components in sequence
- **REST API**: RESTful endpoints for programmatic access to all dashboard features
- **Modern UI**: Dark-themed, responsive interface with gradient accents and smooth animations

#### 11. Research Paper (`research_paper.tex`)
Comprehensive LaTeX research paper documenting the entire ATA system:
- **System Architecture**: Detailed description of all 11 core components with diagrams
- **Mathematical Formulations**: Equations for Digital Soul Hash generation, imitation learning, democratic index calculation, trust dynamics
- **Implementation Details**: Technology stack, performance considerations, scalability analysis
- **Evaluation Results**: Simulation outcomes and dashboard performance metrics
- **Applications and Use Cases**: Population collapse research, insurance risk modeling, democratic resilience analysis
- **References**: Academic citations for agent-based modeling, imitation learning, and social simulation
- **PDF Compilation**: Automated script to compile LaTeX to PDF with bibliography

#### 12. Terminal Dashboard (`terminal_dashboard.py`)
CLI-based dashboard with deployment, download, settings, and run features:
- **Interactive Menu System**: Terminal-based navigation similar to Claude Code's IDE
- **Component Execution**: Run any ATA component from terminal
- **Deployment Management**: Start/stop web dashboard, check deployment status
- **Data Export**: Download/export all data types (CSV, JSON)
- **Settings Management**: Configure default parameters, auto-save, ports
- **Real-time Status**: View system status and logs in terminal
- **Rich UI**: Beautiful terminal interface with colors and formatting (requires `rich` library)

#### 13. Parameter Optimizer (`parameter_optimizer.py`)
Machine learning-based parameter tuning for self-sustaining operation:
- **Bayesian Optimization**: Intelligent parameter search using Thompson sampling
- **Genetic Algorithms**: Evolutionary parameter optimization with crossover and mutation
- **Multi-Objective Optimization**: Optimize for democratic index, economic health, social cohesion
- **Parameter Spaces**: Define search spaces for continuous and discrete parameters
- **Optimization History**: Track parameter evolution and objective values
- **Auto-Tuning**: Automatically adjust simulation parameters based on outcomes

#### 14. Decision Engine (`decision_engine.py`)
Automated decision-making system for autonomous operation:
- **Rule-Based Decisions**: Define rules that trigger based on system state
- **Policy Recommendations**: Generate policy suggestions for democratic health
- **Emergency Response**: Automatic activation of collapse hedge mechanisms
- **Parameter Adjustments**: Auto-tune parameters based on analysis results
- **Priority System**: Critical, high, medium, low priority decisions
- **Autonomous Controller**: Continuous decision cycles for self-sustaining operation
- **Decision History**: Track all decisions made and their execution results

### 🚀 Quick Start

#### Generate Test Population (100 citizens)
```bash
python digital_soul_generator.py
```

#### Generate Large-Scale Population (100,000 citizens)
```bash
python digital_soul_generator.py --scale 100000 --output-csv digital_souls_100k.csv --output-json digital_souls_100k.json --no-sample
```

#### Run Virtual City Simulation
```bash
python virtual_city_simulator.py --citizens digital_souls.json --days 7 --steps 3
```

#### Run Democratic Voting System
```bash
python democratic_voting_system.py --citizens digital_souls.json --proposals 5
```

#### Test Lazarus Clause (Population Collapse Scenario)
```bash
python democratic_voting_system.py --citizens digital_souls.json --population-ratio 0.3
```

#### Run Age-Group Workflows
```bash
python age_group_workflows.py --citizens digital_souls.json --sessions 1000
```

#### Setup Decentralized Storage Network
```bash
python decentralized_storage.py --citizens digital_souls.json --nodes 10 --replication 3 --sample 1000
```

#### Run Robot-to-Internet Workflow
```bash
python robot_internet_workflow.py --citizens digital_souls.json --workflows 10
```

#### Analyze Virtual City Integration
```bash
python virtual_city_integration.py --sns-posts robot_workflow_sns_posts.csv --population-ratio 1.0
```

#### Initialize Global Architecture
```bash
python global_architecture.py --citizens digital_souls_100k.json --activities 100
```

#### Simulate Agent Communication
```bash
python agent_communication_protocol.py --simulate
```

#### Launch Integrated Dashboard
```bash
python dashboard.py
```
Access the dashboard at http://localhost:5001

#### Compile Research Paper to PDF
```bash
./compile_paper.sh
```
Requires pdflatex and bibtex (TeX Live or MacTeX)

#### Launch Terminal Dashboard
```bash
python terminal_dashboard.py
```
Interactive CLI with deployment, download, settings, and run features

#### Run Parameter Optimizer
```bash
python parameter_optimizer.py
```
Test ML-based parameter optimization

#### Run Decision Engine
```bash
python decision_engine.py
```
Test automated decision-making system

### 📊 Data Structure

#### Digital Soul (Citizen Profile)
```csv
citizen_id,digital_soul_hash,birth_date,age,gender,life_stage,archetype,memory_event_type,memory_narrative,memory_age_at_event,memory_emotional_weight,trust,fear,altruism,ambition,curiosity,social_credit_score,insurance_risk_tier,routine,risk_averse,tech_savvy,social_engagement,health_consciousness
ALPHA-77-902,a1b2c3d4...,1995-03-15,29,Female,Early Career,The Stoic Engineer,discovery,Finding astronomy books in the attic...,12,0.85,0.6,0.4,0.5,0.8,0.7,62.3,Standard,0.9,0.8,0.9,0.6,0.7
```

#### Robot Observation
```csv
session_id,citizen_id,timestamp,observation_type,detected_risk,context,sensor_data
SR-901,ALPHA-77-902,2024-04-30T10:30:00,eating_behavior,MEDIUM,User is eating fast food,"{""calories"": 1200, ""sugar"": 50}"
```

#### Internet Task
```csv
task_id,citizen_id,task_type,trigger_observation,content,platform,ethical_guardrail,requires_approval,user_approved,executed,premium_impact
TASK-12345,ALPHA-77-902,amazon_purchase,User is eating fast food,Ordering health supplements,Amazon,User Approval Required,True,True,True,-5.0
```

### 🛡️ Safety & Ethics

#### Synthetic Data Guardrails
- **No Real PII**: Uses synthetic identifiers (ALPHA-77-902 format)
- **Air-Gapped Generation**: Designed for local, non-cloud execution
- **Anonymized Metadata**: Stores behavioral patterns, not raw footage
- **No Real Names/SSNs**: All data is procedurally generated

#### Ethical Safeguards in Simulation
- **Human-in-the-Loop (HITL)**: Robots require approval for sensitive actions
- **Privacy Veil**: Data stored as anonymized metadata
- **Consent Granularity**: Users can toggle specific internet task categories
- **Algorithmic Transparency**: Natural language explanations for premium changes
- **Right to Delete**: Kill switch for database wiping

#### Lazarus Clause (Population Collapse Protocol)
- **Activation Threshold**: Triggers when democratic index falls below 0.3 or physical population ratio below 0.5
- **Proxy Voting**: Digital souls vote as democratic proxies until physical population recovers
- **Emergency Powers**: Infrastructure maintenance, resource allocation, constitutional protection
- **Deactivation**: Automatically deactivates when population recovers
- **Purpose**: Maintains democratic infrastructure during demographic collapse scenarios

#### Data Air-Gapping
- **Encrypted Vaults**: Sensitive data encrypted and isolated from external networks
- **Classification Levels**: PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
- **Access Control**: Decryption keys required for vault access
- **Audit Logging**: All access attempts logged for accountability
- **Memory Ownership**: Core memory data belongs to the user, not insurers

### 📈 Scaling to 100,000 Citizens

The framework uses **Recursive Archetyping** for efficient scaling:
1. Create 100 Archetypes with unique memory templates
2. Generate 1,000 variations per archetype with random mutations
3. Apply census-weighted demographic distributions
4. Generate unique Digital Soul Hash for each citizen

**Performance**: ~100 citizens/second on standard hardware

### 🏙️ Virtual City Simulation Mechanics

#### Democratic Health Index
- Calculated from average social credit scores across population
- Affected by city-wide events (resource shortages, policy changes, social movements)
- Range: 0.0 (collapsed) to 1.0 (thriving)

#### Risk-Based Premium Adjustment
- **Low Risk**: -$5 to -$10 premium (healthy behaviors)
- **Standard**: $0 baseline
- **High Risk**: +$5 to +$25 premium (risky behaviors)

#### Internet Task Types
- **YouTube Research**: Automated content consumption and summarization
- **SNS Post**: Social media content generation for reputation management
- **Amazon Purchase**: Risk-reducing product orders
- **Policy Analysis**: Insurance policy monitoring
- **Smart Home Trigger**: Emergency protocol activation

### 🔧 Command-Line Options

#### Digital Soul Generator
```
--scale N              Number of citizens to generate (default: 100)
--output-csv FILE      CSV output filename (default: digital_souls.csv)
--output-json FILE     JSON output filename (default: digital_souls.json)
--no-sample            Skip displaying sample citizen profile
```

#### Virtual City Simulator
```
--citizens FILE        Path to citizen JSON file (default: digital_souls.json)
--days N               Number of days to simulate (default: 1)
--steps N              Observation steps per citizen per day (default: 3)
--output PREFIX        Output file prefix (default: simulation)
```

#### Democratic Voting System
```
--citizens FILE        Path to citizen JSON file (default: digital_souls.json)
--proposals N          Number of proposals to create and vote on (default: 5)
--population-ratio     Physical population ratio (1.0 = full population, triggers Lazarus below 0.5)
--output PREFIX        Output file prefix (default: voting)
```

#### Age-Group Workflows
```
--citizens FILE        Path to citizen JSON file (default: digital_souls.json)
--sessions N           Number of workflow sessions to simulate (default: 1000)
--output PREFIX        Output file prefix (default: robot_workflows)
```

#### Decentralized Storage
```
--citizens FILE        Path to citizen JSON file (default: digital_souls.json)
--nodes N              Number of storage nodes (default: 10)
--replication N        Replication factor for data shards (default: 3)
--sample N             Number of citizens to store (0 = all, default: 1000)
--output PREFIX        Output file prefix (default: storage_network)
```

#### Robot-to-Internet Workflow
```
--citizens FILE        Path to citizen JSON file (default: digital_souls.json)
--workflows N          Number of workflows to execute (default: 10)
--output PREFIX        Output file prefix (default: robot_workflow)
```

#### Virtual City Integration
```
--sns-posts FILE       Path to SNS posts CSV file (default: robot_workflow_sns_posts.csv)
--population-ratio     Physical population ratio (1.0 = full population)
--output PREFIX        Output file prefix (default: city_analysis)
```

#### Global Architecture
```
--citizens FILE       Path to citizen JSON file (default: digital_souls_100k.json)
--activities N        Number of activities to simulate per city (default: 100)
--output PREFIX       Output file prefix (default: global_architecture)
```

#### Agent Communication Protocol
```
--simulate            Run agent communication simulation
--agents N            Number of agents to simulate (default: 10)
```

### 📁 Output Files

- `digital_souls.csv` - Complete citizen profiles in CSV format
- `digital_souls.json` - Complete citizen profiles in JSON format
- `simulation_observations.csv` - Robot observations during simulation
- `simulation_tasks.csv` - Automated internet tasks generated
- `simulation_events.csv` - City-wide democratic events
- `voting_proposals.csv` - Democratic proposals created
- `voting_votes.csv` - Individual votes cast by digital souls
- `robot_workflows.csv` - Age-group specific workflow executions
- `storage_network_nodes.csv` - Storage node information
- `storage_network_shards.csv` - Data shard distribution
- `storage_network_airgap_logs.csv` - Air-gapped vault access logs
- `robot_workflow_history.csv` - Complete workflow execution records
- `robot_workflow_lifelog.csv` - Life log entries with perception data
- `robot_workflow_sns_posts.csv` - Generated SNS posts with digital signatures
- `city_analysis_sentiment.csv` - Sentiment analysis results for all posts
- `city_analysis_economic.csv` - Economic flow analysis by archetype
- `city_analysis_democratic.csv` - Democratic health index and collapse risk
- `global_architecture_souls.csv` - Global soul records with migration history
- `global_architecture_life_updates.csv` - Life update packets from all cities
- `agent_communication_messages.csv` - Message history between agents
- `agent_communication_conversations.csv` - Public and private conversation records
- `research_paper.pdf` - Compiled research paper in PDF format (generated from LaTeX)
- `optimization_history.json` - Parameter optimization history with iterations and objective values
- `decision_history.json` - Decision engine history with all decisions made and execution results

### 🧪 Research Applications

This framework enables research into:
- **Democratic Resilience**: Can AI agents maintain peaceful societies under resource scarcity?
- **Generational Continuity**: Can robots "pass down" memories to prevent knowledge loss?
- **Insurance Personalization**: How does behavioral data affect risk stratification?
- **Social Credit Systems**: What are the implications of automated reputation management?
- **Population Collapse**: Can synthetic populations model demographic transition scenarios?
- **Age-Based Digital Behavior**: How do different generations interact with automated internet services?
- **Lazarus Protocol Effectiveness**: Can proxy voting maintain democratic infrastructure during collapse?
- **Decentralized Data Sovereignty**: How does distributed storage affect privacy and resilience?
- **Imitation Learning**: How can robots learn from human demonstrations and adapt to robotic morphology?
- **Physical-Digital Bridge**: How do physical activities influence digital persona and content generation?
- **Archetype-Based Social Impact**: How do different personality types affect collective insurance costs and social cohesion?
- **Spatial-Temporal Video Analysis**: How can robots extract actionable data from video for skill acquisition?
- **Cross-Cultural Localization**: How do cultural adapters modify content for different city environments?
- **Global Resilience**: How does distributed city architecture affect global democratic stability?
- **Migration Patterns**: How does cross-city migration affect identity preservation and behavioral adaptation?
- **Agent Communication**: How do multi-layer communication protocols affect agent coordination and trust?
- **Trust Dynamics**: How does truth sharing and emotional exchange build trust between agents?
- **Real-time Coordination**: How do motor/sensor signals enable efficient multi-agent task completion?
- **Dashboard Usability**: How do interactive web interfaces enhance researcher understanding of complex agent-based simulations?
- **Real-time Monitoring**: How does live status monitoring improve experimental control and data collection?
- **Integrated Simulation**: How do multi-component workflows provide more comprehensive insights than isolated simulations?
- **Parameter Optimization**: How can machine learning automatically tune simulation parameters for optimal outcomes?
- **Autonomous Decision-Making**: How can rule-based systems make policy recommendations without human intervention?
- **Self-Sustaining Systems**: How can closed-loop feedback create autonomous operation without manual oversight?
- **Flywheel Dynamics**: How do optimization and decision-making create reinforcing improvement cycles?
- **Bayesian Optimization**: How can intelligent parameter search improve simulation efficiency?
- **Genetic Algorithms**: How can evolutionary optimization adapt system parameters over time?
- **Emergency Automation**: How can autonomous systems respond to collapse risks faster than human operators?

### 📝 License

See LICENSE file for details.

### 🤝 Contributing

This is a research framework for exploring ethical implications of AI-mediated social systems. Use responsibly and in accordance with ethical guidelines for synthetic data generation.
