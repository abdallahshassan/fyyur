from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, AnyOf, URL, Regexp, Optional

STATES = [
    ('AL', 'AL'),
    ('AK', 'AK'),
    ('AZ', 'AZ'),
    ('AR', 'AR'),
    ('CA', 'CA'),
    ('CO', 'CO'),
    ('CT', 'CT'),
    ('DE', 'DE'),
    ('DC', 'DC'),
    ('FL', 'FL'),
    ('GA', 'GA'),
    ('HI', 'HI'),
    ('ID', 'ID'),
    ('IL', 'IL'),
    ('IN', 'IN'),
    ('IA', 'IA'),
    ('KS', 'KS'),
    ('KY', 'KY'),
    ('LA', 'LA'),
    ('ME', 'ME'),
    ('MT', 'MT'),
    ('NE', 'NE'),
    ('NV', 'NV'),
    ('NH', 'NH'),
    ('NJ', 'NJ'),
    ('NM', 'NM'),
    ('NY', 'NY'),
    ('NC', 'NC'),
    ('ND', 'ND'),
    ('OH', 'OH'),
    ('OK', 'OK'),
    ('OR', 'OR'),
    ('MD', 'MD'),
    ('MA', 'MA'),
    ('MI', 'MI'),
    ('MN', 'MN'),
    ('MS', 'MS'),
    ('MO', 'MO'),
    ('PA', 'PA'),
    ('RI', 'RI'),
    ('SC', 'SC'),
    ('SD', 'SD'),
    ('TN', 'TN'),
    ('TX', 'TX'),
    ('UT', 'UT'),
    ('VT', 'VT'),
    ('VA', 'VA'),
    ('WA', 'WA'),
    ('WV', 'WV'),
    ('WI', 'WI'),
    ('WY', 'WY'),
]

GENRES = [
    ('Alternative', 'Alternative'),
    ('Blues', 'Blues'),
    ('Classical', 'Classical'),
    ('Country', 'Country'),
    ('Electronic', 'Electronic'),
    ('Folk', 'Folk'),
    ('Funk', 'Funk'),
    ('Hip-Hop', 'Hip-Hop'),
    ('Heavy Metal', 'Heavy Metal'),
    ('Instrumental', 'Instrumental'),
    ('Jazz', 'Jazz'),
    ('Musical Theatre', 'Musical Theatre'),
    ('Pop', 'Pop'),
    ('Punk', 'Punk'),
    ('R&B', 'R&B'),
    ('Reggae', 'Reggae'),
    ('Rock n Roll', 'Rock n Roll'),
    ('Soul', 'Soul'),
    ('Other', 'Other'),
]


class ShowForm(Form):
    artist_id = StringField(
        'Artist Id',
        validators=[DataRequired()]
    )
    venue_id = StringField(
        'Venue Id',
        validators=[DataRequired()]
    )
    start_time = DateTimeField(
        'Start Time',
        validators=[DataRequired()],
        format='%Y-%m-%d %H:%M',
        default=datetime.today()
    )


class VenueForm(Form):
    name = StringField(
        'Name', validators=[DataRequired()]
    )
    city = StringField(
        'City', validators=[DataRequired()]
    )
    state = SelectField(
        'State', validators=[DataRequired()],
        choices=STATES
    )
    address = StringField(
        'Address'
    )
    phone = StringField(
        'Phone', validators=[Optional(), Regexp(r'\d{3}-\d{3}-\d{4}', message='Invalid Format')]
    )
    image_link = StringField(
        'Image Link', validators=[DataRequired(), URL()]
    )
    genres = SelectMultipleField(
        'Genres', validators=[DataRequired()],
        choices=GENRES
    )
    website = StringField(
        'Website', validators=[Optional(), URL()]
    )
    facebook_link = StringField(
        'Facebook Link', validators=[Optional(), URL()]
    )
    seeking_talent = BooleanField(
        'Seeking Talent'
    )
    seeking_description = TextAreaField(
        'Seeking Talent Description'
    )


class ArtistForm(Form):
    name = StringField(
        'Name', validators=[DataRequired()]
    )
    city = StringField(
        'City', validators=[DataRequired()]
    )
    state = SelectField(
        'State', validators=[DataRequired()],
        choices=STATES
    )
    phone = StringField(
        'Phone', validators=[Optional(), Regexp(r'\d{3}-\d{3}-\d{4}', message='Invalid Format')]
    )
    image_link = StringField(
        'Image Link', validators=[DataRequired(), URL()]
    )
    genres = SelectMultipleField(
        'Genres', validators=[DataRequired()],
        choices=GENRES
    )
    website = StringField(
        'Website', validators=[Optional(), URL()]
    )
    facebook_link = StringField(
        'Facebook Link', validators=[Optional(), URL()]
    )
    seeking_venue = BooleanField(
        'Seeking Venue'
    )
    seeking_description = TextAreaField(
        'Seeking Description'
    )
