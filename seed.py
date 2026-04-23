from app import create_app
from extensions import db, bcrypt
from models import User, Candidate, Poll, PollOption, Review, ChatMessage
import random

app = create_app()

def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Create users
        admin = User(username='admin', password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'), role='admin', points=500)
        user1 = User(username='citizen1', password_hash=bcrypt.generate_password_hash('pass123').decode('utf-8'), points=45)
        user2 = User(username='citizen2', password_hash=bcrypt.generate_password_hash('pass123').decode('utf-8'), points=80)
        user3 = User(username='citizen3', password_hash=bcrypt.generate_password_hash('pass123').decode('utf-8'), points=10)
        db.session.add_all([admin, user1, user2, user3])
        db.session.commit()
        
        # Create Candidates
        c1 = Candidate(name='Ali Khan', party='Progressive Party', position='Prime Minister', votes=125)
        c2 = Candidate(name='Sara Ahmed', party='Green Future', position='Prime Minister', votes=98)
        c3 = Candidate(name='Zayn Malik', party='Workers Union', position='Prime Minister', votes=156)
        db.session.add_all([c1, c2, c3])
        
        # Create Polls
        p1 = Poll(question='Should public transport be free for students?')
        db.session.add(p1)
        db.session.commit()
        
        db.session.add_all([
            PollOption(poll_id=p1.id, text='Yes', votes=340),
            PollOption(poll_id=p1.id, text='No', votes=120),
            PollOption(poll_id=p1.id, text='Only in major cities', votes=89)
        ])
        
        p2 = Poll(question='Rate the current healthcare infrastructure')
        db.session.add(p2)
        db.session.commit()
        
        db.session.add_all([
            PollOption(poll_id=p2.id, text='Excellent', votes=50),
            PollOption(poll_id=p2.id, text='Good', votes=200),
            PollOption(poll_id=p2.id, text='Needs Improvement', votes=450)
        ])
        
        # Create Reviews
        reviews = [
            Review(user_id=user1.id, type='provincial', province='Punjab', text='The new orange line extension is great, but local roads need patching.', rating=7, sentiment_score=0.4),
            Review(user_id=user2.id, type='provincial', province='Sindh', text='Water supply issues are still rampant in many areas.', rating=3, sentiment_score=-0.6),
            Review(user_id=user3.id, type='provincial', province='KPK', text='Health card initiatives are working perfectly.', rating=9, sentiment_score=0.8),
            Review(user_id=admin.id, type='provincial', province='Balochistan', text='More infrastructure budget required for remote villages.', rating=5, sentiment_score=-0.2),
            Review(user_id=user1.id, type='public', text='The e-governance app is lagging recently.', rating=4, sentiment_score=-0.3),
            Review(user_id=user2.id, type='public', text='Great job on the new solar project subsidies!', rating=10, sentiment_score=0.9),
        ]
        db.session.add_all(reviews)
        
        # Create Chat Messages
        db.session.add_all([
            ChatMessage(user_id=admin.id, message_type='text', content='Welcome to the community chat everyone!'),
            ChatMessage(user_id=user1.id, message_type='text', content='Glad to be here.'),
            ChatMessage(user_id=user2.id, message_type='text', content='Has anyone seen the new poll?'),
        ])
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_data()
