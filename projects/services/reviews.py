class ReviewService:
    
    def get():
        pass
    
    
    def post():
        pass
    
    
    @staticmethod
    def get_reviews(project):
        return project.reviews.all()
    
    @staticmethod
    def total_reviews(project):
        reviews = project.reviews.all()
        return sum([review.get_review_stars() for review in reviews])
    
    @staticmethod
    def average_rating(project):
        reviews = project.reviews.all()
        total_rating = ReviewService.total_reviews(project)
        return total_rating / len(reviews) if reviews else 0