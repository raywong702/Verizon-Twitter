from app import db
from sqlalchemy.dialects.postgresql import JSON


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String())
    screen_name = db.Column(db.String())
    place = db.Column(db.String())
    text = db.Column(db.String())
    json = db.Column(JSON)
    __table_args__ = (db.UniqueConstraint('time', 'screen_name', 'text'), )

    def __init__(self, time, screen_name, place, text, json):
        self.time = time
        self.screen_name = screen_name
        self.place = place
        self.text = text
        self.json = json

    def __repr__(self):
###        return '<id {}>'.format(self.id)
        return '<{} ::: {} ::: {} ::: {}>'.format(self.time,
                                                  self.screen_name,
                                                  self.place,
                                                  self.text
                                                 )
