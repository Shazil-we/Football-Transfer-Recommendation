from flask import Flask, render_template, request, jsonify
from recommender import TransferRecommender

app = Flask(__name__)
rec_engine = TransferRecommender(data_dir=".")

@app.before_request
def startup():
    if not rec_engine.is_loaded:
        rec_engine.load_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/clubs', methods=['GET'])
def get_clubs():
    clubs = rec_engine.get_clubs()
    return jsonify(clubs)

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.json
    club_name = data.get('club_name')
    subrole = data.get('subrole')
    top_k = int(data.get('top_k', 10))

    if not club_name or not subrole:
        return jsonify({"error": "Missing club_name or subrole"}), 400

    recommendations = rec_engine.recommend(club_name, subrole, top_k)
    
    if "error" in recommendations:
        return jsonify(recommendations), 404

    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    