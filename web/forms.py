from wtforms import Form, StringField, TextAreaField

class ChannelForm(Form):
    id              = StringField('Id*')
    
    title_          = StringField('Titre*')
    link_           = StringField('URL*')
    description_    = TextAreaField('Description*')
    itunes_category_= StringField('iTunes cat*')
    language_       = StringField('Langue*')
    author_         = StringField('Auteur*')
    image_          = StringField('Image*')
    last_build_date_= StringField('Mis à jour le*')
    created         = StringField('Création*')

    title           = StringField('Titre Tootak')
    description     = TextAreaField('Description Tootak')    
    mood            = StringField('Mood')
    image           = StringField('Image Tootak')
    

    def populate(self, channel):
        self.title_.process_data(channel.title_)
        self.link_.process_data(channel.link_)
        self.description_.process_data(channel.description_)
        self.itunes_category_.process_data(channel.itunes_category_)
        self.language_.process_data(channel.language_)
        self.author_.process_data(channel.author_)
        self.image_.process_data(channel.image_)
        self.last_build_date_.process_data(channel.last_build_date_)
        self.created.process_data(channel.created)

        self.title.process_data(channel.title)
        self.description.process_data(channel.description)
        self.mood.process_data(channel.mood)
        self.image.process_data(channel.image)
        