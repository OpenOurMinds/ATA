#!/usr/bin/env python3
import random
import csv
import os
import math

# Target files
demographics_file = "data/demographics_source.csv"
sentiment_file = "data/social_media_sentiment.csv"

# Configuration
num_citizens = 5000
num_posts = 10000
seed_val = 100

random.seed(seed_val)

archetypes = [
    "The Stoic Engineer",
    "The Disillusioned Artist",
    "The Community Builder",
    "The Ambitious Entrepreneur",
    "The Cautious Observer",
    "The Idealistic Activist"
]

activity_templates = [
    {"type": "exercise", "risk": "LOW", "desc": "Running in the park"},
    {"type": "exercise", "risk": "LOW", "desc": "Yoga session at home"},
    {"type": "cooking", "risk": "LOW", "desc": "Preparing a healthy meal"},
    {"type": "driving", "risk": "MEDIUM", "desc": "Commuting during rush hour"},
    {"type": "heavy_lifting", "risk": "MEDIUM", "desc": "Moving boxes into building"},
    {"type": "socializing", "risk": "LOW", "desc": "Meeting friends at cafe"},
    {"type": "working", "risk": "LOW", "desc": "Focused desk work"},
    {"type": "shopping", "risk": "LOW", "desc": "Grocery shopping"},
    {"type": "fast_food", "risk": "HIGH", "desc": "Eating at fast food restaurant"},
    {"type": "smoking", "risk": "HIGH", "desc": "Smoking outside building"},
    {"type": "cycling", "risk": "MEDIUM", "desc": "Cycling without helmet"},
    {"type": "gardening", "risk": "LOW", "desc": "Community garden maintenance"},
    {"type": "volunteering", "risk": "LOW", "desc": "Helping at local shelter"},
    {"type": "studying", "risk": "LOW", "desc": "Self-directed learning"},
    {"type": "sports", "risk": "MEDIUM", "desc": "Playing basketball"}
]

# Post content templates to make it look realistic
post_templates = {
    "The Stoic Engineer": [
        "Optimizing the new backend pipeline. System throughput increased by {val}%.",
        "Focused desk work. Code reviews and system refactoring require complete focus.",
        "Commuting during rush hour. The traffic congestion is an optimization problem waiting to be solved.",
        "Running in the park. Maintaining physical systems is as important as digital ones.",
        "Self-directed learning on decentralized protocols. Fascinating logic.",
        "Preparing a healthy meal. Precise measurements yield consistent nutritional results."
    ],
    "The Disillusioned Artist": [
        "Just a cup of black coffee and another gray morning. What are we all running towards?",
        "Focused desk work... or rather, staring at a blank screen wondering if this is all there is.",
        "Commuting during rush hour. A sea of expressionless faces heading to their offices.",
        "Cycling without helmet. Feeling the wind, ignoring the safety margins just to feel alive.",
        "Smoking outside building. Watching the smoke drift away into the rain. Art is transient.",
        "Meeting friends at cafe. Superficial conversations in a crowded room. Nostalgia hurts."
    ],
    "The Community Builder": [
        "Volunteering at the local shelter. So proud of everyone who showed up to help today!",
        "Community garden maintenance. Small seeds, big future. Let's grow together!",
        "Meeting friends at cafe. Great discussions about our neighborhood cleanup project.",
        "Yoga session at home. Centering myself so I can be present for others.",
        "Preparing a healthy meal for the family. Food is love made visible.",
        "Focused desk work. Organizing the community outreach schedule."
    ],
    "The Ambitious Entrepreneur": [
        "Focused desk work. Refining our seed round deck. Scale is everything.",
        "Commuting during rush hour. Taking calls, closing deals. No time wasted.",
        "Meeting friends at cafe. Networking is the real net worth. Pitching a new project.",
        "Playing basketball. Love the competition, always playing to win.",
        "Self-directed learning. Staying ahead of the curve. Innovation waits for no one.",
        "Eating at fast food restaurant. Quick fuel. Speed is more valuable than standard pacing right now."
    ],
    "The Cautious Observer": [
        "Commuting during rush hour. Always keeping an eye on the emergency exits. Better safe than sorry.",
        "Focused desk work. Double-checking all project dependencies to prevent unexpected issues.",
        "Yoga session at home. Quiet, controlled environment. Perfect for avoiding risks.",
        "Grocery shopping. Stocking up on essentials. Preparation is key.",
        "Running in the park. Staying alert, watching the path carefully.",
        "Smoking outside building. Staying on the sidelines, watching the world spin by."
    ],
    "The Idealistic Activist": [
        "Helping at local shelter. Real change happens from the ground up.",
        "Community garden maintenance. Reclaiming green spaces for the people!",
        "Focused desk work. Writing our manifesto for the upcoming climate action plan.",
        "Running in the park. Reminds me what we are fighting to protect.",
        "Self-directed learning. Knowledge is power. Educate, agitate, organize.",
        "Meeting friends at cafe. Planning the next community campaign over hot drinks."
    ]
}

