#!/usr/bin/env python3
import random
import json
import csv
import os
import hashlib
from datetime import datetime, timezone

# Config
seed_val = 42
steps_count = 1000
output_csv = "data/simulation_history_t1_t1000.csv"
output_json = "data/simulation_history_t1_t1000.json"

# Set seed
random.seed(seed_val)

# Data structures
archetypes = [
    "The Stoic Engineer",
    "The Disillusioned Artist",
    "The Community Builder",
    "The Ambitious Entrepreneur",
    "The Cautious Observer",
    "The Idealistic Activist"
]

event_types = [
    "discovery", "loss", "triumph", "betrayal", "journey",
    "friendship", "innovation", "sacrifice", "awakening", "challenge"
]

narrative_templates = {
    "discovery":  ["Found a hidden collection of old books in the attic", "Witnessed an unexpected scientific phenomenon"],
    "loss":       ["Lost a close family member at a young age", "Experienced a sudden financial setback"],
    "triumph":    ["Won a regional academic competition against all odds", "Built something from scratch that changed the community"],
    "betrayal":   ["Trusted advisor turned out to have hidden motives", "Discovered a fundamental institutional lie"],
    "journey":    ["Traveled alone across three countries at age 18", "Relocated to an unfamiliar city for opportunity"],
    "friendship": ["Formed a lifelong bond during a crisis", "Met a mentor who reshaped their worldview"],
    "innovation": ["Invented a tool that solved a persistent local problem", "Proposed a novel approach that was initially rejected"],
    "sacrifice":  ["Gave up a promising career to care for a parent", "Chose community well-being over personal gain"],
    "awakening":  ["Realized the system they trusted was fundamentally flawed", "Had a sudden clarity about purpose"],
    "challenge":  ["Survived a natural disaster", "Overcame a physical limitation through persistence"]
}

activity_types = [
    {"type": "exercise", "risk": "LOW", "description": "Running in the park"},
    {"type": "exercise", "risk": "LOW", "description": "Yoga session at home"},
    {"type": "cooking", "risk": "LOW", "description": "Preparing a healthy meal"},
    {"type": "driving", "risk": "MEDIUM", "description": "Commuting during rush hour"},
    {"type": "heavy_lifting", "risk": "MEDIUM", "description": "Moving boxes into building"},
    {"type": "socializing", "risk": "LOW", "description": "Meeting friends at cafe"},
    {"type": "working", "risk": "LOW", "description": "Focused desk work"},
    {"type": "shopping", "risk": "LOW", "description": "Grocery shopping"},
    {"type": "fast_food", "risk": "HIGH", "description": "Eating at fast food restaurant"},
    {"type": "smoking", "risk": "HIGH", "description": "Smoking outside building"},
    {"type": "cycling", "risk": "MEDIUM", "description": "Cycling without helmet"},
    {"type": "gardening", "risk": "LOW", "description": "Community garden maintenance"},
    {"type": "volunteering", "risk": "LOW", "description": "Helping at local shelter"},
    {"type": "studying", "risk": "LOW", "description": "Self-directed learning"},
    {"type": "sports", "risk": "MEDIUM", "description": "Playing basketball"}
]

def get_life_stage(age):
    if age < 25:
        return "Youth"
    elif age < 35:
        return "Early Career"
    elif age < 45:
        return "Mid Career"
    elif age < 55:
        return "Late Career"
    elif age < 65:
        return "Pre-Retirement"
    elif age < 75:
        return "Retired"
    else:
        return "Elderly"

def get_risk_tier(score):
    if score >= 80:
        return "Low"
    elif score >= 50:
        return "Standard"
    elif score >= 30:
        return "High"
    else:
        return "Critical"

def generate_birth_date(age):
    year = datetime.now().year - age
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year:04d}-{month:02d}-{day:02d}"

