class Event:
    '''
    eg: "id": str(id),
        "summarized_tuple": summarized_tuple,
        "irony": irony,
    '''
    def __init__(self, id=None, summarized_tuple=None, irony=None):
        self.id = id
        self.summarized_tuple = summarized_tuple
        self.irony = irony
        
    def to_dict(self):
        return {
            "id": self.id,
            "summarized_tuple": self.summarized_tuple,
            "irony": self.irony
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            summarized_tuple=data.get("summarized_tuple"),
            irony=data.get("irony")
        )
        
    def __str__(self):
        str = f'Event {self.id}: , summarized_tuple: {self.summarized_tuple}, irony: {self.irony}'
        return str
    
    def extract(self):
        return f"{self.summarized_tuple}"
    
    def get_irony(self):
        return f"{self.irony}"