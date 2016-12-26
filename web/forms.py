from wtforms import Form, StringField, TextAreaField, IntegerField

class ChannelForm(Form):
    id              = StringField('Id*')
    
    title_          = StringField('Titre*')
    link_           = StringField('URL*')
    description_    = TextAreaField('Description*')
    itunes_category_= StringField('iTunes Cat*')
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
        self.id.process_data(channel.id)
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

class ItemForm(Form):
    id              = StringField('Id*')

    channel_        = StringField('Podcast*')
    image_          = StringField('Image*')
    
    title_          = StringField('Titre*')
    description_    = TextAreaField('Description*')
    itunes_category_= StringField('iTunes Cat*')
    pubdate_        = StringField('Date de publication*')
    duration_       = StringField('Durée*')
    audio_url_      = StringField('Lien audio*')

    title           = StringField('Titre Tootak')
    description     = TextAreaField('Description Tootak')    
    mood            = StringField('Mood')
    cat_name        = StringField('Cat durée*')
    created         = StringField('Créé le*')
    

    def populate(self, item, channel):
        self.id.process_data(item.id)
        self.title_.process_data(item.title_)
        self.description_.process_data(item.description_)
        self.itunes_category_.process_data(item.itunes_category_)
        self.pubdate_.process_data(item.pubdate_)
        self.duration_.process_data(item.duration_)
        self.audio_url_.process_data(item.audio_url_)

        self.created.process_data(item.created)
        self.title.process_data(item.title)
        self.description.process_data(item.description)
        self.mood.process_data(item.mood)
        self.cat_name.process_data(item.cat_name)

        self.channel_.process_data(channel.title)
        self.image_.process_data(channel.image)


class TagForm(Form):
    id          = IntegerField('Id*')
    name        = StringField('Nom')
    description = StringField('Description')

    def populate(self, tag):
        self.id.process_data(tag.id)
        self.name.process_data(tag.name)
        self.description.process_data(tag.description)
