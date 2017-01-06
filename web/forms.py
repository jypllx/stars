from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, TextAreaField, IntegerField, SelectField


class ChannelForm(FlaskForm):
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
    source          = StringField('Source')
    country         = StringField('Pays')
    

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
        self.source.process_data(channel.source)
        self.country.process_data(channel.country)

class ItemForm(FlaskForm):
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
    source          = StringField('Source')
    country         = StringField('Pays')
    

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
        self.source.process_data(channel.source)
        self.country.process_data(channel.country)


class TagForm(FlaskForm):
    id          = StringField('Id*')
    name        = StringField('Nom')
    description = StringField('Description')

    def populate(self, tag):
        self.id.process_data(tag.id)
        self.name.process_data(tag.name)
        self.description.process_data(tag.description)

class PlaylistForm(FlaskForm):
    id          = StringField('Id*')
    name        = StringField('Nom')
    description = StringField('Description')
    mood        = SelectField('Mood', coerce=str)

    def set_moods(self, moods):
        self.mood.choices=[]
        for mood in moods:
            self.mood.choices.append((mood,mood))

    def populate(self, playlist):
        self.id.process_data(str(playlist.id))
        self.name.process_data(playlist.name)
        self.description.process_data(playlist.description)
        self.mood.process_data(playlist.mood)

class MoodForm(FlaskForm):
    mood_file = FileField('Upload moods.xlsx')
