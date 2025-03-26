class Preference:
    '''
    eg: "id": str(id),
        "summarized_tuple": summarized_tuple,
    '''
    def __init__(self, id=None, summarized_tuple=None):
        self.id = id
        self.summarized_tuple = summarized_tuple
        
    def to_dict(self):
        return {
            "id": self.id,
            "summarized_tuple": self.summarized_tuple
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            summarized_tuple=data.get("summarized_tuple")
        )
        
    def __str__(self):
        str = f'Preference {self.id}: , summarized_tuple: {self.summarized_tuple}'
        return str
    
    def extract(self):
        return f"{self.summarized_tuple}"