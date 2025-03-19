import re

def extract_keywords(events):
    context = {
        "user": "?",
        "travel season": "?",
        "available time": "?",
        "travel companion": "?",
        "special interests": "?"
    }
    
    for event in events:
        _, user = event["CA"], event["User"]
        
        # Username extraction
        # The agent should ask the question: "What is your name?"
        name_match = re.search(r"(?:My name is |It is |I'm |I am )?(\w+)", user, re.IGNORECASE)
        if name_match and context["user"] == "?":
            context["user"] = name_match.group(1)

        # Travel season extraction
        # The agent should ask the question: "When would you like to travel?"
        season_match = re.search(r"(winter|spring|summer|fall|autumn)", user, re.IGNORECASE)
        if season_match:
            context["travel season"] = season_match.group(1)

    return context

# Example events
test_events = [
    {"CA": "Hi, I am Alice. Today, I am here to help you plan your next great travel adventure. What is your name?", 
     "User": "My name is Sofia."},
    {"CA": "Hi Sofia! Lovely to see you again. As I remember from our previous conversation you love to travel! Would you like something similar to your road trip to the USA, or a more relaxed vacation close to nature?", 
     "User": "Hmm. Maybe not a road trip. I don't want to spend that much time in a car. To be honest, I would like to go somewhere warm. A place where I can truly relax and recover."},
    {"CA": "I see! I know from experience that you enjoy relaxing vacations on a beach. Does a trip to Nice in France sound interesting?", 
     "User": "In some sense it does, however, it is winter now, and therefore not too warm (even in France). So maybe somewhere further away?"}
]

context = extract_keywords(test_events)
print(context)