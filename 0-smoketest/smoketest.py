#!/usr/bin/env python3
"""
Index Random Data into Solr
Generates and indexes sample documents with vectors for testing
"""

import requests
import json
import numpy as np
from datetime import datetime, timedelta
import random
from typing import List

# Configuration
SOLR_URL = "http://localhost:8983/solr/vector_collection"

# Sample data for random document generation
CATEGORIES = ["Technology", "Science", "Health", "Business", "Entertainment", "Sports", "Education", "Travel"]

TITLES = {
    "Technology": [
        "Introduction to Machine Learning",
        "Deep Learning with Neural Networks",
        "Cloud Computing Fundamentals",
        "Cybersecurity Best Practices",
        "Mobile App Development Guide",
        "Blockchain Technology Explained",
        "Artificial Intelligence in Healthcare",
        "Quantum Computing Basics"
    ],
    "Science": [
        "Climate Change and Global Warming",
        "Genetic Engineering Advances",
        "Space Exploration Updates",
        "Particle Physics Research",
        "Marine Biology Discoveries",
        "Renewable Energy Sources",
        "Neuroscience Breakthroughs",
        "Chemistry in Everyday Life"
    ],
    "Health": [
        "Nutrition and Wellness Tips",
        "Mental Health Awareness",
        "Exercise and Fitness Guide",
        "Sleep Hygiene Practices",
        "Preventive Healthcare Strategies",
        "Meditation and Mindfulness",
        "Healthy Eating Habits",
        "Stress Management Techniques"
    ],
    "Business": [
        "Startup Growth Strategies",
        "Digital Marketing Essentials",
        "Financial Planning Guide",
        "Leadership and Management",
        "E-commerce Success Tips",
        "Project Management Methods",
        "Business Analytics Overview",
        "Customer Service Excellence"
    ],
    "Entertainment": [
        "Movie Reviews and Recommendations",
        "Music Production Techniques",
        "Gaming Industry Trends",
        "Streaming Platform Comparison",
        "Photography Tips and Tricks",
        "Creative Writing Basics",
        "Theater and Performance Arts",
        "Digital Art and Design"
    ],
    "Sports": [
        "Football Training Methods",
        "Basketball Strategy Guide",
        "Marathon Running Tips",
        "Yoga and Flexibility",
        "Swimming Techniques",
        "Tennis Skills Development",
        "Cycling for Fitness",
        "Sports Nutrition Guide"
    ],
    "Education": [
        "Online Learning Platforms",
        "Study Techniques for Students",
        "Educational Technology Tools",
        "Language Learning Methods",
        "STEM Education Importance",
        "Critical Thinking Skills",
        "Teaching Strategies",
        "Academic Writing Guide"
    ],
    "Travel": [
        "Budget Travel Tips",
        "Cultural Destinations Guide",
        "Adventure Travel Ideas",
        "Travel Photography Guide",
        "Solo Travel Safety",
        "Sustainable Tourism Practices",
        "City Travel Itineraries",
        "Beach Vacation Planning"
    ]
}

