from main.models import AppModel, models
# Create your models here.

class KnowledgeTextModel(AppModel):
    name = models.CharField(max_length=255, unique=True)
    text = models.TextField()    
    description = models.TextField()
    
class KnowledgePDFModel(AppModel):
    name = models.CharField(max_length=255, unique=True)
    url = models.URLField()    
    description = models.TextField()
    