import mongoengine

mongoengine.connect('planning')

class Planning_cyber(mongoengine.Document):
    title = mongoengine.StringField()
    start_date = mongoengine.DateTimeField()
    end_date = mongoengine.DateTimeField()
    event_id = mongoengine.StringField()

    classrooms = mongoengine.ListField(mongoengine.StringField)
    teachers = mongoengine.ListField(mongoengine.StringField)
    groups = mongoengine.ListField(mongoengine.StringField)