CONTENT_TEMPLATES = {
    "Technology": [
        "This comprehensive guide explores {} and its applications in modern software development. Learn about key concepts, best practices, and real-world implementations.",
        "Discover how {} is revolutionizing the tech industry. This article covers fundamental principles, advanced techniques, and future trends.",
        "An in-depth look at {} for developers and tech enthusiasts. Includes practical examples and step-by-step tutorials.",
        "Understanding {} has become essential for tech professionals. This resource provides insights into core concepts and practical applications."
    ],
    "Science": [
        "Recent research in {} reveals fascinating insights about our world. This article summarizes key findings and their implications.",
        "Exploring the science behind {}. Learn about cutting-edge research, methodologies, and breakthrough discoveries.",
        "Scientists are making remarkable progress in {}. This comprehensive overview covers current understanding and future directions.",
        "The fascinating world of {} explained for curious minds. Discover how researchers are pushing boundaries of knowledge."
    ],
    "Health": [
        "Improve your wellbeing with evidence-based {} recommendations. This guide provides actionable tips and expert advice.",
        "Understanding {} is crucial for maintaining optimal health. Learn about benefits, techniques, and common misconceptions.",
        "A holistic approach to {} that combines traditional wisdom with modern science. Practical strategies for everyday life.",
        "Expert insights on {} for better health outcomes. Includes research-backed methods and lifestyle recommendations."
    ],
    "Business": [
        "Boost your business success with effective {} strategies. This guide offers proven methods and real-world case studies.",
        "Navigate the complexities of {} in today's competitive market. Learn from industry leaders and successful entrepreneurs.",
        "Master the art of {} to drive growth and profitability. Comprehensive resource for business professionals.",
        "Transform your business with innovative {} approaches. Discover techniques that deliver measurable results."
    ],
    "Entertainment": [
        "Dive into the world of {} with this engaging guide. Discover tips, trends, and insider perspectives.",
        "Everything you need to know about {}. From basics to advanced techniques, this resource covers it all.",
        "Explore the creative realm of {} and unlock your potential. Practical advice for enthusiasts and professionals.",
        "The ultimate guide to {} for entertainment lovers. Includes recommendations, reviews, and expert opinions."
    ],
    "Sports": [
        "Elevate your athletic performance with {} training methods. This guide provides expert coaching and workout plans.",
        "Master {} with professional techniques and strategies. Suitable for beginners and experienced athletes alike.",
        "The complete resource for {} enthusiasts. Learn proper form, avoid injuries, and achieve your fitness goals.",
        "Unlock your potential in {} with science-backed training approaches. Includes nutrition and recovery tips."
    ],
    "Education": [
        "Transform your learning experience with {} strategies. Evidence-based methods for academic success.",
        "The comprehensive guide to {} in modern education. Discover innovative approaches and effective tools.",
        "Enhance educational outcomes through {}. This resource combines research findings with practical applications.",
        "Revolutionize your approach to {} and achieve better results. Expert advice for students and educators."
    ],
    "Travel": [
        "Plan your perfect trip with this {} guide. Insider tips, recommendations, and essential travel advice.",
        "Explore the world through {}. Discover hidden gems, cultural experiences, and travel hacks.",
        "Your ultimate resource for {} adventures. From planning to execution, everything you need to know.",
        "Experience unforgettable journeys with {} recommendations. Expert insights for memorable travel experiences."
    ]
}

TAGS_BY_CATEGORY = {
    "Technology": ["ai", "machine-learning", "software", "cloud", "data-science", "programming", "cybersecurity", "web-dev"],
    "Science": ["research", "physics", "biology", "chemistry", "environment", "space", "innovation", "discovery"],
    "Health": ["wellness", "fitness", "nutrition", "mental-health", "exercise", "healthcare", "lifestyle", "medical"],
    "Business": ["entrepreneurship", "marketing", "finance", "management", "strategy", "growth", "analytics", "leadership"],
    "Entertainment": ["movies", "music", "gaming", "streaming", "art", "culture", "media", "creativity"],
    "Sports": ["training", "fitness", "athletics", "competition", "coaching", "performance", "exercise", "nutrition"],
    "Education": ["learning", "teaching", "academic", "skills", "online", "training", "knowledge", "study"],
    "Travel": ["adventure", "culture", "tourism", "destinations", "vacation", "exploration", "backpacking", "leisure"]
}

def generate_vector(dimension: int = 384, seed: int = None) -> List[float]:
    """Generate a normalized random vector"""
    if seed:
        np.random.seed(seed)
    vector = np.random.randn(dimension)
    # Normalize the vector
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    return vector.tolist()

def generate_document(doc_id: int) -> dict:
    """Generate a random document with metadata and vector"""
    category = random.choice(CATEGORIES)
    title = random.choice(TITLES[category])
    content_template = random.choice(CONTENT_TEMPLATES[category])
    
    # Create content by filling template
    topic = title.lower()
    content = content_template.format(topic)
    
    # Add some variety to content length
    if random.random() > 0.5:
        additional_content = f" Additionally, this approach emphasizes practical implementation and real-world scenarios. Many professionals have found success by applying these principles consistently over time."
        content += additional_content
    
    # Select random tags
    available_tags = TAGS_BY_CATEGORY[category]
    num_tags = random.randint(2, 4)
    tags = random.sample(available_tags, num_tags)
    
    # Generate date within last year
    days_ago = random.randint(0, 365)
    created_date = (datetime.now() - timedelta(days=days_ago)).isoformat() + "Z"
    
    # Generate vector with seed based on doc_id for consistency
    vector = generate_vector(384, seed=doc_id)
    
    return {
        "id": f"doc{doc_id}",
        "title": title,
        "content": content,
        "category": category,
        "tags": tags,
        "content_vector": vector,
        "created_date": created_date
    }