def generate_demographics():
    print(f"Generating {num_citizens} demographic records...")
    os.makedirs(os.path.dirname(demographics_file), exist_ok=True)
    
    with open(demographics_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "citizenId", "age", "gender", "archetype", "socialCreditScore",
            "trust", "fear", "altruism", "ambition", "curiosity",
            "routine", "riskAverse", "techSavvy", "socialEngagement", "healthConsciousness"
        ])
        
        for i in range(num_citizens):
            citizen_id = f"ALPHA-{random.randint(0, 99):02d}-{random.randint(0, 999):03d}"
            
            # Realistic Age: Normal distribution centered around 42, bounded in [16, 85]
            age = int(random.normalvariate(42, 15))
            age = max(16, min(85, age))
            
            gender = random.choice(["Male", "Female"])
            archetype = random.choice(archetypes)
            
            # Base personality correlations
            trust = random.uniform(0.1, 0.9)
            fear = random.uniform(0.1, 0.9)
            altruism = random.uniform(0.1, 0.9)
            ambition = random.uniform(0.1, 0.9)
            curiosity = random.uniform(0.1, 0.9)
            
            routine = random.uniform(0.1, 0.9)
            risk_averse = random.uniform(0.1, 0.9)
            tech_savvy = random.uniform(0.1, 0.9)
            social_engagement = random.uniform(0.1, 0.9)
            health_consciousness = random.uniform(0.1, 0.9)
            
            # Apply archetype weights to simulate realistic correlations
            if archetype == "The Stoic Engineer":
                routine = random.uniform(0.6, 0.95)
                risk_averse = random.uniform(0.5, 0.9)
                tech_savvy = random.uniform(0.7, 0.99)
                social_engagement = random.uniform(0.1, 0.4)
                curiosity = random.uniform(0.6, 0.95)
                trust = random.uniform(0.3, 0.7)
                fear = random.uniform(0.2, 0.5)
            elif archetype == "The Disillusioned Artist":
                routine = random.uniform(0.1, 0.4)
                risk_averse = random.uniform(0.2, 0.6)
                social_engagement = random.uniform(0.2, 0.6)
                curiosity = random.uniform(0.7, 0.99)
                trust = random.uniform(0.1, 0.5)
                fear = random.uniform(0.5, 0.9)
                altruism = random.uniform(0.4, 0.8)
            elif archetype == "The Community Builder":
                social_engagement = random.uniform(0.7, 0.99)
                altruism = random.uniform(0.7, 0.99)
                trust = random.uniform(0.6, 0.95)
                routine = random.uniform(0.4, 0.8)
                health_consciousness = random.uniform(0.5, 0.9)
            elif archetype == "The Ambitious Entrepreneur":
                ambition = random.uniform(0.7, 0.99)
                risk_averse = random.uniform(0.1, 0.4)
                tech_savvy = random.uniform(0.6, 0.95)
                social_engagement = random.uniform(0.5, 0.9)
                routine = random.uniform(0.3, 0.7)
            elif archetype == "The Cautious Observer":
                risk_averse = random.uniform(0.7, 0.99)
                routine = random.uniform(0.6, 0.9)
                fear = random.uniform(0.6, 0.95)
                social_engagement = random.uniform(0.1, 0.4)
                trust = random.uniform(0.2, 0.5)
            elif archetype == "The Idealistic Activist":
                altruism = random.uniform(0.7, 0.99)
                social_engagement = random.uniform(0.6, 0.95)
                risk_averse = random.uniform(0.2, 0.5)
                routine = random.uniform(0.1, 0.5)
                trust = random.uniform(0.5, 0.9)
                
            # Social Credit Score: correlated with trust, altruism, health, routine, riskAverse
            sc_factor = (trust + altruism + health_consciousness + routine + risk_averse) / 5.0
            social_credit = 20.0 + sc_factor * 75.0 + random.uniform(-5, 5)
            social_credit = max(20.0, min(99.0, social_credit))
            
            writer.writerow([
                citizen_id, age, gender, archetype, f"{social_credit:.4f}",
                f"{trust:.4f}", f"{fear:.4f}", f"{altruism:.4f}", f"{ambition:.4f}", f"{curiosity:.4f}",
                f"{routine:.4f}", f"{risk_averse:.4f}", f"{tech_savvy:.4f}", f"{social_engagement:.4f}", f"{health_consciousness:.4f}"
            ])
            
    print(f"Demographics dataset written to {demographics_file}")

