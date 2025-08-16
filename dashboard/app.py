import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import psycopg2
from config.config import DB_CONFIG

# Page configuration
st.set_page_config(
    page_title="Box Office Dashboard",
    page_icon="🍿",
    layout="wide"
)

@st.cache_resource  # Cache for 5 minutes
def get_database_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

@st.cache_data(ttl=300)
def load_data():
    """Load data from database"""
    conn = get_database_connection()
    
    # Top movies query
    top_movies_query = """
        SELECT 
            m.title,
            m.release_date,
            ds.popularity,
            ds.vote_average,
            ds.vote_count,
            m.revenue,
            m.budget,
            CASE 
                WHEN m.poster_path IS NOT NULL 
                THEN 'https://image.tmdb.org/t/p/w500' || m.poster_path 
                ELSE NULL 
            END as poster_url
        FROM movies m
        JOIN daily_stats ds ON m.id = ds.movie_id
        WHERE ds.date = (SELECT MAX(date) FROM daily_stats)
        ORDER BY ds.popularity DESC
        LIMIT 20
    """
    
    top_movies = pd.read_sql(top_movies_query, conn)
    
    # Genre popularity query
    genre_query = """
        SELECT 
            g.name as genre,
            AVG(ds.popularity) as avg_popularity,
            COUNT(*) as movie_count
        FROM genres g
        JOIN movie_genres mg ON g.id = mg.genre_id
        JOIN movies m ON mg.movie_id = m.id
        JOIN daily_stats ds ON m.id = ds.movie_id
        WHERE ds.date = (SELECT MAX(date) FROM daily_stats)
        GROUP BY g.name
        ORDER BY avg_popularity DESC
    """
    
    genre_data = pd.read_sql(genre_query, conn)
    
    # Ratings trend (last 7 days if available)
    trend_query = """
        SELECT 
            ds.date,
            AVG(ds.vote_average) as avg_rating,
            AVG(ds.popularity) as avg_popularity
        FROM daily_stats ds
        WHERE ds.date >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY ds.date
        ORDER BY ds.date
    """
    
    trend_data = pd.read_sql(trend_query, conn)
    
    conn.close()
    return top_movies, genre_data, trend_data

def main():
    # Header
    st.title("🍿 Real-Time Box Office Dashboard")
    st.markdown("---")
    
    # Load data
    try:
        top_movies, genre_data, trend_data = load_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_movies = len(top_movies)
        st.metric("Total Movies", total_movies)
    
    with col2:
        avg_rating = top_movies['vote_average'].mean()
        st.metric("Average Rating", f"{avg_rating:.1f}/10")
    
    with col3:
        total_revenue = top_movies['revenue'].sum()
        st.metric("Total Revenue", f"${total_revenue/1e9:.1f}B")
    
    with col4:
        avg_popularity = top_movies['popularity'].mean()
        st.metric("Avg Popularity", f"{avg_popularity:.0f}")
    
    st.markdown("---")
    
    # Main dashboard layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Top Movies by Popularity")
        
        # Create bar chart
        fig = px.bar(
            top_movies.head(10), 
            x='popularity', 
            y='title',
            orientation='h',
            color='vote_average',
            color_continuous_scale='viridis',
            title="Most Popular Movies Today"
        )
        fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎭 Genre Popularity")
        
        # Pie chart for genres
        fig_pie = px.pie(
            genre_data.head(8), 
            values='avg_popularity', 
            names='genre',
            title="Genre Distribution by Popularity"
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Trends section
    if not trend_data.empty:
        st.subheader("📊 Trends Over Time")
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend_data['date'], 
            y=trend_data['avg_rating'],
            mode='lines+markers',
            name='Average Rating',
            yaxis='y'
        ))
        fig_trend.add_trace(go.Scatter(
            x=trend_data['date'], 
            y=trend_data['avg_popularity'],
            mode='lines+markers',
            name='Average Popularity',
            yaxis='y2'
        ))
        
        fig_trend.update_layout(
            title='Rating and Popularity Trends',
            xaxis_title='Date',
            yaxis=dict(title='Average Rating', side='left'),
            yaxis2=dict(title='Average Popularity', side='right', overlaying='y'),
            hovermode='x'
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # Movie details table
    st.subheader("🎬 Movie Details")
    
    # Display table with selected columns
    display_df = top_movies[['title', 'release_date', 'vote_average', 'popularity', 'revenue']].copy()
    display_df['revenue'] = display_df['revenue'].apply(lambda x: f"${x/1e6:.1f}M" if x > 0 else "N/A")
    display_df.columns = ['Title', 'Release Date', 'Rating', 'Popularity', 'Revenue']
    
    st.dataframe(display_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("*Data updated daily via automated ETL pipeline | Source: TMDb API*")

if __name__ == "__main__":
    main()