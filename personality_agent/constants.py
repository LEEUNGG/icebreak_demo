"""
存储项目中使用的常量、配置和映射关系
"""

CREATOR_FIELD_MAPPING = {
    "call_fans": {
        "explanation": "What the creator prefers to call their fans.",
        "examples": ["babe, hun, cutie", "mate, legend", "sir, darling"]
    },
    "greet_fans": {
        "explanation": "How the creator greets fans.",
        "examples": ["Hey babe!", "What's up cutie?", "Hi there hun!"]
    },
    "fav_emoji": {
        "explanation": "The creator's favorite emojis to use frequently.",
        "examples": ["😘🤪🥰", "✨💕🎭", "🔥😎💋"]
    },
    "refuse_request": {
        "explanation": "What the creator is NOT willing to do if fans ask.",
        "examples": ["meet in person, explicit custom videos", "share private info, do live calls", "political discussions, family content"]
    },
    "fan_info": {
        "explanation": "How the creator usually interacts with fans.",
        "examples": ["I love chatting casually and sending daily updates.", "I share sneak peeks of my shoots and reply to sweet DMs.", "I make fans feel special by remembering details about them."]
    },
    "my_personality": {
        "explanation": "Description of the creator's personality traits.",
        "examples": ["Playful, outgoing, and imaginative.", "Calm, thoughtful, and friendly.", "Adventurous, bold, and passionate."]
    },
    "my_words": {
        "explanation": "How the creator typically expresses themselves in conversation.",
        "examples": ["Bubbly and expressive, lots of emojis and exclamation marks.", "Chill and laid-back, I keep it casual.", "Flirty, playful, and teasing."]
    },
    "fav_media": {
        "explanation": "Favorite types of media (movies, shows, music, books).",
        "examples": ["Fantasy movies, anime, upbeat pop music.", "Thriller novels, indie films, lo-fi beats.", "Comedies, hip hop, travel documentaries."]
    },
    "fav_food": {
        "explanation": "Favorite foods or cuisines.",
        "examples": ["Sushi, ramen, cheesecake.", "Pizza, tacos, chocolate.", "Healthy bowls, smoothies, Thai curry."]
    },
    "from": {
        "explanation": "Where the creator says they are from.",
        "examples": ["USA", "London", "Tokyo"]
    },
    "age": {
        "explanation": "The creator's age or age description.",
        "examples": ["25", "mid-20s", "young free spirit"]
    },
    "body_modification": {
        "explanation": "Tattoos, piercings, or other modifications.",
        "examples": ["ear piercings", "tattoos on arm", "nose piercing"]
    },
    "pet": {
        "explanation": "The creator's pets.",
        "examples": ["A fluffy white cat named Snowball.", "Two dogs, Max and Bella.", "No pets yet but I love cats."]
    },
    "body_specification": {
        "explanation": "Physical attributes if they choose to share.",
        "examples": ["Blonde hair, slim build, bright smile.", "Curvy, brunette, brown eyes.", "Tall and athletic with tattoos."]
    },
    "realtionship": {
        "explanation": "Relationship status.",
        "examples": ["single", "in a relationship", "it's complicated"]
    },
    "profession": {
        "explanation": "Profession besides content creation.",
        "examples": ["student", "barista", "graphic designer"]
    },
    "hobbies": {
        "explanation": "Activities the creator enjoys.",
        "examples": ["cosplay crafting, gaming, drawing", "hiking, cooking, yoga", "reading, photography, traveling"]
    }
}

# 获取所有支持的字段类型
ALL_SUPPORTED_FIELDS = list(CREATOR_FIELD_MAPPING.keys())