def generate_sentiment_posts():
    print(f"Generating {num_posts} sentiment posts...")
    os.makedirs(os.path.dirname(sentiment_file), exist_ok=True)
    
    with open(sentiment_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "activityType", "activityDescription", "riskLevel",
            "archetype", "textContent", "sentimentScore"
        ])
        
        for _ in range(num_posts):
            act = random.choice(activity_templates)
            arch = random.choice(archetypes)
            
            # Find templates or make default
            templates = post_templates[arch]
            template = random.choice(templates)
            
            # Format text
            val = random.randint(10, 85)
            text_content = template.replace("{val}", str(val))
            
            # Sentiment score based on the archetype and template content
            # General defaults
            sentiment = random.uniform(0.3, 0.7)
            if arch == "The Stoic Engineer":
                if "Optimizing" in text_content or "learning" in text_content:
                    sentiment = random.uniform(0.7, 0.9)
                else:
                    sentiment = random.uniform(0.4, 0.6)
            elif arch == "The Disillusioned Artist":
                if "coffee" in text_content or "black screen" in text_content or "rush hour" in text_content:
                    sentiment = random.uniform(0.1, 0.35)
                else:
                    sentiment = random.uniform(0.3, 0.5)
            elif arch == "The Community Builder":
                if "Volunteering" in text_content or "garden" in text_content or "friends" in text_content:
                    sentiment = random.uniform(0.8, 0.98)
                else:
                    sentiment = random.uniform(0.6, 0.8)
            elif arch == "The Ambitious Entrepreneur":
                if "closing deals" in text_content or "networking" in text_content or "win" in text_content:
                    sentiment = random.uniform(0.75, 0.95)
                else:
                    sentiment = random.uniform(0.5, 0.7)
            elif arch == "The Cautious Observer":
                if "avoiding risks" in text_content or "safe" in text_content:
                    sentiment = random.uniform(0.55, 0.75)
                elif "Smoking" in text_content:
                    sentiment = random.uniform(0.2, 0.4)
                else:
                    sentiment = random.uniform(0.4, 0.6)
            elif arch == "The Idealistic Activist":
                if "Volunteering" in text_content or "manifesto" in text_content or "Reclaiming" in text_content:
                    sentiment = random.uniform(0.75, 0.98)
                else:
                    sentiment = random.uniform(0.5, 0.8)
                    
            writer.writerow([
                act["type"], act["desc"], act["risk"],
                arch, text_content, f"{sentiment:.4f}"
            ])
            
    print(f"Sentiment posts dataset written to {sentiment_file}")

def main():
    print("🧬 Starting Dataset Generation Pipeline...")
    generate_demographics()
    generate_sentiment_posts()
    print("✅ All source datasets generated successfully!")

if __name__ == "__main__":
    main()