def generate_soul():
    age = random.randint(16, 85)
    gender = random.choice(["Male", "Female"])
    archetype = random.choice(archetypes)
    birth_date = generate_birth_date(age)
    
    event_type = random.choice(event_types)
    narrative = random.choice(narrative_templates[event_type])
    
    memory_age = random.randint(5, max(5, age - 4))
    memory_weight = random.uniform(0.3, 1.0)
    
    # Emotional Resonance
    emotions = {
        "trust": random.uniform(0.1, 0.9),
        "fear": random.uniform(0.1, 0.9),
        "altruism": random.uniform(0.1, 0.9),
        "ambition": random.uniform(0.1, 0.9),
        "curiosity": random.uniform(0.1, 0.9)
    }
    
    social_credit = random.uniform(20, 95)
    
    # Behavior
    behavior = {
        "routine": random.uniform(0.1, 0.9),
        "riskAverse": random.uniform(0.1, 0.9),
        "techSavvy": random.uniform(0.1, 0.9),
        "socialEngagement": random.uniform(0.1, 0.9),
        "healthConsciousness": random.uniform(0.1, 0.9)
    }
    
    citizen_id = f"ALPHA-{random.randint(0, 99):02d}-{random.randint(0, 999):03d}"
    
    # hash
    raw_hash_data = f"{birth_date}|{narrative}|{random.randint(0, 2**63 - 1)}"
    soul_hash = hashlib.sha256(raw_hash_data.encode('utf-8')).hexdigest()
    
    return {
        "citizenId": citizen_id,
        "digitalSoulHash": soul_hash,
        "birthDate": birth_date,
        "age": age,
        "gender": gender,
        "lifeStage": get_life_stage(age),
        "archetype": archetype,
        "memoryAnchor": {
            "eventType": event_type,
            "ageAtEvent": memory_age,
            "emotionalWeight": memory_weight,
            "narrative": narrative,
            "emotions": ["determination", "nostalgia"]
        },
        "emotionalResonance": emotions,
        "socialCreditScore": social_credit,
        "insuranceRiskTier": get_risk_tier(social_credit),
        "behavioralPatterns": behavior
    }

