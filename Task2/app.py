import streamlit as st
import pickle
import pandas as pd
import random

# Page configuration
st.set_page_config(
    page_title="🎬 Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF6B6B;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .movie-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease;
    }
    
    .movie-card:hover {
        transform: translateY(-5px);
    }
    
    .recommendation-header {
        color: #4ECDC4;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 20px 0;
        text-align: center;
    }
    
    .stats-container {
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .search-container {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load movie data and similarity matrix"""
    try:
        movies = pickle.load(open('processed_movie_data.pkl', 'rb'))
        similarity = pickle.load(open('similarity_matrix.pkl', 'rb'))
        return movies, similarity
    except FileNotFoundError:
        st.error("❌ Data files not found! Please ensure 'processed_movie_data.pkl' and 'similarity_matrix.pkl' are in the directory.")
        return None, None

def get_movie_recommendations(movie, movies, similarity, num_recommendations=5):
    """Get movie recommendations with error handling"""
    if movie not in movies['title'].values:
        return ["Movie not found in database."]
    
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:num_recommendations+1]
    
    recommendations = []
    for i, score in movie_list:
        movie_title = movies.iloc[i]['title']
        recommendations.append({
            'title': movie_title,
            'similarity_score': round(score * 100, 1)
        })
    
    return recommendations

def get_random_movies(movies, count=5):
    """Get random movies for suggestions"""
    return random.sample(movies['title'].tolist(), min(count, len(movies)))

# Load data
movies, similarity = load_data()

if movies is not None and similarity is not None:
    # Header
    st.markdown('<h1 class="main-header">🎬 Movie Recommendation System</h1>', unsafe_allow_html=True)
    
    # Sidebar for additional features
    with st.sidebar:
        st.header("🎯 Movie Discovery")
        
        # Statistics
        st.markdown('<div class="stats-container">', unsafe_allow_html=True)
        st.metric("Total Movies", len(movies))
        # st.metric("Recommendations Ready", "✨ Powered by AI")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Random movie suggestions
        st.subheader("🎲 Random Picks")
        if st.button("🔄 Get Random Movies", use_container_width=True):
            st.session_state.random_movies = get_random_movies(movies)
        
        if 'random_movies' in st.session_state:
            for movie in st.session_state.random_movies:
                if st.button(f"🎬 {movie[:30]}{'...' if len(movie) > 30 else ''}", 
                            key=f"random_{movie}", use_container_width=True):
                    st.session_state.selected_movie = movie
        
        # Number of recommendations slider
        st.subheader("⚙️ Settings")
        num_recs = st.slider("Number of recommendations", 3, 10, 5)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Movie selection with search
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        st.subheader("🔍 Find Your Perfect Movie")
        
        # Search functionality
        search_term = st.text_input("🔎 Search for a movie:", placeholder="Type movie name...")
        
        if search_term:
            filtered_movies = movies[movies['title'].str.contains(search_term, case=False, na=False)]['title'].tolist()
            if filtered_movies:
                selected_movie = st.selectbox("Select from search results:", filtered_movies)
            else:
                st.warning("No movies found matching your search.")
                selected_movie = None
        else:
            # Use session state for selected movie if available
            default_movie = st.session_state.get('selected_movie', movies['title'].iloc[0])
            movie_titles = movies['title'].tolist()
            
            if default_movie in movie_titles:
                default_index = movie_titles.index(default_movie)
            else:
                default_index = 0
            
            selected_movie = st.selectbox(
                "Or choose from all movies:",
                movie_titles,
                index=default_index
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Action buttons
        st.subheader("🚀 Actions")
        
        recommend_button = st.button("🎯 Get Recommendations", 
                                   type="primary", 
                                   use_container_width=True)
        
        if st.button("🎲 Surprise Me!", use_container_width=True):
            selected_movie = random.choice(movies['title'].tolist())
            st.session_state.selected_movie = selected_movie
            recommend_button = True
    
    # Display recommendations
    if recommend_button and selected_movie:
        st.markdown(f'<div class="recommendation-header">🌟 Movies Similar to "{selected_movie}"</div>', 
                   unsafe_allow_html=True)
        
        recommendations = get_movie_recommendations(selected_movie, movies, similarity, num_recs)
        
        if isinstance(recommendations, list) and len(recommendations) > 0 and isinstance(recommendations[0], dict):
            # Create columns for better layout
            cols = st.columns(2)
            
            for idx, rec in enumerate(recommendations):
                with cols[idx % 2]:
                    st.markdown(f"""
                    <div class="movie-card">
                        <h3>🎬 {rec['title']}</h3>
                        <p><strong>Match Score:</strong> {rec['similarity_score']}%</p>
                        <div style="background: rgba(255,255,255,0.2); height: 5px; border-radius: 3px; margin: 10px 0;">
                            <div style="background: #4ECDC4; height: 100%; width: {rec['similarity_score']}%; border-radius: 3px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Additional features
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📤 Share Results", use_container_width=True):
                    share_text = f"Check out these movies similar to {selected_movie}:\n"
                    for rec in recommendations:
                        share_text += f"• {rec['title']} ({rec['similarity_score']}% match)\n"
                    st.text_area("Share this:", share_text, height=150)
            
            with col2:
                if st.button("💾 Save Favorites", use_container_width=True):
                    if 'favorites' not in st.session_state:
                        st.session_state.favorites = []
                    st.session_state.favorites.extend([rec['title'] for rec in recommendations])
                    st.success("Added to favorites!")
            
            with col3:
                if st.button("🔄 Get More Like This", use_container_width=True):
                    new_movie = random.choice([rec['title'] for rec in recommendations])
                    st.session_state.selected_movie = new_movie
                    st.rerun()
        
        else:
            st.error("Could not generate recommendations for this movie.")
    
    # Show favorites if they exist
    if 'favorites' in st.session_state and st.session_state.favorites:
        with st.expander("⭐ Your Favorite Recommendations"):
            for fav in set(st.session_state.favorites):  # Remove duplicates
                st.write(f"🎬 {fav}")
            if st.button("🗑️ Clear Favorites"):
                st.session_state.favorites = []
                st.rerun()

else:
    st.error("❌ Unable to load movie data. Please check your data files.")
    st.info("Make sure 'processed_movie_data.pkl' and 'similarity_matrix.pkl' are in your working directory.")