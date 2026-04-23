from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Review, User
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')
analyzer = SentimentIntensityAnalyzer()

PROVINCES = ['Punjab', 'Sindh', 'KPK', 'Balochistan', 'Gilgit Baltistan']

@reviews_bp.route('/<review_type>', methods=['GET'])
def index(review_type):
    if review_type not in ['provincial', 'public']:
        return redirect(url_for('main.index'))
        
    province_filter = request.args.get('province')
    
    query = Review.query.filter_by(type=review_type)
    if review_type == 'provincial' and province_filter in PROVINCES:
        query = query.filter_by(province=province_filter)
        
    reviews = query.order_by(Review.created_at.desc()).all()
    return render_template('reviews/index.html', reviews=reviews, review_type=review_type, current_province=province_filter, provinces=PROVINCES)

@reviews_bp.route('/submit', methods=['POST'])
@login_required
def submit():
    review_type = request.form.get('type', 'public')
    text = request.form.get('text', '')
    province = request.form.get('province')
    rating = request.form.get('rating')
    
    if not text:
        flash('Review text cannot be empty', 'danger')
        return redirect(url_for('reviews.index', review_type=review_type))
        
    # Sentiment Analysis
    vs = analyzer.polarity_scores(text)
    sentiment_score = vs['compound'] # -1 to 1
    
    r_val = int(rating) if rating and rating.isdigit() else None
    
    review = Review(
        user_id=current_user.id,
        type=review_type,
        province=province if review_type == 'provincial' else None,
        text=text,
        rating=r_val,
        sentiment_score=sentiment_score
    )
    
    db.session.add(review)
    current_user.points += 10
    db.session.commit()
    
    flash('Your review has been published!', 'success')
    # pass query parameter if provincial
    if review_type == 'provincial' and province:
        return redirect(url_for('reviews.index', review_type=review_type, province=province))
    return redirect(url_for('reviews.index', review_type=review_type))