def run_simulation(souls):
    cycle_id = f"CYCLE-{random.randint(0, 999999):06d}"
    
    # Observe
    observations = []
    posts = []
    for citizen in souls:
        act = random.choice(activity_types)
        obs = {
            "sessionId": f"SR-{random.randint(0, 999999):06d}",
            "citizenId": citizen["citizenId"],
            "activity": {
                "type": act["type"],
                "riskLevel": act["risk"],
                "description": act["description"],
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            },
            "sensorData": {
                "confidence": random.uniform(0.7, 1.0)
            }
        }
        observations.append(obs)
        
        sentiment = (citizen["emotionalResonance"]["trust"] + citizen["emotionalResonance"]["altruism"]) / 2
        post = {
            "postId": f"POST-{random.randint(0, 999999):06d}",
            "citizenId": citizen["citizenId"],
            "textContent": f"[{citizen['archetype']}] {act['description']}",
            "archetype": citizen["archetype"],
            "sentimentScore": sentiment,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        posts.append(post)
        
    # Analyze
    avg_sentiment = sum(p["sentimentScore"] for p in posts) / len(posts)
    trust_sum = sum(s["emotionalResonance"]["trust"] for s in souls)
    altruism_sum = sum(s["emotionalResonance"]["altruism"] for s in souls)
    ambition_sum = sum(s["emotionalResonance"]["ambition"] for s in souls)
    n = len(souls)
    
    social_cohesion = (trust_sum/n + altruism_sum/n) / 2
    economic_health = ambition_sum / n
    participation_rate = len(posts) / len(souls)
    
    dem_index = avg_sentiment * 0.4 + social_cohesion * 0.3 + economic_health * 0.2 + participation_rate * 0.1
    dem_index = min(1.0, max(0.0, dem_index))
    collapse_risk = 1.0 - dem_index
    
    return {
        "cycleId": cycle_id,
        "citizenCount": len(souls),
        "observationCount": len(observations),
        "postCount": len(posts),
        "democraticHealth": {
            "overallIndex": dem_index,
            "collapseRisk": collapse_risk,
            "socialCohesion": social_cohesion,
            "economicHealth": economic_health,
            "participationRate": participation_rate,
            "dataSufficient": True
        }
    }

def evaluate_decisions(health, params):
    decisions = []
    # RULE-001: Low Democratic Index
    if health["dataSufficient"] and health["overallIndex"] < 0.4:
        decisions.append({
            "id": f"DEC-{random.randint(0, 999999):06d}",
            "type": "policy_recommendation",
            "priority": 3,
            "action": "Increase social cohesion activities by 20%",
            "rationale": "Rule \"Low Democratic Index\" triggered",
            "expectedImpact": {"democraticIndex": 0.1, "socialCohesion": 0.15},
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        })
    # RULE-002: High Collapse Risk
    if health["dataSufficient"] and health["collapseRisk"] > 0.6:
        decisions.append({
            "id": f"DEC-{random.randint(0, 999999):06d}",
            "type": "emergency_response",
            "priority": 4,
            "action": "Activate population collapse hedge",
            "rationale": "Rule \"High Collapse Risk\" triggered",
            "expectedImpact": {"collapseRisk": -0.2, "democraticIndex": 0.05},
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        })
    # RULE-003: Low Economic Health
    if health["dataSufficient"] and health["economicHealth"] < 0.3:
        decisions.append({
            "id": f"DEC-{random.randint(0, 999999):06d}",
            "type": "resource_allocation",
            "priority": 2,
            "action": "Reallocate 10% resources to economic stimulation",
            "rationale": "Rule \"Low Economic Health\" triggered",
            "expectedImpact": {"economicHealth": 0.1},
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        })
    return decisions

def optimize_parameters(health, current_params):
    if not health["dataSufficient"]:
        return current_params
    
    next_params = current_params.copy()
    lr = current_params["learningRate"]
    
    def clamp(v, min_v, max_v):
        return min(max_v, max(min_v, v))
        
    if health["overallIndex"] < 0.5:
        next_params["trustWeight"] = clamp(next_params["trustWeight"] + lr, 0.0, 1.0)
        next_params["altruismWeight"] = clamp(next_params["altruismWeight"] + lr * 0.5, 0.0, 1.0)
        
    if health["economicHealth"] < 0.4:
        next_params["ambitionWeight"] = clamp(next_params["ambitionWeight"] + lr, 0.0, 1.0)
        
    if health["collapseRisk"] > 0.5:
        next_params["fearWeight"] = clamp(next_params["fearWeight"] - lr * 0.5, 0.0, 1.0)
        
    return next_params

def main():
    print("🧬 Simulation Datafile Generator (Python Engine)")
    print("==============================================")
    print(f"Seed: {seed_val}")
    print(f"Steps: {steps_count}")
    
    # Default parameters
    params = {
        "soulCount": 50,
        "trustWeight": 0.30,
        "altruismWeight": 0.25,
        "ambitionWeight": 0.20,
        "curiosityWeight": 0.15,
        "fearWeight": 0.10,
        "learningRate": 0.01,
        "explorationRate": 0.30
    }
    
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    records = []
    
    print(f"Running simulation closed loop for {steps_count} steps...")
    for t in range(1, steps_count + 1):
        timestep = f"t{t}"
        
        # 1. Generate souls
        souls = [generate_soul() for _ in range(params["soulCount"])]
        
        # 2. Run simulation cycle
        sim_res = run_simulation(souls)
        
        # 3. Evaluate decisions
        decisions = evaluate_decisions(sim_res["democraticHealth"], params)
        
        # 4. Record state
        record = {
            "timestep": timestep,
            "cycle_id": sim_res["cycleId"],
            "citizens": sim_res["citizenCount"],
            "observations": sim_res["observationCount"],
            "posts": sim_res["postCount"],
            "overall_index": sim_res["democraticHealth"]["overallIndex"],
            "collapse_risk": sim_res["democraticHealth"]["collapseRisk"],
            "social_cohesion": sim_res["democraticHealth"]["socialCohesion"],
            "economic_health": sim_res["democraticHealth"]["economicHealth"],
            "participation_rate": sim_res["democraticHealth"]["participationRate"],
            "trust_weight": params["trustWeight"],
            "altruism_weight": params["altruismWeight"],
            "ambition_weight": params["ambitionWeight"],
            "curiosity_weight": params["curiosityWeight"],
            "fear_weight": params["fearWeight"],
            "decisions_count": len(decisions),
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        records.append(record)
        
        # 5. Optimize parameters
        params = optimize_parameters(sim_res["democraticHealth"], params)
        
    # Export to CSV
    print(f"Exporting simulation data to CSV: {output_csv}...")
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        header = [
            "timestep", "cycle_id", "citizens", "observations", "posts",
            "overall_index", "collapse_risk", "social_cohesion", "economic_health",
            "participation_rate", "trust_weight", "altruism_weight", "ambition_weight",
            "curiosity_weight", "fear_weight", "decisions_count"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        for r in records:
            writer.writerow({
                "timestep": r["timestep"],
                "cycle_id": r["cycle_id"],
                "citizens": r["citizens"],
                "observations": r["observations"],
                "posts": r["posts"],
                "overall_index": f"{r['overall_index']:.6f}",
                "collapse_risk": f"{r['collapse_risk']:.6f}",
                "social_cohesion": f"{r['social_cohesion']:.6f}",
                "economic_health": f"{r['economic_health']:.6f}",
                "participation_rate": f"{r['participation_rate']:.6f}",
                "trust_weight": f"{r['trust_weight']:.6f}",
                "altruism_weight": f"{r['altruism_weight']:.6f}",
                "ambition_weight": f"{r['ambition_weight']:.6f}",
                "curiosity_weight": f"{r['curiosity_weight']:.6f}",
                "fear_weight": f"{r['fear_weight']:.6f}",
                "decisions_count": r["decisions_count"]
            })
            
    # Export to JSON
    print(f"Exporting simulation data to JSON: {output_json}...")
    with open(output_json, 'w', encoding='utf-8') as jsonfile:
        json.dump(records, jsonfile, indent=2)
        
    print("✅ Success! Simulation data generated successfully!")

if __name__ == "__main__":
    main()