def index_documents(documents: List[dict], batch_size: int = 100) -> None:
    """Index documents in batches"""
    total = len(documents)
    
    for i in range(0, total, batch_size):
        batch = documents[i:i+batch_size]
        
        response = requests.post(
            f"{SOLR_URL}/update/json/docs",
            json=batch,
            params={"commit": "true" if (i + batch_size >= total) else "false"}
        )
        
        if response.status_code == 200:
            print(f"✓ Indexed documents {i+1} to {min(i+batch_size, total)} of {total}")
        else:
            print(f"✗ Error indexing batch {i//batch_size + 1}: {response.text}")
            return
    
    # Final commit
    requests.post(f"{SOLR_URL}/update", params={"commit": "true"})
    print(f"\n✓ Successfully indexed all {total} documents!")

def verify_index():
    """Verify documents were indexed correctly"""
    response = requests.get(
        f"{SOLR_URL}/select",
        params={"q": "*:*", "rows": 0}
    )
    
    if response.status_code == 200:
        result = response.json()
        num_docs = result['response']['numFound']
        print(f"\n{'='*60}")
        print(f"Index Status: {num_docs} documents indexed")
        print(f"{'='*60}")
        
        # Get category breakdown
        facet_response = requests.get(
            f"{SOLR_URL}/select",
            params={
                "q": "*:*",
                "rows": 0,
                "facet": "true",
                "facet.field": "category"
            }
        )
        
        if facet_response.status_code == 200:
            facets = facet_response.json().get('facet_counts', {}).get('facet_fields', {}).get('category', [])
            print("\nDocuments by Category:")
            print("-" * 60)
            for i in range(0, len(facets), 2):
                if i+1 < len(facets):
                    print(f"  {facets[i]}: {facets[i+1]} documents")
        
        return num_docs
    else:
        print(f"✗ Error verifying index: {response.text}")
        return 0

def show_sample_documents(num_samples: int = 5):
    """Display sample documents from the index"""
    response = requests.get(
        f"{SOLR_URL}/select",
        params={
            "q": "*:*",
            "rows": num_samples,
            "fl": "id,title,category,tags",
            "sort": "random_" + str(random.randint(1000, 9999)) + " desc"
        }
    )
    
    if response.status_code == 200:
        docs = response.json()['response']['docs']
        print(f"\n{'='*60}")
        print(f"Sample Documents ({num_samples} random documents):")
        print(f"{'='*60}\n")
        
        for i, doc in enumerate(docs, 1):
            print(f"{i}. [{doc['category']}] {doc['title']}")
            print(f"   ID: {doc['id']}")
            print(f"   Tags: {', '.join(doc['tags'])}")
            print()

def main():
    print("="*60)
    print("Solr Random Data Indexer")
    print("="*60)
    
    # Get number of documents to generate
    try:
        num_docs = int(input("\nHow many documents to generate? [default: 100]: ") or "100")
    except ValueError:
        num_docs = 100
    
    if num_docs < 1 or num_docs > 10000:
        print("⚠ Number must be between 1 and 10000. Using default: 100")
        num_docs = 100
    
    print(f"\n{'='*60}")
    print(f"Generating {num_docs} random documents...")
    print(f"{'='*60}\n")
    
    # Generate documents
    documents = []
    for i in range(1, num_docs + 1):
        doc = generate_document(i)
        documents.append(doc)
        if i % 20 == 0:
            print(f"Generated {i}/{num_docs} documents...")
    
    print(f"\n✓ Generated {len(documents)} documents")
    
    # Index documents
    print(f"\n{'='*60}")
    print("Indexing documents to Solr...")
    print(f"{'='*60}\n")
    
    index_documents(documents)
    
    # Verify indexing
    verify_index()
    
    # Show samples
    show_sample_documents(5)
    
    print(f"\n{'='*60}")
    print("Indexing Complete!")
    print(f"{'='*60}")
    print(f"\nYou can now search your documents at:")
    print(f"  Admin UI: http://localhost:8983/solr/#/vector_collection")
    print(f"  Query: http://localhost:8983/solr/vector_collection/select?q=*:*")
    print()

if __name__ == "__main__":
    main()