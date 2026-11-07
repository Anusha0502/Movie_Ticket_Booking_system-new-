import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(page_title="Movie Booking Dashboard", layout="wide")

# ---------- Get data from MySQL ----------
@st.cache_data
def load_data():
    conn = mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"]
    )
    sql = """
    SELECT b.booking_id, u.name AS user_name, m.movie_name, m.genre,
           t.theater_name, t.location, s.show_time,
           b.seats, b.total_amount, b.booking_date
    FROM Bookings b
    JOIN Users u ON b.user_id = u.user_id
    JOIN Shows s ON b.show_id = s.show_id
    JOIN Movies m ON s.movie_id = m.movie_id
    JOIN Theaters t ON s.theater_id = t.theater_id
    """
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    columns = [c[0] for c in cur.description]
    cur.close()
    conn.close()
    df = pd.DataFrame(rows, columns=columns)
    df["total_amount"] = df["total_amount"].astype(float)
    return df

df = load_data()

# ---------- Title ----------
st.title("🎬 Movie Booking Dashboard")

# ---------- Sidebar filter ----------
st.sidebar.header("Filters")
locations = st.sidebar.multiselect(
    "Select location",
    options=df["location"].unique(),
    default=df["location"].unique()
)
df = df[df["location"].isin(locations)]

# ---------- Top numbers ----------
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"₹{df['total_amount'].sum():,.0f}")
col2.metric("Total Bookings", len(df))
col3.metric("Total Seats", int(df["seats"].sum()))

# ---------- Charts ----------
left, right = st.columns(2)

with left:
    st.subheader("Revenue by Movie")
    movie_rev = df.groupby("movie_name")["total_amount"].sum().sort_values(ascending=False)
    st.bar_chart(movie_rev)

with right:
    st.subheader("Revenue by Genre")
    st.bar_chart(df.groupby("genre")["total_amount"].sum())

# ---------- Table ----------
st.subheader("All Bookings")
st.dataframe(df, use_container_width=True)

# ---------- Download button ----------
st.download_button(
    "Download bookings as CSV",
    df.to_csv(index=False),
    file_name="bookings.csv",
    mime="text/csv"
)