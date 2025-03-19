class Event:
    '''
    eg: "id": 1,
        "question": "Hi, I am Alice. Today, I am here to help you plan your next great travel adventure. What is your name?",
        "user_answer": "My name is Sofia.",
        "emotion": "neutral"
    '''
    def __init__(self, id=None, question=None, user_answer=None, emotion=None):
        self.id = id
        self.question = question
        self.user_answer = user_answer
        self.emotion = emotion
        
    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "user_answer": self.user_answer,
            "emotion": self.emotion
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            question=data.get("question"),
            user_answer=data.get("user_answer"),
            emotion=data.get("emotion")
        )
        
    def __str__(self):
        str = f'Event {self.id}: question: {self.question}, user_answer: {self.user_answer}, emotion: {self.emotion}'
        return str
    
    def extract(self):
        return f"{self.question}? {self.user_answer}"